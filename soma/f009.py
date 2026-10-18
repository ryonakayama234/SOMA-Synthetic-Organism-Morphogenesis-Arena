"""F009 research-only force-origin and momentum accounting, frozen 1D A-F cases.

This is a standalone ideal mechanical comparison. No cell-facing API, ground-contact
dynamics, real powertrain or alteration of adopted F007 semantics is implied.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

SCHEMA = "f009.momentum.v1"
CASES = ("A", "B", "C", "D", "E", "F")
COLUMNS = (
    "step_index", "time_s", "x_a_m", "x_b_m", "v_a_m_s", "v_b_m_s",
    "external_force_a_n", "external_force_b_n", "internal_force_a_n",
    "internal_force_b_n", "ground_traction_n", "ground_reaction_n",
    "link_force_a_n", "link_force_b_n", "p_before_kg_m_s",
    "p_after_kg_m_s", "external_impulse_ns", "momentum_residual_ns",
)
SOURCE_PATHS = (
    "soma/f009.py", "experiments/F009/run_suite.py",
    "experiments/F009/verify.py", "tests/test_f009.py",
    ".github/workflows/f009.yml", "topics/F009-reaction-momentum/SPEC.md",
    "experiments/F009/PLAN.md", "findings/F009-validation.md",
    "experiments/F009/README.md", "docs/ARCHITECTURE.md",
    "docs/DATA_CONTRACTS.md", "README.md", "AGENTS.md",
)


def config_for(case: str) -> dict:
    if type(case) is not str or case not in CASES:
        raise ValueError("unknown F009 fixed control")
    return {
        "schema_version": SCHEMA, "experiment_id": "F009-" + case,
        "seed": None, "dt_s": 0.25, "duration_s": 1.0,
        "mass_a_kg": 1.0, "mass_b_kg": 1.0,
        "x_a0_m": 0.0, "x_b0_m": 0.5,
        "v_a0_m_s": 0.0, "v_b0_m_s": 0.0,
        "link_length_m": 0.5, "attached": case != "E",
        "force_origin": "legacy_effective" if case == "A" else
            "internal_pair" if case == "B" else "ground_contact",
        "drive_command_n": 2.0,
        "contact_enabled": case in ("C", "E", "F"),
        "traction_limit_n": 1.0 if case == "F" else 2.0,
    }


def validate(cfg: dict) -> str:
    if type(cfg) is not dict or type(cfg.get("experiment_id")) is not str:
        raise ValueError("invalid F009 config")
    key = cfg["experiment_id"]
    if not key.startswith("F009-"):
        raise ValueError("invalid F009 experiment ID")
    case = key[5:]
    if cfg != config_for(case) or set(cfg) != set(config_for(case)):
        raise ValueError("not an exact preregistered F009 A-F control")
    # Disallow bool-as-int or alternate numeric kinds in a fixed case.
    expected = config_for(case)
    for name, value in cfg.items():
        if type(value) is not type(expected[name]):
            raise ValueError("invalid F009 field type: " + name)
    return case


def step_forces(cfg: dict) -> tuple[float, float, float, float, float]:
    mode = cfg["force_origin"]
    u = cfg["drive_command_n"]
    ext_a = 0.0
    internal_a = 0.0
    internal_b = 0.0
    traction = 0.0
    if mode == "legacy_effective":
        ext_a = u
    elif mode == "internal_pair":
        internal_a, internal_b = u, -u
    else:
        if cfg["contact_enabled"]:
            traction = math.copysign(min(abs(u), cfg["traction_limit_n"]), u)
            ext_a = traction
    return ext_a, 0.0, internal_a, internal_b, traction


def simulate(cfg: dict) -> list[dict]:
    validate(cfg)
    h = cfg["dt_s"]
    m_a, m_b = cfg["mass_a_kg"], cfg["mass_b_kg"]
    x_a, x_b = cfg["x_a0_m"], cfg["x_b0_m"]
    v_a, v_b = cfg["v_a0_m_s"], cfg["v_b0_m_s"]
    rows = [dict(zip(COLUMNS, (
        0, 0.0, x_a, x_b, v_a, v_b,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, m_a*v_a+m_b*v_b, 0.0, 0.0,
    )))]
    for index in range(1, 5):
        ext_a, ext_b, int_a, int_b, traction = step_forces(cfg)
        fa, fb = ext_a + int_a, ext_b + int_b
        p_before = m_a*v_a + m_b*v_b
        if cfg["attached"]:
            total = m_a + m_b
            v_a = v_a + h*(fa+fb)/total
            v_b = v_a
            dx = h*v_a
            x_a, x_b = x_a + dx, x_b + dx
            link_b = (m_b/total)*fa - (m_a/total)*fb
        else:
            v_a += h*fa/m_a
            v_b += h*fb/m_b
            x_a += h*v_a
            x_b += h*v_b
            link_b = 0.0
        p_after = m_a*v_a + m_b*v_b
        impulse = h*(ext_a+ext_b)
        residual = (p_after-p_before)-impulse
        row = (
            index, index*h, x_a, x_b, v_a, v_b,
            ext_a, ext_b, int_a, int_b, traction, -traction,
            -link_b, link_b, p_before, p_after, impulse, residual,
        )
        if not all(math.isfinite(float(z)) for z in row):
            raise ValueError("nonfinite F009 derived state")
        rows.append(dict(zip(COLUMNS, row)))
    return rows


def source_hashes(repo: Path | None = None) -> dict[str, str]:
    root = repo or Path(__file__).resolve().parents[1]
    return {
        name: hashlib.sha256((root/name).read_bytes()).hexdigest()
        for name in SOURCE_PATHS
    }


def save_run(cfg: dict, target: Path) -> None:
    """Generate a private run folder; caller owns staged publication and audit."""
    validate(cfg)
    target.mkdir(parents=True, exist_ok=False)
    (target/"config.json").write_text(
        json.dumps(cfg, sort_keys=True, ensure_ascii=False, indent=2)+"\n",
        encoding="utf-8",
    )
    with (target/"steps.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(simulate(cfg))
    digests = {
        name: hashlib.sha256((target/name).read_bytes()).hexdigest()
        for name in ("config.json", "steps.csv")
    }
    manifest = {
        "schema_version": "f009.evidence.v1",
        "case": cfg["experiment_id"],
        "artifacts": digests,
        "source_hashes": source_hashes(),
        "status": "model_result_candidate_not_adopted",
    }
    (target/"manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, ensure_ascii=False, indent=2)+"\n",
        encoding="utf-8",
    )
