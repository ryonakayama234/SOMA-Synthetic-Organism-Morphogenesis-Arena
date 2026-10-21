"""Independent saved-file F015 audit. NEVER import soma.f015 or F015 producer.

Re-derives constrained mechanics, A-observation, B bit and all scientific
comparisons from saved F007 world rows. This is a same-author independent
implementation, not an external human/experimental physics validation.
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

GROUPS=("L-linked","F-fixed","T-tracking","N-free","E-disabled")
FORCES=((2.,"u2"),(1.,"u1"),(0.,"u0"))
PACKET_COLUMNS=("source","step_index","time_s","moved")
SOURCE_FILES=(
    "soma/f015.py", "experiments/F015/run_suite.py",
    "experiments/F015/verify.py", "tests/test_f015.py",
    ".github/workflows/f015.yml", "topics/F015-active-body-probing/SPEC.md",
    "experiments/F015/PLAN.md", "experiments/F015/README.md",
    "findings/F015-validation.md", "docs/ARCHITECTURE.md",
    "docs/DATA_CONTRACTS.md", "README.md", "AGENTS.md",
)
FILES={"config.json","F007/config.json","F007/states.csv",
       "F007/ledger/events.csv","F007/link_events.csv","F007/motion.svg",
       "F007/manifest.json","a_local.csv","b_packets.csv"}
TOL=1e-12


def require(ok: bool, label: str) -> None:
    if not ok:
        raise AssertionError("F015 independent oracle: "+label)


def eq(actual, wanted, key: str) -> None:
    if wanted is None or type(wanted) in (bool,str,int):
        require(type(actual) is type(wanted) and actual==wanted,key)
    else:
        require(type(actual) in (int,float) and math.isfinite(actual) and
                abs(actual-float(wanted)) <= TOL,key+" got "+repr(actual)+
                " wanted "+repr(wanted))


def acceleration(group: str, u: Q) -> tuple[Q,Q]:
    if group in ("L-linked","T-tracking"):
        return u/2,u/2
    if group=="F-fixed":
        return u-1,Q(1)
    if group=="N-free":
        return u,Q(0)
    if group=="E-disabled":
        return Q(0),Q(0)
    raise AssertionError("unknown case")


def expected_status(group: str) -> tuple[str,str,int,float]:
    if group in ("L-linked","T-tracking"):
        return "observation_signature_same","observation_signature_same",0,0.
    if group=="F-fixed":
        return "observation_signature_changed","observation_signature_changed",4,1.
    if group=="N-free":
        return "observation_signature_changed","observation_signature_changed",8,1.
    return "inconclusive","inconclusive",8,1.


def verify_suite(directory: Path, trusted_origin: dict) -> dict:
    root=Path(directory)
    manifest=json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    require(set(manifest)=={"schema_version","origin","cases","artifacts"},"manifest fields")
    require(manifest["schema_version"]=="f015.evidence.v1" and
            manifest["origin"]==trusted_origin and
            manifest["cases"]==list(GROUPS),"manifest contract")
    require(set(trusted_origin)=={"f007","f015_source_hashes"} and
            set(trusted_origin["f015_source_hashes"])==set(SOURCE_FILES),
            "trusted source inventory")
    project=Path(__file__).resolve().parents[2]
    for p,digest in trusted_origin["f015_source_hashes"].items():
        require(type(digest) is str and len(digest)==64 and
                hashlib.sha256((project/p).read_bytes()).hexdigest()==digest,
                "source-bound hash: "+p)
    expect={"probe_schedule.json","comparison.json"}
    for group in GROUPS:
        for _,tag in FORCES:
            expect.update(group+"/"+tag+"/"+p for p in FILES)
    seen={p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    require(seen==expect|{"manifest.json"} and
            set(manifest["artifacts"])==expect,"artifact inventory exact")
    for p,digest in manifest["artifacts"].items():
        require(type(digest) is str and len(digest)==64 and
                hashlib.sha256((root/p).read_bytes()).hexdigest()==digest,
                "artifact hash: "+p)
    schedule=json.loads((root/"probe_schedule.json").read_text(encoding="utf-8"))
    require(set(schedule)=={"schema_version","forces_n","full_reset_each_trial",
                            "duration_s","dt_s","packet_threshold_m_s"} and
            schedule["schema_version"]=="f015.probe.v1" and
            schedule["forces_n"]==[2.,1.,0.] and
            schedule["full_reset_each_trial"] is True,"fixed global probe")
    for name,value in (("duration_s",1.),("dt_s",.25),
                       ("packet_threshold_m_s",1e-10)):
        eq(schedule[name],value,"probe "+name)

    for group in GROUPS:
        for force,tag in FORCES:
            prefix=group+"/"+tag
            folder=root/prefix
            audit_run(folder/"F007",trusted_origin=trusted_origin["f007"])
            envelope=json.loads((folder/"config.json").read_text(encoding="utf-8"))
            require(set(envelope)=={"schema_version","experiment_id","case_id",
                        "u_n","dt_s","duration_s","packet_threshold_m_s",
                        "full_reset","seed"} and
                    envelope["schema_version"]=="f015.probe.v1" and
                    envelope["experiment_id"]=="F015-"+group+"-"+tag and
                    envelope["case_id"]==group and
                    envelope["full_reset"] is True and
                    envelope["seed"] is None,"envelope "+prefix)
            for name,value in (("u_n",force),("dt_s",.25),("duration_s",1.),
                               ("packet_threshold_m_s",1e-10)):
                eq(envelope[name],value,"envelope "+prefix+name)
            cfg=json.loads((folder/"F007/config.json").read_text(encoding="utf-8"))
            require(cfg["schema_version"]=="f007.v1" and cfg["seed"] is None and
                    cfg["experiment_id"]=="F015-"+group+"-"+tag,
                    "world config identifier")
            for name,value in (("dt_s",.25),("duration_s",1.),
                               ("drag_per_s",0.),("motor_force_n",force)):
                eq(cfg[name],value,"world config "+prefix+name)
            require(cfg["link"]=={"initially_attached":group=="L-linked",
                       "length_m":.5,"detach_time_s":None},"link "+prefix)
            cells=cfg["cells"]
            require([x["id"] for x in cells]==["A","B"],"cell IDs")
            for i,cell in enumerate(cells):
                for name,value in (("mass_kg",1.),("initial_x_m",i*.5),
                                   ("initial_v_m_s",0.)):
                    eq(cell[name],value,"cell reset "+prefix+name)
            eq(cells[0]["initial_balance_uj"],
               0 if group=="E-disabled" else 3_000_000,"A budget")
            eq(cells[1]["initial_balance_uj"],0,"B budget")
            dA=(-1. if group=="F-fixed" else -force/2 if group=="T-tracking" else 0.)
            dB=(1. if group=="F-fixed" else force/2 if group=="T-tracking" else 0.)
            eq(cells[0]["external_force_n"],dA,"hidden A fixed/tracking")
            eq(cells[1]["external_force_n"],dB,"hidden B fixed/tracking")
            raw=read_csv(folder/"F007/states.csv",STATE_COLUMNS,
                         strings=("decision_reason",),flags=("attached",),
                         integers=("step_index","spent_a_uj","balance_a_uj",
                                   "balance_b_uj","ledger_event_index"))
            local=read_csv(folder/"a_local.csv",COLUMNS,strings=("status",),
                           integers=("step_index","balance_a_uj"))
            peer=read_csv(folder/"b_packets.csv",PACKET_COLUMNS,
                          strings=("source",),flags=("moved",),
                          integers=("step_index",))
            require(len(raw)==5 and len(local)==len(peer)==4,"row lengths "+prefix)
            a,b=acceleration(group,Q(str(force)))
            h=Q(1,4)
            for k,(prev,row,loc,packet) in enumerate(zip(raw,raw[1:],local,peer),1):
                mark=prefix+" step "+str(k)+" "
                eq(row["v_a_m_s"],a*k*h,mark+"A velocity")
                eq(row["v_b_m_s"],b*k*h,mark+"B velocity")
                eq(row["x_a_m"],a*h*h*k*(k+1)/2,mark+"A position")
                eq(row["x_b_m"],Q(1,2)+b*h*h*k*(k+1)/2,mark+"B position")
                applied=0. if group=="E-disabled" else force
                eq(row["motor_applied_n"],applied,mark+"applied force")
                reference={
                    "step_index":k,"time_s":k*.25,"dt_s":.25,
                    "v_prev_m_s":prev["v_a_m_s"],
                    "v_a_m_s":row["v_a_m_s"],
                    "motor_command_n":force,"motor_applied_n":applied,
                    "balance_a_uj":row["balance_a_uj"],
                    "observed_accel_m_s2":a,
                    "expected_accel_m_s2": None if applied==0 else applied,
                    "residual_m_s2":None if applied==0 else a-Q(str(applied)),
                    "status":("not_excited" if applied==0 else
                              "nominal" if a==Q(str(applied)) else "anomaly"),
                }
                require(set(loc)==set(reference),"local field allowlist")
                for name,want in reference.items():
                    eq(loc[name],want,mark+"local "+name)
                require(set(packet)==set(PACKET_COLUMNS),"one-bit fields")
                eq(packet["source"],"B",mark+"packet source")
                eq(packet["step_index"],k,mark+"packet seq")
                eq(packet["time_s"],k*.25,mark+"packet clock")
                eq(packet["moved"],abs(float(b*h))>1e-10,mark+"packet bit")

    # Observational comparisons: source bytes must match, not guessed state tags.
    for _,tag in FORCES:
        l=root/"L-linked"/tag
        t=root/"T-tracking"/tag
        require((l/"a_local.csv").read_bytes()==(t/"a_local.csv").read_bytes() and
                (l/"b_packets.csv").read_bytes()==(t/"b_packets.csv").read_bytes(),
                "tracking-world indistinguishable "+tag)
        if tag=="u2":
            f=root/"F-fixed"/tag
            require((l/"a_local.csv").read_bytes()==(f/"a_local.csv").read_bytes() and
                    (l/"b_packets.csv").read_bytes()==(f/"b_packets.csv").read_bytes(),
                    "original baseline equality")
        else:
            require((l/"a_local.csv").read_bytes()!=
                    (root/"F-fixed"/tag/"a_local.csv").read_bytes(),
                    "post-intervention A-only detection")

    comparison=json.loads((root/"comparison.json").read_text(encoding="utf-8"))
    require(set(comparison)=={"schema_version","science_status","researcher_truth_only",
        "topology_identified","fixed_cases","force_levels_n","intervals",
        "outcomes","dropout_diagnostics","LFT_u2_full_observation_equal",
        "L_T_all_interventions_equal","L_F_A_only_separated",
        "B_unique_incremental_value"},"summary keys")
    require(comparison["schema_version"]=="f015.comparison.v1" and
            comparison["science_status"]=="software_model_candidate_not_adopted" and
            comparison["researcher_truth_only"] is True and
            comparison["topology_identified"] is False and
            comparison["fixed_cases"]==list(GROUPS) and
            comparison["force_levels_n"]==[2.,1.,0.] and
            comparison["intervals"]==60,"comparison identity")
    for p in ("LFT_u2_full_observation_equal","L_T_all_interventions_equal",
              "L_F_A_only_separated"):
        require(comparison[p] is True,p)
    require(comparison["B_unique_incremental_value"] is False,"false B utility claim")
    require(set(comparison["outcomes"])==set(GROUPS),"outcome coverage")
    for group in GROUPS:
        item=comparison["outcomes"][group]
        wantA,wantAB,wantN,wantError=expected_status(group)
        require(set(item)=={"schema_version","a_only_status","a_plus_peer_status",
                "a_max_abs_residual_m_s2","peer_mismatch_steps",
                "peer_incremental_discrimination","interpretation"},"result schema")
        require(item["schema_version"]=="f015.comparison.v1" and
                item["a_only_status"]==wantA and
                item["a_plus_peer_status"]==wantAB and
                item["peer_mismatch_steps"]==wantN and
                item["peer_incremental_discrimination"] is False and
                item["interpretation"]=="relative_to_frozen_reference_not_topology",
                "independent outcome "+group)
        eq(item["a_max_abs_residual_m_s2"],wantError,group+" observed max error")
    require(set(comparison["dropout_diagnostics"])=={"u2","u1","u0"},
            "dropout coverage")
    for key,result in comparison["dropout_diagnostics"].items():
        require(result["a_only_status"]=="observation_signature_same" and
                result["a_plus_peer_status"]=="inconclusive" and
                result["peer_incremental_discrimination"] is False and
                result["peer_mismatch_steps"]==0,
                "dropout must retain observed packets and uncertainty "+key)
    return {"cases":15,"a_local_intervals":60,"b_packet_intervals":60,
            "dropout_controls":3,"L_F_A_only_separated":True,
            "L_T_indistinguishable":True,"peer_incremental_discrimination":False,
            "topology_identified":False,"evidence_files":len(seen)}
