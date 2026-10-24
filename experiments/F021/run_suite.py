"""F021 frozen 4,608-world evidence producer; outputs are never tracked in Git."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from soma.f021 import grid, simulate

FREEZE_COMMIT = "8f82e3b0283b6523041647b38335c466034478f3"


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def provenance():
    proc = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
    return proc.stdout.strip()


def produce(dest: Path, *, smoke: bool = False) -> dict:
    dest.mkdir(parents=True, exist_ok=False)
    main = dest / "worlds.jsonl"
    count = ambiguous = both_positive = mixed = both_negative = neutral = 0
    different_claimants = 0
    rows = {}
    with main.open("w", encoding="utf-8", newline="\n") as h:
        for scene in grid():
            if smoke and count >= 16:
                break
            world = simulate(scene)
            h.write(canonical(world) + "\n")
            count += 1
            ambiguous += world["ambiguous_steps"]
            key = (scene["seed"], scene["sign"], scene["b_relative"],
                   scene["balance_uj"], scene["fee_uj"], scene["count"],
                   scene["radius_m"])
            rows[(key, scene["arm"])] = world
    # Counterfactual YY/NN with matched commands, budgets, fixed resource field.
    pair_count = 0
    seed_metrics = {str(i): {"pairs": 0, "ambiguous_steps": 0,
                              "both_positive": 0, "mixed": 0,
                              "both_negative": 0, "neutral": 0}
                    for i in range(32)}
    for (key, arm), world in rows.items():
        seed_metrics[str(key[0])]["ambiguous_steps"] += world["ambiguous_steps"]
        if arm != "YY":
            continue
        other = rows.get((key, "NN"))
        if other is None:
            if smoke:
                continue
            raise ArithmeticError("missing paired NN world")
        pair_count += 1
        diff = [world["net_uj"][c] - other["net_uj"][c] for c in ("A", "B")]
        label = ("both_positive" if diff[0] > 0 and diff[1] > 0 else
                 "both_negative" if diff[0] < 0 and diff[1] < 0 else
                 "neutral" if diff[0] == 0 or diff[1] == 0 else "mixed")
        if label == "both_positive": both_positive += 1
        elif label == "both_negative": both_negative += 1
        elif label == "mixed": mixed += 1
        else: neutral += 1
        seed_metrics[str(key[0])]["pairs"] += 1
        seed_metrics[str(key[0])][label] += 1
        who_a = {h["patch_id"]: h["winner"] for h in world["harvests"]}
        who_b = {h["patch_id"]: h["winner"] for h in other["harvests"]}
        if who_a != who_b:
            different_claimants += 1
    if not smoke and (count != 4608 or pair_count != 2304):
        raise ArithmeticError("frozen sample missing")
    result = {"schema": "f021.summary.v1", "status": "observed_simulation_only",
              "worlds": count, "paired_yy_nn": pair_count,
              "ambiguous_steps": ambiguous, "both_positive": both_positive,
              "both_negative": both_negative, "mixed": mixed, "neutral": neutral,
              "claimant_map_different_pairs": different_claimants,
              "seed_blocks": 32 if not smoke else len({k[0] for k, a in rows}),
              "per_seed": seed_metrics, "smoke": smoke}
    (dest / "summary.json").write_text(canonical(result) + "\n", encoding="utf-8")
    meta = {"schema": "f021.evidence.v1", "freeze_commit": FREEZE_COMMIT,
            "source_commit": provenance(), "worlds_sha256": sha(main),
            "summary_sha256": sha(dest / "summary.json"),
            "mode": "smoke" if smoke else "primary"}
    (dest / "manifest.json").write_text(canonical(meta) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--smoke", action="store_true", default=False)
    args = p.parse_args()
    print(canonical(produce(args.out, smoke=args.smoke)))
