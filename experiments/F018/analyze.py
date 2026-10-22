"""Report only independently audited F018 saved-world results; no learned consent."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .verify import verify


def analyze(root: Path) -> dict:
    result = verify(root)
    data = [json.loads(line) for line in (root/"summary.jsonl").read_text("utf-8").splitlines()]
    f = lambda x: x["delta_fixed_uj"]
    o = lambda x: x["delta_outside_uj"]
    cases = {}
    for layout in ("NONE","B_LINK","A_SOLO","DUAL_LINK","DUAL_SOLO"):
        subset = [s for s in data if s["scenario_id"].startswith(layout+"-")]
        cases[layout] = {
            "count":len(subset),
            "both_fixed_positive":sum(1 for s in subset if all(v>0 for v in f(s).values())),
            "both_outside_positive":sum(1 for s in subset if all(v>0 for v in o(s).values())),
            "one_or_more_outside_negative":sum(1 for s in subset if any(v<0 for v in o(s).values())),
        }
    def example(layout: str) -> dict:
        key = f"{layout}-s+1-r010-fee100000"
        sample = next(s for s in data if s["scenario_id"] == key)
        return {k: sample[k] for k in ("scenario_id","primary_net_uj",
                "outside_best_uj","delta_fixed_uj","delta_outside_uj")}
    return {**result, "by_resource_layout":cases,
            "example_dual_link":example("DUAL_LINK"),
            "example_b_link":example("B_LINK"),
            "interpretation": "deterministic artificial terminal resources; researcher-only ex-post outside menu; no autonomous learning, ecological generalization, or voluntary joining shown"}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    r = analyze(p.parse_args().root)
    print(json.dumps(r,sort_keys=True,indent=2))


if __name__ == "__main__":
    main()
