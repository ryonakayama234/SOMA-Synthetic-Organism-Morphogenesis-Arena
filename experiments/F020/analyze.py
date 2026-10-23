"""F020 descriptive paired analysis: original 32 field seeds are the blocks.

No inferential independence assigned to 6144 worlds or 3072 reused-field
counterfactual pairs. No favorable sign or nonzero result is assumed.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path

from .verify import audit_run


def summarize(root: Path) -> dict:
    evidence = audit_run(Path(root))
    pairs: dict[tuple[str, str], dict] = defaultdict(dict)
    with (Path(root) / "worlds.jsonl").open("r", encoding="utf-8") as fp:
        for line in fp:
            w = json.loads(line)
            pairs[(w["scenario"]["scenario_id"], w["arm"])][w["credit_mode"]] = w
    by_group = defaultdict(lambda: {"pairs": 0, "changed": 0,
                                    "enabled": 0, "positive": 0, "negative": 0,
                                    "claimant_changed": 0})
    by_seed = {s: {"pairs": 0, "changed": 0, "enabled": 0} for s in range(32)}
    for (scene_id, arm), forks in pairs.items():
        active, deferred = forks["feedback"], forks["deferred_credit"]
        scene = active["scenario"]
        seed, balance = scene["base_seed"], scene["initial_balance_uj"]
        a_states, d_states = active["states"], deferred["states"]
        delta = (a_states[-1]["x_a_m"] - d_states[-1]["x_a_m"]) * scene["motor_sign"]
        changed = a_states[-1]["x_a_m"] != d_states[-1]["x_a_m"]
        enabled = any(a["motor_applied_n"] != 0. and d["motor_applied_n"] == 0.
                      for a, d in zip(a_states[1:], d_states[1:]))
        ownership = lambda w: {h["patch_id"]: h["winner_cell_id"]
                               for h in w["harvests"]}
        switch = ownership(active) != ownership(deferred)
        group = by_group[f"{balance}uJ/{arm}"]
        group["pairs"] += 1
        group["changed"] += int(changed)
        group["enabled"] += int(enabled)
        group["positive"] += int(delta > 1e-11)
        group["negative"] += int(delta < -1e-11)
        group["claimant_changed"] += int(switch)
        block = by_seed[seed]
        block["pairs"] += 1
        block["changed"] += int(changed)
        block["enabled"] += int(enabled)
    if len(pairs) != 3072:
        raise AssertionError("bad paired sample cardinality")
    result = {"status": "DESCRIPTIVE_SOURCE_BOUND_PRIMARY_OBSERVATION",
              "source_sha": evidence["source_sha"],
              "protocol_sha": "f3e3a4de4ff47677db575efaafe342655dede6c2",
              "field_seed_blocks": 32,
              "scenarios": evidence["scenarios"],
              "worlds": evidence["worlds"],
              "paired_topology_credit_comparisons": len(pairs),
              "overall": evidence["counts"],
              "by_balance_and_topology": dict(sorted(by_group.items())),
              "seed_block_nonzero_count": sum(v["changed"] > 0 for v in by_seed.values()),
              "per_seed_block": by_seed,
              "interpretation_limit": (
                  "32 reused F019 field seed blocks, not 3072 independent samples; "
                  "researcher-fixed topology, A-only effective motor, no learner")}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    result = summarize(parser.parse_args().root)
    print(json.dumps(result, sort_keys=True, separators=(",", ":"),
                     allow_nan=False, ensure_ascii=True))


if __name__ == "__main__":
    main()
