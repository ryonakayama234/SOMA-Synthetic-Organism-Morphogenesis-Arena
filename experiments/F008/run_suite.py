"""Execute preregistered F008 A-E using the unchanged F007 model.

F covers negative tests, independent saved-oracle checking and exact byte replay.
No synthetic hidden labels are passed to soma.f008.detect.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from soma.f007 import Config, STATE_COLUMNS, provenance, publish_dir, save_run
from soma.f008 import COLUMNS, analyze
from experiments.F007.run_suite import baseline
from experiments.F007.verify import read_csv
from experiments.F008.verify import verify_suite

CASES = ("A-free", "B-linked", "C-cut", "D-hidden-force", "E-empty-battery")


def configuration(case: str) -> dict:
    if case not in CASES:
        raise ValueError("unknown preregistered case")
    raw = baseline(case)
    raw["experiment_id"] = "F008-" + case
    if case == "A-free":
        raw["link"]["initially_attached"] = False
    elif case == "C-cut":
        raw["link"]["detach_time_s"] = .5
    elif case == "D-hidden-force":
        raw["link"]["initially_attached"] = False
        raw["cells"][0]["external_force_n"] = -1.
    elif case == "E-empty-battery":
        raw["link"]["initially_attached"] = False
        raw["cells"][0]["initial_balance_uj"] = 0
    return raw


def build(stage: Path, origin: dict) -> dict:
    for case in CASES:
        directory = stage / case
        directory.mkdir(parents=True)
        source = directory / "F007"
        save_run(Config.from_dict(configuration(case)), source, identity=origin)
        world = read_csv(
            source / "states.csv", STATE_COLUMNS,
            strings=("decision_reason",),
            flags=("attached",),
            integers=("step_index", "spent_a_uj", "balance_a_uj",
                      "balance_b_uj", "ledger_event_index"),
        )
        local = analyze(world)
        with (directory / "local.csv").open("w", encoding="utf-8", newline="") as fp:
            writer = csv.DictWriter(fp, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(local)

    comparison = {
        "schema_version": "f008.evidence.v1",
        "design_ref": "F008 issue 22, design PR 23; controls A-E unchanged",
        "expected_free_accel_m_s2": 2,
        "expected_linked_and_hidden_force_accel_m_s2": 1,
        "expected_cut_accel_m_s2": [1,1,2,2],
        "confound_cannot_prove_attachment": True,
        "science_status": "model_result_pending_independent_review",
    }
    (stage / "comparison.json").write_text(
        json.dumps(comparison, sort_keys=True, indent=2, allow_nan=False)+"\n",
        encoding="utf-8",
    )
    artifacts = {
        str(path.relative_to(stage)):hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(stage.rglob("*")) if path.is_file()
    }
    manifest = {
        "schema_version": "f008.evidence.v1",
        "origin": origin,
        "artifacts": artifacts,
        "source": "adopted F007 saved oracle; F008 independent local verifier",
        "cases": list(CASES),
    }
    (stage / "manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2, allow_nan=False)+"\n",
        encoding="utf-8",
    )
    return verify_suite(stage, trusted_origin=origin)


def suite(destination: Path, *, origin: dict | None = None) -> dict:
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(str(destination))
    identity = provenance() if origin is None else origin
    stage = Path(tempfile.mkdtemp(prefix="." + destination.name + "-stage-",
                                  dir=destination.parent))
    try:
        result = build(stage, identity)
        publish_dir(stage, destination)
        return result
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def compare_bytes(first: Path, second: Path) -> int:
    paths_a = {str(p.relative_to(first)):p for p in first.rglob("*") if p.is_file()}
    paths_b = {str(p.relative_to(second)):p for p in second.rglob("*") if p.is_file()}
    if paths_a.keys() != paths_b.keys():
        raise AssertionError("replay inventory mismatch")
    for key in paths_a:
        if paths_a[key].read_bytes() != paths_b[key].read_bytes():
            raise AssertionError("non-deterministic artifact: " + key)
    return len(paths_a)


def run_pair(first: Path, second: Path) -> dict:
    first, second = Path(first), Path(second)
    if first == second or first.exists() or second.exists():
        raise FileExistsError("require two new distinct destinations")
    identity = provenance()
    created = []
    try:
        result = suite(first, origin=identity)
        created.append(first)
        suite(second, origin=identity)
        created.append(second)
        result["byte_equal_files"] = compare_bytes(first, second)
        return result
    except BaseException:
        for path in created:
            shutil.rmtree(path)
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--replay-output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run_pair(args.output_dir, args.replay_output_dir)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
