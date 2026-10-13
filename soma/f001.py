"""F001: one-dimensional motion with linear velocity drag.

This is a deliberately simple dynamical model, NOT a contact/rigid-body
simulator and NOT an energy-consumption model.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import subprocess
from typing import Any
from xml.sax.saxutils import escape

SCHEMA_VERSION = "f001.v1"
MODEL = "1d_linear_drag"
HEADERS = ("time_s", "x_m", "v_m_s", "force_n")


@dataclass(frozen=True)
class RunConfig:
    schema_version: str
    experiment_id: str
    seed: int
    model: str
    mass_kg: float
    drag_per_s: float
    force_n: float
    dt_s: float
    duration_s: float
    initial_x_m: float = 0.0
    initial_v_m_s: float = 0.0

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION or self.model != MODEL:
            raise ValueError("unsupported schema_version or model")
        if not self.experiment_id or not isinstance(self.experiment_id, str):
            raise ValueError("experiment_id must be a nonempty string")
        if type(self.seed) is not int:
            raise ValueError("seed must be an integer")
        for name in ("mass_kg", "drag_per_s", "force_n", "dt_s", "duration_s", "initial_x_m", "initial_v_m_s"):
            val = getattr(self, name)
            if not isinstance(val, (int, float)) or not math.isfinite(val):
                raise ValueError(f"{name} must be finite")
        if self.mass_kg <= 0 or self.dt_s <= 0 or self.duration_s <= 0 or self.drag_per_s < 0:
            raise ValueError("mass, dt, duration > 0 and drag >= 0 required")
        if self.dt_s * self.drag_per_s > 1:
            raise ValueError("dt_s * drag_per_s must be <= 1 (non-oscillatory drag update)")
        count = self.duration_s / self.dt_s
        if not math.isfinite(count) or count > 1_000_000 or count < 1:
            raise ValueError("step count must be in [1, 1_000_000]")
        if not math.isclose(count, round(count), rel_tol=1e-12, abs_tol=1e-12):
            raise ValueError("duration_s must be an integer multiple of dt_s")

    @property
    def steps(self) -> int:
        return round(self.duration_s / self.dt_s)

    @classmethod
    def from_json(cls, path: Path) -> RunConfig:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("config must be an object")
        return cls(**data)


@dataclass(frozen=True)
class State:
    time_s: float
    x_m: float
    v_m_s: float
    force_n: float


def step(x: float, v: float, *, mass_kg: float, drag_per_s: float, force_n: float, dt_s: float) -> tuple[float, float]:
    """Semi-implicit Euler: velocity updated before position."""
    v_next = v + dt_s * (force_n / mass_kg - drag_per_s * v)
    x_next = x + dt_s * v_next
    return x_next, v_next


def simulate(config: RunConfig) -> list[State]:
    x, v = config.initial_x_m, config.initial_v_m_s
    states: list[State] = []
    for i in range(config.steps + 1):
        states.append(State(i * config.dt_s, x, v, config.force_n))
        if i < config.steps:
            x, v = step(x, v, mass_kg=config.mass_kg, drag_per_s=config.drag_per_s, force_n=config.force_n, dt_s=config.dt_s)
    return states


def analytic_state(config: RunConfig, t: float) -> tuple[float, float]:
    """Exact solution of the CONTINUOUS ODE, useful for numerical-error checks."""
    a = config.force_n / config.mass_kg
    g = config.drag_per_s
    if g == 0:
        return config.initial_x_m + config.initial_v_m_s*t + .5*a*t*t, config.initial_v_m_s + a*t
    z = g * t
    # Dimensionless integrals avoid subtracting terms of order a/g.
    phi1 = -math.expm1(-z) / z if z != 0 else 1.0
    if abs(z) < 0.01:
        # (z + expm1(-z))/z**2 loses precision when z is small.
        phi2 = 0.5 - z/6 + z*z/24 - z**3/120 + z**4/720 - z**5/5040
    else:
        phi2 = (z + math.expm1(-z)) / (z*z)
    v = config.initial_v_m_s * math.exp(-z) + a*t*phi1
    x = config.initial_x_m + config.initial_v_m_s*t*phi1 + a*t*t*phi2
    return x, v


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_revision() -> str | None:
    try:
        p = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True, timeout=2)
        return p.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def _polyline(states: list[State], attr: str, top: float, height: float, color: str) -> str:
    values = [getattr(s, attr) for s in states]
    lo, hi = min(values), max(values)
    if hi == lo:
        lo -= 1.0
        hi += 1.0
    span = hi-lo
    xleft, width = 78.0, 580.0
    points = " ".join(f"{xleft+i*width/(len(states)-1):.2f},{top+height-(z-lo)/span*height:.2f}" for i,z in enumerate(values))
    return (f'<rect x="78" y="{top}" width="580" height="{height}" fill="none" stroke="#cbd5e1"/>'
            f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2"/>'
            f'<text x="74" y="{top+12}" text-anchor="end" font-size="12">{hi:.4g}</text>'
            f'<text x="74" y="{top+height}" text-anchor="end" font-size="12">{lo:.4g}</text>')


def plot_svg(states: list[State], experiment_id: str) -> str:
    title = escape(experiment_id)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="720" height="420" viewBox="0 0 720 420">'
            f'<rect width="720" height="420" fill="white"/>'
            f'<g font-family="Arial,sans-serif" fill="#334155">'
            f'<text x="78" y="29" font-size="18" font-weight="bold">{title}: motion trace</text>'
            f'<text x="78" y="53" font-size="13">position x [m]</text>'
            + _polyline(states, "x_m", 63, 130, "#2563eb")
            + '<text x="78" y="231" font-size="13">velocity v [m/s]</text>'
            + _polyline(states, "v_m_s", 242, 130, "#0f766e")
            + f'<text x="78" y="395" font-size="12">0 s</text>'
            + f'<text x="658" y="395" font-size="12" text-anchor="end">{states[-1].time_s:.5g} s</text>'
            + '</g></svg>')


def save_run(config: RunConfig, output_dir: Path) -> dict[str, Any]:
    """Create an immutable output directory; never overwrite past observations."""
    states = simulate(config)
    output_dir.mkdir(parents=True, exist_ok=False)
    config_path = output_dir / "config.json"
    config_path.write_text(json.dumps(asdict(config), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    csv_path = output_dir / "states.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        writer.writerows((s.time_s, s.x_m, s.v_m_s, s.force_n) for s in states)
    svg_path = output_dir / "motion.svg"
    svg_path.write_text(plot_svg(states, config.experiment_id), encoding="utf-8")
    exact_x, exact_v = analytic_state(config, config.duration_s)
    actual = states[-1]
    manifest = {
        "experiment_id": config.experiment_id,
        "schema_version": SCHEMA_VERSION,
        "model": MODEL,
        "integration": "semi_implicit_euler",
        "python_code_git_commit": _git_revision(),
        "seed": config.seed,
        "seed_note": "not used: this experiment has no randomness",
        "sample_count": len(states),
        "final_x_m": actual.x_m,
        "final_v_m_s": actual.v_m_s,
        "analytic_x_m": exact_x,
        "analytic_v_m_s": exact_v,
        "absolute_x_error_m": abs(actual.x_m-exact_x),
        "absolute_v_error_m_s": abs(actual.v_m_s-exact_v),
        "artifacts": {name: _sha256(output_dir/name) for name in ("config.json", "states.csv", "motion.svg")},
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="SOMA F001: simulate a single 1D cell")
    parser.add_argument("--config", type=Path, required=True, help="JSON experiment settings")
    parser.add_argument("--output-dir", type=Path, required=True, help="NEW output directory, no overwrite")
    args = parser.parse_args()
    config = RunConfig.from_json(args.config)
    summary = save_run(config, args.output_dir)
    print(json.dumps({"output_dir": str(args.output_dir), **{k: v for k, v in summary.items() if k in ("final_x_m", "final_v_m_s", "absolute_x_error_m")}}, indent=2))


if __name__ == "__main__":
    main()
