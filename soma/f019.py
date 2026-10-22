"""F019: investigator-only, finite trajectory-blind resource ecology for F007/F018.

No learner, mid-run topology update, true docking, energy transfer or B motor.
A resource is external energy assigned to the cell that FIRST enters its patch.
"""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import math

from soma.f002 import Cell as EnergyCell, Event, apply_event, new_ledger
from soma.f007 import Config as MotionConfig, simulate as motion_simulate
from soma.f018 import AttachmentIntent, resolve_attachment

SCHEMA = "f019.v1"
ARMS = ("YY", "YN", "NY", "NN")
MOTORS = (-2.0, 0.0, 2.0)
CAPACITY_UJ = 20_000_000
INITIAL_UJ = 10_000_000
PATCH_UJ = 1_000_000
SEEDS = tuple(range(32))
SIGNS = (-1, 1)
FEES_UJ = (0, 100_000)
PATCH_COUNTS = (2, 5)
RADII_M = (0.02, 0.06)


def field_for(seed: int, count: int, radius: float) -> dict:
    """Fixed SHA256-grid sampler; neither scores nor predicted paths enter."""
    if type(seed) is not int or seed not in SEEDS or type(count) is not int or count not in PATCH_COUNTS:
        raise ValueError("nonfrozen seed or count")
    if type(radius) is not float or radius not in RADII_M:
        raise ValueError("nonfrozen radius")
    patches = []
    for i in range(count):
        for draw in range(10_000):
            message = f"F019-field-v1|seed={seed}|patch={i}|draw={draw}".encode("ascii")
            index = int.from_bytes(hashlib.sha256(message).digest()[:8], "big") % 121
            center = (index - 60) * 0.025
            if abs(center) <= radius or abs(center - 0.1) <= radius:
                continue
            patches.append({"patch_id": f"P{i}", "center_m": center,
                            "radius_m": radius, "initial_available_uj": PATCH_UJ})
            break
        else:
            raise ArithmeticError("generator exhausted predeclared draw limit")
    return {"field_id": f"s{seed:02d}-n{count}-r{int(radius*1000):03d}",
            "generator_version": "sha256-grid-v1", "seed": seed, "patches": patches}


def scenario_for(seed: int, sign: int, fee: int, count: int, radius: float) -> dict:
    if type(sign) is not int or sign not in SIGNS or type(fee) is not int or fee not in FEES_UJ:
        raise ValueError("nonfrozen motor sign or fee")
    field = field_for(seed, count, radius)
    return {"schema_version": SCHEMA,
            "scenario_id": f"{field['field_id']}-sign{sign:+d}-fee{fee:06d}",
            "base_seed": seed, "motor_sign": sign, "join_fee_uj": fee, "field": field}


def scenario_grid() -> list[dict]:
    result = [scenario_for(s, u, fee, n, r) for s in SEEDS for u in SIGNS
              for fee in FEES_UJ for n in PATCH_COUNTS for r in RADII_M]
    assert len(result) == 512 and len({v["scenario_id"] for v in result}) == 512
    return result


def validate_scene(scene: dict) -> None:
    if type(scene) is not dict or set(scene) != {"schema_version", "scenario_id",
             "base_seed", "motor_sign", "join_fee_uj", "field"} or scene["schema_version"] != SCHEMA:
        raise ValueError("scene schema")
    fld = scene["field"]
    if type(fld) is not dict or set(fld) != {"field_id", "generator_version", "seed", "patches"}:
        raise ValueError("field schema")
    expected = scenario_for(scene["base_seed"], scene["motor_sign"],
                            scene["join_fee_uj"], len(fld["patches"]),
                            fld["patches"][0]["radius_m"])
    if scene != expected:
        raise ValueError("noncanonical or path-tuned resource scene")


def _config(scene: dict, joined: bool, motor: float) -> MotionConfig:
    fee = scene["join_fee_uj"] if joined else 0
    return MotionConfig.from_dict({
        "schema_version": "f007.v1", "experiment_id": "F019-" + scene["scenario_id"],
        "seed": None, "dt_s": 0.25, "duration_s": 1.0, "drag_per_s": 0.0,
        "cells": [
            {"id": "A", "mass_kg": 1.0, "initial_x_m": 0.0, "initial_v_m_s": 0.0,
             "external_force_n": 0.0, "capacity_uj": CAPACITY_UJ,
             "initial_balance_uj": INITIAL_UJ - fee},
            {"id": "B", "mass_kg": 1.0, "initial_x_m": 0.1, "initial_v_m_s": 0.0,
             "external_force_n": 0.0, "capacity_uj": CAPACITY_UJ,
             "initial_balance_uj": INITIAL_UJ - fee},
        ], "motor_force_n": motor,
        "link": {"initially_attached": joined, "length_m": 0.1, "detach_time_s": None},
    })


def first_entry(x0: float, x1: float, center: float, radius: float) -> float | None:
    """First fractional intersection with a closed 1D interval, x linear in f."""
    if not all(type(x) in (float, int) and math.isfinite(x)
               for x in (x0, x1, center, radius)) or radius < 0:
        raise ValueError("nonfinite/invalid segment or radius")
    lo, hi = center - radius, center + radius
    if lo <= x0 <= hi:
        return 0.0
    if x0 == x1 or max(x0, x1) < lo or min(x0, x1) > hi:
        return None
    entry_boundary = lo if x1 > x0 else hi
    fraction = (entry_boundary - x0) / (x1 - x0)
    if not 0.0 <= fraction <= 1.0:
        raise ArithmeticError("segment entry outside step")
    return fraction


def harvests_from_states(field: dict, states: list[dict]) -> list[dict]:
    """World-local destructive claims; initial field is never mutated."""
    remaining = {p["patch_id"]: p["initial_available_uj"] for p in field["patches"]}
    result = []
    for k in range(1, len(states)):
        previous, current = states[k-1], states[k]
        candidates = []
        for patch in field["patches"]:
            ident = patch["patch_id"]
            if remaining[ident] == 0:
                continue
            for cell in ("A", "B"):
                ckey = "x_a_m" if cell == "A" else "x_b_m"
                frac = first_entry(previous[ckey], current[ckey],
                                   patch["center_m"], patch["radius_m"])
                if frac is not None:
                    candidates.append((frac, ident, cell))
        for frac, ident, cell in sorted(candidates):
            amount = remaining[ident]
            if not amount:
                continue
            remaining[ident] = 0
            result.append({
                "patch_id": ident, "step_index": k,
                "entry_fraction_in_step": frac,
                "entry_time_s": (k - 1 + frac) * .25,
                "winner_cell_id": cell,
                "available_before_uj": amount, "acquired_uj": amount,
                "available_after_uj": 0, "ordinal": len(result) + 1,
            })
    return result


def simulate_world(scene: dict, arm: str, motor_force_n: float | None = None) -> dict:
    validate_scene(scene)
    if type(arm) is not str or arm not in ARMS:
        raise ValueError("consent arm")
    motor = float(2 * scene["motor_sign"]) if motor_force_n is None else motor_force_n
    if type(motor) is not float or motor not in MOTORS:
        raise ValueError("nonfrozen motor action")
    gate = _config(scene, False, motor)
    joined = resolve_attachment(AttachmentIntent("A", 0, arm[0] == "Y"),
                                AttachmentIntent("B", 0, arm[1] == "Y"), gate)
    states, _motor_events, link_events, physical_ledger = motion_simulate(_config(scene, joined, motor))
    claims = harvests_from_states(scene["field"], states)
    by_step: dict[int, list[dict]] = {}
    for hit in claims:
        by_step.setdefault(hit["step_index"], []).append(hit)
    ledger = new_ledger([EnergyCell("A", CAPACITY_UJ, INITIAL_UJ),
                         EnergyCell("B", CAPACITY_UJ, INITIAL_UJ)])
    events = []
    acquired = {"A": 0, "B": 0}
    motor_spent = {"A": 0, "B": 0}
    join_spent = {"A": 0, "B": 0}

    def post(k: int, event: Event) -> None:
        nonlocal ledger
        ledger, entry = apply_event(ledger, event)
        events.append({"step_index": k, **asdict(entry),
                       "balance_a_uj": ledger.cell("A").balance_uj,
                       "balance_b_uj": ledger.cell("B").balance_uj})

    if joined and scene["join_fee_uj"]:
        for cell in ("A", "B"):
            post(0, Event("spend", scene["join_fee_uj"], source_id=cell))
            join_spent[cell] += scene["join_fee_uj"]
    for k in range(1, 5):
        spent = states[k]["spent_a_uj"]
        if spent:
            post(k, Event("spend", spent, source_id="A"))
            motor_spent["A"] += spent
        for hit in by_step.get(k, []):
            post(k, Event("acquire", hit["acquired_uj"], target_id=hit["winner_cell_id"]))
            acquired[hit["winner_cell_id"]] += hit["acquired_uj"]
    for cell in ("A", "B"):
        if ledger.cell(cell).balance_uj - acquired[cell] != physical_ledger.cell(cell).balance_uj:
            raise ArithmeticError("F007/F002 disagreement over fee and motor cost")
    if ledger.residual_uj:
        raise ArithmeticError("F002 energy residual")
    net = {c: acquired[c] - motor_spent[c] - join_spent[c] for c in ("A", "B")}
    return {"scenario_id": scene["scenario_id"], "arm": arm, "motor_force_n": motor,
            "attached": joined, "states": states, "link_events": link_events,
            "harvests": claims, "events": events, "net_uj": net,
            "acquired_uj": acquired, "motor_spent_uj": motor_spent,
            "join_spent_uj": join_spent,
            "ledger": {"initial_total_uj": ledger.initial_total_uj,
                       "acquired_uj": ledger.acquired_uj,
                       "spent_uj": ledger.spent_uj, "loss_uj": ledger.loss_uj,
                       "residual_uj": ledger.residual_uj,
                       "balance_a_uj": ledger.cell("A").balance_uj,
                       "balance_b_uj": ledger.cell("B").balance_uj,
                       "event_count": ledger.event_index}}


def summarize(scene: dict, primary: dict[str, dict], outside: dict[float, dict]) -> dict:
    if set(primary) != set(ARMS) or set(outside) != set(MOTORS):
        raise ValueError("missing paired fork")
    a, b = primary["YY"], primary["NN"]
    maxima = {c: max(outside[u]["net_uj"][c] for u in MOTORS) for c in ("A", "B")}
    fixed = {c: a["net_uj"][c] - b["net_uj"][c] for c in ("A", "B")}
    opt = {c: a["net_uj"][c] - maxima[c] for c in ("A", "B")}
    def ownership(world: dict) -> dict:
        return {h["patch_id"]: h for h in world["harvests"]}
    yy, nn = ownership(a), ownership(b)
    patch_comparison = []
    for patch in scene["field"]["patches"]:
        ident = patch["patch_id"]
        w1 = yy.get(ident)
        w0 = nn.get(ident)
        c1, c0 = (w1 or {}).get("winner_cell_id"), (w0 or {}).get("winner_cell_id")
        t1, t0 = (w1 or {}).get("entry_time_s"), (w0 or {}).get("entry_time_s")
        patch_comparison.append({
            "patch_id": ident, "winner_yy": c1, "winner_nn": c0,
            "entry_time_yy_s": t1, "entry_time_nn_s": t0,
            "winner_changed": c1 != c0,
            "entry_time_yy_minus_nn_s": t1-t0 if t1 is not None and t0 is not None else None,
        })
    return {"scenario_id": scene["scenario_id"], "base_seed": scene["base_seed"],
            "field_id": scene["field"]["field_id"],
            "patch_comparison": patch_comparison,
            "winner_switch_count": sum(int(x["winner_changed"]) for x in patch_comparison),
            "primary_net_uj": {arm: primary[arm]["net_uj"] for arm in ARMS},
            "outside_net_uj": {str(int(u)): outside[u]["net_uj"] for u in MOTORS},
            "outside_best_uj": maxima,
            "outside_best_motors_n": {
                c: [int(u) for u in MOTORS if outside[u]["net_uj"][c] == maxima[c]]
                for c in ("A", "B")},
            "delta_fixed_uj": fixed, "delta_outside_uj": opt,
            "pareto_fixed": all(x > 0 for x in fixed.values()),
            "pareto_outside": all(x > 0 for x in opt.values()),
            "unclaimed_yy_uj": PATCH_UJ * len(scene["field"]["patches"]) -
                               sum(h["acquired_uj"] for h in a["harvests"]),
            "unclaimed_nn_uj": PATCH_UJ * len(scene["field"]["patches"]) -
                               sum(h["acquired_uj"] for h in b["harvests"])}
