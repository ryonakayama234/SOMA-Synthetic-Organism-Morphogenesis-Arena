"""Independently re-derive F016 from SAVED traces, without f016/simulator imports.

Same-author independent implementation is NOT external human peer review.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import math
import subprocess

SOURCE_FILES = {
    "soma/f002.py", "soma/f005.py", "soma/f007.py", "soma/f016.py",
    "experiments/F016/run_suite.py", "experiments/F016/verify.py",
    "tests/test_f016.py", ".github/workflows/f016.yml",
    "topics/F016-communication-value/SPEC.md", "experiments/F016/PLAN.md",
    "findings/F016-validation.md", "docs/ARCHITECTURE.md", "docs/DATA_CONTRACTS.md",
}
GROUPS = ("A0", "K", "S", "T", "H", "I")
TARGETS = (.625, -.625, .625, -.625)
SHUFFLE = (True, True, False, False)
PREDICTED = {"A0": 500000, "K": 450000, "S": 450000,
             "T": 1950000, "H": 0, "I": -1050000}
STEP_SPENT = (62500, 187500, 312500, 437500)


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError("F016 independent evidence rejection: " + reason)


def near(actual: object, expected: float, label: str, tolerance: float = 1e-12) -> None:
    require(type(actual) in (int, float) and math.isfinite(actual)
            and abs(actual - expected) <= tolerance, label)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify_episode(record: dict, group: str, trial: int) -> None:
    require(record["schema"] == "f016.action.v1" and record["group"] == group
            and type(record["trial"]) is int and record["trial"] == trial,
            "identity mismatch")
    target = TARGETS[trial]
    true_right = target > 0.1
    expected_fee = 0 if group == "A0" else (2_000_000 if group == "H" else 50_000)
    expected_right = {"A0": True, "K": True, "S": SHUFFLE[trial],
                      "T": true_right, "H": true_right, "I": not true_right}[group]
    packet = record["packet"]
    if group == "A0":
        require(packet is None, "A-only has packet")
    else:
        require(type(packet) is dict
                and packet == {"source_id": "B", "step_index": 0,
                               "time_s": 0.0, "resource_right": expected_right},
                "packet source/time/bit forged")
    direction = 1 if expected_right else -1
    force = 2.0 * direction
    cfg = record["f007_config"]
    require(cfg["schema_version"] == "f007.v1" and cfg["experiment_id"] == f"F016-{group}-{trial}"
            and cfg["seed"] is None and cfg["dt_s"] == .25
            and cfg["duration_s"] == 1.0 and cfg["drag_per_s"] == 0.0
            and cfg["motor_force_n"] == force
            and cfg["link"] == {"initially_attached": True, "length_m": .1,
                                "detach_time_s": None}, "physical world cfg")
    require(cfg["cells"] == [
        {"id": "A", "mass_kg": 1.0, "initial_x_m": 0.0, "initial_v_m_s": 0.0,
         "external_force_n": 0.0, "capacity_uj": 20_000_000,
         "initial_balance_uj": 10_000_000},
        {"id": "B", "mass_kg": 1.0, "initial_x_m": 0.1, "initial_v_m_s": 0.0,
         "external_force_n": 0.0, "capacity_uj": 20_000_000,
         "initial_balance_uj": 10_000_000},
    ], "mass/initial position/balance world cfg")
    require(record["b_observed_right"] is true_right, "B truth projection")
    near(record["target_x_m"], target, "resource target")
    near(record["motor_command_n"], force, "force")
    rows = record["states"]
    require(type(rows) is list and len(rows) == 5, "raw state count")
    balance = 10_000_000
    for k, row in enumerate(rows):
        require(type(row["step_index"]) is int and row["step_index"] == k
                and row["attached"] is True, "step/link")
        near(row["time_s"], k/4, "time")
        near(row["x_a_m"], force*k*(k+1)/64, "semi-implicit x")
        near(row["x_b_m"], .1 + force*k*(k+1)/64, "rigid xB")
        near(row["v_a_m_s"], force*k/8, "velocity A")
        near(row["v_b_m_s"], force*k/8, "velocity B")
        spent = 0 if k == 0 else STEP_SPENT[k-1]
        balance -= spent
        require(row["spent_a_uj"] == spent and row["balance_a_uj"] == balance
                and row["balance_b_uj"] == 10_000_000,
                "F007 per-step battery")
        near(row["motor_applied_n"], 0 if k == 0 else force,
             "motor applied")
        near(row["link_force_b_n"], 0 if k == 0 else force/2, "link impulse force")
        near(row["link_force_a_n"], 0 if k == 0 else -force/2, "reaction force")
        near(row["mechanical_residual_j"], 0, "mechanical energy residual")
        if k:
            near(row["motor_positive_work_j"], spent/1e6, "motor positive work")
            near(row["kinetic_delta_j"], spent/1e6, "kinetic delta")
        else:
            near(row["motor_positive_work_j"], 0, "initial motor work")
    motor_log = record["f007_motor_events"]
    require(type(motor_log) is list and len(motor_log) == 4,
            "F007 motor ledger event count")
    for k, e in enumerate(motor_log):
        require(e["amount_uj"] == STEP_SPENT[k] and e["source_id"] == "A"
                and e["kind"] == "spend" and e["event_index"] == k+1,
                "F007 ledger event")

    success = force * target > 0
    reward = 3_000_000 if success else 0
    net = reward - 1_000_000 - expected_fee
    require(record["reached"] is success
            and record["acquired_uj"] == reward
            and record["motor_spent_uj"] == 1_000_000
            and record["communication_spent_uj"] == expected_fee
            and record["net_uj"] == net
            and record["ledger_residual_uj"] == 0, "independent task/net result")
    require(record["balance_a_uj"] == 9_000_000 + reward
            and record["balance_b_uj"] == 10_000_000 - expected_fee,
            "F002 aggregate ending balance")
    sidecar = record["f002_sidecar_events"]
    require(type(sidecar) is list and len(sidecar) == 4 + (group != "A0") + success,
            "F002 event count")
    expected_actions = ([("spend", "B", None, expected_fee)] if group != "A0" else []) + [
        ("spend", "A", None, amount) for amount in STEP_SPENT
    ] + ([("acquire", None, "A", reward)] if success else [])
    for i, (entry, action) in enumerate(zip(sidecar, expected_actions)):
        kind, source, recipient, amount = action
        require(entry["event_index"] == i+1
                and entry["kind"] == kind and entry["source_id"] == source
                and entry["target_id"] == recipient and entry["amount_uj"] == amount
                and entry["residual_uj"] == 0, "F002 event/sidecar sequence")


def verify_suite(root: Path) -> dict:
    root = Path(root)
    manifest = read_json(root/"manifest.json")
    require(manifest["schema"] == "f016.evidence.v1", "manifest schema")
    src = manifest["source"]
    require(set(src["source_hashes"]) == SOURCE_FILES, "source file omission")
    checkout = Path(__file__).resolve().parents[2]
    git_head = subprocess.run(["git", "-C", str(checkout), "rev-parse", "HEAD"],
                              capture_output=True, check=True, text=True, timeout=5).stdout.strip()
    require(src["git_commit"] == git_head and not src["git_dirty"],
            "untrusted source commit / dirty")
    for name, expected in src["source_hashes"].items():
        require(digest(checkout/name) == expected, "source changed after trial: " + name)
    expected_files = {"comparison.json"} | {
        f"{g}_{t}{ending}" for g in GROUPS for t in range(4)
        for ending in (".json", "_states.csv")
    }
    require(set(manifest["artifacts"]) == expected_files, "missing/replaced artifact")
    for name, expected_hash in manifest["artifacts"].items():
        require(digest(root/name) == expected_hash, "bad artifact hash: " + name)
    require({p.name for p in root.iterdir()} == expected_files | {"manifest.json"},
            "extra or missing evidence file")

    totals = {}
    summary_rows = []
    for group in GROUPS:
        nets = []
        for trial in range(4):
            saved = read_json(root/f"{group}_{trial}.json")
            verify_episode(saved, group, trial)  # independent of source module
            with (root/f"{group}_{trial}_states.csv").open(encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                observed = list(reader)
            require(len(observed) == 5, "CSV length")
            for row, saved_row in zip(observed, saved["states"]):
                require(set(row) == set(saved_row), "CSV schema")
                require(all(row[field] == ("" if value is None else str(value))
                            for field, value in saved_row.items()), "CSV/JSON truth mismatch")
            nets.append(saved["net_uj"])
            summary_rows.append({
                "group": group, "trial": trial,
                "target_x_m": saved["target_x_m"],
                "motor_command_n": saved["motor_command_n"],
                "reached": saved["reached"],
                "motor_spent_uj": saved["motor_spent_uj"],
                "communication_spent_uj": saved["communication_spent_uj"],
                "acquired_uj": saved["acquired_uj"],
                "net_uj": saved["net_uj"],
            })
        require(sum(nets) % 4 == 0, "expected integer mean")
        totals[group] = sum(nets)//4
    report = read_json(root/"comparison.json")
    require(report["schema"] == "f016.suite.v1"
            and report["number_of_primary_runs"] == 24
            and report["preregistered_mean_net_uj"] == PREDICTED
            and report["mean_net_uj"] == totals == PREDICTED
            and report["observed"] == summary_rows, "false scientific result")
    return {"cases": 24, "mean_net_uj": totals, "verified_artifacts": len(expected_files)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify_suite(args.root), sort_keys=True))


if __name__ == "__main__":
    main()
