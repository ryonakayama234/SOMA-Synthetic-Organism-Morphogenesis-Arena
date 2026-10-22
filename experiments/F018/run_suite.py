"""F018 deterministic, immutable 630-world preregistered raw-data producer.

90 scenarios * (four fixed-motor consent arms + three NN outside actions).
All outputs are OFF-WORLD researcher records. No agent observes any scenario.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess

from soma.f007 import STATE_COLUMNS
from soma.f018 import (ARMS, OUTSIDE_MOTORS_N, scenario_grid,
                        simulate_world, summarize)

SOURCE_FILES = (
    "soma/f001.py", "soma/f002.py", "soma/f005.py", "soma/f007.py",
    "soma/f018.py", "experiments/F018/run_suite.py",
    "experiments/F018/verify.py", "experiments/F018/analyze.py",
    "experiments/F018/attack_test.py", "tests/test_f018.py",
    "tests/test_f018_experiment.py", ".github/workflows/f018.yml",
    "experiments/F018/PLAN.md", "topics/F018-attachment-value/SPEC.md",
    "findings/F018-validation.md", "docs/ARCHITECTURE.md",
    "docs/DATA_CONTRACTS.md", "README.md",
)
ARTIFACTS = (
    "worlds.jsonl", "states.csv", "events.jsonl",
    "ledger.jsonl", "summary.jsonl",
)


def canonical(record: dict) -> str:
    return json.dumps(record, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False) + "\n"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def provenance() -> dict:
    root = Path(__file__).resolve().parents[2]
    revision = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True, text=True, capture_output=True,
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
        check=True, text=True, capture_output=True,
    ).stdout.strip()
    if dirty:
        raise ValueError("F018 refuses to claim clean-source evidence from dirty checkout")
    return {"git_commit": revision, "git_dirty": False,
            "source_hashes": {p: sha(root / p) for p in SOURCE_FILES}}


def save_suite(output_root: Path) -> dict:
    identity = provenance()
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=False)
    worlds = 0
    scenes = scenario_grid()
    counts = {"pareto_fixed": 0, "pareto_outside": 0}
    with (output_root / "worlds.jsonl").open("w", encoding="utf-8") as wf, (
         output_root / "events.jsonl").open("w", encoding="utf-8") as ef, (
         output_root / "ledger.jsonl").open("w", encoding="utf-8") as lf, (
         output_root / "summary.jsonl").open("w", encoding="utf-8") as sf, (
         output_root / "states.csv").open("w", encoding="utf-8", newline="") as cf:
        writer = csv.DictWriter(cf, fieldnames=("world_id", *STATE_COLUMNS),
                                lineterminator="\n")
        writer.writeheader()

        def persist(scene: dict, arm: str, motor: float, label: str) -> dict:
            nonlocal worlds
            record = simulate_world(scene, arm, motor)
            world_id = f"{scene['scenario_id']}::{label}"
            world = {
                "world_id": world_id, "scenario": scene,
                "arm": arm, "motor_force_n": motor,
                "attached": record["attached"],
                "link_events": record["link_events"],
                "claims": record["claims"],
                "net_uj": record["net_uj"],
                "acquired_uj": record["acquired_uj"],
                "motor_spent_uj": record["motor_spent_uj"],
                "join_spent_uj": record["join_spent_uj"],
            }
            wf.write(canonical(world))
            for row in record["states"]:
                writer.writerow({"world_id": world_id, **row})
            for event in record["events"]:
                ef.write(canonical({"world_id": world_id, **event}))
            lf.write(canonical({"world_id": world_id, **record["ledger"]}))
            worlds += 1
            return record

        for scene in scenes:
            fixed_motor = 2.0 * scene["motor_sign"]
            main = {arm: persist(scene, arm, fixed_motor, f"primary-{arm}")
                    for arm in ARMS}
            outside = {motor: persist(scene, "NN", motor,
                       f"outside-{int(motor):+d}")
                       for motor in OUTSIDE_MOTORS_N}
            score = summarize(main, outside)
            sf.write(canonical(score))
            counts["pareto_fixed"] += int(score["pareto_fixed"])
            counts["pareto_outside"] += int(score["pareto_outside"])
    if worlds != 630:
        raise ArithmeticError("F018 preregistration cardinality violation")
    manifest = {
        "schema_version": "f018.evidence.v1",
        "scenarios": len(scenes), "worlds": worlds, "steps_per_world": 4,
        "primary_worlds": len(scenes)*len(ARMS),
        "outside_worlds": len(scenes)*len(OUTSIDE_MOTORS_N),
        "random_seed": None, "stochastic_draws": 0,
        "counts": counts, "provenance": identity,
        "artifact_sha256": {p: sha(output_root / p) for p in ARTIFACTS},
    }
    (output_root / "manifest.json").write_text(
        canonical(manifest), encoding="utf-8")
    return manifest


def main() -> None:
    p = argparse.ArgumentParser(description="F018 frozen 630-world producer")
    p.add_argument("--output-root", type=Path, required=True)
    a = p.parse_args()
    m = save_suite(a.output_root)
    print(canonical({"root": str(a.output_root), "worlds": m["worlds"],
                     "counts": m["counts"]}).strip())


if __name__ == "__main__":
    main()
