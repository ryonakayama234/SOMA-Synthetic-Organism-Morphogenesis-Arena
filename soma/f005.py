"""F005: battery-gated 1D motor actuation (idealized positive mechanical work).

F001 supplies motion; F002 supplies integer-microjoule accounting. This module
provides neither sensors nor an autonomous agent. All states here are world truth.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import subprocess
from typing import Any
from xml.sax.saxutils import escape

from soma.f001 import step as f001_step
from soma.f002 import Cell, Event, LedgerState, MAX_UJ, apply_event, new_ledger

SCHEMA = "f005.v1"
MAX_STEPS = 10_000
CELL_ID = "A"
STATE_COLUMNS = (
    "step_index", "time_s", "x_m", "v_m_s", "motor_command_n",
    "motor_applied_n", "external_force_n", "candidate_motor_work_j",
    "candidate_motor_positive_work_j", "motor_positive_work_j",
    "motor_work_j", "external_work_j", "drag_work_j", "kinetic_delta_j",
    "mechanical_residual_j", "spent_uj", "balance_uj", "ledger_event_index",
    "decision_reason",
)
EVENT_COLUMNS = (
    "step_index", "time_s", "event_index", "kind", "source_id", "target_id",
    "amount_uj", "eta_bps", "received_uj", "loss_uj", "external_in_uj",
    "external_out_uj", "residual_uj",
)


def _finite(value: Any, name: str) -> float:
    if type(value) not in (int, float):
        raise ValueError(f"{name} must be a finite number, not boolean")
    try:
        n = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f"{name} is not representable") from exc
    if not math.isfinite(n):
        raise ValueError(f"{name} must be finite")
    return n


def _safe_id(identifier: Any) -> bool:
    if not isinstance(identifier, str) or not 1 <= len(identifier) <= 120:
        return False
    return all(
        ord(ch) in (9, 10, 13) or 0x20 <= ord(ch) <= 0xD7FF
        or 0xE000 <= ord(ch) <= 0xFFFD
        or 0x10000 <= ord(ch) <= 0x10FFFF
        for ch in identifier
    )


def _check_finite(**values: float) -> None:
    for key, value in values.items():
        if not math.isfinite(value):
            raise ValueError(f"non-finite derived {key}")


@dataclass(frozen=True)
class Config:
    schema_version: str
    experiment_id: str
    seed: None
    mass_kg: float
    drag_per_s: float
    dt_s: float
    duration_s: float
    initial_x_m: float
    initial_v_m_s: float
    motor_force_n: float
    external_force_n: float
    capacity_uj: int
    initial_balance_uj: int

    def __post_init__(self) -> None:
        # Every public construction path (including dataclasses.replace) must
        # enforce the same contract before simulation or output can begin.
        raw = asdict(self)
        if raw["schema_version"] != SCHEMA or not _safe_id(raw["experiment_id"]):
            raise ValueError("invalid schema or XML 1.0 experiment_id")
        if raw["seed"] is not None:
            raise ValueError("F005 is deterministic: seed must be null")
        floats = {}
        for name in (
            "mass_kg", "drag_per_s", "dt_s", "duration_s", "initial_x_m",
            "initial_v_m_s", "motor_force_n", "external_force_n",
        ):
            floats[name] = _finite(raw[name], name)
        if floats["mass_kg"] <= 0 or floats["dt_s"] <= 0 or floats["duration_s"] <= 0:
            raise ValueError("mass, dt and duration must be positive")
        if floats["drag_per_s"] < 0 or floats["drag_per_s"] * floats["dt_s"] > 1:
            raise ValueError("drag must be >= 0 and dt*drag <= 1")
        if (type(raw["capacity_uj"]) is not int
                or not 1 <= raw["capacity_uj"] <= MAX_UJ
                or type(raw["initial_balance_uj"]) is not int
                or not 0 <= raw["initial_balance_uj"] <= raw["capacity_uj"]):
            raise ValueError("capacity and balance must be bounded integer microjoules")
        # Decimal-grid decision independent of decimal.getcontext() precision.
        ratio = Fraction(str(raw["duration_s"])) / Fraction(str(raw["dt_s"]))
        if ratio.denominator != 1 or not 1 <= ratio.numerator <= MAX_STEPS:
            raise ValueError("duration must be an exact decimal multiple of dt, <=10000 steps")
        normalized_ratio = Fraction(str(floats["duration_s"])) / Fraction(str(floats["dt_s"]))
        if normalized_ratio != ratio:
            raise ValueError("float normalization must preserve the exact decimal time grid")
        for name, value in floats.items():
            object.__setattr__(self, name, value)

    @classmethod
    def from_dict(cls, raw: object) -> "Config":
        if not isinstance(raw, dict) or raw.keys() != set(cls.__dataclass_fields__):
            raise ValueError("F005 config keys do not match f005.v1")
        return cls(**raw)

    @classmethod
    def from_json(cls, path: Path) -> "Config":
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))

    @property
    def steps(self) -> int:
        return int(Fraction(str(self.duration_s)) / Fraction(str(self.dt_s)))

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Motion:
    x_m: float
    v_m_s: float


def initial(cfg: Config) -> tuple[Motion, LedgerState]:
    return (Motion(cfg.initial_x_m, cfg.initial_v_m_s),
            new_ledger([Cell(CELL_ID, cfg.capacity_uj, cfg.initial_balance_uj)]))


def positive_motor_work(u: float, v0: float, v1: float, h: float) -> float:
    """Integrate max(0,u*v(t)) for linearly interpolated interval velocity.

    This is ideal positive MECHANICAL work, not the electrical battery draw.
    F005's signed motor work still uses the original F004 midpoint formula.
    """
    _check_finite(u=u, v0=v0, v1=v1, h=h)
    if h <= 0:
        raise ValueError("step duration must be positive")
    # Determine power sign from velocity and command DIRECTION, avoiding
    # premature u*v underflow to zero (which would otherwise grant free motion).
    if u == 0:
        return 0.0
    orientation = 1.0 if u > 0 else -1.0
    a, b = orientation * v0, orientation * v1
    if a <= 0 and b <= 0:
        return 0.0
    if a >= 0 and b >= 0:
        # Preserve F004's binary64 midpoint-work order on nonreversing steps.
        work = (u * h) * ((v0 + v1) / 2)
    else:
        positive, negative = max(a, b), -min(a, b)
        scale = max(positive, negative)
        alpha = (positive / scale) / ((positive / scale) + (negative / scale))
        work = ((abs(u) * h) * positive) * alpha / 2
    _check_finite(positive_motor_work=work)
    if work < 0 or (work == 0 and (a > 0 or b > 0)):
        raise ValueError("positive motor work became negative or underflowed")
    return work


def advance(cfg: Config, motion: Motion, ledger: LedgerState,
            step_index: int) -> tuple[Motion, LedgerState, dict, dict | None]:
    """One transaction: no changes to motion or ledger on a failed proposal.

    With positive battery but zero POSITIVE work, motor action is free in this
    deliberately ideal, nonregenerative model. Empty battery always gates it.
    """
    if type(step_index) is not int or step_index < 1 or step_index > cfg.steps:
        raise ValueError("invalid step index")
    if len(ledger.cells) != 1 or ledger.cells[0].cell_id != CELL_ID:
        raise ValueError("F005 requires one A cell in F002 ledger")
    if ledger.cells[0].capacity_uj != cfg.capacity_uj:
        raise ValueError("ledger capacity mismatch")
    _check_finite(x_m=motion.x_m, v_m_s=motion.v_m_s)
    balance = ledger.cell(CELL_ID).balance_uj
    u, fe, h = cfg.motor_force_n, cfg.external_force_n, cfg.dt_s
    candidate_work = None
    candidate_positive = None
    cost = 0
    entry = None
    if balance == 0:
        applied = 0.0
        reason = "zero_balance"
    elif u == 0:
        applied = 0.0
        reason = "zero_command"
    else:
        total_force = u + fe
        _check_finite(total_force=total_force)
        cx, cv = f001_step(motion.x_m, motion.v_m_s, mass_kg=cfg.mass_kg,
                          drag_per_s=cfg.drag_per_s, force_n=total_force, dt_s=h)
        _check_finite(candidate_x=cx, candidate_v=cv)
        candidate_work = (u * h) * ((motion.v_m_s + cv) / 2)
        _check_finite(candidate_work=candidate_work)
        candidate_positive = positive_motor_work(u, motion.v_m_s, cv, h)
        quantized = candidate_positive * 1_000_000
        _check_finite(quantized=quantized)
        cost = math.ceil(quantized)
        if cost <= balance:
            applied, reason = u, ("accepted_positive_work" if cost else "accepted_nonpositive_work")
        else:
            applied, reason, cost = 0.0, "insufficient_balance", 0
    if applied:
        # cx/cv were already computed and checked.
        next_x, next_v = cx, cv
    else:
        next_x, next_v = f001_step(
            motion.x_m, motion.v_m_s, mass_kg=cfg.mass_kg,
            drag_per_s=cfg.drag_per_s, force_n=fe, dt_s=h,
        )
    _check_finite(next_x=next_x, next_v=next_v)
    mid = (motion.v_m_s + next_v) / 2
    motor_work = (applied * h) * mid
    motor_positive_work = positive_motor_work(applied, motion.v_m_s, next_v, h)
    external_work = (fe * h) * mid
    drag_work = (cfg.mass_kg * cfg.drag_per_s * motion.v_m_s * h) * mid
    kinetic_delta = (cfg.mass_kg * next_v * next_v / 2
                     - cfg.mass_kg * motion.v_m_s * motion.v_m_s / 2)
    residual = kinetic_delta - (motor_work + external_work - drag_work)
    _check_finite(mid=mid, motor_work=motor_work, external_work=external_work,
                  drag_work=drag_work, kinetic_delta=kinetic_delta,
                  mechanical_residual=residual, motor_positive_work=motor_positive_work)
    next_ledger = ledger
    if cost > 0:
        # F002 validates and returns a new immutable ledger. No partial write.
        next_ledger, accepted = apply_event(
            ledger, Event(kind="spend", amount_uj=cost, source_id=CELL_ID)
        )
        entry = {"step_index": step_index, "time_s": step_index * h,
                 **asdict(accepted)}
    _check_finite(time_s=step_index * h)
    row = {
        "step_index": step_index, "time_s": step_index * h,
        "x_m": next_x, "v_m_s": next_v, "motor_command_n": u,
        "motor_applied_n": applied, "external_force_n": fe,
        "candidate_motor_work_j": candidate_work,
        "candidate_motor_positive_work_j": candidate_positive,
        "motor_positive_work_j": motor_positive_work, "motor_work_j": motor_work,
        "external_work_j": external_work, "drag_work_j": drag_work,
        "kinetic_delta_j": kinetic_delta, "mechanical_residual_j": residual,
        "spent_uj": cost, "balance_uj": next_ledger.cell(CELL_ID).balance_uj,
        "ledger_event_index": entry["event_index"] if entry else None,
        "decision_reason": reason,
    }
    return Motion(next_x, next_v), next_ledger, row, entry


def simulate(cfg: Config) -> tuple[list[dict], list[dict], LedgerState]:
    motion, ledger = initial(cfg)
    rows = [{
        "step_index": 0, "time_s": 0.0, "x_m": motion.x_m, "v_m_s": motion.v_m_s,
        "motor_command_n": cfg.motor_force_n, "motor_applied_n": 0.0,
        "external_force_n": cfg.external_force_n, "candidate_motor_work_j": None,
        "candidate_motor_positive_work_j": None, "motor_positive_work_j": 0.0,
        "motor_work_j": 0.0, "external_work_j": 0.0, "drag_work_j": 0.0,
        "kinetic_delta_j": 0.0, "mechanical_residual_j": 0.0,
        "spent_uj": 0, "balance_uj": ledger.cell(CELL_ID).balance_uj,
        "ledger_event_index": None, "decision_reason": "initial",
    }]
    events = []
    for idx in range(1, cfg.steps + 1):
        motion, ledger, row, event = advance(cfg, motion, ledger, idx)
        rows.append(row)
        if event is not None:
            events.append(event)
    if ledger.residual_uj != 0:
        raise ValueError("F002 ledger accounting failed")
    return rows, events, ledger


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def provenance() -> dict:
    root = Path(__file__).resolve().parents[1]
    try:
        run = lambda *args: subprocess.run(
            ["git", "-C", str(root), *args], check=True, text=True,
            capture_output=True, timeout=3,
        ).stdout.strip()
        commit = run("rev-parse", "HEAD")
        dirty = bool(run("status", "--porcelain", "--untracked-files=all"))
    except (OSError, subprocess.SubprocessError):
        commit, dirty = None, None
    return {
        "git_commit": commit, "git_dirty": dirty,
        "f005_sha256": sha(Path(__file__)),
        "f001_sha256": sha(root / "soma" / "f001.py"),
        "f002_sha256": sha(root / "soma" / "f002.py"),
    }


def plot_svg(rows: list[dict], title: str, capacity: int) -> str:
    """Display-only decimation. Source evidence remains complete CSV."""
    width, height = 810, 460
    samples = rows[::max(1, len(rows) // 400)]
    if samples[-1] is not rows[-1]:
        samples.append(rows[-1])
    times = rows[-1]["time_s"]
    panels = [
        ("x_m", 78, 180, "#2563eb", "Position [m]"),
        ("v_m_s", 218, 320, "#059669", "Velocity [m/s]"),
        ("balance_uj", 358, 442, "#b45309", "Battery [microjoules]"),
    ]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="40" y="28" font-family="Arial" font-size="18">{escape(title)}: F005 motor and battery</text>',
    ]
    for key, top, bottom, color, label in panels:
        vals = [r[key] for r in rows]
        low, high = min(vals), max(vals)
        if key == "balance_uj":
            low, high = 0, capacity
        # Normalize before subtracting or multiplying: finite world values can
        # still overflow in 680*time or in high-low across opposite signs.
        scale = max(abs(low), abs(high)) or 1
        low_scaled, high_scaled = low / scale, high / scale
        span = high_scaled - low_scaled if high != low else 1
        pts = " ".join(
            f'{90 + 680*(r["time_s"]/times):.3f},{bottom-(bottom-top)*((r[key]/scale-low_scaled)/span):.3f}'
            for r in samples
        )
        parts.extend([
            f'<text x="90" y="{top-13}" font-family="Arial" font-size="12">{label}</text>',
            f'<path d="M90 {top}V{bottom}H770" fill="none" stroke="#64748b"/>',
            f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{pts}"/>',
        ])
    parts.append('</svg>')
    return "".join(parts)


def save_run(cfg: Config, directory: Path, *, identity: dict | None = None,
             suite_sha256: str | None = None) -> dict:
    rows, events, ledger = simulate(cfg)  # no output on invalid physics
    svg = plot_svg(rows, cfg.experiment_id, cfg.capacity_uj)
    source = provenance() if identity is None else identity
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "ledger").mkdir(exist_ok=False)
    (directory / "config.json").write_text(
        json.dumps(cfg.to_dict(), indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    for filename, keys, items in (
        ("states.csv", STATE_COLUMNS, rows),
        ("ledger/events.csv", EVENT_COLUMNS, events),
    ):
        with (directory / filename).open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=keys)
            writer.writeheader()
            writer.writerows(items)
    (directory / "motion_energy.svg").write_text(svg, encoding="utf-8")
    artifacts = ("config.json", "states.csv", "ledger/events.csv", "motion_energy.svg")
    manifest = {
        "schema_version": SCHEMA, "experiment_id": cfg.experiment_id,
        "model": "1d_battery_limited_motor_ideal",
        "integration": "semi_implicit_euler; midpoint_signed_work; linear_velocity_positive_work",
        "seed": None, "seed_note": "no randomness", "samples": len(rows),
        "events": len(events), "final_balance_uj": ledger.cell(CELL_ID).balance_uj,
        "spent_uj": ledger.spent_uj, "residual_uj": ledger.residual_uj,
        **source, "suite_sha256": suite_sha256,
        "artifacts": {name: sha(directory / name) for name in artifacts},
    }
    (directory / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="SOMA F005 one-cell motor energy experiment")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    cfg = Config.from_json(args.config)
    manifest = save_run(cfg, args.output_dir)
    print(json.dumps({"balance_uj": manifest["final_balance_uj"],
                      "spent_uj": manifest["spent_uj"],
                      "residual_uj": manifest["residual_uj"]}))


if __name__ == "__main__":
    main()
