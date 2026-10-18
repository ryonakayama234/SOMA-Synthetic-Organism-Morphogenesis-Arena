"""F008 independent saved-evidence verifier: does not import soma.f008.

Checks the local CSV against a separate A-only recurrence over independently
verified F007 saved states, then checks the frozen A-E scientific controls.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

from experiments.F007.verify import audit_run, require

LOCAL_COLUMNS = (
    "step_index", "time_s", "dt_s", "v_prev_m_s", "v_a_m_s",
    "motor_command_n", "motor_applied_n", "balance_a_uj",
    "observed_accel_m_s2", "expected_accel_m_s2", "residual_m_s2", "status",
)
SOURCE_FLOATS = ("time_s", "v_a_m_s", "motor_command_n", "motor_applied_n")
CONTROL_ACCEL = {
    "A-free": [2., 2., 2., 2.],
    "B-linked": [1., 1., 1., 1.],
    "C-cut": [1., 1., 2., 2.],
    "D-hidden-force": [1., 1., 1., 1.],
    "E-empty-battery": [0., 0., 0., 0.],
}
TOL = 1e-12

# Independent, frozen interpretation of the researcher-facing summary.
# A re-signed comparison.json is not evidence unless these scientific
# reference fields agree with the preregistration and the saved raw data.
EXPECTED_COMPARISON = {
    "schema_version": "f008.evidence.v1",
    "design_ref": "F008 issue 22, design PR 23; controls A-E unchanged",
    "expected_free_accel_m_s2": 2,
    "expected_linked_and_hidden_force_accel_m_s2": 1,
    "expected_cut_accel_m_s2": [1, 1, 2, 2],
    "confound_cannot_prove_attachment": True,
    "science_status": "model_result_pending_independent_review",
}
EXPECTED_SOURCE = "adopted F007 saved oracle; F008 independent local verifier"

# Explicit trusted checkout dependency list. The saved manifest cannot choose it.
F008_SOURCE_FILES = (
    "soma/f008.py",
    "experiments/F008/run_suite.py",
    "experiments/F008/verify.py",
    "tests/test_f008.py",
    ".github/workflows/f008.yml",
    "topics/F008-local-load-detection/SPEC.md",
    "experiments/F008/PLAN.md",
    "experiments/F008/README.md",
    "experiments/F008/IMPLEMENTATION_DECISIONS.md",
    "findings/F008-validation.md",
    "docs/ARCHITECTURE.md",
    "docs/DATA_CONTRACTS.md",
    "README.md",
    "AGENTS.md",
)


def f008_source_hashes() -> dict[str, str]:
    root = Path(__file__).resolve().parents[2]
    return {rel: hashlib.sha256((root / rel).read_bytes()).hexdigest()
            for rel in F008_SOURCE_FILES}



def read(path: Path) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as fp:
        reader = csv.DictReader(fp)
        header = tuple(reader.fieldnames or ())
        rows = list(reader)
    require(all(None not in r for r in rows), "malformed CSV columns")
    return header, rows


def numeric(value: str) -> float | None:
    if value == "":
        return None
    n = float(value)
    require(math.isfinite(n), "invalid nonfinite local value")
    return n


def equal(actual: float | None, reference: float | None, label: str) -> None:
    if reference is None:
        require(actual is None, label + ": expected null")
    else:
        require(actual is not None and abs(actual-reference) <= TOL,
                label + ": wrong numeric value")


def check_case(case_dir: Path, *, trusted_origin: dict) -> list[dict]:
    source = case_dir / "F007"
    audit_run(source, trusted_origin=trusted_origin)
    head, world = read(source / "states.csv")
    require("v_a_m_s" in head and "balance_a_uj" in head, "source schema")
    columns, local = read(case_dir / "local.csv")
    require(columns == LOCAL_COLUMNS, "unexpected local column or leakage")
    require(len(local) == len(world)-1 == 4, "frozen four-step control")

    for i, (previous, current, row) in enumerate(zip(world, world[1:], local), 1):
        interval = float(current["time_s"])-float(previous["time_s"])
        require(interval > 0 and math.isfinite(interval), "bad source interval")
        observed = (float(current["v_a_m_s"])-float(previous["v_a_m_s"]))/interval
        applied = float(current["motor_applied_n"])
        reference = {
            "step_index": int(current["step_index"]),
            "time_s": float(current["time_s"]),
            "dt_s": interval,
            "v_prev_m_s": float(previous["v_a_m_s"]),
            "v_a_m_s": float(current["v_a_m_s"]),
            "motor_command_n": float(current["motor_command_n"]),
            "motor_applied_n": applied,
            "balance_a_uj": int(current["balance_a_uj"]),
            "observed_accel_m_s2": observed,
            "expected_accel_m_s2": applied if applied else None,
            "residual_m_s2": observed-applied if applied else None,
            "status": ("not_excited" if applied == 0 else
                       "anomaly" if abs(observed-applied)>TOL else "nominal"),
        }
        for key in LOCAL_COLUMNS:
            value = row[key]
            if key == "status":
                require(value == reference[key], f"{i}/{key}")
            elif key in ("step_index", "balance_a_uj"):
                require(value == str(reference[key]), f"{i}/{key}")
            else:
                equal(numeric(value), reference[key], f"{i}/{key}")
        equal(numeric(row["observed_accel_m_s2"]),
              CONTROL_ACCEL[case_dir.name][i-1], case_dir.name+"/frozen acceleration")
    return local


def verify_suite(directory: Path, *, trusted_origin: dict) -> dict:
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    require(manifest["schema_version"] == "f008.evidence.v1", "suite schema")
    require(manifest["cases"] == list(CONTROL_ACCEL), "noncanonical case inventory")
    require(manifest["source"] == EXPECTED_SOURCE, "noncanonical evidence source")
    comparison = json.loads((directory / "comparison.json").read_text(encoding="utf-8"))
    require(comparison == EXPECTED_COMPARISON,
            "researcher-facing scientific summary disagrees with frozen plan")
    require(manifest["origin"] == trusted_origin, "trusted checkout identity")
    require(set(trusted_origin.get("f008_source_hashes", {})) == set(F008_SOURCE_FILES),
            "missing or altered F008 dependency list")
    require(trusted_origin["f008_source_hashes"] == f008_source_hashes(),
            "F008 source hashes differ from trusted checkout")

    actual = {str(p.relative_to(directory)) for p in directory.rglob("*") if p.is_file()
              and p.relative_to(directory).as_posix() != "manifest.json"}
    require(actual == set(manifest["artifacts"]), "artifact inventory changed")
    for rel, expected_hash in manifest["artifacts"].items():
        actual_hash = hashlib.sha256((directory / rel).read_bytes()).hexdigest()
        require(actual_hash == expected_hash, "artifact hash mismatch: " + rel)
    local = {case:check_case(directory/case, trusted_origin=trusted_origin)
             for case in CONTROL_ACCEL}
    # Same entire A-only time series from mechanically different worlds.
    require(local["B-linked"] == local["D-hidden-force"],
            "linked versus unknown external-force observational equivalence")
    for case, expected_attached in (("B-linked", "True"), ("D-hidden-force", "False")):
        _, rows = read(directory/case/"F007"/"states.csv")
        require(all(r["attached"] == expected_attached for r in rows),
                "confound lacks independent physical state")
    _, cut = read(directory/"C-cut"/"F007"/"states.csv")
    require([r["attached"] for r in cut] == ["True","True","False","False","False"],
            "post-event cut truth")
    require([r["status"] for r in local["C-cut"]]
            == ["anomaly","anomaly","nominal","nominal"], "cut transition")
    require(all(r["status"] == "not_excited" and r["residual_m_s2"] == ""
                for r in local["E-empty-battery"]), "invalid motor-off inference")
    return {"status":"supported_discrete_candidate", "cases":len(local),
            "observations":sum(len(rows) for rows in local.values()),
            "linked_external_indistinguishable":True,
            "world_truth_leaked_to_local_csv":False,
            "f007_source_audited":True}
