"""Produce all 24 F016 pre-registered, independently reset runs and raw evidence."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess

from soma.f007 import STATE_COLUMNS
from soma.f016 import GROUPS, EXPECTED_MEAN_NET_UJ, run_episode
from experiments.F016.verify import verify_suite

SOURCE_FILES = (
    "soma/f002.py", "soma/f005.py", "soma/f007.py", "soma/f016.py",
    "experiments/F016/run_suite.py", "experiments/F016/verify.py",
    "tests/test_f016.py", ".github/workflows/f016.yml",
    "topics/F016-communication-value/SPEC.md",
    "experiments/F016/PLAN.md",
    "findings/F016-validation.md", "docs/ARCHITECTURE.md",
    "docs/DATA_CONTRACTS.md",
)


def canonical(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_provenance() -> dict:
    root = Path(__file__).resolve().parents[2]
    sha = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                         capture_output=True, check=True, text=True, timeout=5).stdout.strip()
    dirty = bool(subprocess.run(["git", "-C", str(root), "status", "--porcelain",
                                "--untracked-files=all"], capture_output=True,
                               check=True, text=True, timeout=5).stdout.strip())
    return {"git_commit": sha, "git_dirty": dirty, "source_hashes": {
        p: fingerprint(root / p) for p in SOURCE_FILES}}


def suite(root: Path) -> dict:
    root = Path(root)
    if root.exists():
        raise FileExistsError("F016 output directory must not preexist")
    src = source_provenance()  # take once, BEFORE creating artifacts
    root.mkdir(parents=True)
    files = []
    summary = []
    for group in GROUPS:
        for trial in range(4):
            run = run_episode(group, trial)
            name = f"{group}_{trial}"
            data_file = root / f"{name}.json"
            data_file.write_bytes(canonical(run))
            files.append(data_file)
            states_file = root / f"{name}_states.csv"
            with states_file.open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=STATE_COLUMNS, lineterminator="\n")
                writer.writeheader()
                for row in run["states"]:
                    writer.writerow(row)
            files.append(states_file)
            summary.append({
                "group": group, "trial": trial, "target_x_m": run["target_x_m"],
                "motor_command_n": run["motor_command_n"], "reached": run["reached"],
                "motor_spent_uj": run["motor_spent_uj"],
                "communication_spent_uj": run["communication_spent_uj"],
                "acquired_uj": run["acquired_uj"], "net_uj": run["net_uj"],
            })
    report = {
        "schema": "f016.suite.v1", "number_of_primary_runs": len(summary),
        "preregistered_mean_net_uj": EXPECTED_MEAN_NET_UJ,
        "observed": summary,
        "mean_net_uj": {
            g: sum(x["net_uj"] for x in summary if x["group"] == g) // 4
            for g in GROUPS
        },
        "claims_excluded": ["physical_radio", "emergent_semantics",
                            "topology_certification", "general_robot_behavior"],
    }
    report_path = root / "comparison.json"
    report_path.write_bytes(canonical(report))
    files.append(report_path)
    manifest = {
        "schema": "f016.evidence.v1", "source": src,
        "artifacts": {p.relative_to(root).as_posix(): fingerprint(p) for p in files},
    }
    (root / "manifest.json").write_bytes(canonical(manifest))
    verify_suite(root)  # separate saved-file math oracle, not scientific peer review
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()
    result = suite(args.output_root)
    print(json.dumps({"runs": result["number_of_primary_runs"],
                      "mean_net_uj": result["mean_net_uj"]}, sort_keys=True))


if __name__ == "__main__":
    main()
