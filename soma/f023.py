"""F023.v1: prescribed t=0 privately funded 2D impulse, then immutable F022 passive TOI.

Ideal external ground explicitly receives opposite impulse. Not locomotion,
self-directed encounter, learned policy or formation of an attached body.
"""
from __future__ import annotations

from fractions import Fraction
import math

from soma import f022

SCHEMA = "f023.archive.v1"
FREEZE_COMMIT = "76dcc1db7ae12737705da06c155933d0a8251853"
FIELDS = f022.FIELDS + (
    "command_ax_ns", "command_ay_ns", "command_bx_ns", "command_by_ns",
    "initial_balance_a_uj", "initial_balance_b_uj",
)


def grid() -> list[dict]:
    """Exactly 15 frozen synthetic calibration scenes; no random draws."""
    base = dict(world_id="Q01", x_a_m=-1., y_a_m=0.,
                vx_a_mps=1., vy_a_mps=0., x_b_m=1., y_b_m=1.01,
                vx_b_mps=-1., vy_b_mps=0., mass_a_kg=1.,
                mass_b_kg=1., radius_a_m=.5, radius_b_m=.5,
                restitution=1., duration_s=2., sample_dt_s=.25,
                command_ax_ns=0., command_ay_ns=0.,
                command_bx_ns=0., command_by_ns=0.,
                initial_balance_a_uj=0, initial_balance_b_uj=0)
    worlds = []
    def add(number, **changes):
        worlds.append(dict(base, world_id=f"Q{number:02d}", **changes))
    add(1)
    add(2, command_ay_ns=.02, initial_balance_a_uj=200)
    add(3, command_ay_ns=-.02, initial_balance_a_uj=200)
    add(4, command_ay_ns=.02, initial_balance_a_uj=199)
    add(5, command_ay_ns=.02, initial_balance_a_uj=200,
        initial_balance_b_uj=900000)
    add(6, command_by_ns=-.02, initial_balance_b_uj=200)
    add(7, command_ay_ns=.02, initial_balance_a_uj=200, restitution=.5)
    add(8, x_a_m=9., y_a_m=-7., x_b_m=11., y_b_m=-5.99,
        command_ay_ns=.02, initial_balance_a_uj=200)
    add(9, x_a_m=0., y_a_m=-1., x_b_m=-1.01, y_b_m=1.,
        vx_a_mps=0., vy_a_mps=1., vx_b_mps=0., vy_b_mps=-1.,
        command_ax_ns=-.02, initial_balance_a_uj=200)
    add(10, x_a_m=1., y_a_m=1.01, vx_a_mps=-1., vy_a_mps=0.,
        x_b_m=-1., y_b_m=0., vx_b_mps=1., vy_b_mps=0.,
        command_by_ns=.02, initial_balance_b_uj=200)
    add(11, vx_a_mps=-1., vx_b_mps=1.)
    add(12, vx_b_mps=1.)
    add(13, command_ax_ns=-.2)
    add(14, y_b_m=0.)
    add(15, x_a_m=-10., y_a_m=0., x_b_m=10., y_b_m=0.,
        vx_a_mps=100., vx_b_mps=-100.)
    return worlds


def validate(s: dict) -> None:
    if not isinstance(s, dict) or set(s) != set(FIELDS):
        raise ValueError("F023 schema keys")
    if not isinstance(s["world_id"], str) or not s["world_id"]:
        raise ValueError("world ID")
    for k in FIELDS:
        if k == "world_id":
            continue
        v = s[k]
        if k.startswith("initial_balance_"):
            if type(v) is not int or not 0 <= v <= 1000000:
                raise ValueError("private balance")
        elif type(v) not in (float, int) or not math.isfinite(v):
            raise ValueError(f"nonfinite {k}")
    if (s["mass_a_kg"] != 1. or s["mass_b_kg"] != 1. or
        s["radius_a_m"] != .5 or s["radius_b_m"] != .5 or
        s["restitution"] not in (1., .5) or
        s["duration_s"] != 2. or s["sample_dt_s"] != .25):
        raise ValueError("outside frozen physics")
    if math.hypot(s["x_b_m"]-s["x_a_m"], s["y_b_m"]-s["y_a_m"]) <= 1.:
        raise ValueError("initial touching/overlap")
    if any(abs(s[k]) > 100 for k in (
        "x_a_m","y_a_m","x_b_m","y_b_m",
        "vx_a_mps","vy_a_mps","vx_b_mps","vy_b_mps")):
        raise ValueError("position or speed outside bound")
    if any(abs(s[k]) > .25 for k in (
        "command_ax_ns","command_ay_ns","command_bx_ns","command_by_ns")):
        raise ValueError("impulse component outside bound")


def _work_and_charge(vx: float, vy: float, jx: float, jy: float):
    """Exact decimal rational billing avoids false ceil(200.00000000000003)."""
    vx, vy, jx, jy = (Fraction(str(t)) for t in (vx, vy, jx, jy))
    work = vx*jx + vy*jy + (jx*jx + jy*jy)/2
    positive = max(Fraction(0), work) * 1000000
    charge = (positive.numerator + positive.denominator - 1)//positive.denominator
    return float(work), int(charge)


def simulate(s: dict):
    """Return saved frames, two actuation rows, contacts, ledger rows, audit row."""
    validate(s)
    actions, ledgers, post_vel = [], [], {}
    for label in ("a", "b"):
        before = (s[f"vx_{label}_mps"], s[f"vy_{label}_mps"])
        cmd = (s[f"command_{label}x_ns"], s[f"command_{label}y_ns"])
        balance = s[f"initial_balance_{label}_uj"]
        work, candidate_charge = _work_and_charge(*before, *cmd)
        if cmd == (0, 0):
            decision = "idle"
        elif candidate_charge > balance:
            decision = "insufficient_private_budget"
        else:
            decision = "applied"
        applied = cmd if decision == "applied" else (0., 0.)
        charge = candidate_charge if decision == "applied" else 0
        after = (before[0] + applied[0], before[1] + applied[1])
        actual_work = work if decision == "applied" else 0.
        post_vel[label] = after
        actions.append(dict(world_id=s["world_id"], cell_id=label.upper(),
                            time_s=0., command_x_ns=cmd[0], command_y_ns=cmd[1],
                            applied_x_ns=applied[0], applied_y_ns=applied[1],
                            ground_x_ns=-applied[0], ground_y_ns=-applied[1],
                            pre_vx_mps=before[0], pre_vy_mps=before[1],
                            post_vx_mps=after[0], post_vy_mps=after[1],
                            candidate_work_j=work, applied_work_j=actual_work,
                            candidate_charge_uj=candidate_charge,
                            charge_uj=charge, decision=decision))
        ledgers.append(dict(world_id=s["world_id"], cell_id=label.upper(),
                            balance_before_uj=balance, charge_uj=charge,
                            balance_after_uj=balance-charge))
    physical = {k: s[k] for k in f022.FIELDS}
    for label in ("a", "b"):
        physical[f"vx_{label}_mps"],physical[f"vy_{label}_mps"] = post_vel[label]
    frames, contacts = f022.simulate(physical)
    if len(frames) != 9 or len(contacts) > 1:
        raise ArithmeticError("frozen event/sample cardinality")
    ke_before = .5 * sum(s[k]**2 for k in (
        "vx_a_mps","vy_a_mps","vx_b_mps","vy_b_mps"))
    ke_after = frames[-1]["total_ke_j"]
    applied_work = sum(a["applied_work_j"] for a in actions)
    loss = 0.
    overlap = 0.
    if contacts:
        e = contacts[0]
        g = ((e["pre_vx_b_mps"]-e["pre_vx_a_mps"])*e["normal_x"]+
             (e["pre_vy_b_mps"]-e["pre_vy_a_mps"])*e["normal_y"])
        loss = .25*(1.-s["restitution"]**2)*g*g
        overlap = max(0., 1.-math.hypot(e["pre_x_b_m"]-e["pre_x_a_m"],
                                         e["pre_y_b_m"]-e["pre_y_a_m"]))
    pmx = (frames[-1]["vx_a_mps"]+frames[-1]["vx_b_mps"] -
           s["vx_a_mps"]-s["vx_b_mps"] +
           sum(a["ground_x_ns"] for a in actions))
    pmy = (frames[-1]["vy_a_mps"]+frames[-1]["vy_b_mps"] -
           s["vy_a_mps"]-s["vy_b_mps"] +
           sum(a["ground_y_ns"] for a in actions))
    audit = dict(world_id=s["world_id"], contact_count=len(contacts),
                 classification=contacts[0]["kind"] if contacts else "none",
                 initial_ke_j=ke_before, final_ke_j=ke_after,
                 applied_work_j=applied_work, collision_loss_j=loss,
                 momentum_residual_kg_mps=max(abs(pmx),abs(pmy)),
                 energy_residual_j=ke_after-ke_before-applied_work+loss,
                 overlap_bound_m=overlap)
    if (audit["momentum_residual_kg_mps"] > 1e-9 or
        abs(audit["energy_residual_j"]) > 1e-9 or overlap > 1e-9):
        raise ArithmeticError("energy, external reaction, or overlap mismatch")
    return frames, actions, contacts, ledgers, audit
