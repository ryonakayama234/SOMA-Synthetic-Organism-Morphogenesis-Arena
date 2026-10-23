"""Rehashed tampering must fail the from-disk semantic oracle, not only SHA checks."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import shutil
import tempfile
from .verify import verify, sha

ATTACKS = ("world_net", "harvest_winner", "harvest_time", "ledger_balance",
           "energy_event", "physics_position", "motor_diagnostic",
           "paired_score", "resource_field", "manifest_totals")

def encoded(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"

def modify(path: Path, attack: str) -> None:
    if path.suffix == ".csv":
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            fields, rows = reader.fieldnames, list(reader)
        if attack == "physics_position":
            rows[1]["x_a_m"] = ".1234567"
        elif attack == "motor_diagnostic":
            target = next(r for r in rows if r["step_index"] == "1")
            target["decision_reason"] = "forged"
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        return
    lines = path.read_text("utf-8").splitlines()
    payload = json.loads(lines[0])
    if attack == "world_net":
        payload["net_uj"]["A"] += 1
    elif attack == "harvest_winner":
        payload["winner_cell_id"] = "B" if payload["winner_cell_id"] == "A" else "A"
    elif attack == "harvest_time":
        payload["entry_fraction_in_step"] += 0.001
    elif attack == "ledger_balance":
        payload["balance_b_uj"] += 1
    elif attack == "energy_event":
        payload["amount_uj"] += 1
    elif attack == "paired_score":
        payload["winner_switch_count"] += 1
    elif attack == "resource_field":
        payload["scenario"]["field"]["patches"][0]["center_m"] += .001
    elif attack == "manifest_totals":
        payload["worlds"] -= 1
    else:
        raise ValueError("unknown attack")
    lines[0] = encoded(payload).rstrip("\n")
    path.write_text("\n".join(lines)+"\n", encoding="utf-8")

def run_attacks(root: Path) -> dict:
    root = Path(root)
    verify(root)
    targets = {
        "world_net": "worlds.jsonl", "harvest_winner": "harvests.jsonl",
        "harvest_time": "harvests.jsonl", "ledger_balance": "ledger.jsonl",
        "energy_event": "events.jsonl", "physics_position": "states.csv",
        "motor_diagnostic": "states.csv", "paired_score": "summary.jsonl",
        "resource_field": "worlds.jsonl", "manifest_totals": "manifest.json",
    }
    rejected = []
    for attack in ATTACKS:
        with tempfile.TemporaryDirectory(prefix="f019-rehashed-") as folder:
            target_root = Path(folder) / "modified"
            shutil.copytree(root, target_root)
            target = target_root / targets[attack]
            modify(target, attack)
            manifest = target_root / "manifest.json"
            m = json.loads(manifest.read_text("utf-8"))
            if attack != "manifest_totals":
                m["artifact_sha256"][target.name] = sha(target)
                manifest.write_text(encoded(m), encoding="utf-8")
            try:
                verify(target_root)
            except (ValueError, AssertionError, KeyError, IndexError):
                rejected.append(attack)
            else:
                raise AssertionError("verifier accepted rehashed " + attack)
    return {"rehashed_attacks_rejected": rejected, "count": len(rejected)}

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    print(json.dumps(run_attacks(p.parse_args().root), sort_keys=True))

if __name__ == "__main__":
    main()
