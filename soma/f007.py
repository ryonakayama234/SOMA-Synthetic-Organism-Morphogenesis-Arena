"""F007: one driven cell A pulls a passive cell B across an ideal 1D rigid link.

World truth only. Motor force is an EXTERNAL EFFECTIVE FORCE; the ground/reaction
mechanism and electric powertrain are not modeled. No agent, sensors or learning.
"""
from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import subprocess
from xml.sax.saxutils import escape

from soma.f001 import step as f001_step
from soma.f002 import Cell as BatteryCell, Event, LedgerState, apply_event, new_ledger, MAX_UJ
from soma.f005 import positive_motor_work

SCHEMA = "f007.v1"
MAX_STEPS = 10_000
STATE_COLUMNS = (
    "step_index", "time_s", "attached", "x_a_m", "x_b_m", "v_a_m_s", "v_b_m_s",
    "motor_command_n", "motor_applied_n", "external_force_a_n", "external_force_b_n",
    "link_force_a_n", "link_force_b_n", "candidate_motor_work_j",
    "candidate_motor_positive_work_j", "motor_work_j", "motor_positive_work_j",
    "external_work_j", "drag_work_j", "link_work_j", "kinetic_delta_j",
    "mechanical_residual_j", "spent_a_uj", "balance_a_uj", "balance_b_uj",
    "ledger_event_index", "decision_reason",
)
LEDGER_COLUMNS = (
    "step_index", "time_s", "event_index", "kind", "source_id", "target_id",
    "amount_uj", "eta_bps", "received_uj", "loss_uj", "external_in_uj",
    "external_out_uj", "residual_uj",
)
LINK_COLUMNS = (
    "time_s", "kind", "attached_before", "attached_after",
    "x_a_before_m", "x_a_after_m", "x_b_before_m", "x_b_after_m",
    "v_a_before_m_s", "v_a_after_m_s", "v_b_before_m_s", "v_b_after_m_s",
    "link_force_before_n",
)


def finite(value: object, field: str, *, positive: bool = False,
           nonnegative: bool = False) -> float:
    if type(value) not in (int, float):
        raise ValueError(field + ": expected finite number (not boolean)")
    try:
        n = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(field + ": unrepresentable number") from exc
    if not math.isfinite(n) or (positive and n <= 0) or (nonnegative and n < 0):
        raise ValueError(field + ": invalid range")
    return n


def all_finite(**values: float) -> None:
    if not all(math.isfinite(z) for z in values.values()):
        raise ValueError("non-finite derived value")


def exact(obj: object, fields: tuple[str, ...], name: str) -> dict:
    if not isinstance(obj, dict) or set(obj) != set(fields):
        raise ValueError(name + ": wrong fields")
    return obj


@dataclass(frozen=True)
class CellConfig:
    id: str
    mass_kg: float
    initial_x_m: float
    initial_v_m_s: float
    external_force_n: float
    capacity_uj: int
    initial_balance_uj: int


@dataclass(frozen=True)
class Config:
    schema_version: str
    experiment_id: str
    seed: None
    dt_s: float
    duration_s: float
    drag_per_s: float
    cells: tuple[CellConfig, CellConfig]
    motor_force_n: float
    initially_attached: bool
    length_m: float
    detach_time_s: float | None
    steps: int
    detach_step: int | None

    @classmethod
    def from_dict(cls, raw: object) -> "Config":
        d = exact(raw, ("schema_version", "experiment_id", "seed",
                       "dt_s", "duration_s", "drag_per_s", "cells",
                       "motor_force_n", "link"), "config")
        name = d["experiment_id"]
        if d["schema_version"] != SCHEMA or d["seed"] is not None:
            raise ValueError("schema or seed")
        if (type(name) is not str or not 1 <= len(name) <= 120 or
                not all(ch in "\t\n\r" or 0x20 <= ord(ch) <= 0xD7FF or
                        0xE000 <= ord(ch) <= 0xFFFD or
                        0x10000 <= ord(ch) <= 0x10FFFF for ch in name)):
            raise ValueError("experiment_id: invalid XML 1.0 text")
        dt = finite(d["dt_s"], "dt_s", positive=True)
        dur = finite(d["duration_s"], "duration_s", positive=True)
        drag = finite(d["drag_per_s"], "drag_per_s", nonnegative=True)
        if not math.isfinite(dt * drag) or dt * drag > 1:
            raise ValueError("unstable dt * drag")
        raw_steps = Fraction(str(d["duration_s"])) / Fraction(str(d["dt_s"]))
        normal_steps = Fraction(str(dur)) / Fraction(str(dt))
        if raw_steps.denominator != 1 or raw_steps != normal_steps or not 1 <= raw_steps <= MAX_STEPS:
            raise ValueError("invalid exact time grid")
        motor = finite(d["motor_force_n"], "motor_force_n")
        if type(d["cells"]) is not list or len(d["cells"]) != 2:
            raise ValueError("exactly two cells A and B")
        cells = []
        for i, c in enumerate(d["cells"]):
            c = exact(c, ("id", "mass_kg", "initial_x_m", "initial_v_m_s",
                          "external_force_n", "capacity_uj", "initial_balance_uj"), "cell")
            if c["id"] != ("A", "B")[i]:
                raise ValueError("ordered cell ids A, B required")
            cap, balance = c["capacity_uj"], c["initial_balance_uj"]
            if type(cap) is not int or not 1 <= cap <= MAX_UJ:
                raise ValueError("invalid capacity")
            if type(balance) is not int or not 0 <= balance <= cap:
                raise ValueError("invalid balance")
            cells.append(CellConfig(
                c["id"], finite(c["mass_kg"], "mass", positive=True),
                finite(c["initial_x_m"], "x"), finite(c["initial_v_m_s"], "v"),
                finite(c["external_force_n"], "external"), cap, balance))
        link = exact(d["link"], ("initially_attached", "length_m", "detach_time_s"), "link")
        if type(link["initially_attached"]) is not bool:
            raise ValueError("link flag")
        length = finite(link["length_m"], "length_m", positive=True)
        cut = link["detach_time_s"]
        if cut is not None:
            cut = finite(cut, "detach_time_s")
            cut_steps = Fraction(str(d["link"]["detach_time_s"])) / Fraction(str(d["dt_s"]))
            if (not link["initially_attached"] or not 0 < cut < dur or
                    cut_steps.denominator != 1 or
                    cut_steps != Fraction(str(cut)) / Fraction(str(dt))):
                raise ValueError("invalid detach time/grid")
            cut_step = int(cut_steps)
        else:
            cut_step = None
        a, b = cells
        if link["initially_attached"] and (
                b.initial_x_m - a.initial_x_m != length or
                b.initial_v_m_s != a.initial_v_m_s):
            raise ValueError("initial link constraints violated: no silent snapping")
        all_finite(mass_sum=a.mass_kg + b.mass_kg,
                   total_force=motor + a.external_force_n + b.external_force_n,
                   time_end=int(raw_steps) * dt)
        return cls(SCHEMA, name, None, dt, dur, drag, (a, b), motor,
                   link["initially_attached"], length, cut, int(raw_steps), cut_step)

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version, "experiment_id": self.experiment_id,
            "seed": None, "dt_s": self.dt_s, "duration_s": self.duration_s,
            "drag_per_s": self.drag_per_s, "cells": [asdict(c) for c in self.cells],
            "motor_force_n": self.motor_force_n,
            "link": {"initially_attached": self.initially_attached,
                     "length_m": self.length_m, "detach_time_s": self.detach_time_s},
        }


def link_event(t: float, kind: str, before: bool, after: bool,
               x: tuple[float, float], v: tuple[float, float], link_b: float) -> dict:
    return dict(time_s=t, kind=kind, attached_before=before, attached_after=after,
                x_a_before_m=x[0], x_a_after_m=x[0],
                x_b_before_m=x[1], x_b_after_m=x[1],
                v_a_before_m_s=v[0], v_a_after_m_s=v[0],
                v_b_before_m_s=v[1], v_b_after_m_s=v[1],
                link_force_before_n=link_b)


def motion(cfg: Config, x: tuple[float, float], v: tuple[float, float],
           attached: bool, applied: float) -> tuple[tuple[float, float], tuple[float, float], float]:
    a, b = cfg.cells
    fa, fb = applied + a.external_force_n, b.external_force_n
    all_finite(fa=fa, fb=fb, total=fa+fb)
    if attached:
        nx, nv = f001_step(x[0], v[0], mass_kg=a.mass_kg+b.mass_kg,
                          drag_per_s=cfg.drag_per_s, force_n=fa+fb, dt_s=cfg.dt_s)
        next_x = (nx, x[1] + (nx - x[0]))
        next_v = (nv, nv)
        # Newton's 3rd law, using mass ratios to avoid intermediate products.
        link_b = (b.mass_kg / (a.mass_kg+b.mass_kg)) * fa - (
            a.mass_kg / (a.mass_kg+b.mass_kg)) * fb
    else:
        ax, av = f001_step(x[0], v[0], mass_kg=a.mass_kg,
                          drag_per_s=cfg.drag_per_s, force_n=fa, dt_s=cfg.dt_s)
        bx, bv = f001_step(x[1], v[1], mass_kg=b.mass_kg,
                          drag_per_s=cfg.drag_per_s, force_n=fb, dt_s=cfg.dt_s)
        next_x, next_v, link_b = (ax, bx), (av, bv), 0.0
    all_finite(xa=next_x[0], xb=next_x[1], va=next_v[0],
               vb=next_v[1], link_b=link_b)
    return next_x, next_v, link_b


def simulate(cfg: Config) -> tuple[list[dict], list[dict], list[dict], LedgerState]:
    a, b = cfg.cells
    ledger = new_ledger([BatteryCell("A", a.capacity_uj, a.initial_balance_uj),
                         BatteryCell("B", b.capacity_uj, b.initial_balance_uj)])
    x, v = (a.initial_x_m, b.initial_x_m), (a.initial_v_m_s, b.initial_v_m_s)
    attached = cfg.initially_attached
    link_events = [link_event(0., "attach_initial", False, True, x, v, 0.)] if attached else []
    rows = [{
        "step_index": 0, "time_s": 0.0, "attached": attached,
        "x_a_m": x[0], "x_b_m": x[1], "v_a_m_s": v[0], "v_b_m_s": v[1],
        "motor_command_n": cfg.motor_force_n, "motor_applied_n": 0.0,
        "external_force_a_n": a.external_force_n, "external_force_b_n": b.external_force_n,
        "link_force_a_n": 0.0, "link_force_b_n": 0.0,
        "candidate_motor_work_j": None, "candidate_motor_positive_work_j": None,
        "motor_work_j": 0.0, "motor_positive_work_j": 0.0,
        "external_work_j": 0.0, "drag_work_j": 0.0, "link_work_j": 0.0,
        "kinetic_delta_j": 0.0, "mechanical_residual_j": 0.0,
        "spent_a_uj": 0, "balance_a_uj": a.initial_balance_uj,
        "balance_b_uj": b.initial_balance_uj, "ledger_event_index": None,
        "decision_reason": "initial",
    }]
    ledger_events = []
    h, u = cfg.dt_s, cfg.motor_force_n
    for k in range(1, cfg.steps + 1):
        prev_x, prev_v = x, v
        cost, candidate_work, candidate_positive = 0, None, None
        if ledger.cell("A").balance_uj == 0:
            applied, reason = 0., "zero_balance"
        elif u == 0:
            applied, reason = 0., "zero_command"
        else:
            tx, tv, unused_link = motion(cfg, x, v, attached, u)
            candidate_work = (u * h) * ((v[0] + tv[0]) / 2)
            candidate_positive = positive_motor_work(u, v[0], tv[0], h)
            micro = candidate_positive * 1_000_000
            all_finite(candidate_work=candidate_work, micro=micro)
            cost = math.ceil(micro)
            if cost <= ledger.cell("A").balance_uj:
                applied = u
                reason = "accepted_positive_work" if cost else "accepted_nonpositive_work"
                x, v, link_b = tx, tv, unused_link
            else:
                applied, reason, cost = 0., "insufficient_balance", 0
        if applied == 0:
            # Never reject a non-motor force or mechanical link due to A's battery.
            x, v, link_b = motion(cfg, prev_x, prev_v, attached, 0.)
        mid_a, mid_b = (prev_v[0]+v[0])/2, (prev_v[1]+v[1])/2
        motor_work = (applied*h) * mid_a
        motor_positive = positive_motor_work(applied, prev_v[0], v[0], h)
        external_work = h*(a.external_force_n*mid_a + b.external_force_n*mid_b)
        drag_work = h*cfg.drag_per_s*(a.mass_kg*prev_v[0]*mid_a + b.mass_kg*prev_v[1]*mid_b)
        link_work = h*(-link_b*mid_a + link_b*mid_b) if attached else 0.
        kinetic_delta = (
            (a.mass_kg*v[0]**2 + b.mass_kg*v[1]**2)
            -(a.mass_kg*prev_v[0]**2 + b.mass_kg*prev_v[1]**2)
        )/2
        mechanical_residual = kinetic_delta - (
            motor_work + external_work - drag_work + link_work)
        all_finite(motor_work=motor_work, motor_positive=motor_positive,
                   external_work=external_work, drag_work=drag_work,
                   link_work=link_work, kinetic_delta=kinetic_delta,
                   mechanical_residual=mechanical_residual)
        entry_index = None
        if cost:
            ledger, event = apply_event(
                ledger, Event(kind="spend", amount_uj=cost, source_id="A"))
            event_row = {"step_index": k, "time_s": k*h, **asdict(event)}
            ledger_events.append(event_row)
            entry_index = event.event_index
        if attached and cfg.detach_step == k:
            link_events.append(link_event(k*h, "detach", True, False, x, v, link_b))
            attached = False
        rows.append({
            "step_index": k, "time_s": k*h, "attached": attached,
            "x_a_m": x[0], "x_b_m": x[1], "v_a_m_s": v[0], "v_b_m_s": v[1],
            "motor_command_n": u, "motor_applied_n": applied,
            "external_force_a_n": a.external_force_n, "external_force_b_n": b.external_force_n,
            # Force describes the POST-event link state; before-force is in link_events.
            "link_force_a_n": -link_b if attached else 0.,
            "link_force_b_n": link_b if attached else 0.,
            "candidate_motor_work_j": candidate_work,
            "candidate_motor_positive_work_j": candidate_positive,
            "motor_work_j": motor_work, "motor_positive_work_j": motor_positive,
            "external_work_j": external_work, "drag_work_j": drag_work,
            "link_work_j": link_work, "kinetic_delta_j": kinetic_delta,
            "mechanical_residual_j": mechanical_residual, "spent_a_uj": cost,
            "balance_a_uj": ledger.cell("A").balance_uj,
            "balance_b_uj": ledger.cell("B").balance_uj,
            "ledger_event_index": entry_index, "decision_reason": reason,
        })
    if ledger.residual_uj != 0:
        raise ValueError("energy ledger conservation failed")
    return rows, ledger_events, link_events, ledger


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def provenance() -> dict:
    root = Path(__file__).resolve().parents[1]
    try:
        def run(*args: str) -> str:
            return subprocess.run(["git", "-C", str(root), *args], check=True,
                                  capture_output=True, text=True, timeout=3).stdout.strip()
        commit, dirty = run("rev-parse", "HEAD"), bool(run("status", "--porcelain", "--untracked-files=all"))
    except (OSError, subprocess.SubprocessError):
        commit, dirty = None, None
    return {"git_commit": commit, "git_dirty": dirty,
            "source_hashes": {path: sha(root / path) for path in (
                "soma/f001.py", "soma/f002.py", "soma/f003.py",
                "soma/f005.py", "soma/f007.py",
                "topics/F007-linked-motor-work/SPEC.md",
                "experiments/F007/PLAN.md", "experiments/F007/run_suite.py", "experiments/F007/verify.py")}}


def plot_svg(rows: list[dict], title: str) -> str:
    tmax = rows[-1]["time_s"]
    xvals = [r[key] for r in rows for key in ("x_a_m", "x_b_m")]
    lo, hi = min(xvals), max(xvals)
    scale = max(1., abs(lo), abs(hi))
    mn, mx = lo/scale, hi/scale
    span = mx-mn if mx != mn else 1.
    subset = rows[::max(1, len(rows)//400)]
    if subset[-1] is not rows[-1]:
        subset.append(rows[-1])
    paths = []
    for key, color in (("x_a_m","#2563eb"),("x_b_m","#059669")):
        points = " ".join(
            f'{70+620*(r["time_s"]/tmax):.3f},{180-140*((r[key]/scale-mn)/span):.3f}'
            for r in subset)
        paths.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2"/>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="780" height="230" '
            'viewBox="0 0 780 230"><rect width="780" height="230" fill="white"/>'
            f'<text x="70" y="24" font-family="Arial" font-size="16">{escape(title)}</text>'
            '<path d="M70 40V180H690" stroke="#64748b" fill="none"/>'
            + "".join(paths) + '</svg>')


def save_run(cfg: Config, directory: Path, *, identity: dict | None = None) -> dict:
    rows, spends, links, ledger = simulate(cfg)
    svg = plot_svg(rows, cfg.experiment_id)
    origin = provenance() if identity is None else identity
    # Config and physics are validated before publishing a normal run.
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "ledger").mkdir(exist_ok=False)
    (directory / "config.json").write_text(
        json.dumps(cfg.to_dict(), sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    for rel, columns, data in (
        ("states.csv", STATE_COLUMNS, rows),
        ("ledger/events.csv", LEDGER_COLUMNS, spends),
        ("link_events.csv", LINK_COLUMNS, links),
    ):
        with (directory / rel).open("w", encoding="utf-8", newline="") as fp:
            w = csv.DictWriter(fp, fieldnames=columns)
            w.writeheader()
            w.writerows(data)
    (directory / "motion.svg").write_text(svg, encoding="utf-8")
    artifacts = ("config.json", "states.csv", "ledger/events.csv",
                 "link_events.csv", "motion.svg")
    manifest = {"schema_version": SCHEMA, "model": "1d_two_cell_effective_motor_rigid_link",
                "experiment_id": cfg.experiment_id, "seed": None, "samples": len(rows),
                "ledger_events": len(spends), "link_events": len(links),
                "spent_uj": ledger.spent_uj, "final_balances_uj": {
                    c.cell_id: c.balance_uj for c in ledger.cells},
                "ledger_residual_uj": ledger.residual_uj, "origin": origin,
                "artifacts": {rel: sha(directory / rel) for rel in artifacts}}
    (directory / "manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return manifest
