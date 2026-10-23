"""F020 on-disk adversarial rehash tests against the independent semantic auditor."""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from .verify import audit_run, sha

ATTACKS = (
    "physics_position", "motor_applied", "patch_claimant",
    "harvest_timestamp", "same_step_credit", "pending_amount",
    "ledger_source", "field_geometry", "manifest_counts",
)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False) + "\n"


def attack_world(original: list[str], attack: str) -> list[str]:
    rows = original.copy()
    target = None
    for i, line in enumerate(rows):
        world = json.loads(line)
        if attack in ("patch_claimant", "harvest_timestamp",
                      "same_step_credit") and not world["harvests"]:
            continue
        if attack == "pending_amount" and (
                world["credit_mode"] != "deferred_credit" or
                not world["harvests"]):
            continue
        if attack == "ledger_source" and not any(
                e["kind"] == "spend" for e in world["events"]):
            continue
        target = (i, world)
        break
    if target is None:
        raise AssertionError("no world suitable for " + attack)
    i, obj = target
    if attack == "physics_position":
        obj["states"][2]["x_a_m"] += .0001
    elif attack == "motor_applied":
        obj["states"][1]["motor_applied_n"] = 77.
    elif attack == "patch_claimant":
        hit = obj["harvests"][0]
        hit["winner_cell_id"] = "A" if hit["winner_cell_id"] == "B" else "B"
    elif attack == "harvest_timestamp":
        obj["harvests"][0]["entry_time_s"] += .001
    elif attack == "same_step_credit":
        obj["states"][1]["available_a_before_uj"] += 1_000_000
    elif attack == "pending_amount":
        obj["states"][1]["pending_a_uj"] += 1
    elif attack == "ledger_source":
        next(e for e in obj["events"] if e["kind"] == "spend")["source_id"] = "B"
    elif attack == "field_geometry":
        obj["scenario"]["field"]["patches"][0]["center_m"] += .01
    else:
        raise AssertionError("unimplemented tamper")
    rows[i] = canonical(obj).rstrip("\n")
    return rows


def run_attacks(root: Path) -> dict:
    root = Path(root)
    audit_run(root)
    originals = (root / "worlds.jsonl").read_text("utf-8").splitlines()
    original_manifest = json.loads((root / "manifest.json").read_text("utf-8"))
    rejected = []
    for kind in ATTACKS:
        with tempfile.TemporaryDirectory(prefix="f020-rehashed-") as td:
            dest = Path(td)
            (dest / "worlds.jsonl").write_text(
                "\n".join(attack_world(originals, kind)) + "\n"
                if kind != "manifest_counts" else
                (root / "worlds.jsonl").read_text("utf-8"), encoding="utf-8")
            manifest = json.loads(json.dumps(original_manifest))
            if kind == "manifest_counts":
                manifest["worlds"] = 6143
            else:
                manifest["artifact_sha256"]["worlds.jsonl"] = sha(dest / "worlds.jsonl")
            (dest / "manifest.json").write_text(canonical(manifest), "utf-8")
            try:
                audit_run(dest)
            except (ValueError, AssertionError, KeyError, TypeError, IndexError):
                rejected.append(kind)
            else:
                raise AssertionError("rehashed semantic forgery was accepted: " + kind)
    if len(rejected) != len(ATTACKS):
        raise AssertionError("adversarial suite incomplete")
    return {"rehashed_attacks_rejected": rejected, "count": len(rejected)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    print(canonical(run_attacks(parser.parse_args().root)).strip())


if __name__ == "__main__":
    main()
