"""F014 frozen 15-run F007 experiment, local B packets, and two-root replay."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from soma.f007 import Config, STATE_COLUMNS, provenance, publish_dir, save_run
from soma.f008 import COLUMNS, analyze, project_local
from soma.f014 import PeerPacket, THRESHOLD_M_S, estimate_trial, packet_csv_row
from experiments.F007.run_suite import baseline
from experiments.F007.verify import read_csv
from experiments.F014.verify import verify_suite

GROUPS = ("L-linked", "G-ghost", "C-coforced", "N-free", "E-unexcited")
FORCES = ((2., "u2"), (1., "u1"), (.5, "u05"))
PACKET_COLUMNS = ("source", "step_index", "time_s", "moved")
SOURCE_FILES = (
    "soma/f014.py", "experiments/F014/run_suite.py",
    "experiments/F014/verify.py", "tests/test_f014.py",
    ".github/workflows/f014.yml",
    "topics/F014-peer-body-observability/SPEC.md",
    "experiments/F014/PLAN.md", "experiments/F014/README.md",
    "findings/F014-validation.md", "docs/ARCHITECTURE.md",
    "docs/DATA_CONTRACTS.md", "README.md", "AGENTS.md",
)


def configuration(group: str, force: float) -> dict:
    if group not in GROUPS or type(force) not in (int, float) or force not in (2., 1., .5):
        raise ValueError("non-preregistered F014 condition")
    c = baseline("B-linked")
    c["experiment_id"] = "F014-" + group + "-" + dict(FORCES)[force]
    c["motor_force_n"] = float(force)
    c["link"]["initially_attached"] = group == "L-linked"
    if group in ("G-ghost", "C-coforced"):
        c["cells"][0]["external_force_n"] = -float(force)/2
    if group == "C-coforced":
        c["cells"][1]["external_force_n"] = float(force)/2
    if group == "E-unexcited":
        c["cells"][0]["initial_balance_uj"] = 0
    return c


def origin_snapshot() -> dict:
    root = Path(__file__).resolve().parents[2]
    return {"f007": provenance(),
            "f014_source_hashes": {
                name: hashlib.sha256((root/name).read_bytes()).hexdigest()
                for name in SOURCE_FILES}}


def _json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, sort_keys=True, indent=2,
                               allow_nan=False) + "\n", encoding="utf-8")


def make_run(path: Path, group: str, force: float, origin: dict) -> dict:
    path.mkdir(parents=True)
    # Explicit frozen F014 envelope: researcher-only, never passed to inference.
    _json(path/"config.json", {
        "schema_version": "f014.config.v1",
        "experiment_id": "F014-"+group+"-"+dict(FORCES)[force],
        "case_id": group, "u_n": float(force),
        "dt_s": .25, "duration_s": 1.,
        "packet_threshold_m_s": THRESHOLD_M_S, "seed": None,
    })
    save_run(Config.from_dict(configuration(group, force)), path/"F007",
             identity=origin["f007"])
    rows = read_csv(path/"F007/states.csv", STATE_COLUMNS,
                    strings=("decision_reason",), flags=("attached",),
                    integers=("step_index", "spent_a_uj", "balance_a_uj",
                              "balance_b_uj", "ledger_event_index"))
    locals_ = [project_local(p, q) for p, q in zip(rows, rows[1:])]
    with (path/"a_local.csv").open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(analyze(rows))
    # This adapter is researcher-only and must never supply B numeric velocity
    # or F007 coupling/external forces to soma.f014. Only the boolean survives.
    packets = tuple(PeerPacket("B", q["step_index"], q["time_s"],
                              abs(q["v_b_m_s"]-p["v_b_m_s"]) > THRESHOLD_M_S)
                    for p, q in zip(rows, rows[1:]))
    with (path/"b_packets.csv").open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=PACKET_COLUMNS)
        writer.writeheader()
        writer.writerows(packet_csv_row(p) for p in packets)
    return estimate_trial(tuple(locals_), packets)


def build(stage: Path, origin: dict) -> dict:
    outcomes = {}
    for group in GROUPS:
        outcomes[group] = {}
        for force, tag in FORCES:
            outcomes[group][tag] = make_run(stage/group/tag, group, force, origin)
    separated, counterexample, local_identical = True, True, True
    dropout = {}
    for _, tag in FORCES:
        base = stage/"L-linked"/tag
        ghost = stage/"G-ghost"/tag
        coforced = stage/"C-coforced"/tag
        linked_bits = (base/"b_packets.csv").read_bytes()
        ghost_bits = (ghost/"b_packets.csv").read_bytes()
        cf_bits = (coforced/"b_packets.csv").read_bytes()
        separated &= linked_bits != ghost_bits
        counterexample &= linked_bits == cf_bits
        local_identical &= all(
            (base/"a_local.csv").read_bytes() == (stage/group/tag/"a_local.csv").read_bytes()
            for group in ("G-ghost", "C-coforced"))
        # Deliberately drop the second B packet without rerunning the world.
        with (base/"F007/states.csv").open(newline="", encoding="utf-8") as fp:
            raw = list(csv.DictReader(fp))
        converted = read_csv(base/"F007/states.csv", STATE_COLUMNS,
                             strings=("decision_reason",), flags=("attached",),
                             integers=("step_index", "spent_a_uj", "balance_a_uj",
                                       "balance_b_uj", "ledger_event_index"))
        local = tuple(project_local(a, b) for a, b in zip(converted, converted[1:]))
        bits = tuple(PeerPacket("B", k, k*.25, True) for k in range(1, 5))
        altered = bits[:1] + (None,) + bits[2:]
        dropout[tag] = estimate_trial(local, altered)
        if dropout[tag]["status"] != "inconclusive":
            raise AssertionError("missing B packet must cause inconclusive result")
    if not (separated and counterexample and local_identical):
        raise AssertionError("frozen F014 observation hypotheses contradicted")
    _json(stage/"comparison.json", {
        "schema_version": "f014.comparison.v1",
        "science_status": "software_model_candidate_not_adopted",
        "researcher_truth_only": True, "fixed_cases": list(GROUPS),
        "force_levels_n": [2., 1., .5], "intervals": 60,
        "outcomes": outcomes, "dropout_diagnostics": dropout,
        "A_local_LGC_byte_equal": local_identical,
        "L_G_peer_bits_differ": separated,
        "L_C_full_observation_equal": counterexample,
        "topology_identified": False,
    })
    paths = {p.relative_to(stage).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(stage.rglob("*")) if p.is_file()}
    _json(stage/"manifest.json", {
        "schema_version": "f014.evidence.v1",
        "origin": origin, "cases": list(GROUPS), "artifacts": paths,
    })
    return verify_suite(stage, origin)


def _check_paths(a: Path, b: Path) -> None:
    a, b = a.resolve(), b.resolve()
    if a == b or a in b.parents or b in a.parents:
        raise ValueError("same/nested replay targets")
    if a.exists() or b.exists():
        raise FileExistsError("refusing existing evidence output")


def suite(output: Path, replay: Path, *, origin: dict | None = None) -> dict:
    a, b = Path(output), Path(replay)
    _check_paths(a, b)
    a.parent.mkdir(parents=True, exist_ok=True)
    b.parent.mkdir(parents=True, exist_ok=True)
    identity = origin_snapshot() if origin is None else origin
    sa = Path(tempfile.mkdtemp(prefix=".f014-A-", dir=a.parent))
    sb = Path(tempfile.mkdtemp(prefix=".f014-B-", dir=b.parent))
    try:
        result = build(sa, identity)
        build(sb, identity)
        first = {p.relative_to(sa).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sa.rglob("*") if p.is_file()}
        second = {p.relative_to(sb).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in sb.rglob("*") if p.is_file()}
        if first != second:
            raise AssertionError("F014 independent replay mismatch")
        _check_paths(a, b)
        publish_dir(sa, a)
        try:
            publish_dir(sb, b)
        except BaseException:
            shutil.rmtree(a)
            raise
        return {**result, "byte_replay": True, "replay_files": len(first)}
    finally:
        for p in (sa, sb):
            if p.exists():
                shutil.rmtree(p)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--replay-output-dir", required=True)
    args = parser.parse_args()
    print(json.dumps(suite(Path(args.output_dir), Path(args.replay_output_dir)),
                     sort_keys=True))


if __name__ == "__main__":
    main()
