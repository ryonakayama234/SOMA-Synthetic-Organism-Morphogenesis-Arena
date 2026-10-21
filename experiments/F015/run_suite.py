"""F015: fifteen independently reset F007 worlds + immutable evidence."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from soma.f007 import Config, STATE_COLUMNS, provenance, publish_dir, save_run
from soma.f008 import COLUMNS, LocalObservation, analyze, project_local
from soma.f014 import PeerPacket, THRESHOLD_M_S, packet_csv_row
from soma.f015 import ProbeTrial, analyze_probe, SAME, CHANGED, UNKNOWN
from experiments.F007.run_suite import baseline
from experiments.F007.verify import read_csv
from experiments.F015.verify import verify_suite

GROUPS = ("L-linked", "F-fixed", "T-tracking", "N-free", "E-disabled")
FORCES = ((2., "u2"), (1., "u1"), (0., "u0"))
PACKET_COLUMNS = ("source", "step_index", "time_s", "moved")
LOCAL_KEYS = ("step_index", "time_s", "dt_s", "v_prev_m_s", "v_a_m_s",
              "motor_command_n", "motor_applied_n", "balance_a_uj")
SOURCE_FILES = (
    "soma/f015.py", "experiments/F015/run_suite.py",
    "experiments/F015/verify.py", "tests/test_f015.py",
    ".github/workflows/f015.yml", "topics/F015-active-body-probing/SPEC.md",
    "experiments/F015/PLAN.md", "experiments/F015/README.md",
    "findings/F015-validation.md", "docs/ARCHITECTURE.md",
    "docs/DATA_CONTRACTS.md", "README.md", "AGENTS.md",
)


def configuration(group: str, force: float) -> dict:
    if group not in GROUPS or type(force) not in (int, float) or force not in (2., 1., 0.):
        raise ValueError("non-preregistered F015 case/command")
    cfg = baseline("B-linked")
    cfg["experiment_id"] = "F015-" + group + "-" + dict(FORCES)[float(force)]
    cfg["motor_force_n"] = float(force)
    cfg["link"]["initially_attached"] = group == "L-linked"
    if group == "F-fixed":
        cfg["cells"][0]["external_force_n"] = -1.
        cfg["cells"][1]["external_force_n"] = +1.
    elif group == "T-tracking":
        cfg["cells"][0]["external_force_n"] = -float(force)/2
        cfg["cells"][1]["external_force_n"] = +float(force)/2
    if group == "E-disabled":
        cfg["cells"][0]["initial_balance_uj"] = 0
    return cfg


def origin_snapshot() -> dict:
    root = Path(__file__).resolve().parents[2]
    return {"f007": provenance(), "f015_source_hashes": {
        p: hashlib.sha256((root/p).read_bytes()).hexdigest() for p in SOURCE_FILES}}


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, sort_keys=True, indent=2, allow_nan=False)+"\n",
                    encoding="utf-8")


def load_trial(folder: Path) -> ProbeTrial:
    local = read_csv(folder/"a_local.csv", COLUMNS,
                     strings=("status",), integers=("step_index", "balance_a_uj"))
    packets = read_csv(folder/"b_packets.csv", PACKET_COLUMNS,
                       strings=("source",), flags=("moved",),
                       integers=("step_index",))
    return ProbeTrial(
        tuple(LocalObservation(**{k: row[k] for k in LOCAL_KEYS}) for row in local),
        tuple(PeerPacket(**packet) for packet in packets),
    )


def make_run(folder: Path, group: str, force: float, origin: dict) -> None:
    folder.mkdir(parents=True)
    tag = dict(FORCES)[force]
    write_json(folder/"config.json", {
        "schema_version": "f015.probe.v1",
        "experiment_id": "F015-"+group+"-"+tag,
        "case_id": group, "u_n": force,
        "dt_s": .25, "duration_s": 1.,
        "packet_threshold_m_s": THRESHOLD_M_S,
        "full_reset": True, "seed": None,
    })
    save_run(Config.from_dict(configuration(group,force)), folder/"F007",
             identity=origin["f007"])
    rows = read_csv(folder/"F007/states.csv", STATE_COLUMNS,
                    strings=("decision_reason",), flags=("attached",),
                    integers=("step_index","spent_a_uj","balance_a_uj",
                              "balance_b_uj","ledger_event_index"))
    with (folder/"a_local.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(analyze(rows))
    # Researcher-only adapter. The inferred model never sees these world rows.
    packets = (PeerPacket("B", q["step_index"], q["time_s"],
                          abs(q["v_b_m_s"] - p["v_b_m_s"]) > THRESHOLD_M_S)
               for p, q in zip(rows, rows[1:]))
    with (folder/"b_packets.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PACKET_COLUMNS)
        writer.writeheader()
        writer.writerows(packet_csv_row(x) for x in packets)


def build(stage: Path, origin: dict) -> dict:
    for group in GROUPS:
        for force, tag in FORCES:
            make_run(stage/group/tag, group, force, origin)
    outcomes = {group: analyze_probe(tuple(
        load_trial(stage/group/tag) for _, tag in FORCES))
        for group in GROUPS}
    if any(outcomes[g]["a_only_status"] != SAME for g in ("L-linked","T-tracking")):
        raise AssertionError("linked vs tracking reference mismatch")
    if outcomes["F-fixed"]["a_only_status"] != CHANGED or (
            outcomes["N-free"]["a_only_status"] != CHANGED) or (
            outcomes["E-disabled"]["a_only_status"] != UNKNOWN):
        raise AssertionError("frozen causal discrimination not met")
    if any(result["peer_incremental_discrimination"] for result in outcomes.values()):
        raise AssertionError("B-bit falsely credited as unique discrimination")
    base = stage/"L-linked"/"u2"
    if any((base/"a_local.csv").read_bytes() !=
           (stage/g/"u2"/"a_local.csv").read_bytes() or
           (base/"b_packets.csv").read_bytes() !=
           (stage/g/"u2"/"b_packets.csv").read_bytes()
           for g in ("F-fixed","T-tracking")):
        raise AssertionError("u2 baseline L/F/T equivalence contradicted")
    if any((stage/"L-linked"/tag/"a_local.csv").read_bytes() !=
           (stage/"T-tracking"/tag/"a_local.csv").read_bytes() or
           (stage/"L-linked"/tag/"b_packets.csv").read_bytes() !=
           (stage/"T-tracking"/tag/"b_packets.csv").read_bytes()
           for _,tag in FORCES):
        raise AssertionError("all-probe tracking counterexample contradicted")
    dropout = {}
    for _, tag in FORCES:
        trials = [load_trial(stage/"L-linked"/t) for _, t in FORCES]
        index = [t for _,t in FORCES].index(tag)
        original = trials[index]
        trials[index] = ProbeTrial(original.a_local,
                    original.b_packets[:1]+(None,)+original.b_packets[2:])
        dropout[tag] = analyze_probe(tuple(trials))
        if dropout[tag]["a_plus_peer_status"] != UNKNOWN:
            raise AssertionError("missing packet treated as false")
    write_json(stage/"probe_schedule.json", {
        "schema_version": "f015.probe.v1", "forces_n": [2.,1.,0.],
        "full_reset_each_trial": True, "duration_s": 1.,
        "dt_s": .25, "packet_threshold_m_s": THRESHOLD_M_S,
    })
    write_json(stage/"comparison.json", {
        "schema_version":"f015.comparison.v1",
        "science_status":"software_model_candidate_not_adopted",
        "researcher_truth_only":True,"topology_identified":False,
        "fixed_cases":list(GROUPS),"force_levels_n":[2.,1.,0.],
        "intervals":60,"outcomes":outcomes,
        "dropout_diagnostics":dropout,
        "LFT_u2_full_observation_equal":True,
        "L_T_all_interventions_equal":True,
        "L_F_A_only_separated":True,
        "B_unique_incremental_value":False,
    })
    paths = {p.relative_to(stage).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(stage.rglob("*")) if p.is_file()}
    write_json(stage/"manifest.json", {
        "schema_version":"f015.evidence.v1",
        "origin":origin,"cases":list(GROUPS),"artifacts":paths,
    })
    return verify_suite(stage, origin)


def suite(output: Path, replay: Path, *, origin: dict | None = None) -> dict:
    a,b = Path(output).resolve(),Path(replay).resolve()
    if a == b or a in b.parents or b in a.parents or a.exists() or b.exists():
        raise ValueError("same, nested, or existing evidence path")
    a.parent.mkdir(parents=True,exist_ok=True)
    b.parent.mkdir(parents=True,exist_ok=True)
    snapshot = origin_snapshot() if origin is None else origin
    sa = Path(tempfile.mkdtemp(prefix=".f015-A-", dir=a.parent))
    sb = Path(tempfile.mkdtemp(prefix=".f015-B-", dir=b.parent))
    try:
        out = build(sa, snapshot)
        build(sb, snapshot)
        x = {p.relative_to(sa).as_posix(): p.read_bytes()
             for p in sa.rglob("*") if p.is_file()}
        y = {p.relative_to(sb).as_posix(): p.read_bytes()
             for p in sb.rglob("*") if p.is_file()}
        if x != y:
            raise AssertionError("F015 byte replay failed")
        publish_dir(sa,a)
        try:
            publish_dir(sb,b)
        except BaseException:
            shutil.rmtree(a)
            raise
        return {**out, "byte_replay":True,"replay_files":len(x)}
    finally:
        for p in (sa,sb):
            if p.exists():
                shutil.rmtree(p)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir",required=True)
    parser.add_argument("--replay-output-dir",required=True)
    args=parser.parse_args()
    print(json.dumps(suite(Path(args.output_dir),Path(args.replay_output_dir)),
                     sort_keys=True))


if __name__=="__main__":
    main()
