"""Independent F007 saved-file oracle, not calling F007 motion/simulate or F005 work.

The oracle uses exact Fraction integrals for small rational pre-registered
controls; its integer cost checks are limited to these controls because F005's
binary64 rounding semantics need separately specified reference on other inputs.
"""
from __future__ import annotations

import csv
from fractions import Fraction as Q
import hashlib
import json
import math
from pathlib import Path


def require(test: bool, label: str) -> None:
    if not test:
        raise AssertionError(label)


def positive_reference(u: float, v0: float, v1: float, h: float) -> Q:
    """Exact rational integral of positive power for linear velocity interpolation."""
    u, v0, v1, h = map(Q, (u, v0, v1, h))
    a, b = u*v0, u*v1
    if a >= 0 and b >= 0:
        return h*(a+b)/2
    if a <= 0 and b <= 0:
        return Q(0)
    positive = max(a,b)
    negative = -min(a,b)
    return h * positive**2 / (2*(positive+negative))


def read_csv(path: Path, columns: tuple[str, ...], *, strings=(), flags=(), integers=()) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        require(tuple(reader.fieldnames or ()) == columns, "unexpected CSV columns: " + str(path))
        out = []
        for raw in reader:
            line = {}
            for key, val in raw.items():
                if key in strings:
                    line[key] = val
                elif key in flags:
                    require(val in ("True", "False"), key+": invalid boolean")
                    line[key] = (val == "True")
                elif val == "":
                    line[key] = None
                elif key in integers:
                    line[key] = int(val)
                else:
                    line[key] = float(val)
                    require(math.isfinite(line[key]), "non-finite "+key)
            out.append(line)
    return out


def compare(actual, expected, name: str, *, tolerance=1e-12) -> None:
    if expected is None or isinstance(expected,(bool,str,int)):
        require(actual == expected, name + ": exact mismatch " + repr((actual,expected)))
    else:
        require(actual is not None and math.isfinite(actual) and
                abs(actual-expected) <= tolerance, name+": numeric mismatch "+repr((actual,expected)))


def audit_run(directory: Path, *, trusted_origin: dict | None = None) -> dict:
    # Trusted identity MUST originate outside the saved/possibly tampered manifest.
    # Git/source hashes validate a checkout, not the human who historically ran it.
    # Every hash is checked, then EVERY saved numerical row and event is re-derived.
    root = directory.resolve()
    m = json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    c = json.loads((root/"config.json").read_text(encoding="utf-8"))
    if trusted_origin is not None:
        require(m.get("origin") == trusted_origin, "origin vs externally supplied trusted identity")
        required = {
            "soma/f001.py", "soma/f002.py", "soma/f003.py", "soma/f005.py",
            "soma/f007.py", "topics/F007-linked-motor-work/SPEC.md",
            "experiments/F007/PLAN.md",
            "experiments/F007/run_suite.py",
            "experiments/F007/verify.py",
        }
        require(set(trusted_origin["source_hashes"]) == required,
                "trusted source dependency set")
        project = Path(__file__).resolve().parents[2]
        for rel, expected_hash in trusted_origin["source_hashes"].items():
            require(hashlib.sha256((project / rel).read_bytes()).hexdigest() == expected_hash,
                    "trusted checkout source mismatch: " + rel)
    require(m["schema_version"] == "f007.v1" and c["schema_version"] == "f007.v1",
            "schema")
    expected_files = {"config.json","states.csv","ledger/events.csv","link_events.csv","motion.svg"}
    require(set(m["artifacts"]) == expected_files, "manifest artifact contract")
    for name, digest in m["artifacts"].items():
        require(hashlib.sha256((root/name).read_bytes()).hexdigest()==digest, "sha "+name)
    # Import only field definitions, NOT runtime dynamics.
    from soma.f007 import STATE_COLUMNS, LEDGER_COLUMNS, LINK_COLUMNS
    ints = {"step_index","spent_a_uj","balance_a_uj","balance_b_uj","ledger_event_index"}
    states = read_csv(root/"states.csv",STATE_COLUMNS,
                      strings=("decision_reason",), flags=("attached",), integers=ints)
    ledger = read_csv(root/"ledger/events.csv",LEDGER_COLUMNS,
                      strings=("kind","source_id","target_id"),
                      integers={"step_index","event_index","amount_uj","eta_bps",
                                "received_uj","loss_uj","external_in_uj","external_out_uj","residual_uj"})
    links = read_csv(root/"link_events.csv", LINK_COLUMNS,strings=("kind",),
                     flags=("attached_before","attached_after"))
    a,b=c["cells"]; u=c["motor_force_n"]; h=c["dt_s"]; d=c["drag_per_s"]
    ma,mb=a["mass_kg"],b["mass_kg"]
    fa,fb=a["external_force_n"],b["external_force_n"]
    mass=ma+mb
    total_steps=Q(str(c["duration_s"]))/Q(str(h))
    require(total_steps.denominator==1 and len(states)==int(total_steps)+1,"trace length")
    require(m["samples"]==len(states),"sample count")
    require(m["ledger_events"]==len(ledger) and m["link_events"]==len(links),"event counts")
    x=[a["initial_x_m"],b["initial_x_m"]]
    v=[a["initial_v_m_s"],b["initial_v_m_s"]]
    remaining=a["initial_balance_uj"]
    balance_b=b["initial_balance_uj"]
    attached=c["link"]["initially_attached"]
    detach=c["link"]["detach_time_s"]
    cut_k=int(Q(str(detach))/Q(str(h))) if detach is not None else None
    expected_links=[]
    if attached:
        expected_links.append((0,"attach_initial",False,True,x[:],v[:],0.))
    expected_ledger=[]
    max_error=0.
    for k,row in enumerate(states):
        applied=0.
        reason="initial"
        cand=None; cand_plus=None
        spent=0
        motor_work=0.; motor_positive=0.; external_work=0.; drag_work=0.
        link_work=0.; delta_k=0.; residual=0.
        link_b=0.
        if k:
            old_x,old_v=x[:],v[:]
            reason="zero_balance" if remaining==0 else "zero_command" if u==0 else "attempt"
            if reason=="attempt":
                # Candidate equation written independently, no imported simulator.
                ftotal=u+fa+fb if attached else u+fa
                effective_mass=mass if attached else ma
                candidate_v=v[0] + h*(ftotal/effective_mass-d*v[0])
                cand=(u*h)*((v[0]+candidate_v)/2)
                pw_exact=positive_reference(u,v[0],candidate_v,h)
                cand_plus=float(pw_exact)
                micro_cost=math.ceil(pw_exact*1_000_000)
                if micro_cost <= remaining:
                    applied=u
                    spent=micro_cost
                    reason="accepted_positive_work" if spent else "accepted_nonpositive_work"
                else:
                    reason="insufficient_balance"
            forces=(applied+fa,fb)
            if attached:
                new_v=v[0]+h*((forces[0]+forces[1])/mass-d*v[0])
                v=[new_v,new_v]
                delta_x=h*v[0]
                x=[x[0]+delta_x,x[1]+delta_x]
                link_b=mb*(forces[0]+forces[1])/mass-forces[1]
            else:
                v=[v[0]+h*(forces[0]/ma-d*v[0]),
                   v[1]+h*(forces[1]/mb-d*v[1])]
                x=[x[0]+h*v[0],x[1]+h*v[1]]
            mida,midb=(old_v[0]+v[0])/2,(old_v[1]+v[1])/2
            motor_work=(applied*h)*mida
            motor_positive=float(positive_reference(applied,old_v[0],v[0],h))
            external_work=h*(fa*mida+fb*midb)
            drag_work=h*d*(ma*old_v[0]*mida+mb*old_v[1]*midb)
            link_work=h*link_b*(midb-mida) if attached else 0.
            delta_k=(ma*(v[0]*v[0]-old_v[0]*old_v[0])+
                     mb*(v[1]*v[1]-old_v[1]*old_v[1]))/2
            residual=delta_k-(motor_work+external_work-drag_work+link_work)
            remaining-=spent
            if spent:
                expected_ledger.append((k,spent,remaining))
            if attached and k==cut_k:
                expected_links.append((k,"detach",True,False,x[:],v[:],link_b))
                attached=False
        expected = {
            "step_index":k,"time_s":k*h,"attached":attached,
            "x_a_m":x[0],"x_b_m":x[1],"v_a_m_s":v[0],"v_b_m_s":v[1],
            "motor_command_n":u,"motor_applied_n":applied,
            "external_force_a_n":fa,"external_force_b_n":fb,
            "link_force_a_n":-link_b if attached else 0.,
            "link_force_b_n":link_b if attached else 0.,
            "candidate_motor_work_j":cand,
            "candidate_motor_positive_work_j":cand_plus,
            "motor_work_j":motor_work,"motor_positive_work_j":motor_positive,
            "external_work_j":external_work,"drag_work_j":drag_work,
            "link_work_j":link_work,"kinetic_delta_j":delta_k,
            "mechanical_residual_j":residual,"spent_a_uj":spent,
            "balance_a_uj":remaining,"balance_b_uj":balance_b,
            "ledger_event_index":len(expected_ledger) if spent else None,
            "decision_reason":reason,
        }
        require(set(row)==set(expected),"state columns")
        for key,want in expected.items():
            compare(row[key],want,f"state {k}/{key}")
            if type(want) is float and row[key] is not None:
                max_error=max(max_error,abs(row[key]-want))
        require(abs(row["mechanical_residual_j"])<=1e-10,"energy balance per-step")
        require(abs(row["link_force_a_n"]+row["link_force_b_n"])<=1e-12,"Newton 3rd")
        if attached:
            require(abs(row["x_b_m"]-row["x_a_m"]-c["link"]["length_m"])<=1e-10,"rigid gap")
            require(abs(row["v_b_m_s"]-row["v_a_m_s"])<=1e-12,"rigid velocity")
    require(len(ledger)==len(expected_ledger),"spend event count")
    total_spend=0
    for row,(k,amount,balance) in zip(ledger,expected_ledger):
        total_spend+=amount
        require(row["step_index"]==k and row["time_s"]==k*h, "ledger time")
        require(row["kind"]=="spend" and row["source_id"]=="A" and row["target_id"]=="",
                "ledger ownership")
        require(row["amount_uj"]==amount and row["event_index"]==expected_ledger.index((k,amount,balance))+1,
                "ledger transaction")
        require(row["residual_uj"]==0 and row["external_out_uj"]==amount,
                "ledger conservation")
        require(row["received_uj"]==0 and row["loss_uj"]==0 and row["external_in_uj"]==0,
                "unexpected energy transfer")
        require(row["eta_bps"] is None,"unexpected transfer efficiency")
    require(len(links)==len(expected_links),"link event count")
    for row,(k,kind,before,after,xx,vv,force) in zip(links,expected_links):
        for key,want in {"time_s":k*h,"kind":kind,"attached_before":before,
                         "attached_after":after,"x_a_before_m":xx[0],"x_a_after_m":xx[0],
                         "x_b_before_m":xx[1],"x_b_after_m":xx[1],
                         "v_a_before_m_s":vv[0],"v_a_after_m_s":vv[0],
                         "v_b_before_m_s":vv[1],"v_b_after_m_s":vv[1],
                         "link_force_before_n":force}.items():
            compare(row[key],want,"link/"+key)
    require(m["spent_uj"]==total_spend and total_spend==a["initial_balance_uj"]-remaining,
            "total spend conservation")
    require(m["final_balances_uj"]=={"A":remaining,"B":balance_b}
            and m["ledger_residual_uj"]==0, "manifest balances")
    require(m["experiment_id"]==c["experiment_id"] and m["seed"] is None,"manifest identity")
    return {"saved_rows_checked":len(states),"spend_events_checked":len(ledger),
            "link_events_checked":len(links),"max_discrete_reference_error":max_error,
            "battery_residual_uj":0,"verdict":"supported"}
