"""F019 frozen 512-scene / 3584-world source-bound producer."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
from soma.f007 import STATE_COLUMNS
from soma.f019 import ARMS, MOTORS, scenario_grid, simulate_world, summarize

ARTIFACTS = ("worlds.jsonl", "states.csv", "harvests.jsonl", "events.jsonl",
             "ledger.jsonl", "summary.jsonl")
SOURCE_FILES = (
    "soma/f001.py", "soma/f002.py", "soma/f003.py", "soma/f005.py",
    "soma/f007.py", "soma/f018.py", "soma/f019.py",
    "experiments/F019/__init__.py", "experiments/F019/run_suite.py",
    "experiments/F019/verify.py", "experiments/F019/attack_test.py",
    "experiments/F019/analyze.py", "experiments/F019/README.md",
    "tests/test_f019.py", "tests/test_f019_experiment.py",
    ".github/workflows/f019.yml", "experiments/F019/PLAN.md",
    "topics/F019-resource-ecology/SPEC.md", "findings/F019-validation.md",
    "docs/ARCHITECTURE.md", "docs/DATA_CONTRACTS.md",
    "docs/research-notes/2026-10-22-temporary-morphology-and-resource-access.md",
    "README.md",
)

def canonical(value: dict) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(",", ":"), allow_nan=False) + "\n"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def provenance() -> dict:
    root = Path(__file__).resolve().parents[2]
    def git(*args: str) -> str:
        return subprocess.run(["git", "-C", str(root), *args], check=True,
                              capture_output=True, text=True, timeout=5).stdout.strip()
    revision = git("rev-parse", "HEAD")
    if git("status", "--porcelain", "--untracked-files=all"):
        raise ValueError("F019 refuses uncommitted or untracked-source evidence")
    return {"git_commit": revision, "git_dirty": False,
            "source_hashes": {p: sha(root / p) for p in SOURCE_FILES}}

def save_suite(root: Path) -> dict:
    identity = provenance()
    root = Path(root)
    root.mkdir(parents=True, exist_ok=False)
    counts = {"pareto_outside": 0, "pareto_fixed": 0, "winner_switches": 0}
    scenes = scenario_grid()
    nworlds = 0
    with (root/"worlds.jsonl").open("w", encoding="utf-8") as wf, \
         (root/"harvests.jsonl").open("w", encoding="utf-8") as hf, \
         (root/"events.jsonl").open("w", encoding="utf-8") as ef, \
         (root/"ledger.jsonl").open("w", encoding="utf-8") as lf, \
         (root/"summary.jsonl").open("w", encoding="utf-8") as sf, \
         (root/"states.csv").open("w", encoding="utf-8", newline="") as cf:
        writer = csv.DictWriter(cf, fieldnames=("world_id", *STATE_COLUMNS), lineterminator="\n")
        writer.writeheader()
        def save(scene: dict, arm: str, motor: float, label: str) -> dict:
            nonlocal nworlds
            result = simulate_world(scene, arm, motor)
            wid = f"{scene['scenario_id']}::{label}"
            wf.write(canonical({
                "world_id": wid, "scenario": scene,
                "arm": arm, "motor_force_n": motor, "attached": result["attached"],
                "link_events": result["link_events"], "harvests": result["harvests"],
                "acquired_uj": result["acquired_uj"],
                "motor_spent_uj": result["motor_spent_uj"],
                "join_spent_uj": result["join_spent_uj"], "net_uj": result["net_uj"],
            }))
            for row in result["states"]:
                writer.writerow({"world_id": wid, **row})
            for event in result["harvests"]:
                hf.write(canonical({"world_id": wid, **event}))
            for event in result["events"]:
                ef.write(canonical({"world_id": wid, **event}))
            lf.write(canonical({"world_id": wid, **result["ledger"]}))
            nworlds += 1
            return result
        for scene in scenes:
            fixed = float(scene["motor_sign"] * 2)
            primary = {arm: save(scene, arm, fixed, f"primary-{arm}") for arm in ARMS}
            outside = {motor: save(scene, "NN", motor, f"outside-{int(motor):+d}")
                       for motor in MOTORS}
            score = summarize(scene, primary, outside)
            sf.write(canonical(score))
            counts["pareto_outside"] += int(score["pareto_outside"])
            counts["pareto_fixed"] += int(score["pareto_fixed"])
            counts["winner_switches"] += score["winner_switch_count"]
    if len(scenes) != 512 or nworlds != 3584:
        raise ArithmeticError("frozen F019 cardinality mismatch")
    manifest = {
        "schema_version": "f019.evidence.v1", "scenarios": len(scenes),
        "worlds": nworlds, "primary_worlds": 4 * len(scenes),
        "outside_worlds": 3 * len(scenes), "steps_per_world": 4,
        "seed_values": list(range(32)), "counts": counts, "provenance": identity,
        "artifact_sha256": {p: sha(root/p) for p in ARTIFACTS},
    }
    (root/"manifest.json").write_text(canonical(manifest), encoding="utf-8")
    return manifest

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True, type=Path)
    result = save_suite(parser.parse_args().output_root)
    print(canonical({"worlds": result["worlds"], "scenarios": result["scenarios"],
                     "counts": result["counts"]}).strip())

if __name__ == "__main__":
    main()
