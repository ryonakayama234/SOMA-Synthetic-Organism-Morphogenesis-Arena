"""F018 semantic falsification even when a forger updates SHA256 manifests."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import shutil
import tempfile

from .verify import verify, sha
from .run_suite import canonical


def run_attacks(root: Path) -> dict:
    verify(root)
    cases = ("score", "physics", "ledger",
             "state_initial_candidate", "state_initial_work",
             "state_reason", "state_motor_index",
             "state_zero_motor_candidate")
    rejected = []
    for attack in cases:
        with tempfile.TemporaryDirectory(prefix="f018-attack-") as folder:
            test = Path(folder)/"altered"
            shutil.copytree(root, test)
            if attack == "score":
                path = test/"worlds.jsonl"
                lines = path.read_text("utf-8").splitlines()
                first = json.loads(lines[0])
                first["net_uj"]["A"] += 1
                lines[0] = canonical(first).rstrip("\n")
                path.write_text("\n".join(lines)+"\n",encoding="utf-8")
            elif attack == "physics" or attack.startswith("state_"):
                path = test/"states.csv"
                with path.open("r",newline="",encoding="utf-8") as fp:
                    reader = csv.DictReader(fp)
                    headers = reader.fieldnames
                    rows = list(reader)
                if attack == "physics":
                    rows[0]["x_a_m"] = "0.125"
                elif attack == "state_initial_candidate":
                    rows[0]["candidate_motor_work_j"] = "0.0"  # should be null
                elif attack == "state_initial_work":
                    rows[0]["motor_positive_work_j"] = "9.0"
                elif attack == "state_reason":
                    rows[1]["decision_reason"] = "forged_accepted"
                elif attack == "state_motor_index":
                    rows[1]["ledger_event_index"] = "999"
                elif attack == "state_zero_motor_candidate":
                    target = next(row for row in rows
                        if row["world_id"].endswith("outside-+0") and
                           row["step_index"] == "1")
                    target["candidate_motor_positive_work_j"] = "0.0"
                with path.open("w",newline="",encoding="utf-8") as fp:
                    writer = csv.DictWriter(fp,fieldnames=headers,lineterminator="\n")
                    writer.writeheader()
                    writer.writerows(rows)
            else:
                path = test/"events.jsonl"
                lines = path.read_text("utf-8").splitlines()
                first = json.loads(lines[0])
                first["amount_uj"] += 1
                lines[0] = canonical(first).rstrip("\n")
                path.write_text("\n".join(lines)+"\n",encoding="utf-8")
            manifest_path = test/"manifest.json"
            manifest = json.loads(manifest_path.read_text("utf-8"))
            manifest["artifact_sha256"][path.name] = sha(path)
            manifest_path.write_text(canonical(manifest),encoding="utf-8")
            try:
                verify(test)
            except (ValueError, KeyError, AssertionError):
                rejected.append(attack)
            else:
                raise AssertionError("independent oracle accepted rehashed "+attack+" forgery")
    return {"rehashed_semantic_attacks_rejected":rejected}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    print(json.dumps(run_attacks(p.parse_args().root),sort_keys=True))


if __name__ == "__main__":
    main()
