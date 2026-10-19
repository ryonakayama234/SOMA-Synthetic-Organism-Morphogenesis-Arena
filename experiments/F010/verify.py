"""F010 independent saved-data oracle.

NEVER imports soma.f010 estimator, F008 detector or F007 simulate. Checks every
F007 raw state with the *existing* independent F007 saved oracle, and all A-only
F008 columns plus F010 response summaries via separate Fraction arithmetic.
Researcher-only: world truth stays in this verifier, not local estimator.
"""
from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction as Q
from pathlib import Path

from soma.f007 import STATE_COLUMNS
from soma.f008 import COLUMNS
from experiments.F007.verify import audit_run, read_csv

GROUPS=("A-linked","B-constant","C-adaptive","D-free","E-empty")
FORCE_TAGS=((2.,"u2"),(1.,"u1"),(.5,"u05"))
SOURCE_FILES=(
    "soma/f010.py","experiments/F010/run_suite.py",
    "experiments/F010/verify.py","tests/test_f010.py",".github/workflows/f010.yml",
    "topics/F010-local-identifiability/SPEC.md","experiments/F010/PLAN.md",
    "experiments/F010/README.md","findings/F010-validation.md",
    "docs/ARCHITECTURE.md","docs/DATA_CONTRACTS.md",
    "README.md","AGENTS.md","library/INDEX.md",
)
SUBFILES={
    "F007/config.json","F007/states.csv","F007/ledger/events.csv",
    "F007/link_events.csv","F007/motion.svg","F007/manifest.json","local.csv",
}
TOL=1e-12


def require(condition: bool, message: str):
    if not condition:
        raise AssertionError("F010 oracle: "+message)


def equal(actual, expected, field: str):
    if expected is None or isinstance(expected,(str,bool,int)):
        require(type(actual) is type(expected) and actual==expected,field+" exact")
    else:
        require(type(actual) in (int,float) and math.isfinite(actual) and
                abs(actual-float(expected))<=TOL,field+" rational")


def _acc(group: str, u: Q) -> Q:
    if group in ("A-linked","C-adaptive"):
        return u/2
    if group=="B-constant":
        return u-1
    if group=="D-free":
        return u
    if group=="E-empty":
        return Q(0)
    raise ValueError("unknown control group")


def _expected_result(group: str) -> dict:
    if group in ("A-linked","C-adaptive"):
        slope,offset,signature=Q(1,2),Q(0),"inertia_like"
    elif group=="B-constant":
        slope,offset,signature=Q(1),Q(-1),"offset_like"
    elif group=="D-free":
        slope,offset,signature=Q(1),Q(0),"nominal_like"
    else:
        return {"status":"inconclusive","reason":"rejected_or_unstable_applied_excitation",
                "alpha_per_kg":None,"beta_m_s2":None,
                "holdout_residual_m_s2":None,"response_signature":None}
    return {"status":"affine_response_fit","reason":"fixed_ideal_1d_discrete_response_only",
            "alpha_per_kg":slope,"beta_m_s2":offset,
            "holdout_residual_m_s2":Q(0),"response_signature":signature}


def verify_suite(directory: Path, trusted_origin: dict) -> dict:
    root=Path(directory)
    manifest=json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    require(set(manifest)=={"schema_version","origin","cases","artifacts"},"manifest schema")
    require(manifest["schema_version"]=="f010.evidence.v1","manifest version")
    require(manifest["origin"]==trusted_origin,"origin externally supplied")
    require(manifest["cases"]==list(GROUPS),"frozen group order")
    require(set(trusted_origin)=={"f007","f010_source_hashes"},"origin fields")
    require(set(trusted_origin["f010_source_hashes"])==set(SOURCE_FILES),"source inventory")
    repo=Path(__file__).resolve().parents[2]
    for source,sha in trusted_origin["f010_source_hashes"].items():
        require(hashlib.sha256((repo/source).read_bytes()).hexdigest()==sha,
                "source checkout hash mismatch: "+source)

    expected=set(("comparison.json",))
    for group in GROUPS:
        for _,tag in FORCE_TAGS:
            expected.update(group+"/"+tag+"/"+rel for rel in SUBFILES)
    actual={p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    require(actual==expected|{"manifest.json"},"unexpected or missing evidence path")
    require(set(manifest["artifacts"])==expected,"artifact inventory")
    for rel,digest in manifest["artifacts"].items():
        require(type(digest) is str and len(digest)==64,"bad digest")
        require(hashlib.sha256((root/rel).read_bytes()).hexdigest()==digest,
                "evidence digest mismatch: "+rel)
    summaries={}
    for group in GROUPS:
        for force,tag in FORCE_TAGS:
            name=group+"/"+tag
            run=root/name
            # Independently verifies F007 forces, battery ledger, link, and every source row.
            audit_run(run/"F007",trusted_origin=trusted_origin["f007"])
            config=json.loads((run/"F007/config.json").read_text(encoding="utf-8"))
            require(config["schema_version"]=="f007.v1","F007 version "+name)
            require(config["experiment_id"]=="F010-"+group+"-"+tag,"experiment ID "+name)
            equal(config["dt_s"],.25,"dt "+name)
            equal(config["duration_s"],1.,"duration "+name)
            equal(config["drag_per_s"],0.,"drag "+name)
            equal(config["motor_force_n"],force,"force "+name)
            equal(config["cells"][0]["mass_kg"],1.,"A mass "+name)
            equal(config["cells"][1]["mass_kg"],1.,"B mass "+name)
            equal(config["cells"][0]["initial_balance_uj"],0 if group=="E-empty" else 3_000_000,
                  "A initial balance "+name)
            equal(config["cells"][1]["initial_balance_uj"],0,"B balance "+name)
            require(config["link"]["initially_attached"]==(group=="A-linked"),
                    "world coupling control "+name)
            external=-1. if group=="B-constant" else (-force/2 if group=="C-adaptive" else 0.)
            equal(config["cells"][0]["external_force_n"],external,"world external "+name)
            states=read_csv(run/"F007/states.csv",STATE_COLUMNS,
                            strings=("decision_reason",),flags=("attached",),
                            integers=("step_index","spent_a_uj","balance_a_uj",
                                      "balance_b_uj","ledger_event_index"))
            local=read_csv(run/"local.csv",COLUMNS,
                           strings=("status",),
                           integers=("step_index","balance_a_uj"))
            require(len(states)==5 and len(local)==4,"fixed row counts "+name)
            a=_acc(group,Q(str(force)))
            h=Q(1,4)
            for i,(prev,current,row) in enumerate(zip(states,states[1:],local),start=1):
                prefix=name+" row "+str(i)+" "
                # Exact rational Newton + semi-implicit Euler, separate from F007 source.
                equal(current["v_a_m_s"],a*i*h,prefix+"v")
                equal(current["x_a_m"],a*h*h*i*(i+1)/2,prefix+"x")
                equal(current["v_b_m_s"],a*i*h if group=="A-linked" else 0.,prefix+"B v")
                equal(current["x_b_m"],Q(1,2)+(a*h*h*i*(i+1)/2 if group=="A-linked" else 0),
                      prefix+"B x")
                applied=0. if group=="E-empty" else force
                equal(current["motor_applied_n"],applied,prefix+"applied force")
                expected={
                    "step_index":i,"time_s":i*.25,"dt_s":.25,
                    "v_prev_m_s":prev["v_a_m_s"],
                    "v_a_m_s":current["v_a_m_s"],
                    "motor_command_n":force,
                    "motor_applied_n":applied,
                    "balance_a_uj":current["balance_a_uj"],
                    "observed_accel_m_s2":a,
                    "expected_accel_m_s2":None if group=="E-empty" else force,
                    "residual_m_s2":None if group=="E-empty" else a-Q(str(force)),
                    "status":"not_excited" if group=="E-empty" else (
                        "nominal" if a==Q(str(force)) else "anomaly"),
                }
                require(set(row)==set(expected),"A-local schema "+prefix)
                for key,val in expected.items():
                    equal(row[key],val,prefix+key)
            summaries[name]={"a":float(a),"final_v":states[-1]["v_a_m_s"],
                             "final_x":states[-1]["x_a_m"]}
    for _,tag in FORCE_TAGS:
        require((root/"A-linked"/tag/"local.csv").read_bytes() ==
                (root/"C-adaptive"/tag/"local.csv").read_bytes(),
                "A-linked/C-adaptive exact A-local equivalence "+tag)
    comparison=json.loads((root/"comparison.json").read_text(encoding="utf-8"))
    require(set(comparison)=={"schema_version","science_status","question",
                              "fixed_cases","force_levels_n","signatures",
                              "counterexample","researcher_truth_only"},
            "comparison contract")
    require(comparison["schema_version"]=="f010.evidence.v1","comparison version")
    require(comparison["science_status"]=="software_model_candidate_not_adopted",
            "science claim tampered")
    require(comparison["question"]=="A-local force-response identifiability; no topology identification",
            "question tampered")
    require(comparison["counterexample"]==
            "A-linked and C-adaptive have identical A-local time/battery histories",
            "counterexample tampered")
    require(comparison["researcher_truth_only"] is True,"world/local meaning tampered")
    require(comparison["fixed_cases"]==list(GROUPS),"case labels")
    require(comparison["force_levels_n"]==[2.,1.,.5],"force labels")
    require(set(comparison["signatures"])==set(GROUPS),"missing response signature")
    for group,measured in comparison["signatures"].items():
        require(set(measured)=={"schema_version","status","reason","alpha_per_kg",
                               "beta_m_s2","holdout_residual_m_s2",
                               "response_signature","topology_verified"},
                "response keys "+group)
        require(measured["schema_version"]=="f010.signature.v1","response version")
        require(measured["topology_verified"] is False,"improper topology assertion")
        for key,ref in _expected_result(group).items():
            equal(measured[key],ref,"response "+group+"/"+key)
    return {"cases":15,"local_intervals":60,"evidence_files":len(actual),
            "model_controls_supported":4,"unexcited_inconclusive":1,
            "linked_adaptive_exact_local_equivalence":True,
            "topology_identified":False}
