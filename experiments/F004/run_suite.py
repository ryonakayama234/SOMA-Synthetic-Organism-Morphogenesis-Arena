"""F004 preregistered A-F controls and evidence replay.

Oracle operates on SAVED CSV only; does not call f004.advance/simulate or f001.step.
All numerical expectations are preregistered (see experiments/F004/PLAN.md).
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
from pathlib import Path
import tempfile

from soma.f004 import Config, EVENT_COLUMNS, STATE_COLUMNS, provenance, save_run

FLOAT_FIELDS = (
    "time_s", "x_m", "v_m_s", "motor_command_n", "motor_applied_n",
    "external_force_n", "candidate_motor_work_j", "motor_work_j",
    "external_work_j", "drag_work_j", "kinetic_delta_j", "mechanical_residual_j",
)
INT_FIELDS = ("step_index", "spent_uj", "balance_uj", "ledger_event_index")


def require(ok, explanation):
    if not ok:
        raise AssertionError(explanation)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def base(label, *, motor=1., external=0., battery=1_000_000, velocity=0.,
         dt=.1, drag=0., duration=1., capacity=1_000_000, mass=1.):
    return dict(
        schema_version="f004.v1", experiment_id="F004-" + label, seed=None,
        mass_kg=mass, drag_per_s=drag, dt_s=dt, duration_s=duration,
        initial_x_m=0., initial_v_m_s=velocity, motor_force_n=motor,
        external_force_n=external, capacity_uj=capacity, initial_balance_uj=battery,
    )


def read_rows(path, columns):
    with path.open(newline="", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        require(tuple(reader.fieldnames or ()) == columns, "CSV column contract")
        rows = []
        for raw in reader:
            require(None not in raw, "CSV unexpected extra column")
            item = {}
            for key, value in raw.items():
                if key in ("decision_reason", "kind", "source_id", "target_id"):
                    item[key] = value if value else None
                elif key in ("step_index", "spent_uj", "balance_uj", "ledger_event_index",
                             "event_index", "amount_uj", "eta_bps", "received_uj", "loss_uj",
                             "external_in_uj", "external_out_uj", "residual_uj"):
                    item[key] = None if value == "" else int(value)
                else:
                    item[key] = None if value == "" else float(value)
                    require(item[key] is None or math.isfinite(item[key]), "non-finite CSV data")
            rows.append(item)
        return rows


def near(actual, expected, name, tolerance=1e-12):
    require(actual is not None and math.isfinite(actual) and
            abs(actual - expected) <= tolerance, "independent oracle " + name)


def verify_saved_run(cfg, folder):
    """Detects missing/changed artifacts, then checks every saved timestep and event."""
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    require(manifest["schema_version"] == "f004.v1", "manifest schema")
    require(manifest["experiment_id"] == cfg.experiment_id, "manifest experiment id")
    for filename, digest in manifest["artifacts"].items():
        require(sha(folder / filename) == digest, "saved artifact checksum: " + filename)
    require(json.loads((folder / "config.json").read_text(encoding="utf-8"))
            == cfg.to_dict(), "saved config changed")
    rows = read_rows(folder / "states.csv", STATE_COLUMNS)
    events = read_rows(folder / "ledger/events.csv", EVENT_COLUMNS)
    require(len(rows) == cfg.steps + 1, "state row count")
    require(manifest["samples"] == len(rows), "manifest sample count")
    require(manifest["events"] == len(events), "manifest event count")
    x, v = cfg.initial_x_m, cfg.initial_v_m_s
    balance = cfg.initial_balance_uj
    events_seen = 0
    applied_motor_steps = 0
    total_spent = 0
    max_motion_err = 0.
    max_kinetic_residual = 0.
    for k, row in enumerate(rows):
        require(row["step_index"] == k, "step index")
        near(row["time_s"], k * cfg.dt_s, "time")
        require(row["motor_command_n"] == cfg.motor_force_n and
                row["external_force_n"] == cfg.external_force_n, "logged force provenance")
        if k == 0:
            require(row["decision_reason"] == "initial" and
                    row["ledger_event_index"] is None and
                    row["candidate_motor_work_j"] is None and
                    row["motor_applied_n"] == 0 and row["spent_uj"] == 0,
                    "initial row")
        else:
            u, ext, h = cfg.motor_force_n, cfg.external_force_n, cfg.dt_s
            prospective = None
            spent = 0
            if balance == 0:
                applied, decision = 0., "zero_balance"
            elif u == 0:
                applied, decision = 0., "zero_command"
            else:
                # Explicit independent Euler reference, NOT f001_step/f004.advance.
                velocity_candidate = v + h * ((u + ext)/cfg.mass_kg - cfg.drag_per_s*v)
                position_candidate = x + h * velocity_candidate
                prospective = (u * h) * ((v + velocity_candidate) / 2)
                require(math.isfinite(velocity_candidate) and
                        math.isfinite(position_candidate) and math.isfinite(prospective),
                        "oracle candidate non-finite")
                needed = math.ceil(max(0., prospective) * 1_000_000)
                if needed <= balance:
                    applied = u
                    spent = needed
                    decision = "accepted_positive_work" if spent else "accepted_nonpositive_work"
                else:
                    applied, decision = 0., "insufficient_balance"
            vn = v + h * ((applied + ext)/cfg.mass_kg - cfg.drag_per_s*v)
            xn = x + h * vn
            mid = (v + vn)/2
            motor_j = (applied*h)*mid
            external_j = (ext*h)*mid
            drag_j = (cfg.mass_kg*cfg.drag_per_s*v*h)*mid
            delta_j = cfg.mass_kg*vn*vn/2 - cfg.mass_kg*v*v/2
            residual = delta_j - (motor_j+external_j-drag_j)
            require(abs(residual) <= 1e-10, "mechanical identity residual")
            for name, exp in (
                ("motor_applied_n", applied), ("motor_work_j", motor_j),
                ("external_work_j", external_j), ("drag_work_j", drag_j),
                ("kinetic_delta_j", delta_j), ("mechanical_residual_j", residual),
            ):
                near(row[name], exp, name, 1e-12)
            if prospective is None:
                require(row["candidate_motor_work_j"] is None, "candidate must be null")
            else:
                near(row["candidate_motor_work_j"], prospective, "candidate motor work")
            require(row["decision_reason"] == decision, "wrong battery decision")
            require(row["spent_uj"] == spent, "wrong quantized microjoule spend")
            if applied != 0:
                applied_motor_steps += 1
            balance -= spent
            total_spent += spent
            require(balance >= 0, "negative balance")
            if spent:
                events_seen += 1
                require(row["ledger_event_index"] == events_seen, "event to step linkage")
                ev = events[events_seen - 1]
                require(ev["step_index"] == k and ev["event_index"] == events_seen and
                        ev["kind"] == "spend" and ev["source_id"] == "A" and
                        ev["target_id"] is None and ev["amount_uj"] == spent,
                        "independent ledger event linkage")
                near(ev["time_s"], k*h, "event timestamp")
                require(ev["eta_bps"] is None and ev["received_uj"] == 0 and
                        ev["loss_uj"] == 0 and ev["external_in_uj"] == 0 and
                        ev["external_out_uj"] == spent and ev["residual_uj"] == 0,
                        "F002 event accounting")
            else:
                require(row["ledger_event_index"] is None, "zero-spend event prohibited")
            x, v = xn, vn
            max_kinetic_residual = max(max_kinetic_residual, abs(residual))
        max_motion_err = max(max_motion_err, abs(row["x_m"]-x), abs(row["v_m_s"]-v))
        near(row["x_m"], x, "position")
        near(row["v_m_s"], v, "velocity")
        require(row["balance_uj"] == balance, "balance does not match oracle")
    require(events_seen == len(events), "extra ledger events")
    require(manifest["final_balance_uj"] == balance, "manifest final balance")
    require(manifest["spent_uj"] == total_spent, "manifest cumulative spend")
    require(manifest["residual_uj"] == 0 and
            balance + total_spent == cfg.initial_balance_uj, "exact F002 conservation")
    return {"independent_all_steps": True, "ledger_event_crosscheck": True,
            "artifact_hashes": True, "integer_residual_uj": 0,
            "max_motion_error": max_motion_err,
            "max_mechanical_residual_j": max_kinetic_residual,
            "final_x_m": x, "final_v_m_s": v,
            "final_balance_uj": balance, "spend_event_count": events_seen,
            "applied_motor_steps": applied_motor_steps}


def suite(output):
    source = Path(__file__).read_bytes()
    identity = provenance()
    source_sha = hashlib.sha256(source).hexdigest()
    output.mkdir(parents=True, exist_ok=False)
    (output / "suite_source.py").write_bytes(source)
    settings = {
        "A-external": base("A-external", motor=0., external=1.),
        "B-full": base("B-full"),
        "C-empty": base("C-empty", battery=0),
        "D-low": base("D-low", battery=300_000),
        "E-brake": base("E-brake", motor=-1., velocity=1.),
        "F-zero-battery-cancel": base("F-zero-battery-cancel", external=-1., battery=0),
        "F-free-work-positive-balance": base("F-free-work-positive-balance",
                                             external=-1., battery=1),
        "F-submicrojoule": base("F-submicrojoule", motor=.001, battery=1, dt=.01,
                                duration=.02),
        "F-dt05": base("F-dt05", dt=.05),
        "F-drag": base("F-drag", motor=1., external=.25, drag=.2, dt=.05),
    }
    cases = {}
    for name, raw in settings.items():
        cfg = Config.from_dict(raw)
        manifest = save_run(cfg, output/name, identity=identity, suite_sha256=source_sha)
        verified = verify_saved_run(cfg, output/name)
        cases[name] = {**verified, "artifact_sha256": manifest["artifacts"]}

    expected = {
        "A-external": (.55, 1., 1_000_000, 0),
        "B-full": (.55, 1., 499_995, 10),
        "C-empty": (0., 0., 0, 0),
        "D-low": (.49, .7, 54_996, 7),
        "E-brake": (.45, 0., 1_000_000, 0),
    }
    for name, (x, v, balance, events) in expected.items():
        item = cases[name]
        near(item["final_x_m"], x, name + " x", 1e-12)
        near(item["final_v_m_s"], v, name + " v", 1e-12)
        require(item["final_balance_uj"] == balance, name + " battery")
        require(item["spend_event_count"] == events, name + " spend event count")
    require(cases["E-brake"]["applied_motor_steps"] == 10 and
            cases["E-brake"]["spend_event_count"] == 0,
            "braking still applies motor force while spending no battery")
    empty_cancel = read_rows(output/"F-zero-battery-cancel"/"states.csv", STATE_COLUMNS)
    near(empty_cancel[1]["v_m_s"], -.1, "empty cancellation velocity")
    near(empty_cancel[1]["x_m"], -.01, "empty cancellation position")
    require(empty_cancel[1]["motor_applied_n"] == 0., "zero-battery loophole")
    free = read_rows(output/"F-free-work-positive-balance"/"states.csv", STATE_COLUMNS)
    require(free[1]["motor_applied_n"] == 1. and free[1]["spent_uj"] == 0 and
            free[1]["balance_uj"] == 1, "ideal free holding work")
    tiny = read_rows(output/"F-submicrojoule"/"states.csv", STATE_COLUMNS)
    require(tiny[1]["spent_uj"] == 1 and tiny[2]["motor_applied_n"] == 0 and
            tiny[2]["decision_reason"] == "zero_balance", "sub-microjoule rounding")
    fine = cases["B-full"]["final_x_m"]
    half = cases["F-dt05"]["final_x_m"]
    near(fine, .55, "F discretization .1")
    near(half, .525, "F discretization .05")
    require(abs(half-.5) < abs(fine-.5), "F convergence to continuous x=.5")
    reject_inputs = [
        ("zero-mass", {"mass_kg": 0}),
        ("negative-drag", {"drag_per_s": -1}),
        ("unstable-drag", {"drag_per_s": 12}),
        ("offgrid-dt", {"dt_s": .03}),
        ("nonfinite-force", {"motor_force_n": float("nan")}),
        ("infinite-external", {"external_force_n": float("inf")}),
        ("bool-balance", {"initial_balance_uj": True}),
        ("negative-balance", {"initial_balance_uj": -1}),
        ("over-capacity", {"initial_balance_uj": 1_000_001}),
        ("too-many-steps", {"dt_s": .00001}),
        ("invalid-xml-id", {"experiment_id": "invalid\u0000id"}),
        ("surrogate-id", {"experiment_id": "invalid\ud800id"}),
        ("bad-seed", {"seed": 4}),
        ("mass-overflow", {"mass_kg": 1e-300, "motor_force_n": 1e300}),
        ("sum-force-overflow", {"motor_force_n": 1e308, "external_force_n": 1e308}),
        ("unknown-key", {"unexpected": 1}),
    ]
    rejected = []
    for label, changes in reject_inputs:
        raw = copy.deepcopy(settings["B-full"])
        raw.update(changes)
        invalid_dir = output/("REJECT-"+label)
        try:
            save_run(Config.from_dict(raw), invalid_dir, identity=identity, suite_sha256=source_sha)
        except (ValueError, OverflowError) as exc:
            # OverflowError is NOT a valid accepted rejection: our public API promises ValueError.
            valid = type(exc) is ValueError and not invalid_dir.exists()
            reason = str(exc)
        else:
            valid, reason = False, "accepted"
        require(valid, "invalid input accepted: "+label+"; "+reason)
        rejected.append({"case": label, "change": repr(changes), "pass": valid,
                         "reason": reason, "no_output": not invalid_dir.exists()})
    (output/"rejections.json").write_text(
        json.dumps(rejected, indent=2, ensure_ascii=True, allow_nan=False)+"\n",
        encoding="utf-8",
    )
    cfg = Config.from_dict(settings["B-full"])
    save_run(cfg, output/"B-full-replay", identity=identity, suite_sha256=source_sha)
    verify_saved_run(cfg, output/"B-full-replay")
    compare_names = ("config.json", "states.csv", "ledger/events.csv",
                     "motion_energy.svg", "manifest.json")
    for name in compare_names:
        require((output/"B-full"/name).read_bytes() ==
                (output/"B-full-replay"/name).read_bytes(),
                "B full trace byte replay: "+name)
    # Tamper actual CSV on isolated copy. Independent verifier MUST reject even
    # if rows have otherwise valid syntax; hash check covers the saved original.
    with tempfile.TemporaryDirectory() as temp:
        folder = Path(temp)
        (folder/"ledger").mkdir()
        for item in compare_names:
            dest = folder/item
            dest.write_bytes((output/"B-full"/item).read_bytes()) if item != "ledger/events.csv" else (folder/"ledger/events.csv").write_bytes((output/"B-full"/item).read_bytes())
        states = folder/"states.csv"
        rows = states.read_text(encoding="utf-8").splitlines()
        rows[2] = rows[2].replace(",0.03,", ",9.03,", 1)
        # Ensure mutation independent of exact float spelling.
        if states.read_text(encoding="utf-8").splitlines()[2] == rows[2]:
            rows[2] += " "
        states.write_text("\n".join(rows)+"\n",encoding="utf-8")
        try:
            verify_saved_run(cfg,folder)
        except (AssertionError, ValueError):
            tamper_rejected = True
        else:
            tamper_rejected = False
        require(tamper_rejected, "tampered CSV passed verifier")
    comparison = {
        "schema_version": "f004.comparison.v1",
        "status": "local_software_checks_passed",
        "scope": "1D one-cell ideal positive-work motor; not hardware or emergence",
        "provenance": identity, "suite_sha256": source_sha,
        "suite_source_artifact": "suite_source.py",
        "cases": cases, "preregistered_rational_reference": {
            "B-full_balance_uj": 500_000, "D-low_balance_uj": 55_000,
        },
        "preregistered_binary64_reference": {
            "B-full_balance_uj": 499_995, "D-low_balance_uj": 54_996,
        },
        "rejections": rejected, "rejections_sha256": sha(output/"rejections.json"),
        "checks": {"A_to_F": True, "independent_csv_oracle": True,
                   "integer_accounting": True, "zero_balance_gate": True,
                   "float_rounding_prereg": True, "tamper_rejection": tamper_rejected,
                   "same_config_byte_replay": True, "F001_F002_F003_regression": "requires CI"},
    }
    (output/"comparison.json").write_text(
        json.dumps(comparison, indent=2, ensure_ascii=False, allow_nan=False)+"\n",
        encoding="utf-8",
    )
    return comparison


def verify_replay(first, second):
    files1 = sorted(p.relative_to(first) for p in first.rglob("*") if p.is_file())
    files2 = sorted(p.relative_to(second) for p in second.rglob("*") if p.is_file())
    require(files1 == files2, "full suite replay file list")
    for relative in files1:
        require((first/relative).read_bytes() == (second/relative).read_bytes(),
                "full suite replay mismatch: " + str(relative))
    report = {"identical": True, "file_count": len(files1),
              "sha256": {str(p): sha(first/p) for p in files1}}
    (first/"full_suite_replay.json").write_text(
        json.dumps(report, indent=2)+"\n",encoding="utf-8",
    )
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--replay-output-dir", type=Path)
    args = parser.parse_args()
    first = suite(args.output_dir)
    if args.replay_output_dir is not None:
        suite(args.replay_output_dir)
        verify_replay(args.output_dir, args.replay_output_dir)
    print(json.dumps({
        "status": first["status"], "controls": len(first["cases"]),
        "invalid_rejections": len(first["rejections"]),
        "full_replay": args.replay_output_dir is not None,
        "B_final_balance_uj": first["cases"]["B-full"]["final_balance_uj"],
        "D_final_balance_uj": first["cases"]["D-low"]["final_balance_uj"],
    }, indent=2))


if __name__ == "__main__":
    main()
