"""Independent, from-saved-bytes F018 mechanical, resource and ledger oracle.

Does not import soma.f018, soma.f007 or the suite producer. Checks semantic
content even when a malicious writer rehashes the raw artifacts and manifest.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import subprocess

ARTIFACTS = ("worlds.jsonl", "states.csv", "events.jsonl",
             "ledger.jsonl", "summary.jsonl")
STATE_FIELDS = (
    "step_index", "time_s", "attached", "x_a_m", "x_b_m", "v_a_m_s", "v_b_m_s",
    "motor_command_n", "motor_applied_n", "external_force_a_n", "external_force_b_n",
    "link_force_a_n", "link_force_b_n", "candidate_motor_work_j",
    "candidate_motor_positive_work_j", "motor_work_j", "motor_positive_work_j",
    "external_work_j", "drag_work_j", "link_work_j", "kinetic_delta_j",
    "mechanical_residual_j", "spent_a_uj", "balance_a_uj", "balance_b_uj",
    "ledger_event_index", "decision_reason",
)
# Imported contract intentionally NOT used: compare all saved columns to independent core.
F007_FIELDS = None


def fail(msg: str) -> None:
    raise ValueError("F018 independent oracle: " + msg)


def close(actual: object, expected: float, where: str) -> None:
    try:
        v = float(actual)
    except (ValueError, TypeError, OverflowError):
        fail(where + " is nonnumeric")
    if not math.isfinite(v) or not math.isclose(v, expected, abs_tol=1e-11, rel_tol=1e-11):
        fail(where + f" expected={expected} actual={actual}")


def equal(actual: object, expected: object, where: str) -> None:
    if type(actual) is not type(expected) or actual != expected:
        fail(where + f" expected={expected!r} actual={actual!r}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            fail("empty jsonl record")
        value = json.loads(line, parse_constant=lambda x: fail("nonfinite JSON " + x))
        if type(value) is not dict:
            fail("record must be object")
        rows.append(value)
    return rows


def expected_patches(scene: dict) -> list[dict]:
    if set(scene) != {"schema_version", "scenario_id", "layout", "motor_sign",
                      "terminal_radius_m", "join_fee_uj", "patches"}:
        fail("scene keys")
    sign, radius, fee, layout = (scene["motor_sign"],
                                 scene["terminal_radius_m"],
                                 scene["join_fee_uj"], scene["layout"])
    if type(sign) is not int or sign not in (-1, 1):
        fail("sign")
    if type(radius) is not float or radius not in (0.01, 0.05, 0.2):
        fail("radius")
    if type(fee) is not int or fee not in (0, 100000, 500000):
        fail("fee")
    if type(layout) is not str or layout not in (
            "NONE", "B_LINK", "A_SOLO", "DUAL_LINK", "DUAL_SOLO"):
        fail("layout")
    if scene["schema_version"] != "f018.v1":
        fail("scene version")
    centers = {
        "NONE": (),
        "B_LINK": (0.1 + 0.625*sign,),
        "A_SOLO": (1.25*sign,),
        "DUAL_LINK": (0.625*sign, 0.1+0.625*sign),
        "DUAL_SOLO": (1.25*sign, 0.1),
    }[layout]
    patches = [{"id": f"P{k}", "center_m": v, "radius_m": radius,
                "amount_uj": 3000000} for k, v in enumerate(centers)]
    expected_id = f"{layout}-s{sign:+d}-r{int(radius*1000):03d}-fee{fee:06d}"
    equal(scene["scenario_id"], expected_id, "scene id")
    equal(scene["patches"], patches, "frozen patch geometry")
    return patches


def check_world(world: dict, saved_states: list[dict],
                saved_events: list[dict], ledger: dict) -> dict:
    scene = world["scenario"]
    patches = expected_patches(scene)
    arm, motor = world["arm"], world["motor_force_n"]
    if arm not in ("YY", "YN", "NY", "NN") or type(arm) is not str:
        fail("arm")
    if type(motor) is not float or motor not in (-2.0, 0.0, 2.0):
        fail("motor")
    attached = arm == "YY"
    equal(world["attached"], attached, "consent gate")
    if len(saved_states) != 5:
        fail("saved state count")
    x_a, x_b, v_a, v_b = 0.0, 0.1, 0.0, 0.0
    fee = scene["join_fee_uj"] if attached else 0
    balances = {"A": 10000000, "B": 10000000}
    spent = {"A": 0, "B": 0}
    acquired = {"A": 0, "B": 0}
    motor_spent = 0
    event_index = 0
    expected_entries = []
    link = world["link_events"]
    if attached:
        if len(link) != 1 or link[0]["kind"] != "attach_initial":
            fail("joined link event")
        first = link[0]
        equal(first["attached_before"], False, "link prestate")
        equal(first["attached_after"], True, "link poststate")
        close(first["time_s"], 0.0, "link event time")
        for key,value in (("x_a_before_m",0.0),("x_a_after_m",0.0),
                          ("x_b_before_m",0.1),("x_b_after_m",0.1),
                          ("v_a_before_m_s",0.0),("v_a_after_m_s",0.0),
                          ("v_b_before_m_s",0.0),("v_b_after_m_s",0.0),
                          ("link_force_before_n",0.0)):
            close(first[key],value,"no-snap link event "+key)
    elif link:
        fail("nonconsenting world has link event")

    def make_event(step: int, kind: str, value: int, cell: str) -> None:
        nonlocal event_index
        if value <= 0 or type(value) is not int:
            fail("event must be positive integer microjoules")
        if kind == "spend":
            if balances[cell] < value:
                fail("negative private balance")
            balances[cell] -= value
            spent[cell] += value
        else:
            if balances[cell] + value > 20000000:
                fail("capacity overflow")
            balances[cell] += value
            acquired[cell] += value
        event_index += 1
        expected_entries.append({
            "step_index": step, "event_index": event_index,
            "kind": kind, "amount_uj": value,
            "source_id": cell if kind == "spend" else None,
            "target_id": cell if kind == "acquire" else None,
            "eta_bps": None, "received_uj": 0, "loss_uj": 0,
            "external_in_uj": value if kind == "acquire" else 0,
            "external_out_uj": value if kind == "spend" else 0,
            "residual_uj": 0,
            "balance_a_uj": balances["A"],
            "balance_b_uj": balances["B"],
        })

    if fee:
        for c in ("A", "B"):
            make_event(0, "spend", fee, c)
    # Fee events are validated before motion, but excluded from F007's
    # own motor event_index field because F007 received post-fee balances.

    previous_kinetic = 0.0
    motor_event_index = 0  # F007 ledger starts *after* F018 join fee, separately.
    for k, record in enumerate(saved_states):
        if set(record) != {"world_id", *STATE_FIELDS}:
            fail("unexpected F007 state columns")
        if record["world_id"] != world["world_id"]:
            fail("state world lineage")
        try:
            idx = int(record["step_index"])
            t = float(record["time_s"])
        except (TypeError, ValueError):
            fail("invalid state index/time")
        if idx != k:
            fail("state order")
        close(t, k*.25, "time")
        if record["attached"] != str(attached):
            fail("attached state")
        close(record["motor_command_n"], motor, "motor command")
        close(record["external_force_a_n"], 0, "external A force")
        close(record["external_force_b_n"], 0, "external B force")
        if k:
            old_a, old_b = v_a, v_b
            if attached:
                v_a += motor*.25/2
                v_b = v_a
                x_a += v_a*.25
                x_b += v_b*.25
            else:
                v_a += motor*.25
                x_a += v_a*.25
            work = motor*.25*(old_a+v_a)/2
            positive = max(0.0, work)
            cost = math.ceil(positive*1000000)
            if cost:
                make_event(k, "spend", cost, "A")
                motor_spent += cost
                motor_event_index += 1
            # F007's diagnostic ledger_event_index is its own MOTOR ledger,
            # which omits the separate upfront F018 join fee events.
            equal(record["ledger_event_index"],
                  str(motor_event_index) if cost else "",
                  "F007 per-step motor event index")
            equal(record["decision_reason"],
                  "accepted_positive_work" if cost else "zero_command",
                  "F007 physical motor decision reason")
            if motor == 0.:
                equal(record["candidate_motor_work_j"], "",
                      "zero-command nullable candidate motor work")
                equal(record["candidate_motor_positive_work_j"], "",
                      "zero-command nullable candidate positive work")
            close(record["motor_applied_n"], motor if motor else 0., "motor applied")
            close(record["motor_work_j"], work, "motor work")
            close(record["motor_positive_work_j"], positive, "positive motor work")
            close(record["candidate_motor_work_j"], work if motor else 0.0, "candidate work") if motor else None
            close(record["candidate_motor_positive_work_j"], positive, "candidate positive work") if motor else None
            close(record["spent_a_uj"], cost, "per-step motor cost")
            kinetic = (v_a*v_a + v_b*v_b)/2
            close(record["kinetic_delta_j"], kinetic-previous_kinetic, "kinetic delta")
            close(record["mechanical_residual_j"], 0, "mechanical residual")
            previous_kinetic = kinetic
            close(record["balance_a_uj"], balances["A"], "motor balance A")
            close(record["balance_b_uj"], balances["B"], "motor balance B")
        else:
            close(record["motor_applied_n"], 0, "initial applied")
            close(record["balance_a_uj"], balances["A"], "initial fee A")
            close(record["balance_b_uj"], balances["B"], "initial fee B")
            # Explicitly audit *all* F007 initial state columns, including nulls.
            # These are easy to tamper with and must not be accepted after rehashing.
            equal(record["candidate_motor_work_j"], "",
                  "initial candidate motor work must be null")
            equal(record["candidate_motor_positive_work_j"], "",
                  "initial candidate positive work must be null")
            equal(record["ledger_event_index"], "",
                  "initial motor event index must be null")
            equal(record["decision_reason"], "initial", "initial decision reason")
            for key in ("motor_work_j", "motor_positive_work_j",
                        "kinetic_delta_j", "mechanical_residual_j",
                        "spent_a_uj"):
                close(record[key], 0.0, "initial "+key)
        close(record["x_a_m"], x_a, "position A")
        close(record["x_b_m"], x_b, "position B")
        close(record["v_a_m_s"], v_a, "velocity A")
        close(record["v_b_m_s"], v_b, "velocity B")
        if attached:
            close(x_b-x_a, 0.1, "link distance")
            close(v_b-v_a, 0., "link velocity")
            link_b = motor / 2 if k else 0.0
        else:
            link_b = 0.0
        close(record["link_force_a_n"], -link_b, "link force A")
        close(record["link_force_b_n"], link_b, "link force B")
        close(record["external_work_j"], 0, "external work")
        close(record["drag_work_j"], 0, "drag work")
        close(record["link_work_j"], 0, "internal link work")
    # Harvest only AFTER all four mechanical steps.
    claims = []
    xs = {"A": x_a, "B": x_b}
    for patch in patches:
        eligible = sorted((abs(xs[c]-patch["center_m"]), c)
                          for c in ("A","B")
                          if abs(xs[c]-patch["center_m"]) <= patch["radius_m"])
        if eligible:
            distance, cell = eligible[0]
            claims.append({"patch_id": patch["id"], "cell_id": cell,
                           "amount_uj": patch["amount_uj"], "distance_m": distance})
            make_event(4, "acquire", patch["amount_uj"], cell)
    if len(claims) != len(world["claims"]):
        fail("claim count")
    for actual, expected in zip(world["claims"], claims):
        for field in ("patch_id", "cell_id", "amount_uj"):
            equal(actual[field], expected[field], "claim " + field)
        close(actual["distance_m"], expected["distance_m"], "claim distance")
    if saved_events != expected_entries:
        fail("individual chronological F002 event ledger mismatch")
    if set(ledger) != {"world_id", "initial_total_uj", "acquired_uj",
                       "spent_uj", "loss_uj", "residual_uj",
                       "balance_a_uj", "balance_b_uj", "event_count"}:
        fail("ledger summary fields")
    if ledger["world_id"] != world["world_id"]:
        fail("ledger lineage")
    baseline = 20000000
    truth = {
        "initial_total_uj": baseline,
        "acquired_uj": sum(acquired.values()),
        "spent_uj": sum(spent.values()), "loss_uj": 0,
        "residual_uj": baseline + sum(acquired.values()) -
            sum(spent.values()) - sum(balances.values()),
        "balance_a_uj": balances["A"], "balance_b_uj": balances["B"],
        "event_count": event_index,
    }
    if {k: v for k,v in ledger.items() if k != "world_id"} != truth:
        fail("final integer ledger mismatch")
    if truth["residual_uj"] != 0:
        fail("conservation residual")
    joined_fee = {c: fee if attached else 0 for c in ("A","B")}
    own_motor = {"A": motor_spent, "B": 0}
    net = {c: acquired[c]-own_motor[c]-joined_fee[c] for c in ("A","B")}
    for key,expected in (("net_uj", net), ("acquired_uj", acquired),
                         ("motor_spent_uj", own_motor),
                         ("join_spent_uj", joined_fee)):
        equal(world[key], expected, key)
    return net


def verify(root: Path) -> dict:
    root = Path(root)
    manifest = json.loads((root/"manifest.json").read_text("utf-8"))
    if manifest["schema_version"] != "f018.evidence.v1":
        fail("manifest version")
    if set(manifest["artifact_sha256"]) != set(ARTIFACTS):
        fail("artifact inventory")
    for name in ARTIFACTS:
        if sha(root/name) != manifest["artifact_sha256"][name]:
            fail("raw byte hash " + name)
    source_root = Path(__file__).resolve().parents[2]
    provenance = manifest["provenance"]
    current_sha = subprocess.run(
        ["git","-C",str(source_root),"rev-parse","HEAD"],
        check=True, capture_output=True,text=True).stdout.strip()
    if current_sha != provenance["git_commit"] or provenance["git_dirty"] is not False:
        fail("source commit provenance")
    expected_sources = {
        "soma/f001.py","soma/f002.py","soma/f005.py","soma/f007.py",
        "soma/f018.py","experiments/F018/run_suite.py",
        "experiments/F018/verify.py","experiments/F018/analyze.py",
        "experiments/F018/attack_test.py","tests/test_f018.py",
        "tests/test_f018_experiment.py",".github/workflows/f018.yml",
        "experiments/F018/PLAN.md","topics/F018-attachment-value/SPEC.md",
        "findings/F018-validation.md","docs/ARCHITECTURE.md",
        "docs/DATA_CONTRACTS.md","README.md",
    }
    if set(provenance["source_hashes"]) != expected_sources:
        fail("source hash inventory incomplete")
    for name, digest in provenance["source_hashes"].items():
        if sha(source_root/name) != digest:
            fail("source byte hash " + name)

    worlds = read_jsonl(root/"worlds.jsonl")
    raw_events = read_jsonl(root/"events.jsonl")
    ledgers = read_jsonl(root/"ledger.jsonl")
    summaries = read_jsonl(root/"summary.jsonl")
    with (root/"states.csv").open("r", encoding="utf-8", newline="") as fp:
        reader = csv.DictReader(fp)
        if reader.fieldnames != ["world_id", *STATE_FIELDS]:
            fail("states.csv header")
        states = list(reader)
    if len(worlds) != 630 or len(ledgers) != 630 or len(summaries) != 90 or len(states) != 3150:
        fail("frozen scenario/world cardinality")
    by_states, by_events, by_ledger, by_world = {}, {}, {}, {}
    for row in states:
        by_states.setdefault(row["world_id"], []).append(row)
    for row in raw_events:
        rid = row.pop("world_id")
        by_events.setdefault(rid, []).append(row)
    for row in ledgers:
        if row["world_id"] in by_ledger:
            fail("duplicate ledger")
        by_ledger[row["world_id"]] = row
    for row in worlds:
        rid = row["world_id"]
        if rid in by_world or rid not in by_ledger:
            fail("duplicate or missing world")
        by_world[rid] = row
    if set(by_world) != set(by_states) or set(by_world) != set(by_ledger):
        fail("orphaned world state/ledger")
    if set(by_events)-set(by_world):
        fail("orphaned events")
    observed_nets = {}
    for row in worlds:
        rid = row["world_id"]
        observed_nets[rid] = check_world(
            row, by_states[rid], by_events.get(rid, []), by_ledger[rid])
    expected_scenes = set(itertools.product(
        ("NONE","B_LINK","A_SOLO","DUAL_LINK","DUAL_SOLO"),
        (-1,1), (0.01,0.05,0.2), (0,100000,500000)))
    actual_scenes = set()
    counts = {"pareto_fixed":0,"pareto_outside":0}
    if len({x["scenario_id"] for x in summaries}) != 90:
        fail("duplicate scene summary")
    for summary in summaries:
        sid = summary["scenario_id"]
        prefix = sid+"::"
        matching = [x for x in worlds if x["scenario"]["scenario_id"] == sid]
        if len(matching) != 7:
            fail("missing arms for " + sid)
        example = matching[0]["scenario"]
        actual_scenes.add((example["layout"], example["motor_sign"],
                           example["terminal_radius_m"], example["join_fee_uj"]))
        ids = {x["world_id"] for x in matching}
        expected_ids = {prefix+"primary-"+arm for arm in ("YY","YN","NY","NN")}
        expected_ids |= {prefix+f"outside-{u:+d}" for u in (-2,0,2)}
        if ids != expected_ids:
            fail("incorrect arm/outside lineage")
        # Freeze treatment *actions*, not merely treatment names/scores.
        for world in matching:
            if world["scenario"] != example:
                fail("within-pair scene mutation")
            label = world["world_id"][len(prefix):]
            if label.startswith("primary-"):
                equal(world["arm"], label[len("primary-"):], "primary arm")
                equal(world["motor_force_n"], 2.0*example["motor_sign"],
                      "primary fixed A-motor")
            else:
                if not label.startswith("outside-"):
                    fail("unknown treatment label")
                equal(world["arm"], "NN", "outside consent")
                try:
                    action = float(int(label[len("outside-"):]))
                except ValueError:
                    fail("unregistered outside action label")
                equal(world["motor_force_n"], action, "outside A-motor")
        primary = {arm: observed_nets[prefix+"primary-"+arm]
                   for arm in ("YY","YN","NY","NN")}
        outside = {u: observed_nets[prefix+f"outside-{u:+d}"]
                   for u in (-2,0,2)}
        maxima = {c:max(outside[u][c] for u in outside) for c in ("A","B")}
        fixed = {c:primary["YY"][c]-primary["NN"][c] for c in ("A","B")}
        own = {c:primary["YY"][c]-maxima[c] for c in ("A","B")}
        audit = {
            "scenario_id": sid, "primary_net_uj": primary,
            "outside_net_uj": {str(u): outside[u] for u in (-2,0,2)},
            "outside_best_uj": maxima,
            "outside_best_motors_n": {
                c:[u for u in (-2,0,2) if outside[u][c] == maxima[c]]
                for c in ("A","B")},
            "delta_fixed_uj": fixed, "delta_outside_uj": own,
            "pareto_fixed": all(v>0 for v in fixed.values()),
            "pareto_outside": all(v>0 for v in own.values()),
            "net_sum_join_uj": sum(primary["YY"].values()),
            "net_sum_separate_uj": sum(primary["NN"].values()),
        }
        if audit != summary:
            fail("summary causal estimand mismatch")
        for key in counts:
            counts[key] += int(audit[key])
    if actual_scenes != expected_scenes:
        fail("preregistered factorial incomplete")
    for key,value in (("scenarios",90),("worlds",630),("steps_per_world",4),
                      ("primary_worlds",360),("outside_worlds",270),
                      ("stochastic_draws",0)):
        if manifest[key] != value:
            fail("manifest count " + key)
    if manifest["random_seed"] is not None or manifest["counts"] != counts:
        fail("manifest result count")
    return {"scenarios":90,"worlds":630,"counts":counts,"semantic_verified":True}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    x = verify(p.parse_args().root)
    print(json.dumps(x, sort_keys=True))


if __name__ == "__main__":
    main()
