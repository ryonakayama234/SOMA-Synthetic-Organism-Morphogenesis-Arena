"""F018: researcher-fixed bilateral attachment gate and individual payoff assay.

This is NOT an attachment learner, physical docking model, or emergent body.
All scene geometry and paired-world differences are researcher-only world truth.
F007 owns ideal 1D dynamics and A-only motor work; F002 owns integer-uJ ledger.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math

from soma.f002 import Cell as BatteryCell, Event, apply_event, new_ledger
from soma.f007 import Config as MotionConfig, simulate as motion_simulate

SCHEMA = "f018.v1"
LAYOUTS = ("NONE", "B_LINK", "A_SOLO", "DUAL_LINK", "DUAL_SOLO")
SIGNS = (-1, 1)
RADII_M = (0.01, 0.05, 0.2)
FEES_UJ = (0, 100_000, 500_000)
OUTSIDE_MOTORS_N = (-2.0, 0.0, 2.0)
ARMS = ("YY", "YN", "NY", "NN")
PATCH_AWARD_UJ = 3_000_000
INITIAL_BALANCE_UJ = 10_000_000
CAPACITY_UJ = 20_000_000


@dataclass(frozen=True)
class AttachmentIntent:
    cell_id: str
    step_index: int
    request_attach: bool

    def __post_init__(self) -> None:
        if self.cell_id not in ("A", "B") or type(self.cell_id) is not str:
            raise ValueError("attachment cell must be A or B")
        if type(self.step_index) is not int or self.step_index != 0:
            raise ValueError("F018 only accepts step-0 intent")
        if type(self.request_attach) is not bool:
            raise ValueError("request_attach must be a strict boolean")


def resolve_attachment(a: AttachmentIntent, b: AttachmentIntent,
                       cfg: MotionConfig) -> bool:
    """Never snap geometry, force consent, share energy, or award link score."""
    if a.cell_id != "A" or b.cell_id != "B":
        raise ValueError("intent order must be A then B")
    if cfg.initially_attached or cfg.detach_time_s is not None:
        raise ValueError("gate expects unlinked F007 initial world")
    if not (a.request_attach and b.request_attach):
        return False
    ca, cb = cfg.cells
    if cb.initial_x_m - ca.initial_x_m != cfg.length_m:
        raise ValueError("link distance mismatch: no invisible docking")
    if ca.initial_v_m_s != cb.initial_v_m_s:
        raise ValueError("link velocity mismatch: no free impulse")
    return True


def scenario_grid() -> list[dict]:
    """Exactly 5*2*3*3=90 deterministic preregistered worlds."""
    result = []
    for layout in LAYOUTS:
        for sign in SIGNS:
            joined_a, joined_b = 0.625 * sign, 0.1 + 0.625 * sign
            solo_a, solo_b = 1.25 * sign, 0.1
            centers = {
                "NONE": (),
                "B_LINK": (joined_b,),
                "A_SOLO": (solo_a,),
                "DUAL_LINK": (joined_a, joined_b),
                "DUAL_SOLO": (solo_a, solo_b),
            }[layout]
            for radius in RADII_M:
                for fee in FEES_UJ:
                    result.append({
                        "schema_version": SCHEMA,
                        "scenario_id": (
                            f"{layout}-s{sign:+d}-r{int(radius*1000):03d}"
                            f"-fee{fee:06d}"
                        ),
                        "layout": layout, "motor_sign": sign,
                        "terminal_radius_m": radius, "join_fee_uj": fee,
                        "patches": [
                            {"id": f"P{index}", "center_m": center,
                             "radius_m": radius, "amount_uj": PATCH_AWARD_UJ}
                            for index, center in enumerate(centers)
                        ],
                    })
    assert len(result) == 90 and len({x["scenario_id"] for x in result}) == 90
    return result


def validate_scenario(scene: dict) -> None:
    if type(scene) is not dict or set(scene) != {
        "schema_version", "scenario_id", "layout", "motor_sign",
        "terminal_radius_m", "join_fee_uj", "patches"
    }:
        raise ValueError("wrong f018.v1 scene fields")
    # Match the exact frozen factorial, without invented post-hoc cases.
    if scene["schema_version"] != SCHEMA or not isinstance(scene["scenario_id"], str):
        raise ValueError("scene schema/id")
    if type(scene["motor_sign"]) is not int or scene["motor_sign"] not in SIGNS:
        raise ValueError("scene sign")
    if type(scene["join_fee_uj"]) is not int or scene["join_fee_uj"] not in FEES_UJ:
        raise ValueError("scene fee")
    if type(scene["terminal_radius_m"]) is not float or scene["terminal_radius_m"] not in RADII_M:
        raise ValueError("scene radius")
    canonical = next((s for s in scenario_grid()
                      if s["scenario_id"] == scene["scenario_id"]), None)
    if canonical is None or scene != canonical:
        raise ValueError("noncanonical or post-hoc scene")


def _f007_config(scene: dict, joined: bool, motor_n: float) -> MotionConfig:
    fee = scene["join_fee_uj"] if joined else 0
    config = {
        "schema_version": "f007.v1",
        "experiment_id": "F018-" + scene["scenario_id"],
        "seed": None, "dt_s": 0.25, "duration_s": 1.0, "drag_per_s": 0.0,
        "cells": [
            {"id": "A", "mass_kg": 1.0, "initial_x_m": 0.0,
             "initial_v_m_s": 0.0, "external_force_n": 0.0,
             "capacity_uj": CAPACITY_UJ,
             "initial_balance_uj": INITIAL_BALANCE_UJ - fee},
            {"id": "B", "mass_kg": 1.0, "initial_x_m": 0.1,
             "initial_v_m_s": 0.0, "external_force_n": 0.0,
             "capacity_uj": CAPACITY_UJ,
             "initial_balance_uj": INITIAL_BALANCE_UJ - fee},
        ],
        "motor_force_n": motor_n,
        "link": {"initially_attached": joined, "length_m": 0.1,
                 "detach_time_s": None},
    }
    return MotionConfig.from_dict(config)


def terminal_claims(scene: dict, last_row: dict) -> list[dict]:
    """Finite, terminal-only, one claimant per patch; ties to A."""
    claims = []
    xs = {"A": last_row["x_a_m"], "B": last_row["x_b_m"]}
    for patch in scene["patches"]:
        candidates = sorted(
            (abs(xs[cell] - patch["center_m"]), cell)
            for cell in ("A", "B")
            if abs(xs[cell] - patch["center_m"]) <= patch["radius_m"]
        )
        if candidates:
            distance, winner = candidates[0]
            claims.append({"patch_id": patch["id"], "cell_id": winner,
                           "amount_uj": patch["amount_uj"], "distance_m": distance})
    return claims


def simulate_world(scene: dict, arm: str, motor_force_n: float | None = None) -> dict:
    validate_scenario(scene)
    if arm not in ARMS or type(arm) is not str:
        raise ValueError("invalid consent arm")
    requested = 2.0 * scene["motor_sign"] if motor_force_n is None else motor_force_n
    if type(requested) is not float or requested not in OUTSIDE_MOTORS_N:
        raise ValueError("unregistered motor action")
    # A separate unlinked config is used for the gate; the final F007 config
    # is built after fee assignment so motor-acceptance honors the paid fee.
    gate_cfg = _f007_config(scene, False, requested)
    intent_a = AttachmentIntent("A", 0, arm[0] == "Y")
    intent_b = AttachmentIntent("B", 0, arm[1] == "Y")
    joined = resolve_attachment(intent_a, intent_b, gate_cfg)
    cfg = _f007_config(scene, joined, requested)
    states, f007_ledger, link_events, physical_ledger = motion_simulate(cfg)

    ledger = new_ledger([
        BatteryCell("A", CAPACITY_UJ, INITIAL_BALANCE_UJ),
        BatteryCell("B", CAPACITY_UJ, INITIAL_BALANCE_UJ),
    ])
    events = []
    acquired = {"A": 0, "B": 0}
    motor_spent = {"A": 0, "B": 0}
    join_spent = {"A": 0, "B": 0}

    def post(step: int, e: Event) -> None:
        nonlocal ledger
        ledger, entry = apply_event(ledger, e)
        events.append({"step_index": step, **asdict(entry),
                       "balance_a_uj": ledger.cell("A").balance_uj,
                       "balance_b_uj": ledger.cell("B").balance_uj})

    if joined and scene["join_fee_uj"]:
        for cell in ("A", "B"):
            post(0, Event("spend", scene["join_fee_uj"], source_id=cell))
            join_spent[cell] += scene["join_fee_uj"]
    for k, state in enumerate(states[1:], start=1):
        if state["spent_a_uj"]:
            spent = state["spent_a_uj"]
            post(k, Event("spend", spent, source_id="A"))
            motor_spent["A"] += spent
    if (ledger.cell("A").balance_uj != physical_ledger.cell("A").balance_uj
            or ledger.cell("B").balance_uj != physical_ledger.cell("B").balance_uj):
        raise ArithmeticError("fee/motor F002 and F007 ledgers diverged")
    claims = terminal_claims(scene, states[-1])
    for hit in claims:
        post(4, Event("acquire", hit["amount_uj"], target_id=hit["cell_id"]))
        acquired[hit["cell_id"]] += hit["amount_uj"]
    net = {cell: acquired[cell] - motor_spent[cell] - join_spent[cell]
           for cell in ("A", "B")}
    if ledger.residual_uj != 0:
        raise ArithmeticError("energy ledger residual")
    return {
        "scenario_id": scene["scenario_id"], "arm": arm,
        "motor_force_n": requested, "attached": joined,
        "states": states, "events": events, "link_events": link_events,
        "claims": claims, "acquired_uj": acquired,
        "motor_spent_uj": motor_spent, "join_spent_uj": join_spent,
        "net_uj": net,
        "ledger": {
            "initial_total_uj": ledger.initial_total_uj,
            "acquired_uj": ledger.acquired_uj, "spent_uj": ledger.spent_uj,
            "loss_uj": ledger.loss_uj, "residual_uj": ledger.residual_uj,
            "balance_a_uj": ledger.cell("A").balance_uj,
            "balance_b_uj": ledger.cell("B").balance_uj,
            "event_count": ledger.event_index,
        }
    }


def summarize(primary: dict[str, dict], outside: dict[float, dict]) -> dict:
    if set(primary) != set(ARMS) or set(outside) != set(OUTSIDE_MOTORS_N):
        raise ValueError("missing paired treatment")
    joined, separate = primary["YY"], primary["NN"]
    maxima = {
        cell: max(world["net_uj"][cell] for world in outside.values())
        for cell in ("A", "B")
    }
    delta_fixed = {cell: joined["net_uj"][cell] - separate["net_uj"][cell]
                   for cell in ("A", "B")}
    delta_outside = {cell: joined["net_uj"][cell] - maxima[cell]
                     for cell in ("A", "B")}
    return {
        "scenario_id": joined["scenario_id"],
        "primary_net_uj": {arm: primary[arm]["net_uj"] for arm in ARMS},
        "outside_net_uj": {str(int(u)): outside[u]["net_uj"]
                           for u in OUTSIDE_MOTORS_N},
        "outside_best_uj": maxima,
        "outside_best_motors_n": {
            cell: [int(u) for u in OUTSIDE_MOTORS_N
                   if outside[u]["net_uj"][cell] == maxima[cell]]
            for cell in ("A", "B")
        },
        "delta_fixed_uj": delta_fixed,
        "delta_outside_uj": delta_outside,
        "pareto_fixed": all(v > 0 for v in delta_fixed.values()),
        "pareto_outside": all(v > 0 for v in delta_outside.values()),
        "net_sum_join_uj": sum(joined["net_uj"].values()),
        "net_sum_separate_uj": sum(separate["net_uj"].values()),
    }
