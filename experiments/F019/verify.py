"""From-disk F019 audit, independently rederiving hash fields, F007 physics,
segment hits, F002 chronology and all paired scores. Never import producers.
This is computational independence, not independent human peer review.
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import subprocess

ARTIFACTS = ("worlds.jsonl", "states.csv", "harvests.jsonl", "events.jsonl",
             "ledger.jsonl", "summary.jsonl")
STATE_FIELDS = ("step_index", "time_s", "attached", "x_a_m", "x_b_m",
                "v_a_m_s", "v_b_m_s", "motor_command_n", "motor_applied_n",
                "external_force_a_n", "external_force_b_n", "link_force_a_n",
                "link_force_b_n", "candidate_motor_work_j",
                "candidate_motor_positive_work_j", "motor_work_j",
                "motor_positive_work_j", "external_work_j", "drag_work_j",
                "link_work_j", "kinetic_delta_j", "mechanical_residual_j",
                "spent_a_uj", "balance_a_uj", "balance_b_uj",
                "ledger_event_index", "decision_reason")
CELL_IDS = ("A", "B")


def fail(message: str) -> None:
    raise ValueError("F019 independent verifier: " + message)


def equal(actual: object, expected: object, label: str) -> None:
    if type(actual) is not type(expected):
        fail(label + " unexpected data type")
    if type(expected) is float:
        if not math.isfinite(actual) or not math.isclose(actual, expected, rel_tol=1e-11, abs_tol=1e-11):
            fail(label + f" number mismatch {actual} vs {expected}")
    elif type(expected) is dict:
        if set(actual) != set(expected):
            fail(label + " keys")
        for k in expected:
            equal(actual[k], expected[k], label + "." + str(k))
    elif type(expected) is list:
        if len(actual) != len(expected):
            fail(label + " length")
        for k, (got, intended) in enumerate(zip(actual, expected)):
            equal(got, intended, label + f"[{k}]")
    elif actual != expected:
        fail(label + f" mismatch {actual!r} vs {expected!r}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def records(path: Path) -> list[dict]:
    out = []
    for text in path.read_text("utf-8").splitlines():
        if not text:
            fail(path.name + " empty row")
        o = json.loads(text, parse_constant=lambda x: fail("non-finite JSON"))
        if type(o) is not dict:
            fail(path.name + " nonobject row")
        out.append(o)
    return out


def original_field(seed: int, count: int, r: float) -> dict:
    """Independent SHA256 calculation, no soma.f019 reference."""
    patches = []
    for n in range(count):
        valid = False
        for draw in range(10000):
            data = f"F019-field-v1|seed={seed}|patch={n}|draw={draw}".encode("ascii")
            number = int.from_bytes(hashlib.sha256(data).digest()[0:8], "big")
            # Preserve the frozen v1 producer's exact IEEE-754 serialization path.
            # Dividing by 40 is mathematically equal, but can differ by one ulp
            # and fails byte-exact seed-scene replay; this is not a model change.
            center = (number % 121 - 60) * .025
            if abs(center) <= r or abs(center - .1) <= r:
                continue
            patches.append(dict(patch_id=f"P{n}", center_m=center,
                                radius_m=r, initial_available_uj=1000000))
            valid = True
            break
        if not valid:
            fail("frozen generator exhausted")
    return {"field_id": f"s{seed:02d}-n{count}-r{int(r*1000):03d}",
            "generator_version": "sha256-grid-v1", "seed": seed,
            "patches": patches}


def expected_scenes() -> list[dict]:
    out = []
    for seed in range(32):
        for sign in (-1, 1):
            for fee in (0, 100000):
                for count in (2, 5):
                    for radius in (.02, .06):
                        field = original_field(seed, count, radius)
                        out.append({"schema_version": "f019.v1",
                                    "scenario_id": f"{field['field_id']}-sign{sign:+d}-fee{fee:06d}",
                                    "base_seed": seed, "motor_sign": sign,
                                    "join_fee_uj": fee, "field": field})
    if len(out) != 512:
        fail("design universe wrong")
    return out


def expected_hit_set(field: dict, positions: list[tuple[float, float]]) -> list[dict]:
    """Patch-centric first passage; computes all candidate (time, cell) pairs."""
    winners = []
    for patch in field["patches"]:
        candidates = []
        low = patch["center_m"] - patch["radius_m"]
        high = patch["center_m"] + patch["radius_m"]
        for step in range(1, len(positions)):
            for index, cell in enumerate(CELL_IDS):
                left, right = positions[step-1][index], positions[step][index]
                if max(left, right) < low or min(left, right) > high:
                    continue
                if low <= left <= high:
                    part = 0.0
                elif right == left:
                    continue
                elif right > left:
                    part = (low - left) / (right - left)
                else:
                    part = (high - left) / (right - left)
                if part < 0.0 or part > 1.0:
                    fail("independent interpolation invariant")
                candidates.append((step, part, cell))
        if candidates:
            step, part, cell = min(candidates)
            winners.append((step, part, patch["patch_id"], cell,
                            patch["initial_available_uj"]))
    winners.sort(key=lambda v: (v[0], v[1], v[2], v[3]))
    return [{"patch_id": pid, "step_index": k,
             "entry_fraction_in_step": fraction,
             "entry_time_s": (k-1+fraction)/4.,
             "winner_cell_id": cell, "available_before_uj": amount,
             "acquired_uj": amount, "available_after_uj": 0,
             "ordinal": i+1}
            for i, (k, fraction, pid, cell, amount) in enumerate(winners)]


def check_world(world: dict, states: list[dict], harvests: list[dict],
                events: list[dict], ledger: dict) -> dict:
    scene = world["scenario"]
    arm, u = world["arm"], world["motor_force_n"]
    if arm not in ("YY", "YN", "NY", "NN") or type(arm) is not str:
        fail("unregistered consent arm")
    if type(u) is not float or u not in (-2., 0., 2.):
        fail("unregistered motor")
    attached = arm == "YY"
    equal(world["attached"], attached, "physical gate")
    fee = scene["join_fee_uj"] if attached else 0
    link_events = ([{
        "time_s": 0.0, "kind": "attach_initial",
        "attached_before": False, "attached_after": True,
        "x_a_before_m": 0.0, "x_a_after_m": 0.0,
        "x_b_before_m": 0.1, "x_b_after_m": 0.1,
        "v_a_before_m_s": 0.0, "v_a_after_m_s": 0.0,
        "v_b_before_m_s": 0.0, "v_b_after_m_s": 0.0,
        "link_force_before_n": 0.0,
    }] if attached else [])
    equal(world["link_events"], link_events, "link events")
    if len(states) != 5:
        fail("five state rows required")
    xA, xB, vA, vB = 0., .1, 0., 0.
    balances_motion = {"A": 10000000 - fee, "B": 10000000 - fee}
    positions = []
    state_costs = []
    running_motor = 0
    for k, row in enumerate(states):
        equal(set(row), {"world_id", *STATE_FIELDS}, f"state keys {k}")
        equal(row["world_id"], world["world_id"], "state lineage")
        oldVA, oldVB = vA, vB
        if k:
            vA += u * .25 / (2. if attached else 1.)
            if attached:
                vB = vA
            xA += .25*vA
            if attached:
                xB += .25*vB
            motor_work = u * .25 * (oldVA + vA)/2.
            cost = math.ceil(max(motor_work, 0.)*1000000)
            balances_motion["A"] -= cost
            if balances_motion["A"] < 0:
                fail("frozen world's motor unexpectedly unaffordable")
            if cost:
                running_motor += 1
            kinetic = ((vA*vA+vB*vB)-(oldVA*oldVA+oldVB*oldVB))/2.
            linkB = u / 2. if attached else 0.
            reason = "accepted_positive_work" if cost else "zero_command"
        else:
            motor_work, cost, kinetic, linkB = 0., 0, 0., 0.
            reason = "initial"
        intended = {
            "step_index": str(k), "time_s": k*.25, "attached": str(attached),
            "x_a_m": xA, "x_b_m": xB, "v_a_m_s": vA, "v_b_m_s": vB,
            "motor_command_n": u, "motor_applied_n": u if k and u else 0.,
            "external_force_a_n": 0., "external_force_b_n": 0.,
            "link_force_a_n": -linkB, "link_force_b_n": linkB,
            "candidate_motor_work_j": motor_work if k and u else None,
            "candidate_motor_positive_work_j": max(0., motor_work) if k and u else None,
            "motor_work_j": motor_work, "motor_positive_work_j": max(0., motor_work),
            "external_work_j": 0., "drag_work_j": 0., "link_work_j": 0.,
            "kinetic_delta_j": kinetic,
            "mechanical_residual_j": kinetic - motor_work,
            "spent_a_uj": str(cost),
            "balance_a_uj": str(balances_motion["A"]),
            "balance_b_uj": str(balances_motion["B"]),
            "ledger_event_index": str(running_motor) if cost else "",
            "decision_reason": reason,
        }
        for field, value in intended.items():
            saved = row[field]
            if field in ("step_index", "attached", "spent_a_uj", "balance_a_uj",
                         "balance_b_uj", "ledger_event_index", "decision_reason"):
                equal(saved, value, "state."+field)
            elif value is None:
                equal(saved, "", "null state."+field)
            else:
                try:
                    numeric = float(saved)
                except (ValueError, OverflowError):
                    fail("invalid numeric state."+field)
                equal(numeric, float(value), "state."+field)
        state_costs.append(cost)
        positions.append((xA, xB))
    expected_harvests = expected_hit_set(scene["field"], positions)
    equal(world["harvests"], expected_harvests, "world harvest order")
    equal(harvests, [{"world_id": world["world_id"], **hit}
                     for hit in expected_harvests], "harvest raw file")

    balance = {"A": 10000000, "B": 10000000}
    spent = {"A": 0, "B": 0}
    acquired = {"A": 0, "B": 0}
    motor_spent = {"A": 0, "B": 0}
    join_spent = {"A": 0, "B": 0}
    expected_events = []
    def event(step: int, kind: str, cell: str, amount: int):
        if type(amount) is not int or amount <= 0:
            fail("invalid F002 event amount")
        if kind == "spend":
            balance[cell] -= amount
            spent[cell] += amount
        else:
            balance[cell] += amount
            acquired[cell] += amount
        if balance[cell] < 0 or balance[cell] > 20000000:
            fail("cell capacity or private balance violated")
        expected_events.append({
            "world_id": world["world_id"], "step_index": step,
            "event_index": len(expected_events)+1,
            "kind": kind, "source_id": cell if kind == "spend" else None,
            "target_id": cell if kind == "acquire" else None,
            "amount_uj": amount, "eta_bps": None, "received_uj": 0,
            "loss_uj": 0, "external_in_uj": amount if kind == "acquire" else 0,
            "external_out_uj": amount if kind == "spend" else 0,
            "residual_uj": 0,
            "balance_a_uj": balance["A"], "balance_b_uj": balance["B"],
        })
    if fee:
        for cell in CELL_IDS:
            event(0, "spend", cell, fee)
            join_spent[cell] += fee
    for k in range(1, 5):
        if state_costs[k]:
            event(k, "spend", "A", state_costs[k])
            motor_spent["A"] += state_costs[k]
        for hit in expected_harvests:
            if hit["step_index"] == k:
                event(k, "acquire", hit["winner_cell_id"], hit["acquired_uj"])
    equal(events, expected_events, "F002 event chronology")
    equal(world["acquired_uj"], acquired, "acquired resource")
    equal(world["motor_spent_uj"], motor_spent, "motor debit")
    equal(world["join_spent_uj"], join_spent, "join debit")
    net = {cell: acquired[cell] - motor_spent[cell] - join_spent[cell]
           for cell in CELL_IDS}
    equal(world["net_uj"], net, "per-cell net")
    expected_ledger = {
        "world_id": world["world_id"],
        "initial_total_uj": 20000000, "acquired_uj": sum(acquired.values()),
        "spent_uj": sum(spent.values()), "loss_uj": 0, "residual_uj": 0,
        "balance_a_uj": balance["A"], "balance_b_uj": balance["B"],
        "event_count": len(expected_events),
    }
    equal(ledger, expected_ledger, "ledger")
    if sum(balance.values()) + sum(spent.values()) != 20000000 + sum(acquired.values()):
        fail("global energy accounting")
    return {"net": net, "harvests": expected_harvests}


def compare_pair(scene: dict, primary: dict, outside: dict) -> dict:
    yy, nn = primary["YY"], primary["NN"]
    best = {c: max(outside[u]["net"][c] for u in (-2., 0., 2.)) for c in CELL_IDS}
    fixed = {c: yy["net"][c] - nn["net"][c] for c in CELL_IDS}
    opt = {c: yy["net"][c] - best[c] for c in CELL_IDS}
    def mapped(rec):
        return {r["patch_id"]: r for r in rec["harvests"]}
    jm, sm = mapped(yy), mapped(nn)
    comparisons = []
    for p in scene["field"]["patches"]:
        j, s = jm.get(p["patch_id"]), sm.get(p["patch_id"])
        aj, as_ = (j or {}).get("winner_cell_id"), (s or {}).get("winner_cell_id")
        tj, ts = (j or {}).get("entry_time_s"), (s or {}).get("entry_time_s")
        comparisons.append({"patch_id": p["patch_id"], "winner_yy": aj, "winner_nn": as_,
                            "entry_time_yy_s": tj, "entry_time_nn_s": ts,
                            "winner_changed": aj != as_,
                            "entry_time_yy_minus_nn_s": tj-ts if tj is not None and ts is not None else None})
    return {
        "scenario_id": scene["scenario_id"], "base_seed": scene["base_seed"],
        "field_id": scene["field"]["field_id"], "patch_comparison": comparisons,
        "winner_switch_count": sum(v["winner_changed"] for v in comparisons),
        "primary_net_uj": {arm: primary[arm]["net"] for arm in ("YY", "YN", "NY", "NN")},
        "outside_net_uj": {str(int(u)): outside[u]["net"] for u in (-2., 0., 2.)},
        "outside_best_uj": best,
        "outside_best_motors_n": {c: [int(u) for u in (-2., 0., 2.)
                                       if outside[u]["net"][c] == best[c]] for c in CELL_IDS},
        "delta_fixed_uj": fixed, "delta_outside_uj": opt,
        "pareto_fixed": all(v > 0 for v in fixed.values()),
        "pareto_outside": all(v > 0 for v in opt.values()),
        "unclaimed_yy_uj": 1000000*len(scene["field"]["patches"]) -
                           sum(h["acquired_uj"] for h in yy["harvests"]),
        "unclaimed_nn_uj": 1000000*len(scene["field"]["patches"]) -
                           sum(h["acquired_uj"] for h in nn["harvests"]),
    }


def verify(root: Path) -> dict:
    root = Path(root)
    manifest = json.loads((root/"manifest.json").read_text("utf-8"),
                          parse_constant=lambda x: fail("manifest nonfinite"))
    equal(manifest["schema_version"], "f019.evidence.v1", "manifest schema")
    equal(manifest["scenarios"], 512, "scenario count")
    equal(manifest["worlds"], 3584, "world count")
    equal(manifest["steps_per_world"], 4, "step count")
    equal(manifest["primary_worlds"], 2048, "primary worlds")
    equal(manifest["outside_worlds"], 1536, "outside worlds")
    equal(manifest["seed_values"], list(range(32)), "frozen seeds")
    equal(set(manifest), {"schema_version", "scenarios", "worlds", "steps_per_world",
                         "primary_worlds", "outside_worlds", "seed_values",
                         "counts", "provenance", "artifact_sha256"}, "manifest keys")
    from . import __path__  # package metadata only; no simulator imports
    _ = __path__
    # Validate source closure and immutable identity even if artifact hashes are rewritten.
    source = Path(__file__).resolve().parents[2]
    revision = subprocess.run(["git", "-C", str(source), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    gitdirty = subprocess.run(["git", "-C", str(source), "status", "--porcelain",
                               "--untracked-files=all"], capture_output=True,
                              text=True, check=True).stdout.strip()
    provenance = manifest["provenance"]
    equal(provenance["git_commit"], revision, "source revision")
    equal(provenance["git_dirty"], False, "clean source recorded")
    if gitdirty:
        fail("dirty verification checkout")
    if set(provenance["source_hashes"]) != set((
        "soma/f001.py", "soma/f002.py", "soma/f003.py", "soma/f005.py",
        "soma/f007.py", "soma/f018.py", "soma/f019.py",
        "experiments/F019/__init__.py", "experiments/F019/run_suite.py",
        "experiments/F019/verify.py", "experiments/F019/attack_test.py",
        "experiments/F019/analyze.py", "experiments/F019/README.md",
        "tests/test_f019.py", "tests/test_f019_experiment.py",
        ".github/workflows/f019.yml", "experiments/F019/PLAN.md",
        "topics/F019-resource-ecology/SPEC.md", "findings/F019-validation.md",
        "docs/ARCHITECTURE.md", "docs/DATA_CONTRACTS.md",
        "docs/research-notes/2026-10-22-temporary-morphology-and-resource-access.md",
        "README.md",
    )):
        fail("source file list differs from frozen verifier")
    for name, digest in provenance["source_hashes"].items():
        equal(sha(source/name), digest, "source SHA "+name)
    equal(set(manifest["artifact_sha256"]), set(ARTIFACTS), "raw inventory")
    for name in ARTIFACTS:
        equal(sha(root/name), manifest["artifact_sha256"][name], "raw SHA "+name)
    worlds, harvests, events, ledger, summaries = (
        records(root/name) for name in (
            "worlds.jsonl", "harvests.jsonl", "events.jsonl",
            "ledger.jsonl", "summary.jsonl"))
    with (root/"states.csv").open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        equal(reader.fieldnames, ["world_id", *STATE_FIELDS], "state schema")
        state_rows = list(reader)
    if len(worlds) != 3584 or len(summaries) != 512 or len(state_rows) != 17920 or len(ledger) != 3584:
        fail("saved cardinality")
    group_states, group_harvests, group_events = defaultdict(list), defaultdict(list), defaultdict(list)
    for rows, dest in ((state_rows, group_states), (harvests, group_harvests),
                       (events, group_events)):
        for row in rows:
            dest[row["world_id"]].append(row)
    if len(group_states) != 3584 or set(group_states) != {w["world_id"] for w in worlds}:
        fail("world lineage or duplicated state groups")
    scene_list = expected_scenes()
    if len({w["world_id"] for w in worlds}) != 3584:
        fail("duplicate world id")
    sum_counts = {"pareto_outside": 0, "pareto_fixed": 0, "winner_switches": 0}
    offset = 0
    for i, scene in enumerate(scene_list):
        primary, outside = {}, {}
        ordering = [(a, float(2*scene["motor_sign"]), f"primary-{a}")
                    for a in ("YY", "YN", "NY", "NN")]
        ordering += [("NN", u, f"outside-{int(u):+d}") for u in (-2., 0., 2.)]
        for arm, motor, label in ordering:
            w, l = worlds[offset], ledger[offset]
            wid = f"{scene['scenario_id']}::{label}"
            equal(w["world_id"], wid, "world ID/order")
            equal(w["scenario"], scene, "trajectory-independent pristine field")
            equal(w["arm"], arm, "world consent label")
            equal(w["motor_force_n"], motor, "world motor")
            expected = check_world(w, group_states[wid], group_harvests[wid],
                                   group_events[wid], l)
            if label.startswith("primary-"):
                primary[arm] = expected
            else:
                outside[motor] = expected
            offset += 1
        score = compare_pair(scene, primary, outside)
        equal(summaries[i], score, "independent paired summary")
        sum_counts["pareto_outside"] += int(score["pareto_outside"])
        sum_counts["pareto_fixed"] += int(score["pareto_fixed"])
        sum_counts["winner_switches"] += score["winner_switch_count"]
    if set(group_harvests) - set(group_states) or set(group_events) - set(group_states):
        fail("orphan saved observations")
    equal(manifest["counts"], sum_counts, "aggregate counts")
    return {"verified_worlds": offset, "verified_scenarios": 512, "counts": sum_counts}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    print(json.dumps(verify(parser.parse_args().root), sort_keys=True))


if __name__ == "__main__":
    main()
