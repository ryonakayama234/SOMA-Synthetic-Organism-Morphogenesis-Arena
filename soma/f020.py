"""F020: resource-earned, SAME-cell NEXT-step motor eligibility in fixed F007 world.

World truth for experimenters only; no learner, physical docking, B motor, or
biological metabolism. F001–F019 v1 source and evidence remain immutable.
"""
from __future__ import annotations

from dataclasses import asdict
import math

from soma.f002 import Cell, Event, apply_event, new_ledger
from soma.f005 import positive_motor_work
from soma.f007 import Config, motion
from soma.f018 import AttachmentIntent, resolve_attachment
from soma.f019 import field_for, first_entry

SCHEMA = "f020.v1"
BALANCES = (75_000, 250_000, 4_000_000)
FEES = (0, 25_000)
MODES = ("feedback", "deferred_credit")
ARMS = ("YY", "NN")
CAPACITY = 20_000_000
STEPS = 4
DT = 0.25


def scene_for(seed: int, sign: int, count: int, radius: float,
              balance: int, fee: int) -> dict:
    if (type(sign) is not int or sign not in (-1, 1)
            or type(balance) is not int or balance not in BALANCES
            or type(fee) is not int or fee not in FEES):
        raise ValueError("non-preregistered F020 factor")
    field = field_for(seed, count, radius)
    return {"schema_version": SCHEMA, "kind": "primary",
            "scenario_id": (f"{field['field_id']}-sign{sign:+d}"
                            f"-bal{balance:07d}-fee{fee:05d}"),
            "base_seed": seed, "motor_sign": sign,
            "initial_balance_uj": balance, "join_fee_uj": fee, "field": field}


def scenario_grid() -> list[dict]:
    worlds = [scene_for(s, sign, n, r, balance, fee)
              for s in range(32) for sign in (-1, 1) for n in (2, 5)
              for r in (.02, .06) for balance in BALANCES for fee in FEES]
    if len(worlds) != 1536 or len({x["scenario_id"] for x in worlds}) != 1536:
        raise ArithmeticError("F020 frozen design size")
    return worlds


def calibration_scene(kind: str = "positive") -> dict:
    """Synthetic calibration ONLY; never include in primary grid or estimand."""
    if kind not in ("positive", "b_only", "empty") or type(kind) is not str:
        raise ValueError("unknown calibration fixture")
    center = {"positive": .0625, "b_only": .1625, "empty": None}[kind]
    patches = ([] if center is None else
               [{"patch_id": "P0", "center_m": center, "radius_m": .005,
                 "initial_available_uj": 1_000_000}])
    return {"schema_version": SCHEMA, "kind": "calibration",
            "scenario_id": "F020-calibration-" + kind, "base_seed": None,
            "motor_sign": 1, "initial_balance_uj": 75_000,
            "join_fee_uj": 0,
            "field": {"field_id": "calibration-" + kind,
                      "generator_version": "synthetic-calibration-only",
                      "seed": None, "patches": patches}}


def validate_scene(scene: dict) -> None:
    if type(scene) is not dict or set(scene) != {
        "schema_version", "kind", "scenario_id", "base_seed",
        "motor_sign", "initial_balance_uj", "join_fee_uj", "field"
    } or scene["schema_version"] != SCHEMA:
        raise ValueError("F020 scene schema")
    if scene["kind"] == "calibration":
        expected = calibration_scene(scene["scenario_id"].removeprefix("F020-calibration-"))
    elif scene["kind"] == "primary":
        fld = scene["field"]
        if type(fld) is not dict or set(fld) != {
            "field_id", "generator_version", "seed", "patches"
        } or type(fld["patches"]) is not list or not fld["patches"]:
            raise ValueError("F020 field schema")
        expected = scene_for(scene["base_seed"], scene["motor_sign"],
                             len(fld["patches"]), fld["patches"][0]["radius_m"],
                             scene["initial_balance_uj"], scene["join_fee_uj"])
    else:
        raise ValueError("F020 scene kind")
    if expected != scene:
        raise ValueError("noncanonical F020 scene or field")


def config_for(scene: dict, attached: bool, motor: float) -> Config:
    bal = scene["initial_balance_uj"] - (scene["join_fee_uj"] if attached else 0)
    return Config.from_dict({
        "schema_version": "f007.v1",
        "experiment_id": "F020-" + scene["scenario_id"], "seed": None,
        "dt_s": DT, "duration_s": 1., "drag_per_s": 0.,
        "cells": [
            {"id": "A", "mass_kg": 1., "initial_x_m": 0.,
             "initial_v_m_s": 0., "external_force_n": 0.,
             "capacity_uj": CAPACITY, "initial_balance_uj": bal},
            {"id": "B", "mass_kg": 1., "initial_x_m": .1,
             "initial_v_m_s": 0., "external_force_n": 0.,
             "capacity_uj": CAPACITY, "initial_balance_uj": bal},
        ],
        "motor_force_n": motor,
        "link": {"initially_attached": attached, "length_m": .1,
                 "detach_time_s": None},
    })


def simulate_world(scene: dict, arm: str, credit_mode: str,
                   motor_force_n: float | None = None) -> dict:
    """Chronological F002/F007/F019 coupling, immutable same-cell credit."""
    validate_scene(scene)
    if type(arm) is not str or arm not in ARMS:
        raise ValueError("unregistered consent arm")
    if type(credit_mode) is not str or credit_mode not in MODES:
        raise ValueError("credit mode")
    motor = (float(2 * scene["motor_sign"]) if motor_force_n is None
             else motor_force_n)
    if type(motor) is not float or motor not in (-2., 0., 2.):
        raise ValueError("motor must be frozen ±2N or calibration off")
    if motor_force_n is not None and motor == 0. and scene["kind"] != "calibration":
        raise ValueError("motor-off forbidden in frozen primary grid")
    gate_cfg = config_for(scene, False, motor)
    attached = resolve_attachment(
        AttachmentIntent("A", 0, arm[0] == "Y"),
        AttachmentIntent("B", 0, arm[1] == "Y"), gate_cfg)
    cfg = config_for(scene, attached, motor)
    initial = scene["initial_balance_uj"]
    ledger = new_ledger([Cell("A", CAPACITY, initial),
                         Cell("B", CAPACITY, initial)])
    events: list[dict] = []
    hits: list[dict] = []
    states: list[dict] = []
    pending = {"A": 0, "B": 0}
    acquired = {"A": 0, "B": 0}
    motor_spent = {"A": 0, "B": 0}
    fee_spent = {"A": 0, "B": 0}
    remaining = {p["patch_id"]: p["initial_available_uj"]
                 for p in scene["field"]["patches"]}
    if len(remaining) != len(scene["field"]["patches"]):
        raise ValueError("duplicate patch id")

    def post(k: int, phase: str, event: Event) -> int:
        nonlocal ledger
        ledger, entry = apply_event(ledger, event)
        events.append({"step_index": k, "phase": phase, **asdict(entry),
                       "balance_a_uj": ledger.cell("A").balance_uj,
                       "balance_b_uj": ledger.cell("B").balance_uj})
        return entry.event_index

    if attached and scene["join_fee_uj"]:
        for cell in ("A", "B"):
            post(0, "fee", Event("spend", scene["join_fee_uj"], source_id=cell))
            fee_spent[cell] += scene["join_fee_uj"]

    x, v = (0., .1), (0., 0.)
    def row(k: int, before_a: int, before_b: int, applied: float,
            candidate: float | None, candidate_cost: int | None,
            spent: int, reason: str, event_idx: int | None,
            residual: float) -> dict:
        return {"step_index": k, "time_s": k * DT,
                "x_a_m": x[0], "x_b_m": x[1],
                "v_a_m_s": v[0], "v_b_m_s": v[1],
                "available_a_before_uj": before_a,
                "available_b_before_uj": before_b,
                "balance_a_uj": ledger.cell("A").balance_uj,
                "balance_b_uj": ledger.cell("B").balance_uj,
                "pending_a_uj": pending["A"], "pending_b_uj": pending["B"],
                "motor_command_n": motor, "motor_applied_n": applied,
                "candidate_positive_work_j": candidate,
                "candidate_charge_uj": candidate_cost,
                "spent_a_uj": spent, "reason": reason,
                "ledger_event_index": event_idx,
                "mechanical_residual_j": residual}
    ba = ledger.cell("A").balance_uj
    bb = ledger.cell("B").balance_uj
    states.append(row(0, ba, bb, 0., None, None, 0, "initial", None, 0.))

    for k in range(1, STEPS + 1):
        prev_x, prev_v = x, v
        before_a = ledger.cell("A").balance_uj
        before_b = ledger.cell("B").balance_uj
        candidate, requested = None, None
        applied, spent, event_idx = 0., 0, None
        if before_a == 0:
            reason = "zero_balance"
        elif motor == 0.:
            reason = "zero_command"
        else:
            trial_x, trial_v, trial_link = motion(cfg, x, v, attached, motor)
            candidate = positive_motor_work(motor, v[0], trial_v[0], DT)
            requested = math.ceil(candidate * 1_000_000)
            if requested <= before_a:
                applied = motor
                spent = requested
                reason = ("accepted_positive_work" if spent else
                          "accepted_nonpositive_work")
                x, v, link_b = trial_x, trial_v, trial_link
            else:
                reason = "insufficient_balance"
        if applied == 0.:
            x, v, link_b = motion(cfg, prev_x, prev_v, attached, 0.)
        if spent:
            event_idx = post(k, "motor", Event("spend", spent, source_id="A"))
            motor_spent["A"] += spent

        mid_a = (prev_v[0] + v[0]) / 2.
        mid_b = (prev_v[1] + v[1]) / 2.
        actual_work = applied * DT * mid_a
        link_work = DT * (-link_b * mid_a + link_b * mid_b) if attached else 0.
        dk = ((v[0] ** 2 + v[1] ** 2)
              - (prev_v[0] ** 2 + prev_v[1] ** 2)) / 2.
        residual = dk - (actual_work + link_work)
        if not math.isfinite(residual) or abs(residual) > 1e-11:
            raise ArithmeticError("F007 mechanical work balance failure")

        candidates = []
        for p in scene["field"]["patches"]:
            ident = p["patch_id"]
            if not remaining[ident]:
                continue
            for cell, ix in (("A", 0), ("B", 1)):
                part = first_entry(prev_x[ix], x[ix], p["center_m"],
                                   p["radius_m"])
                if part is not None:
                    candidates.append((part, ident, cell))
        for part, ident, cell in sorted(candidates):
            amount = remaining[ident]
            if not amount:
                continue
            remaining[ident] = 0
            hit = {"patch_id": ident, "step_index": k,
                   "entry_fraction_in_step": part,
                   "entry_time_s": (k - 1 + part) * DT,
                   "winner_cell_id": cell, "available_before_uj": amount,
                   "acquired_uj": amount, "available_after_uj": 0,
                   "ordinal": len(hits) + 1}
            hits.append(hit)
            acquired[cell] += amount
            if credit_mode == "feedback":
                post(k, "harvest", Event("acquire", amount, target_id=cell))
            else:
                pending[cell] += amount
        states.append(row(k, before_a, before_b, applied, candidate,
                          requested, spent, reason, event_idx, residual))
    if credit_mode == "deferred_credit":
        for hit in hits:
            cell = hit["winner_cell_id"]
            post(STEPS, "settlement",
                 Event("acquire", hit["acquired_uj"], target_id=cell))
            pending[cell] -= hit["acquired_uj"]
        if pending != {"A": 0, "B": 0}:
            raise ArithmeticError("pending settlement mismatch")
    if ledger.residual_uj:
        raise ArithmeticError("F002 ledger conservation failure")
    net = {cell: acquired[cell] - motor_spent[cell] - fee_spent[cell]
           for cell in ("A", "B")}
    summary = {"initial_total_uj": ledger.initial_total_uj,
               "acquired_uj": ledger.acquired_uj,
               "spent_uj": ledger.spent_uj, "loss_uj": ledger.loss_uj,
               "residual_uj": ledger.residual_uj,
               "balance_a_uj": ledger.cell("A").balance_uj,
               "balance_b_uj": ledger.cell("B").balance_uj,
               "event_count": ledger.event_index}
    return {"scenario": scene, "world_id": scene["scenario_id"] + "::" +
            arm + "::" + credit_mode, "arm": arm,
            "credit_mode": credit_mode, "motor_force_n": motor,
            "attached": attached, "states": states, "harvests": hits,
            "events": events, "ledger": summary, "acquired_uj": acquired,
            "spent_motor_uj": motor_spent, "spent_fee_uj": fee_spent,
            "net_uj": net}
