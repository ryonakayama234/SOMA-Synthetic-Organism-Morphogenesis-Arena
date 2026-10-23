"""F020 preregistered 1536-scene/6144-world deterministic saved-data producer.

Run only at clean source HEAD after protocol freeze f3e3a4de. All findings
remain provisional until the no-producer-import auditor and CI pass.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from experiments.F020.verify import PROTOCOL_SHA, SOURCE_FILES, audit_run
from soma.f020 import scenario_grid, simulate_world

ARTIFACTS = ("worlds.jsonl",)


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False) + "\n"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def provenance() -> dict:
    root = Path(__file__).resolve().parents[2]
    def git(*args: str):
        return subprocess.run(["git", "-C", str(root), *args],
                              capture_output=True, text=True, check=True,
                              timeout=5).stdout.strip()
    head = git("rev-parse", "HEAD")
    if git("status", "--porcelain", "--untracked-files=all"):
        raise ValueError("F020 refuses dirty/untracked source provenance")
    return {"git_commit": head, "git_dirty": False,
            "source_hashes": {p: sha(root / p) for p in SOURCE_FILES}}


def save_suite(destination: Path) -> dict:
    origin = provenance()
    dest = Path(destination)
    if dest.exists() or dest.is_symlink():
        raise FileExistsError(str(dest))
    dest.parent.mkdir(parents=True, exist_ok=True)
    # This directory is not marked valid evidence until manifest and auditor pass.
    dest.mkdir()
    count = 0
    changed_pairs = 0
    enabled_pairs = 0
    scenes = scenario_grid()
    with (dest / "worlds.jsonl").open("w", encoding="utf-8", newline="\n") as fp:
        for scene in scenes:
            for arm in ("YY", "NN"):
                x = simulate_world(scene, arm, "feedback")
                y = simulate_world(scene, arm, "deferred_credit")
                for world in (x, y):
                    fp.write(canonical(world))
                    count += 1
                if x["states"][-1]["x_a_m"] != y["states"][-1]["x_a_m"]:
                    changed_pairs += 1
                if any(a["motor_applied_n"] and not b["motor_applied_n"]
                       for a, b in zip(x["states"][1:], y["states"][1:])):
                    enabled_pairs += 1
    if count != 6144 or len(scenes) != 1536:
        raise ArithmeticError("F020 trial count differs from frozen protocol")
    manifest = {
        "schema_version": "f020.evidence.v1",
        "protocol_anchor_sha": PROTOCOL_SHA,
        "scenarios": len(scenes), "worlds": count,
        "steps_per_world": 4, "seed_values": list(range(32)),
        "counts": {"motor_enabled_forks": enabled_pairs,
                   "feedback_changed_trajectory_pairs": changed_pairs},
        "provenance": origin,
        "artifact_sha256": {p: sha(dest / p) for p in ARTIFACTS},
    }
    (dest / "manifest.json").write_text(canonical(manifest), "utf-8")
    # Fail closed before publishing a successful-process result.
    audit_run(dest)
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    manifest = save_suite(parser.parse_args().output_root)
    print(canonical({"source": manifest["provenance"]["git_commit"],
                     "protocol": manifest["protocol_anchor_sha"],
                     "worlds": manifest["worlds"],
                     "counts": manifest["counts"]}).strip())


if __name__ == "__main__":
    main()
