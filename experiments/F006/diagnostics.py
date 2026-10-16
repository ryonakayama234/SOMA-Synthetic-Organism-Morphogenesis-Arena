"""F006: offline timestep-dependence diagnosis from independently verified F005 files.

Never feeds world-truth comparisons into an agent and never changes F005 physics.
F005's saved-file oracle is reused; the cross-dt expectations are separate.
"""
from __future__ import annotations

import csv
from fractions import Fraction
import hashlib
import io
import json
import math
from pathlib import Path

from experiments.F005.run_suite import read_rows, verify_saved_run
from soma.f005 import Config, EVENT_COLUMNS, STATE_COLUMNS

SCHEMA = "f006.v1"
COLUMNS = (
    "case_id", "dt_s", "steps", "final_x_m", "final_v_m_s",
    "positive_work_j", "signed_work_j", "spent_uj", "balance_uj",
    "accepted_steps", "rejected_steps", "reference_x_m", "reference_v_m_s",
    "reference_type", "classification", "verdict",
)

# Independent, preregistered exact-rational discrete references from Wolfram.
# Each tuple is x, v, spent_uj, accepted, rejected, positive_work_J,
# signed_work_J. h=1, .5, .25 except C: 1, .1, .01.
REFERENCES = {
    "A": [(1, 1, 500000, 1, 0, .5, .5),
          (.75, 1, 500000, 2, 0, .5, .5),
          (.625, 1, 500000, 4, 0, .5, .5)],
    "B": [(0, 0, 0, 0, 1, 0, 0),
          (.5, .5, 125000, 1, 1, .125, .125),
          (.5625, .75, 281250, 3, 1, .28125, .28125)],
    "C": [(1, 1, 1, 1, 0, 1e-6, 1e-6),
          (1, 1, 10, 10, 0, 1e-6, 1e-6),
          (1, 1, 100, 100, 0, 1e-6, 1e-6)],
    "D": [(-1, -1, 500000, 1, 0, .5, 0),
          (-.5, -1, 500000, 2, 0, .5, 0),
          (-.25, -1, 500000, 4, 0, .5, 0)],
    "E": [(1, 1, 0, 0, 0, 0, 0),
          (.75, 1, 0, 0, 0, 0, 0),
          (.625, 1, 0, 0, 0, 0, 0)],
}
CLASSES = {
    "A": "integration",
    "B": "budget_gate",
    "C": "quantization",
    "D": "positive_work",
    "E": "external_only",
}
DTS = {"A": (1., .5, .25), "B": (1., .5, .25),
       "C": (1., .1, .01), "D": (1., .5, .25),
       "E": (1., .5, .25)}
ABS_TOL = 1e-12


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError("F006 evidence verification: " + message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False,
                       allow_nan=False, sort_keys=True) + "\n").encode("utf-8")


def csv_bytes(records: list[dict]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(records)
    return stream.getvalue().encode("utf-8")


def _near(a: float, b: float, label: str) -> None:
    require(math.isfinite(a) and abs(a - b) <= ABS_TOL,
            "%s expected %.17g, got %.17g" % (label, b, a))


def analyze_run(cfg: Config, folder: Path, case: str, index: int) -> tuple[dict, dict]:
    """Re-read original F005 evidence and verify all steps without f005.advance."""
    require(cfg.dt_s == DTS[case][index], "unexpected timestep")
    checked = verify_saved_run(cfg, folder)
    states = read_rows(folder / "states.csv", STATE_COLUMNS)
    events = read_rows(folder / "ledger/events.csv", EVENT_COLUMNS)
    final = states[-1]
    accepted = sum(r["motor_applied_n"] != 0 for r in states[1:])
    rejected = sum(r["decision_reason"] in
                   ("insufficient_balance", "zero_balance")
                   and r["motor_command_n"] != 0 for r in states[1:])
    spend = sum(r["spent_uj"] for r in states[1:])
    event_spend = sum(event["amount_uj"] for event in events)
    positive = math.fsum(r["motor_positive_work_j"] for r in states[1:])
    signed = math.fsum(r["motor_work_j"] for r in states[1:])
    exact_endpoints = sum(
        (Fraction(r["motor_positive_work_j"]) for r in states[1:]),
        Fraction(),
    )
    require(event_spend == spend == cfg.initial_balance_uj - final["balance_uj"],
            "integer ledger mismatch")
    require(checked["ledger_event_crosscheck"] and checked["independent_all_steps"],
            "F005 saved-file oracle failed")
    ref_x, ref_v, ref_spent, ref_acc, ref_rej, ref_pos, ref_signed = REFERENCES[case][index]
    for label, actual, expected in (
        ("position", final["x_m"], ref_x), ("velocity", final["v_m_s"], ref_v),
        ("positive work", positive, ref_pos), ("signed work", signed, ref_signed),
    ):
        _near(actual, expected, case + " " + label)
    require((spend, accepted, rejected) == (ref_spent, ref_acc, ref_rej),
            "%s integer spend / acceptance / rejection differs" % case)
    require(accepted + rejected == cfg.steps if cfg.motor_force_n != 0 else
            accepted == 0 and rejected == 0, "motor decision count")
    row = {
        "case_id": case, "dt_s": cfg.dt_s, "steps": cfg.steps,
        "final_x_m": final["x_m"], "final_v_m_s": final["v_m_s"],
        "positive_work_j": positive, "signed_work_j": signed,
        "spent_uj": spend, "balance_uj": final["balance_uj"],
        "accepted_steps": accepted, "rejected_steps": rejected,
        "reference_x_m": ref_x, "reference_v_m_s": ref_v,
        "reference_type": "discrete_exact_fraction",
        "classification": CLASSES[case], "verdict": "supported",
    }
    detail = {
        "case_id": case, "dt_s": cfg.dt_s, "classification": CLASSES[case],
        "verdict": "supported",
        "reference": {"type": "discrete_exact_fraction",
                      "source": "Wolfram preregistration",
                      "x_m": ref_x, "v_m_s": ref_v,
                      "spent_uj": ref_spent,
                      "positive_work_j": ref_pos},
        "raw_run": str(folder.name),
        "artifacts": {
            file: sha(folder / file) for file in
            ("config.json", "states.csv", "ledger/events.csv",
             "motion_energy.svg", "manifest.json")
        },
        "accepted_step_indices": [r["step_index"] for r in states[1:]
                                  if r["motor_applied_n"] != 0],
        "rejected_step_indices": [r["step_index"] for r in states[1:]
                                  if r["decision_reason"] in
                                  ("insufficient_balance", "zero_balance")
                                  and r["motor_command_n"] != 0],
        "ideal_positive_work_j": float(exact_endpoints),
        "binary64_endpoint_sum_j": positive,
        "quantization_excess_uj": checked["quantization"]["exact_rounding_excess_uj"],
        "integer_balance_residual_uj": 0,
    }
    return row, detail


def classify_sweeps(records: list[dict]) -> dict:
    grouped = {key: [r for r in records if r["case_id"] == key]
               for key in DTS}
    require(all(len(group) == len(DTS[key]) for key, group in grouped.items()),
            "missing or duplicate sweep rows")
    a = grouped["A"]
    require([r["final_x_m"] for r in a] == [1., .75, .625],
            "A expected Euler sequence")
    require(all(r["final_v_m_s"] == 1. for r in a),
            "A identical terminal velocity")
    a_errors = [abs(r["final_x_m"] - .5) for r in a]
    require(all(abs(a_errors[i] / a_errors[i+1] - 2.) <= ABS_TOL
                for i in range(2)), "A first-order convergence ratio")
    b = grouped["B"]
    require([r["rejected_steps"] for r in b] == [1, 1, 1] and
            [r["accepted_steps"] for r in b] == [0, 1, 3],
            "B all-or-nothing battery acceptance")
    c = grouped["C"]
    require([r["spent_uj"] for r in c] == [1, 10, 100] and
            all(abs(r["positive_work_j"] - 1e-6) <= ABS_TOL for r in c),
            "C ceil quantization signature")
    d = grouped["D"]
    require(all(abs(r["positive_work_j"] - .5) <= ABS_TOL and
                abs(r["signed_work_j"]) <= ABS_TOL for r in d),
            "D reversal signed-vs-positive work")
    e = grouped["E"]
    require(all(r["spent_uj"] == 0 and r["accepted_steps"] == 0 and
                r["rejected_steps"] == 0 for r in e),
            "E external-only must draw no motor energy")
    return {
        "schema_version": SCHEMA,
        "source_model": "f005.v1",
        "reference_notes": [
            "The Wolfram fractions are exact references for the discrete model.",
            "They are not observations or proof of continuous physical accuracy.",
            "CSV float values are Python binary64 observations verified separately.",
        ],
        "comparisons": {
            "A": {"classification": "integration", "errors_m": a_errors,
                  "reference_continuous_x_m": .5,
                  "observed_error_ratios": [a_errors[0]/a_errors[1],
                                            a_errors[1]/a_errors[2]]},
            "B": {"classification": "budget_gate",
                  "accepted_counts": [r["accepted_steps"] for r in b],
                  "rejected_counts": [r["rejected_steps"] for r in b]},
            "C": {"classification": "quantization",
                  "spent_uj": [r["spent_uj"] for r in c],
                  "positive_work_j": [r["positive_work_j"] for r in c]},
            "D": {"classification": "positive_work",
                  "positive_work_j": [r["positive_work_j"] for r in d],
                  "signed_work_j": [r["signed_work_j"] for r in d]},
            "E": {"classification": "external_only",
                  "spent_uj": [r["spent_uj"] for r in e]},
        },
        "verdict": "supported",
    }


def svg_bytes(rows: list[dict]) -> bytes:
    """SVG is visualization only; exact results live in untouched source CSV."""
    widths = {"A": 80, "B": 205, "C": 330, "D": 455, "E": 580}
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="780" height="340">',
             '<rect width="780" height="340" fill="white"/>',
             '<text x="28" y="28" font-family="Arial" font-size="17">F006: terminal x by dt (preregistered A-E)</text>']
    for name in DTS:
        group = [r for r in rows if r["case_id"] == name]
        x = widths[name]
        parts.append('<text x="%d" y="62" font-family="Arial" font-size="16">%s</text>' % (x, name))
        for i, row in enumerate(group):
            # Consistent display scale: [-1,1] m mapped into 180px.
            y = 252 - 75 * row["final_x_m"]
            parts.append('<circle cx="%d" cy="%.4f" r="5" fill="#2563eb"/>' % (x + i * 22, y))
            parts.append('<text x="%d" y="290" font-family="Arial" font-size="9">h=%g</text>'
                         % (x, row["dt_s"])) if i == 0 else None
    parts.append('<text x="28" y="324" font-family="Arial" font-size="11">Visualization only; use comparison.csv and saved F005 files for evidence.</text></svg>')
    return "".join(parts).encode("utf-8")


def recompute(directory: Path, settings: dict) -> tuple[list[dict], dict]:
    records, details = [], []
    for name in DTS:
        for index, dt in enumerate(DTS[name]):
            key = "%s-dt-%02d" % (name, index)
            config = Config.from_dict(settings[key])
            record, detail = analyze_run(config, directory / key, name, index)
            records.append(record)
            details.append(detail)
    diagnosis = classify_sweeps(records)
    diagnosis["runs"] = details
    return records, diagnosis


def audit_suite(directory: Path, settings: dict) -> dict:
    """Audit source files AND diagnostics, including post-hash semantic tampering."""
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    require(manifest["schema_version"] == SCHEMA, "suite schema")
    hashes = manifest["artifacts"]
    require(set(hashes) == {"sweep.json", "suite_source.py", "comparison.csv",
                            "diagnostics.json", "comparison.svg"},
            "suite artifact set")
    for name, digest in hashes.items():
        require(sha(directory / name) == digest, "suite file sha: " + name)
    require(manifest["suite_sha256"] == sha(directory / "suite_source.py"),
            "suite source hash")
    sweep = json.loads((directory / "sweep.json").read_text(encoding="utf-8"))
    require(sweep["schema_version"] == SCHEMA and
            sweep["source_model"] == "f005.v1" and
            sweep["seed"] is None and
            sweep["runs"] == settings, "sweep run identity")
    records, diagnosis = recompute(directory, settings)
    require((directory / "comparison.csv").read_bytes() == csv_bytes(records),
            "comparison CSV mismatches independently recomputed evidence")
    require((directory / "diagnostics.json").read_bytes() == json_bytes(diagnosis),
            "diagnosis mismatches independently recomputed evidence")
    require((directory / "comparison.svg").read_bytes() == svg_bytes(records),
            "SVG visualization mismatches evidence")
    require(manifest["runs"] == len(records) == 15 and
            manifest["verdict"] == "supported", "manifest run count / verdict")
    for item in diagnosis["runs"]:
        folder = directory / item["raw_run"]
        require(folder.is_dir(), "raw run missing")
        for file, digest in item["artifacts"].items():
            require(sha(folder / file) == digest, "raw artifact checksum")
    return {"runs": len(records), "verdict": diagnosis["verdict"],
            "per_step_independent_oracle": True, "cross_dt_recomputed": True,
            "integer_residual_uj": 0}
