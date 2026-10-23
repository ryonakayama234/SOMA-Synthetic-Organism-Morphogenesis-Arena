"""F020 independent saved-data auditor. NEVER imports soma or producer modules.

Reconstructs canonical SHA256 field, consent/fee/motor/trajectory/first entry,
per-cell integer energy ledger, original chronology and ecological comparisons
from saved JSON data. This is computational independence, not human peer review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

SCHEMA = "f020.v1"
PROTOCOL_SHA = "f3e3a4de4ff47677db575efaafe342655dede6c2"
WORLD_KEYS = {"scenario", "world_id", "arm", "credit_mode", "motor_force_n",
              "attached", "states", "harvests", "events", "ledger",
              "acquired_uj", "spent_motor_uj", "spent_fee_uj", "net_uj"}
BALANCES = (75_000, 250_000, 4_000_000)
SOURCE_FILES = (
    "soma/f001.py", "soma/f002.py", "soma/f005.py",
    "soma/f007.py", "soma/f018.py", "soma/f019.py", "soma/f020.py",
    "experiments/F020/FROZEN_V1.md", "experiments/F020/PLAN.md",
    "experiments/F020/run_suite.py", "experiments/F020/verify.py",
    "experiments/F020/attack_test.py", "experiments/F020/analyze.py",
    "tests/test_f020.py", "tests/test_f020_experiment.py",
    ".github/workflows/f020.yml", "topics/F020-metabolic-feedback/SPEC.md",
    "docs/ARCHITECTURE.md", "docs/DATA_CONTRACTS.md",
    "findings/F020-validation.md",
)


def fail(msg: str):
    raise ValueError("F020 independent auditor: " + msg)


def same(x, y, label="record"):
    if type(x) is not type(y):
        fail(label + " unexpected type")
    if isinstance(y, dict):
        if set(x) != set(y):
            fail(label + " keys")
        for k in y:
            same(x[k], y[k], label + "." + str(k))
    elif isinstance(y, list):
        if len(x) != len(y):
            fail(label + " length")
        for i, (a, b) in enumerate(zip(x, y)):
            same(a, b, label + "[" + str(i) + "]")
    elif type(y) is float:
        if not math.isfinite(x) or not math.isclose(x, y, rel_tol=1e-11, abs_tol=1e-11):
            fail(label + f" float mismatch {x} vs {y}")
    elif x != y:
        fail(label + f" mismatch {x!r} vs {y!r}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def original_field(seed: int, count: int, radius: float):
    if (type(seed) is not int or seed not in range(32)
            or type(count) is not int or count not in (2, 5)
            or type(radius) is not float or radius not in (.02, .06)):
        fail("non-frozen field factors")
    patches = []
    for i in range(count):
        for d in range(10_000):
            msg = f"F019-field-v1|seed={seed}|patch={i}|draw={d}".encode("ascii")
            ix = int.from_bytes(hashlib.sha256(msg).digest()[:8], "big") % 121
            center = (ix - 60) * .025
            if abs(center) <= radius or abs(center - .1) <= radius:
                continue
            patches.append({"patch_id": f"P{i}", "center_m": center,
                            "radius_m": radius, "initial_available_uj": 1_000_000})
            break
        else:
            fail("field generator exhausted")
    return {"field_id": f"s{seed:02d}-n{count}-r{int(radius*1000):03d}",
            "generator_version": "sha256-grid-v1", "seed": seed,
            "patches": patches}


def original_scene(scene: dict) -> dict:
    if type(scene) is not dict or set(scene) != {
        "schema_version", "kind", "scenario_id", "base_seed", "motor_sign",
        "initial_balance_uj", "join_fee_uj", "field"
    } or scene["schema_version"] != SCHEMA:
        fail("invalid scene schema")
    if scene["kind"] == "calibration":
        kind = scene["scenario_id"].removeprefix("F020-calibration-")
        if kind not in ("positive", "b_only", "empty"):
            fail("calibration fixture kind")
        center = {"positive": .0625, "b_only": .1625, "empty": None}[kind]
        patches = ([] if center is None else
                   [{"patch_id": "P0", "center_m": center, "radius_m": .005,
                     "initial_available_uj": 1_000_000}])
        fld = {"field_id": "calibration-" + kind,
               "generator_version": "synthetic-calibration-only",
               "seed": None, "patches": patches}
        expected = {"schema_version": SCHEMA, "kind": "calibration",
                    "scenario_id": "F020-calibration-" + kind,
                    "base_seed": None, "motor_sign": 1,
                    "initial_balance_uj": 75_000, "join_fee_uj": 0, "field": fld}
    elif scene["kind"] == "primary":
        fld = scene["field"]
        if type(fld) is not dict or set(fld) != {
            "field_id", "generator_version", "seed", "patches"
        } or type(fld["patches"]) is not list or not fld["patches"]:
            fail("malformed field")
        seed, sign = scene["base_seed"], scene["motor_sign"]
        bal, fee = scene["initial_balance_uj"], scene["join_fee_uj"]
        if (type(sign) is not int or sign not in (-1, 1)
                or type(bal) is not int or bal not in BALANCES
                or type(fee) is not int or fee not in (0, 25_000)):
            fail("non-frozen primary factor")
        r = fld["patches"][0]["radius_m"]
        canonical_field = original_field(seed, len(fld["patches"]), r)
        expected = {"schema_version": SCHEMA, "kind": "primary",
                    "scenario_id": (f"{canonical_field['field_id']}-sign{sign:+d}"
                                    f"-bal{bal:07d}-fee{fee:05d}"),
                    "base_seed": seed, "motor_sign": sign,
                    "initial_balance_uj": bal, "join_fee_uj": fee,
                    "field": canonical_field}
    else:
        fail("unknown scene kind")
    if scene != expected:
        fail("noncanonical scene or exact resource geometry")
    return expected


def entry_fraction(start: float, stop: float, center: float, radius: float):
    lo, hi = center - radius, center + radius
    if lo <= start <= hi:
        return 0.
    if start == stop or max(start, stop) < lo or min(start, stop) > hi:
        return None
    boundary = lo if stop > start else hi
    f = (boundary - start) / (stop - start)
    if not 0 <= f <= 1:
        fail("entry interpolation")
    return f


def check_world(world: dict) -> None:
    if type(world) is not dict or set(world) != WORLD_KEYS:
        fail("world schema")
    scene = original_scene(world["scenario"])
    arm, mode = world["arm"], world["credit_mode"]
    if arm not in ("YY", "NN") or type(arm) is not str:
        fail("consent arm")
    if mode not in ("feedback", "deferred_credit") or type(mode) is not str:
        fail("credit mode")
    joined = arm == "YY"
    motor = float(2 * scene["motor_sign"])
    if scene["kind"] == "calibration" and world["motor_force_n"] == 0.:
        motor = 0.
    same(world["motor_force_n"], motor, "motor")
    same(world["attached"], joined, "attached")
    same(world["world_id"], scene["scenario_id"]+"::"+arm+"::"+mode, "id")
    if len(world["states"]) != 5:
        fail("step count")

    balance = {"A": scene["initial_balance_uj"],
               "B": scene["initial_balance_uj"]}
    pending = {"A": 0, "B": 0}
    acquired = {"A": 0, "B": 0}
    motor_spent = {"A": 0, "B": 0}
    fee_spent = {"A": 0, "B": 0}
    events, claims, states = [], [], []
    spent_total, acquired_total = 0, 0
    event_idx = 0
    remaining = {p["patch_id"]: p["initial_available_uj"]
                 for p in scene["field"]["patches"]}
    def post(k, phase, kind, cell, amount):
        nonlocal event_idx, spent_total, acquired_total
        if type(amount) is not int or amount <= 0:
            fail("non-positive ledger transaction")
        if kind == "spend":
            if balance[cell] < amount:
                fail("ledger overdraft")
            balance[cell] -= amount
            spent_total += amount
        elif kind == "acquire":
            if balance[cell] + amount > 20_000_000:
                fail("capacity overflow")
            balance[cell] += amount
            acquired_total += amount
        else:
            fail("ledger kind")
        event_idx += 1
        events.append({
            "step_index": k, "phase": phase, "event_index": event_idx,
            "kind": kind, "source_id": cell if kind == "spend" else None,
            "target_id": cell if kind == "acquire" else None,
            "amount_uj": amount, "eta_bps": None,
            "received_uj": 0, "loss_uj": 0,
            "external_in_uj": amount if kind == "acquire" else 0,
            "external_out_uj": amount if kind == "spend" else 0,
            "residual_uj": 0, "balance_a_uj": balance["A"],
            "balance_b_uj": balance["B"],
        })
        return event_idx

    if joined and scene["join_fee_uj"]:
        for cell in ("A", "B"):
            post(0, "fee", "spend", cell, scene["join_fee_uj"])
            fee_spent[cell] += scene["join_fee_uj"]
    x, v = [0., .1], [0., 0.]
    for k in range(5):
        pre_a, pre_b = balance["A"], balance["B"]
        candidate, requested, spent, entry = None, None, 0, None
        applied, residual = 0., 0.
        if k == 0:
            reason = "initial"
        else:
            oldv, oldx = v[:], x[:]
            if pre_a == 0:
                reason = "zero_balance"
            elif motor == 0.:
                reason = "zero_command"
            else:
                trial_v = v[0] + motor * .25 / (2. if joined else 1.)
                # Derive positive work via the oriented velocity trapezoid,
                # independent of the producer's F005 function call.
                oriented_start = (1. if motor > 0 else -1.) * v[0]
                oriented_end = (1. if motor > 0 else -1.) * trial_v
                if oriented_start >= 0 and oriented_end >= 0:
                    candidate = (motor * .25) * ((v[0] + trial_v) / 2.)
                elif oriented_start <= 0 and oriented_end <= 0:
                    candidate = 0.
                else:
                    pos, neg = max(oriented_start, oriented_end), -min(
                        oriented_start, oriented_end)
                    alpha = (pos / max(pos, neg)) / (
                        pos / max(pos, neg) + neg / max(pos, neg))
                    candidate = abs(motor) * .25 * pos * alpha / 2.
                requested = math.ceil(candidate * 1_000_000)
                if requested <= pre_a:
                    applied = motor
                    spent = requested
                    reason = "accepted_positive_work" if spent else "accepted_nonpositive_work"
                else:
                    reason = "insufficient_balance"
            # Re-derive semi-implicit Euler for linked total mass versus solo A.
            inc = applied * .25 / (2. if joined else 1.)
            v[0] += inc
            if joined:
                v[1] = v[0]
            for i in range(2):
                x[i] += .25 * v[i]
            if spent:
                entry = post(k, "motor", "spend", "A", spent)
                motor_spent["A"] += spent
            midpoint = (oldv[0] + v[0]) / 2.
            work = (applied * .25) * midpoint
            kinetic_change = ((v[0]*v[0]+v[1]*v[1]) -
                              (oldv[0]*oldv[0]+oldv[1]*oldv[1]))/2.
            residual = kinetic_change - work
            if abs(residual) > 1e-11:
                fail("mechanical residual outside tolerance")
            candidates = []
            for patch in scene["field"]["patches"]:
                pid = patch["patch_id"]
                if remaining[pid] == 0:
                    continue
                for cell, index in (("A", 0), ("B", 1)):
                    fraction = entry_fraction(oldx[index], x[index],
                                              patch["center_m"], patch["radius_m"])
                    if fraction is not None:
                        candidates.append((fraction, pid, cell))
            for fraction, pid, cell in sorted(candidates):
                amount = remaining[pid]
                if not amount:
                    continue
                remaining[pid] = 0
                hit = {"patch_id": pid, "step_index": k,
                       "entry_fraction_in_step": fraction,
                       "entry_time_s": (k-1+fraction)*.25,
                       "winner_cell_id": cell, "available_before_uj": amount,
                       "acquired_uj": amount, "available_after_uj": 0,
                       "ordinal": len(claims)+1}
                claims.append(hit)
                acquired[cell] += amount
                if mode == "feedback":
                    post(k, "harvest", "acquire", cell, amount)
                else:
                    pending[cell] += amount
        states.append({
            "step_index": k, "time_s": k * .25,
            "x_a_m": x[0], "x_b_m": x[1], "v_a_m_s": v[0], "v_b_m_s": v[1],
            "available_a_before_uj": pre_a,
            "available_b_before_uj": pre_b,
            "balance_a_uj": balance["A"], "balance_b_uj": balance["B"],
            "pending_a_uj": pending["A"], "pending_b_uj": pending["B"],
            "motor_command_n": motor, "motor_applied_n": applied,
            "candidate_positive_work_j": candidate,
            "candidate_charge_uj": requested,
            "spent_a_uj": spent, "reason": reason,
            "ledger_event_index": entry, "mechanical_residual_j": residual,
        })
    if mode == "deferred_credit":
        for hit in claims:
            cell = hit["winner_cell_id"]
            post(4, "settlement", "acquire", cell, hit["acquired_uj"])
            pending[cell] -= hit["acquired_uj"]
        if pending != {"A": 0, "B": 0}:
            fail("terminal pending balance")
    net = {cell: acquired[cell]-motor_spent[cell]-fee_spent[cell]
           for cell in ("A", "B")}
    ledger = {"initial_total_uj": 2*scene["initial_balance_uj"],
              "acquired_uj": acquired_total, "spent_uj": spent_total,
              "loss_uj": 0, "residual_uj": 0,
              "balance_a_uj": balance["A"], "balance_b_uj": balance["B"],
              "event_count": event_idx}
    if ledger["initial_total_uj"]+acquired_total != spent_total+sum(balance.values()):
        fail("ledger conservation")
    for name, expected in (("states", states), ("harvests", claims),
                           ("events", events), ("ledger", ledger),
                           ("acquired_uj", acquired), ("spent_motor_uj", motor_spent),
                           ("spent_fee_uj", fee_spent), ("net_uj", net)):
        same(world[name], expected, name)


def audit_run(directory: Path) -> dict:
    root = Path(__file__).resolve().parents[2]
    dest = Path(directory)
    manifest = json.loads((dest / "manifest.json").read_text("utf-8"))
    if set(manifest) != {
        "schema_version", "protocol_anchor_sha", "scenarios", "worlds",
        "steps_per_world", "seed_values", "counts", "provenance",
        "artifact_sha256"
    } or manifest.get("schema_version") != "f020.evidence.v1":
        fail("manifest schema")
    if manifest["steps_per_world"] != 4 or manifest["seed_values"] != list(range(32)):
        fail("manifest timestep/seed universe")
    if manifest.get("protocol_anchor_sha") != PROTOCOL_SHA:
        fail("protocol freeze anchor")
    origin = manifest.get("provenance")
    if type(origin) is not dict or set(origin) != {
        "git_commit", "git_dirty", "source_hashes"
    } or origin["git_dirty"] is not False:
        fail("provenance clean/source schema")
    actual_head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                                 capture_output=True, text=True, check=True).stdout.strip()
    same(origin["git_commit"], actual_head, "source commit")
    actual_hashes = {p: sha(root / p) for p in SOURCE_FILES}
    same(origin["source_hashes"], actual_hashes, "source hashes")
    if set(manifest.get("artifact_sha256", {})) != {"worlds.jsonl"}:
        fail("artifact set")
    same(manifest["artifact_sha256"]["worlds.jsonl"], sha(dest/"worlds.jsonl"),
         "artifact sha256")
    scenarios = set()
    seen = set()
    counts = {"motor_enabled_forks": 0, "feedback_changed_trajectory_pairs": 0}
    by_pair = {}
    count = 0
    with (dest / "worlds.jsonl").open("r", encoding="utf-8") as fp:
        for line in fp:
            if not line.endswith("\n"):
                fail("noncanonical line ending")
            obj = json.loads(line, parse_constant=lambda x: fail("nonfinite JSON"))
            if json.dumps(obj, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False)+"\n" != line:
                fail("noncanonical record bytes")
            if obj["scenario"]["kind"] != "primary":
                fail("calibration intruded primary run")
            check_world(obj)
            key = obj["world_id"]
            if key in seen:
                fail("duplicate world")
            seen.add(key)
            scenarios.add(obj["scenario"]["scenario_id"])
            pair = (obj["scenario"]["scenario_id"], obj["arm"])
            by_pair.setdefault(pair, {})[obj["credit_mode"]] = obj
            count += 1
    if len(scenarios) != 1536 or count != 6144:
        fail("frozen grid cardinality")
    for (sid, arm), two in by_pair.items():
        if set(two) != {"feedback", "deferred_credit"}:
            fail("missing paired fork")
        x, y = two["feedback"], two["deferred_credit"]
        if x["scenario"] != y["scenario"]:
            fail("counterfactual field mismatch")
        if x["states"][-1]["x_a_m"] != y["states"][-1]["x_a_m"]:
            counts["feedback_changed_trajectory_pairs"] += 1
        if any(a["motor_applied_n"] and not b["motor_applied_n"]
               for a, b in zip(x["states"][1:], y["states"][1:])):
            counts["motor_enabled_forks"] += 1
    if len(by_pair) != 3072:
        fail("pair cardinality")
    expected_pairs = {
        f"s{s:02d}-n{n}-r{int(r*1000):03d}-sign{sg:+d}-bal{b:07d}-fee{fee:05d}"
        for s in range(32) for sg in (-1, 1) for n in (2, 5)
        for r in (.02, .06) for b in BALANCES for fee in (0, 25_000)
    }
    if scenarios != expected_pairs:
        fail("missing/unregistered original scenarios")
    if manifest.get("scenarios") != 1536 or manifest.get("worlds") != 6144:
        fail("manifest count forgery")
    same(manifest["counts"], counts, "summary counts")
    return {"worlds": count, "scenarios": len(scenarios), "counts": counts,
            "source_sha": actual_head}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    print(json.dumps(audit_run(parser.parse_args().directory),
                     sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
