"""F021: frozen two-owner ideal 1D motor/finite-resource experiment.

Prespecified in experiments/F021/FROZEN_V1.md at design commit 8f82e3b.
Investigator-controlled forces and initial link; NOT emergent cooperation,
physical ground reaction, motor electricity, local learning or organismality.
F001-F020 source and schemas are left unchanged.
"""
from __future__ import annotations

from dataclasses import asdict
import math

from soma.f001 import step as f001_step
from soma.f002 import Cell, Event, apply_event, new_ledger
from soma.f005 import positive_motor_work
from soma.f019 import field_for, first_entry

SCHEMA = "f021.v1"
DT = 0.25
STEPS = 4
CAPACITY_UJ = 20_000_000
BALANCES = (80_000, 250_000, 4_000_000)
FEES = (0, 25_000)
ARMS = ("YY", "NN")
B_RELATIVE = (-1, 0, 1)
SIGNS = (-1, 1)
COUNTS = (2, 5)
RADII = (.02, .06)
SEEDS = tuple(range(32))
CELL_IDS = ("A", "B")
SUBSETS = ((), ("A",), ("B",), ("A", "B"))


def scene_for(seed: int, sign: int, b_relative: int, arm: str,
              balance: int, fee: int, count: int, radius: float) -> dict:
    if (type(seed) is not int or seed not in SEEDS
        or type(sign) is not int or sign not in SIGNS
        or type(b_relative) is not int or b_relative not in B_RELATIVE
        or type(arm) is not str or arm not in ARMS
        or type(balance) is not int or balance not in BALANCES
        or type(fee) is not int or fee not in FEES
        or type(count) is not int or count not in COUNTS
        or type(radius) is not float or radius not in RADII):
        raise ValueError("outside frozen F021 primary grid")
    field = field_for(seed, count, radius)
    return {"schema_version": SCHEMA,
            "world_id": f"F021-s{seed:02d}-u{sign:+d}-b{b_relative:+d}-{arm}"
                        f"-bal{balance:07d}-fee{fee:05d}-n{count}-r{int(radius*1000):03d}",
            "seed": seed, "sign": sign, "b_relative": b_relative,
            "arm": arm, "balance_uj": balance, "fee_uj": fee,
            "count": count, "radius_m": radius, "field": field}


def grid():
    for seed in SEEDS:
        for sign in SIGNS:
            for br in B_RELATIVE:
                for arm in ARMS:
                    for bal in BALANCES:
                        for fee in FEES:
                            for count in COUNTS:
                                for radius in RADII:
                                    yield scene_for(seed, sign, br, arm, bal, fee, count, radius)


def _motion(x, v, arm, force_a, force_b):
    if arm == "YY":
        nx, nv = f001_step(x[0], v[0], mass_kg=2., drag_per_s=0.,
                            force_n=force_a + force_b, dt_s=DT)
        dx = nx - x[0]
        link_b = .5 * (force_a - force_b)
        return [nx, x[1] + dx], [nv, nv], [-link_b, link_b]
    xa, va = f001_step(x[0], v[0], mass_kg=1., drag_per_s=0.,
                        force_n=force_a, dt_s=DT)
    xb, vb = f001_step(x[1], v[1], mass_kg=1., drag_per_s=0.,
                        force_n=force_b, dt_s=DT)
    return [xa, xb], [va, vb], [0., 0.]


def motor_gate(x, v, arm: str, command: dict, own_balance: dict) -> dict:
    """Exhaustive simultaneous eligibility, no implicit A-first priority.

    Explicit ambiguity policy: reject all motors and log possible branches.
    This is a conservative *investigator arbitration assumption*, not agency.
    """
    if set(command) != set(CELL_IDS) or set(own_balance) != set(CELL_IDS):
        raise ValueError("motor input IDs")
    for cell in CELL_IDS:
        if command[cell] not in (-2., 0., 2.) or type(command[cell]) is not float:
            raise ValueError("motor command")
        if type(own_balance[cell]) is not int or own_balance[cell] < 0:
            raise ValueError("balance")
    if arm not in ARMS:
        raise ValueError("arm")
    candidates = []
    for subset in SUBSETS:
        applied = {c: command[c] if c in subset else 0. for c in CELL_IDS}
        trial_x, trial_v, link = _motion(x, v, arm, applied["A"], applied["B"])
        work = {}
        charge = {}
        for i, c in enumerate(CELL_IDS):
            w = positive_motor_work(applied[c], v[i], trial_v[i], DT)
            work[c] = w
            charge[c] = math.ceil(w * 1_000_000)
        feasible = all(
            command[c] != 0. and own_balance[c] > 0 and charge[c] <= own_balance[c]
            for c in subset
        )
        candidates.append({"subset": list(subset), "feasible": feasible,
                           "work_j": work, "charge_uj": charge,
                           "trial_v_m_s": trial_v})
    best_size = max(len(c["subset"]) for c in candidates if c["feasible"])
    maximal = [c["subset"] for c in candidates
               if c["feasible"] and len(c["subset"]) == best_size]
    if len(maximal) == 1:
        selected = maximal[0]
        reason = "unique_max_feasible" if selected else "none_feasible"
    else:
        selected = []
        reason = "ambiguous_maximal"
    applied = {c: command[c] if c in selected else 0. for c in CELL_IDS}
    next_x, next_v, link = _motion(x, v, arm, applied["A"], applied["B"])
    chosen = next(c for c in candidates if c["subset"] == selected)
    return {"candidates": candidates, "maximal_feasible": maximal,
            "selected_subset": selected, "reason": reason,
            "applied_n": applied, "next_x_m": next_x, "next_v_m_s": next_v,
            "link_force_n": {c: link[i] for i, c in enumerate(CELL_IDS)},
            "charge_uj": chosen["charge_uj"], "work_j": chosen["work_j"]}


def simulate(scene: dict) -> dict:
    """Single world with chronological debit then resource credit."""
    if type(scene) is not dict or set(scene) != set(scene_for(0, 1, 0, "NN", 80_000, 0, 2, .02)):
        raise ValueError("scene shape")
    expected = scene_for(scene["seed"], scene["sign"], scene["b_relative"],
                         scene["arm"], scene["balance_uj"], scene["fee_uj"],
                         scene["count"], scene["radius_m"])
    if scene != expected:
        raise ValueError("scene not frozen canonical")
    command = {"A": float(2 * scene["sign"]),
               "B": float(2 * scene["sign"] * scene["b_relative"])}
    ledger = new_ledger([Cell("A", CAPACITY_UJ, scene["balance_uj"]),
                         Cell("B", CAPACITY_UJ, scene["balance_uj"])])
    x, v = [0., .1], [0., 0.]
    rem = {p["patch_id"]: p["initial_available_uj"] for p in scene["field"]["patches"]}
    totals = {c: {"acquired_uj": 0, "motor_spent_uj": 0, "fee_spent_uj": 0}
              for c in CELL_IDS}
    steps, harvests, events = [], [], []
    ambiguous = 0

    def post(k, phase, kind, cell, amount):
        nonlocal ledger
        if amount <= 0:
            return
        ev = (Event("spend", amount, source_id=cell) if kind == "spend" else
              Event("acquire", amount, target_id=cell))
        ledger, entry = apply_event(ledger, ev)
        events.append({"step_index": k, "phase": phase, **asdict(entry)})
    if scene["arm"] == "YY":
        for cell in CELL_IDS:
            post(0, "fee", "spend", cell, scene["fee_uj"])
            totals[cell]["fee_spent_uj"] += scene["fee_uj"]

    for k in range(1, STEPS + 1):
        before = {c: ledger.cell(c).balance_uj for c in CELL_IDS}
        prev_x, prev_v = list(x), list(v)
        decision = motor_gate(x, v, scene["arm"], command, before)
        if decision["reason"] == "ambiguous_maximal":
            ambiguous += 1
        x, v = decision["next_x_m"], decision["next_v_m_s"]
        for cell in CELL_IDS:
            spend = decision["charge_uj"][cell]
            if spend:
                post(k, "motor", "spend", cell, spend)
                totals[cell]["motor_spent_uj"] += spend

        hits = []
        for patch in scene["field"]["patches"]:
            ident = patch["patch_id"]
            if not rem[ident]:
                continue
            for i, cell in enumerate(CELL_IDS):
                fraction = first_entry(prev_x[i], x[i], patch["center_m"], patch["radius_m"])
                if fraction is not None:
                    hits.append((fraction, ident, cell))
        gained_this_step = []
        for fraction, ident, cell in sorted(hits):
            amount = rem[ident]
            if not amount:
                continue
            rem[ident] = 0
            claim = {"step_index": k, "patch_id": ident,
                     "fraction": fraction, "winner": cell, "amount_uj": amount}
            harvests.append(claim)
            gained_this_step.append(claim)
            post(k, "harvest", "acquire", cell, amount)
            totals[cell]["acquired_uj"] += amount
        after = {c: ledger.cell(c).balance_uj for c in CELL_IDS}
        if any(not math.isfinite(z) for z in x + v):
            raise ArithmeticError("nonfinite world state")
        if scene["arm"] == "YY" and (abs(x[1] - x[0] - .1) > 1e-11 or
                                      abs(v[1] - v[0]) > 1e-11):
            raise ArithmeticError("link constraint violated")
        kinetic_delta = .5 * sum(v[i]**2 - prev_v[i]**2 for i in range(2))
        signed_work = sum(decision["applied_n"][c] * DT * (prev_v[i] + v[i]) / 2
                          for i, c in enumerate(CELL_IDS))
        if abs(kinetic_delta - signed_work) > 1e-10:
            raise ArithmeticError("motor mechanical residual")
        steps.append({"step_index": k, "x_before_m": prev_x, "v_before_m_s": prev_v,
                      "x_after_m": x, "v_after_m_s": v,
                      "balance_before_uj": before, "balance_after_uj": after,
                      "command_n": command, "decision": decision,
                      "harvests": gained_this_step,
                      "kinetic_delta_j": kinetic_delta,
                      "signed_work_j": signed_work})
    net = {}
    for cell in CELL_IDS:
        net[cell] = (totals[cell]["acquired_uj"]
                     - totals[cell]["motor_spent_uj"]
                     - totals[cell]["fee_spent_uj"])
        if ledger.cell(cell).balance_uj != scene["balance_uj"] + net[cell]:
            raise ArithmeticError("cell ledger mismatch")
    return {"scene": scene, "steps": steps, "harvests": harvests,
            "ledger_events": events, "totals": totals, "net_uj": net,
            "ambiguous_steps": ambiguous, "final_balance_uj":
                {c: ledger.cell(c).balance_uj for c in CELL_IDS}}
