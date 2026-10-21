"""F016: counterfactual *task-level* value of costly B-local 1-bit information.

Only ideal, prerecorded F007 1D two-cell dynamics. This is a fixed semantic
positive control, NOT emergent messaging, physical radio or body inference.
Researcher truth is never an input to choose_force().
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math

from soma.f002 import Cell, Event, apply_event, new_ledger
from soma.f007 import Config, simulate

SCHEMA = "f016.action.v1"
GROUPS = ("A0", "K", "S", "T", "H", "I")
TARGETS_M = (0.625, -0.625, 0.625, -0.625)
SHUFFLED_RIGHT = (True, True, False, False)
LOW_FEE_UJ = 50_000
HIGH_FEE_UJ = 2_000_000
RESOURCE_REWARD_UJ = 3_000_000
INITIAL_UJ = 10_000_000
CAPACITY_UJ = 20_000_000
EXPECTED_MEAN_NET_UJ = {
    "A0": 500_000, "K": 450_000, "S": 450_000,
    "T": 1_950_000, "H": 0, "I": -1_050_000,
}


@dataclass(frozen=True)
class ResourceBit:
    """A receives just a framed B-local Boolean, never a true target coordinate."""
    source_id: str
    step_index: int
    time_s: float
    resource_right: bool


def read_b_local(resource_x_m: float, b_initial_x_m: float) -> bool:
    """Researcher-side sensor projector; only the sign is disclosed to B."""
    if (type(resource_x_m) is not float or type(b_initial_x_m) is not float
            or not math.isfinite(resource_x_m) or not math.isfinite(b_initial_x_m)
            or resource_x_m == b_initial_x_m):
        raise ValueError("invalid B-local projection")
    return resource_x_m > b_initial_x_m


def choose_force(packet: ResourceBit | None) -> float:
    """Controller A: same fixed policy/force budget for every treatment."""
    if packet is None:
        return 2.0
    if (type(packet) is not ResourceBit or packet.source_id != "B"
            or type(packet.step_index) is not int or packet.step_index != 0
            or type(packet.time_s) is not float or packet.time_s != 0.0
            or type(packet.resource_right) is not bool):
        raise ValueError("invalid B-local packet/source/clock")
    return 2.0 if packet.resource_right else -2.0


def configuration(group: str, trial: int, force: float,
                  b_initial_uj: int = INITIAL_UJ) -> Config:
    if (group not in GROUPS or type(trial) is not int or trial not in range(4)
            or type(force) is not float or force not in (-2.0, 2.0)
            or type(b_initial_uj) is not int or not 0 <= b_initial_uj <= CAPACITY_UJ):
        raise ValueError("nonpreregistered F016 config")
    return Config.from_dict({
        "schema_version": "f007.v1",
        "experiment_id": f"F016-{group}-{trial}",
        "seed": None,
        "dt_s": 0.25, "duration_s": 1.0, "drag_per_s": 0.0,
        "cells": [
            {"id": "A", "mass_kg": 1.0, "initial_x_m": 0.0,
             "initial_v_m_s": 0.0, "external_force_n": 0.0,
             "capacity_uj": CAPACITY_UJ, "initial_balance_uj": INITIAL_UJ},
            {"id": "B", "mass_kg": 1.0, "initial_x_m": 0.1,
             "initial_v_m_s": 0.0, "external_force_n": 0.0,
             "capacity_uj": CAPACITY_UJ, "initial_balance_uj": b_initial_uj},
        ],
        "motor_force_n": force,
        "link": {"initially_attached": True, "length_m": 0.1,
                 "detach_time_s": None},
    })


def run_episode(group: str, trial: int, *, b_initial_uj: int = INITIAL_UJ) -> dict:
    """World-side adapter: B senses a side; A chooses; independent ledger audits.

    Source of physical truth is F007. Combined F002 ledger independently REPLAYS
    its motor spending; this is not an additional physical motor expenditure.
    """
    if group not in GROUPS or type(trial) is not int or trial not in range(4):
        raise ValueError("not one of the frozen F016 episodes")
    target = TARGETS_M[trial]
    observed_right = read_b_local(float(target), 0.1)
    fee = 0 if group == "A0" else (HIGH_FEE_UJ if group == "H" else LOW_FEE_UJ)
    can_send = fee > 0 and b_initial_uj >= fee
    packet = None
    if can_send:
        side = {"K": True, "S": SHUFFLED_RIGHT[trial],
                "T": observed_right, "H": observed_right,
                "I": not observed_right}[group]
        packet = ResourceBit("B", 0, 0.0, side)
    force = choose_force(packet)
    config = configuration(group, trial, force, b_initial_uj)
    rows, motor_events, link_events, motor_ledger = simulate(config)
    if not rows or len(rows) != 5 or len(link_events) != 1:
        raise ValueError("F007 trace does not match frozen linked physics")
    if not all(row["attached"] for row in rows):
        raise ValueError("unexpected link state")

    # The independent F002 sidecar replays the ACTUAL F007 motor amounts ONCE.
    sidecar = new_ledger([
        Cell("A", CAPACITY_UJ, INITIAL_UJ),
        Cell("B", CAPACITY_UJ, b_initial_uj),
    ])
    events = []
    if can_send:
        sidecar, entry = apply_event(sidecar, Event(kind="spend", amount_uj=fee,
                                                  source_id="B"))
        events.append(asdict(entry))
    motor_spent = 0
    for row in rows[1:]:
        amount = row["spent_a_uj"]
        if type(amount) is not int or amount < 0:
            raise ValueError("invalid F007 motor spending")
        if amount:
            sidecar, entry = apply_event(sidecar, Event(kind="spend",
                                                       amount_uj=amount, source_id="A"))
            events.append(asdict(entry))
            motor_spent += amount
    if (motor_spent != sum(event["amount_uj"] for event in motor_events)
            or sidecar.cell("A").balance_uj != motor_ledger.cell("A").balance_uj):
        raise ValueError("F007/F002 motor-transaction mismatch")
    success = abs(rows[-1]["x_a_m"] - target) <= 1e-12
    resource_uj = RESOURCE_REWARD_UJ if success else 0
    if success:
        sidecar, entry = apply_event(sidecar, Event(kind="acquire",
                                                   amount_uj=RESOURCE_REWARD_UJ,
                                                   target_id="A"))
        events.append(asdict(entry))
    if sidecar.residual_uj != 0:
        raise ValueError("F002 budget residual")
    return {
        "schema": SCHEMA, "group": group, "trial": trial,
        "target_x_m": target, "b_observed_right": observed_right,
        "packet": asdict(packet) if packet is not None else None,
        "motor_command_n": force, "motor_spent_uj": motor_spent,
        "communication_spent_uj": fee if can_send else 0,
        "acquired_uj": resource_uj, "reached": success,
        "net_uj": resource_uj - motor_spent - (fee if can_send else 0),
        "balance_a_uj": sidecar.cell("A").balance_uj,
        "balance_b_uj": sidecar.cell("B").balance_uj,
        "ledger_residual_uj": sidecar.residual_uj,
        "f007_config": config.to_dict(), "states": rows,
        "f007_motor_events": motor_events, "f002_sidecar_events": events,
    }
