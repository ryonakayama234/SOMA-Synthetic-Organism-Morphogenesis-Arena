"""F005 preregistered A-F controls and evidence replay.

Oracle operates on SAVED CSV only; does not call f005.advance/simulate or f001.step.
All numerical expectations are preregistered (see experiments/F005/PLAN.md).
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
import tempfile

from soma.f005 import Config, EVENT_COLUMNS, STATE_COLUMNS, provenance, save_run

FLOAT_FIELDS = (
    "time_s", "x_m", "v_m_s", "motor_command_n", "motor_applied_n",
    "external_force_n", "candidate_motor_work_j",
    "candidate_motor_positive_work_j", "motor_positive_work_j", "motor_work_j",
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
        schema_version="f005.v1", experiment_id="F005-" + label, seed=None,
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


def reference_positive_work(u, v0, v1, h):
    """Exact integral plus a separately checked f005.v1 rounding reference.

    Fractions use the exact supplied binary64 endpoints, not decimal ideals.
    The integer battery gate must use the published binary64 operation order:
    algebraically equivalent products can differ by one microjoule after ceil.
    This oracle never calls the implementation's work or step functions.
    """
    force, start, end, width = map(Fraction, (u, v0, v1, h))
    p0, p1 = force * start, force * end
    if p0 <= 0 and p1 <= 0:
        exact = Fraction(0)
        rounded = 0.
    elif p0 >= 0 and p1 >= 0:
        exact = width * (p0 + p1) / 2
        rounded = (u * h) * ((v0 + v1) / 2)
    else:
        peak = max(p0, p1)
        exact = width * peak * peak / (2 * abs(p1 - p0))
        # Velocity magnitudes preserve sign even if u*v underflows/overflows.
        positive = abs(v0 if p0 > 0 else v1)
        negative = abs(v1 if p0 > 0 else v0)
        scale = max(positive, negative)
        positive_share = positive / scale
        share = positive_share / (positive_share + negative / scale)
        rounded = ((abs(u) * h) * positive) * share / 2
    require(math.isfinite(rounded) and rounded >= 0 and
            (rounded > 0 or exact == 0), "positive work oracle finite and nonzero")
    expected = float(exact)
    require(math.isclose(rounded, expected, rel_tol=2e-15,
                         abs_tol=4 * math.ulp(expected)),
            "binary64 positive work disagrees with exact Fraction integral")
    return rounded, exact


def near_positive(actual, expected, name):
    require(actual is not None and math.isfinite(actual) and
            (actual == 0 if expected == 0 else actual > 0 and
             math.isclose(actual, expected, rel_tol=2e-15,
                          abs_tol=4 * math.ulp(expected))),
            "independent oracle " + name)


def verify_saved_run(cfg, folder):
    """Detects missing/changed artifacts, then checks every saved timestep and event."""
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    require(manifest["schema_version"] == "f005.v1", "manifest schema")
    require(manifest["experiment_id"] == cfg.experiment_id, "manifest experiment id")
    artifacts = manifest.get("artifacts")
    require(isinstance(artifacts, dict) and set(artifacts) == {
        "config.json", "states.csv", "ledger/events.csv", "motion_energy.svg",
    }, "manifest must hash exactly all four run artifacts")
    for filename, digest in artifacts.items():
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
    exact_positive_total = Fraction(0)
    binary_positive_total = Fraction(0)
    exact_ceiled_total = 0
    positive_intervals = 0
    for k, row in enumerate(rows):
        require(row["step_index"] == k, "step index")
        near(row["time_s"], k * cfg.dt_s, "time")
        require(row["motor_command_n"] == cfg.motor_force_n and
                row["external_force_n"] == cfg.external_force_n, "logged force provenance")
        if k == 0:
            require(row["decision_reason"] == "initial" and
                    row["ledger_event_index"] is None and
                    row["candidate_motor_work_j"] is None and
                    row["candidate_motor_positive_work_j"] is None and
                    row["motor_applied_n"] == 0 and row["spent_uj"] == 0,
                    "initial row")
            require(all(row[name] == 0 for name in (
                "motor_work_j", "motor_positive_work_j",
                "external_work_j", "drag_work_j",
                "kinetic_delta_j", "mechanical_residual_j",
            )), "initial row must have zero interval work and energy delta")
        else:
            u, ext, h = cfg.motor_force_n, cfg.external_force_n, cfg.dt_s
            prospective = None
            prospective_positive = None
            spent = 0
            if balance == 0:
                applied, decision = 0., "zero_balance"
            elif u == 0:
                applied, decision = 0., "zero_command"
            else:
                # Explicit independent Euler reference, NOT f001_step/f005.advance.
                velocity_candidate = v + h * ((u + ext)/cfg.mass_kg - cfg.drag_per_s*v)
                position_candidate = x + h * velocity_candidate
                prospective = (u * h) * ((v + velocity_candidate) / 2)
                require(math.isfinite(velocity_candidate) and
                        math.isfinite(position_candidate) and math.isfinite(prospective),
                        "oracle candidate non-finite")
                prospective_positive, _ = reference_positive_work(u, v, velocity_candidate, h)
                needed = math.ceil(prospective_positive * 1_000_000)
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
            positive_j, exact_positive = reference_positive_work(applied, v, vn, h)
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
            near_positive(row["motor_positive_work_j"], positive_j, "motor_positive_work_j")
            if prospective is None:
                require(row["candidate_motor_work_j"] is None and
                        row["candidate_motor_positive_work_j"] is None,
                        "candidate must be null")
            else:
                near(row["candidate_motor_work_j"], prospective, "candidate signed motor work")
                near_positive(row["candidate_motor_positive_work_j"], prospective_positive,
                              "candidate positive motor work")
            require(row["decision_reason"] == decision, "wrong battery decision")
            require(row["spent_uj"] == spent, "wrong quantized microjoule spend")
            if applied != 0:
                applied_motor_steps += 1
            balance -= spent
            total_spent += spent
            exact_positive_total += exact_positive
            binary_positive_total += Fraction(positive_j)
            exact_ceiled_total += math.ceil(exact_positive * 1_000_000)
            positive_intervals += int(exact_positive > 0)
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
    exact_rounding_excess = exact_ceiled_total - exact_positive_total * 1_000_000
    require((exact_rounding_excess == 0 if positive_intervals == 0 else
             0 <= exact_rounding_excess < positive_intervals),
            "exact per-step quantization bound")
    return {"independent_all_steps": True, "ledger_event_crosscheck": True,
            "artifact_hashes": True, "integer_residual_uj": 0,
            "max_motion_error": max_motion_err,
            "max_mechanical_residual_j": max_kinetic_residual,
            "final_x_m": x, "final_v_m_s": v,
            "final_balance_uj": balance, "spend_event_count": events_seen,
            "applied_motor_steps": applied_motor_steps,
            "quantization": {
                "exact_endpoint_integral_j": str(exact_positive_total),
                "binary64_work_error_j": float(binary_positive_total - exact_positive_total),
                "exact_ceiled_spent_uj": exact_ceiled_total,
                "exact_rounding_excess_uj": str(exact_rounding_excess),
                "binary64_spent_uj": total_spent,
                "binary64_minus_exact_ceiled_uj": total_spent - exact_ceiled_total,
                "positive_intervals": positive_intervals,
            }}


def suite(output):
    """A-F preregistered controls; all acceptance uses reloaded evidence."""
    source = Path(__file__).read_bytes()
    identity = provenance()
    source_sha = hashlib.sha256(source).hexdigest()
    output.mkdir(parents=True, exist_ok=False)
    (output / "suite_source.py").write_bytes(source)
    settings = {
        "A-reversal": base("A-reversal", motor=-2., velocity=1., dt=1.,
                           battery=500_000),
        "B-low": base("B-low", motor=-2., velocity=1., dt=1., battery=1),
        "C-acceleration": base("C-acceleration", motor=1., dt=1.),
        "D-braking": base("D-braking", motor=-1., velocity=1., dt=1.),
        "E-external": base("E-external", motor=0., external=1., dt=1.),
        "F-split": base("F-split", motor=-2., velocity=1., dt=.5),
        "F-asymmetric": base("F-asymmetric", motor=-4., velocity=1.,
                             dt=1., capacity=5_000_000, battery=5_000_000),
        "F-empty": base("F-empty", motor=-2., velocity=1., dt=1., battery=0),
        "F-tiny": base("F-tiny", motor=.001, dt=.01, duration=.02, battery=1),
        "F-drag": base("F-drag", motor=1., external=.25, drag=.2, dt=.05),
        "F-decimal-split": base("F-decimal-split", motor=-2., velocity=1., dt=.1),
        "F-ceil-boundary": base("F-ceil-boundary", motor=-10., velocity=.2,
                                dt=.05, duration=.05, battery=45_000),
        "F-underflow": base("F-underflow", motor=1e-200, external=-1e-200,
                            velocity=1e-200, dt=1e300, duration=1e300, battery=1),
    }
    cases = {}
    for name, raw in settings.items():
        cfg = Config.from_dict(raw)
        manifest = save_run(cfg, output/name, identity=identity, suite_sha256=source_sha)
        verified = verify_saved_run(cfg, output/name)
        cases[name] = {**verified, "artifact_sha256": manifest["artifacts"]}

    expected = {
        "A-reversal": (-1., -1., 0, 1),
        "B-low": (+1., +1., 1, 0),
        "C-acceleration": (+1., +1., 500_000, 1),
        "D-braking": (0., 0., 1_000_000, 0),
        "E-external": (+1., +1., 1_000_000, 0),
        "F-split": (-.5, -1., 500_000, 1),
        "F-asymmetric": (-3., -3., 500_000, 1),
        "F-empty": (+1., +1., 0, 0),
    }
    for name, (x, v, balance, events) in expected.items():
        item = cases[name]
        near(item["final_x_m"], x, name+" x", 1e-12)
        near(item["final_v_m_s"], v, name+" v", 1e-12)
        require(item["final_balance_uj"] == balance, name+" balance")
        require(item["spend_event_count"] == events, name+" events")
    a = read_rows(output/"A-reversal"/"states.csv", STATE_COLUMNS)[1]
    near(a["motor_work_j"], 0., "A signed work")
    near(a["motor_positive_work_j"], .5, "A positive work")
    low = read_rows(output/"B-low"/"states.csv", STATE_COLUMNS)[1]
    require(low["motor_applied_n"] == 0 and
            low["candidate_motor_positive_work_j"] == .5 and
            low["motor_positive_work_j"] == 0, "B gate records attempted vs actual")
    d = read_rows(output/"D-braking"/"states.csv", STATE_COLUMNS)[1]
    near(d["motor_work_j"], -.5, "D signed")
    near(d["motor_positive_work_j"], 0., "D positive")
    asym = read_rows(output/"F-asymmetric"/"states.csv", STATE_COLUMNS)[1]
    near(asym["motor_work_j"], 4., "F asymmetric signed")
    near(asym["motor_positive_work_j"], 4.5, "F asymmetric positive")
    split = read_rows(output/"F-split"/"states.csv", STATE_COLUMNS)
    near(split[1]["motor_positive_work_j"], 0., "F split brake")
    near(split[2]["motor_positive_work_j"], .5, "F split acceleration")
    near(a["motor_positive_work_j"],
         split[1]["motor_positive_work_j"]+split[2]["motor_positive_work_j"],
         "F split invariant")
    tiny = read_rows(output/"F-tiny"/"states.csv", STATE_COLUMNS)
    require(tiny[1]["spent_uj"] == 1 and tiny[2]["motor_applied_n"] == 0,
            "submicrojoule ceil and exhausted battery")
    reject_inputs = [
        ("zero-mass", {"mass_kg": 0}),
        ("negative-drag", {"drag_per_s": -1}),
        ("unstable-drag", {"drag_per_s": 12}),
        ("offgrid-dt", {"dt_s": .03}),
        ("normalization-changes-grid", {"dt_s": 2**53, "duration_s": 6*2**53}),
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
        raw = copy.deepcopy(settings["C-acceleration"])
        raw.update(changes)
        dest = output/("REJECT-"+label)
        try:
            save_run(Config.from_dict(raw), dest, identity=identity, suite_sha256=source_sha)
        except ValueError as exc:
            valid, reason = not dest.exists(), str(exc)
        except OverflowError as exc:
            valid, reason = False, "unexpected OverflowError: "+str(exc)
        else:
            valid, reason = False, "invalid accepted"
        require(valid, "invalid input accepted: "+label+"; "+reason)
        rejected.append({"case": label, "change": repr(changes), "pass": True,
                         "reason": reason, "no_output": True})
    (output/"rejections.json").write_text(
        json.dumps(rejected, indent=2, ensure_ascii=True, allow_nan=False)+"\n",
        encoding="utf-8",
    )
    cfg = Config.from_dict(settings["A-reversal"])
    save_run(cfg, output/"A-reversal-replay", identity=identity, suite_sha256=source_sha)
    verify_saved_run(cfg, output/"A-reversal-replay")
    compare_names = ("config.json", "states.csv", "ledger/events.csv",
                     "motion_energy.svg", "manifest.json")
    for name in compare_names:
        require((output/"A-reversal"/name).read_bytes() ==
                (output/"A-reversal-replay"/name).read_bytes(),
                "A byte replay: "+name)
    with tempfile.TemporaryDirectory() as temp:
        folder = Path(temp)
        (folder/"ledger").mkdir()
        for item in compare_names:
            target = folder/item
            target.write_bytes((output/"A-reversal"/item).read_bytes())
        path = folder/"states.csv"
        content = path.read_text(encoding="utf-8").splitlines()
        content[1] = content[1].replace("0.5", "0.6", 1) if "0.5" in content[1] else content[1]+" "
        path.write_text("\n".join(content)+"\n",encoding="utf-8")
        try:
            verify_saved_run(cfg, folder)
        except (AssertionError, ValueError):
            tamper_rejected = True
        else:
            tamper_rejected = False
        require(tamper_rejected, "tampered CSV accepted")
    comparison = {
        "schema_version": "f005.comparison.v1",
        "status": "local_software_checks_passed",
        "scope": "one-cell 1D ideal positive motor work; not real battery or emergence",
        "provenance": identity, "suite_sha256": source_sha,
        "suite_source_artifact": "suite_source.py",
        "cases": cases,
        "preregistered_rational_reference": {
            "A_positive_j": .5, "A_spent_uj": 500_000,
            "C_positive_j": .5, "D_positive_j": 0.,
            "F_asymmetric_positive_j": 4.5,
        },
        "rejections": rejected, "rejections_sha256": sha(output/"rejections.json"),
        "checks": {"A_to_F": True, "independent_csv_oracle": True,
                   "integer_accounting": True, "positive_work_nonnegative": True,
                   "tamper_rejection": tamper_rejected,
                   "same_config_byte_replay": True,
                   "F001_F002_F003_F004_regression": "requires CI"},
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
        "A_final_balance_uj": first["cases"]["A-reversal"]["final_balance_uj"],
        "B_final_balance_uj": first["cases"]["B-low"]["final_balance_uj"],
    }, indent=2))


if __name__ == "__main__":
    main()
