"""F007 preregistered A-E + F-01..F-06 controls and immutable raw evidence.

Run: python -m experiments.F007.run_suite --output-dir runs/F007-ci --replay-output-dir runs/F007-replay
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from soma.f007 import Config, provenance, save_run
from experiments.F007.verify import audit_run, require


def baseline(case: str) -> dict:
    return {
        "schema_version":"f007.v1", "experiment_id":"F007-"+case,
        "seed":None, "dt_s":0.25, "duration_s":1.0, "drag_per_s":0.0,
        "cells":[
            {"id":"A","mass_kg":1.0,"initial_x_m":0.0,"initial_v_m_s":0.0,
             "external_force_n":0.0,"capacity_uj":3_000_000,"initial_balance_uj":3_000_000},
            {"id":"B","mass_kg":1.0,"initial_x_m":0.5,"initial_v_m_s":0.0,
             "external_force_n":0.0,"capacity_uj":1,"initial_balance_uj":0},
        ],
        "motor_force_n":2.0,
        "link":{"initially_attached":True,"length_m":0.5,"detach_time_s":None},
    }


def scenarios() -> dict[str,dict]:
    result={x:baseline(x) for x in ("A-free","B-linked","C-zero","D-external",
                                     "E-cut","F-01","F-02","F-03","F-04")}
    result["A-free"]["link"]["initially_attached"]=False
    result["C-zero"]["cells"][0]["initial_balance_uj"]=0
    result["D-external"]["motor_force_n"]=0.0
    result["D-external"]["cells"][1]["external_force_n"]=2.0
    result["E-cut"]["link"]["detach_time_s"]=0.5
    result["F-01"]["cells"][0]["initial_balance_uj"]=62_500
    result["F-02"]["cells"][0]["initial_balance_uj"]=1
    result["F-02"]["cells"][0]["external_force_n"]=-2.0
    result["F-03"]["cells"][0]["initial_balance_uj"]=0
    result["F-03"]["cells"][1]["external_force_n"]=2.0
    result["F-04"]["dt_s"]=1.0
    result["F-04"]["motor_force_n"]=-2.0
    result["F-04"]["cells"][0]["initial_balance_uj"]=1_000_000
    result["F-04"]["cells"][0]["initial_v_m_s"]=0.25
    result["F-04"]["cells"][1]["initial_v_m_s"]=0.25
    return result


def theoretical_gates(data: dict[str,dict]) -> None:
    # Literal Wolfram pre-registered references; no call into simulation.
    expected={
        "A-free":(1.25,0.5,2.,0.,2_000_000,0),
        "B-linked":(0.625,1.125,1.,1.,1_000_000,0),
        "C-zero":(0.,0.5,0.,0.,0,0),
        "D-external":(0.625,1.125,1.,1.,0,0),
        "E-cut":(0.8125,0.9375,1.5,0.5,1_250_000,0),
        "F-01":(0.25,0.75,0.25,0.25,62_500,0),
        "F-02":(0.,0.5,0.,0.,0,0),
        "F-03":(0.625,1.125,1.,1.,0,0),
        "F-04":(-0.75,-0.25,-0.75,-0.75,562_500,0),
    }
    for key,reference in expected.items():
        x=data[key]["final"]
        actual=(x["x_a_m"],x["x_b_m"],x["v_a_m_s"],x["v_b_m_s"],
                data[key]["spent_uj"],data[key]["spent_b_uj"])
        for observed,want in zip(actual,reference):
            if isinstance(want,int):
                require(observed==want,key+" integer Wolfram check")
            else:
                require(abs(observed-want)<=1e-12,key+" Wolfram check")
    require(data["B-linked"]["final"]["link_force_b_n"]==1.,"B link force")
    require(data["D-external"]["final"]["link_force_b_n"]==-1.,"D link force")
    require(data["F-03"]["final"]["link_force_b_n"]==-1.,"F-03 link force")
    require(data["F-04"]["final"]["motor_positive_work_j"]==0.5625,"F-04 positive work")
    require(data["F-04"]["final"]["motor_work_j"]==0.5,"F-04 signed work")
    require(data["E-cut"]["final"]["attached"] is False,"cut event")
    require(data["F-01"]["rejected_steps"]==3,"F-01 rejected after first spend")


def reject_inputs() -> list[str]:
    bad=[]
    scenarios_to_break=(
        ("mass-zero",lambda c: c["cells"][0].update(mass_kg=0.)),
        ("nan-force",lambda c: c.update(motor_force_n=float("nan"))),
        ("inf-force",lambda c: c["cells"][1].update(external_force_n=float("inf"))),
        ("bad-grid",lambda c: c.update(duration_s=1.1)),
        ("bad-gap",lambda c: c["cells"][1].update(initial_x_m=0.7)),
        ("bad-speed",lambda c: c["cells"][1].update(initial_v_m_s=0.1)),
        ("negative-balance",lambda c: c["cells"][0].update(initial_balance_uj=-1)),
        ("bad-balance",lambda c: c["cells"][0].update(initial_balance_uj=3_000_001)),
        ("bool-force",lambda c: c.update(motor_force_n=True)),
        ("cut-not-on-grid",lambda c: c["link"].update(detach_time_s=0.3)),
        ("cut-after-duration",lambda c: c["link"].update(detach_time_s=1.1)),
        ("unsupported-seed",lambda c: c.update(seed=0)),
    )
    for name,change in scenarios_to_break:
        c=baseline(name)
        change(c)
        try:
            Config.from_dict(c)
        except (ValueError,TypeError,OverflowError):
            bad.append(name)
        else:
            raise AssertionError("accepted invalid F007 config: "+name)
    return bad


def mutate_detection(source: Path) -> bool:
    with tempfile.TemporaryDirectory(prefix="soma-f007-adversary-") as tmp:
        target=Path(tmp)/"tampered"
        shutil.copytree(source,target)
        p=target/"states.csv"
        data=p.read_text(encoding="utf-8")
        require("0.625" in data,"adversarial case not found")
        p.write_text(data.replace("0.625","0.626",1),encoding="utf-8")
        try:
            audit_run(target)
        except AssertionError:
            return True
        raise AssertionError("failed to detect saved CSV mutation")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def suite(out: Path) -> dict:
    identity=provenance()
    # All configs and physical steps run before publishing the suite directory.
    configs={k:Config.from_dict(v) for k,v in scenarios().items()}
    from soma.f007 import simulate
    for cfg in configs.values():
        simulate(cfg)
    invalid=reject_inputs()
    out.mkdir(parents=True,exist_ok=False)
    (out/"suite_source.py").write_bytes(Path(__file__).read_bytes())
    (out/"oracle_source.py").write_bytes((Path(__file__).parent/"verify.py").read_bytes())
    summaries={}
    for key,cfg in configs.items():
        manifest=save_run(cfg,out/key,identity=identity)
        oracle=audit_run(out/key, trusted_origin=identity)
        import csv
        with (out/key/"states.csv").open(newline="",encoding="utf-8") as fp:
            rows=list(csv.DictReader(fp))
        last=rows[-1]
        final={}
        for k in ("x_a_m","x_b_m","v_a_m_s","v_b_m_s",
                  "link_force_a_n","link_force_b_n",
                  "motor_work_j","motor_positive_work_j"):
            final[k]=float(last[k])
        final["attached"]=last["attached"]=="True"
        summaries[key]={
            "final":final,"spent_uj":manifest["spent_uj"],
            "spent_b_uj":cfg.cells[1].initial_balance_uj-manifest["final_balances_uj"]["B"],
            "rejected_steps":sum(r["decision_reason"] in ("zero_balance","insufficient_balance") and
                                 float(r["motor_command_n"])!=0 for r in rows[1:]),
            "oracle":oracle,
        }
    theoretical_gates(summaries)
    tamper=mutate_detection(out/"B-linked")
    comparison={"schema_version":"f007.evidence.v1","status":"supported_discrete_controls_only",
                "theory":"Wolfram exact rational references; not observed robot physics",
                "cases":summaries,"invalid_inputs_rejected":invalid,
                "hash_tamper_detected":tamper,"caveats":[
                    "Effective motor force has no modeled reaction or ground contact",
                    "Semi-implicit Euler positions differ from velocity-interpolant work trajectory",
                    "Motor gating and per-step ceil depend on dt",
                    "No emergence, self-propulsion, or morphological advantage inferred",
                ]}
    (out/"comparison.json").write_text(
        json.dumps(comparison,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    allfiles=sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file())
    manifest={
        "schema_version":"f007.suite.v1","model":"f007.v1","seed":None,
        "origin":identity,"cases":list(configs),"number_of_runs":len(configs),
        "test_negative_cases":invalid,"tampering_detected":tamper,
        "artifacts":{name:digest(out/name) for name in allfiles},
        "research_verdict":"supported_discrete_controls_only_not_formally_adopted",
    }
    (out/"manifest.json").write_text(
        json.dumps(manifest,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    return manifest


def compare_full(a: Path, b: Path) -> int:
    names_a={p.relative_to(a).as_posix() for p in a.rglob("*") if p.is_file()}
    names_b={p.relative_to(b).as_posix() for p in b.rglob("*") if p.is_file()}
    require(names_a==names_b,"different evidence file set")
    for name in names_a:
        require((a/name).read_bytes()==(b/name).read_bytes(),"replay mismatch: "+name)
    return len(names_a)


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--replay-output-dir",type=Path,required=True)
    args=p.parse_args()
    require(args.output_dir.resolve()!=args.replay_output_dir.resolve(),"distinct dirs required")
    a=suite(args.output_dir)
    suite(args.replay_output_dir)
    checked=compare_full(args.output_dir,args.replay_output_dir)
    print(json.dumps({"status":a["research_verdict"],"runs":a["number_of_runs"],
                      "replay_files_verified":checked,"invalid_rejected":len(a["test_negative_cases"]),
                      "tamper_detected":a["tampering_detected"]},sort_keys=True))


if __name__=="__main__":
    main()
