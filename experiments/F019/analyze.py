"""Descriptive-only F019 reporting from independently verified frozen evidence."""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
from .verify import verify

def analyze(root: Path) -> dict:
    audit = verify(root)
    rows = [json.loads(t) for t in (Path(root)/"summary.jsonl").read_text("utf-8").splitlines()]
    transitions = Counter(
        f"{p['winner_nn'] or 'unclaimed'}->{p['winner_yy'] or 'unclaimed'}"
        for record in rows for p in record["patch_comparison"])
    # Every declared patch must have exactly one pairwise claimant comparison.
    if sum(transitions.values()) != sum(len(row["patch_comparison"]) for row in rows):
        raise AssertionError("paired-patch transition accounting")
    by_seed = {}
    for seed in range(32):
        batch = [row for row in rows if row["base_seed"] == seed]
        by_seed[str(seed)] = {
            "scenarios": len(batch),
            "owner_switches": sum(r["winner_switch_count"] for r in batch),
            "both_outside_positive": sum(r["pareto_outside"] for r in batch),
            "both_outside_negative": sum(all(v < 0 for v in r["delta_outside_uj"].values()) for r in batch),
            "A_outside_negative": sum(r["delta_outside_uj"]["A"] < 0 for r in batch),
            "B_outside_negative": sum(r["delta_outside_uj"]["B"] < 0 for r in batch),
        }
    return {
        "status": "SIMULATED_FROZEN_1D_NOT_ADOPTED",
        "worlds_independently_verified": audit["verified_worlds"],
        "scenarios": len(rows), "independent_environment_seeds": 32,
        "total_patch_owner_switches": sum(r["winner_switch_count"] for r in rows),
        "patch_owner_transitions_NN_to_YY": dict(sorted(transitions.items())),
        "both_outside_positive_scenarios_exploratory": sum(r["pareto_outside"] for r in rows),
        "seed_blocks": by_seed,
        "interpretation": ("These are researcher-fixed, non-learning 1D toy-world causal "
                           "comparisons, not observed voluntary cooperation or emergent bodies."),
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    print(json.dumps(analyze(p.parse_args().root), sort_keys=True))

if __name__ == "__main__":
    main()
