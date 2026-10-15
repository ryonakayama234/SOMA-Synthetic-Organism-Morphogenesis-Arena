"""Run pre-registered F003 contrasts A-F; store immutable evidence.
python -m experiments.F003.run_suite --output-dir /tmp/soma-f003
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from soma.f003 import Config,provenance,save_run

def base(label,*,attached=True,fa=1.,fb=0.,dt=.01,cut=None):
    return {"schema_version":"f003.v1","experiment_id":"F003-"+label,"seed":None,
      "dt_s":dt,"duration_s":10.,"drag_per_s":.2,
      "cells":[{"id":"A","mass_kg":1.,"initial_x_m":0.,"initial_v_m_s":0.,"force_n":fa},
               {"id":"B","mass_kg":1.,"initial_x_m":.5,"initial_v_m_s":0.,"force_n":fb}],
      "link":{"initially_attached":attached,"length_m":.5,"detach_time_s":cut}}

def checksum(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def require(value,why):
    if not value: raise AssertionError(why)

def read_evidence(path):
    """Use persisted evidence, not a second simulation hidden from the artifact."""
    import csv
    from soma.f003 import STATE_COLUMNS, EVENT_COLUMNS

    def read(name, columns, boolean, strings=()):
        with (path/name).open(encoding="utf-8", newline="") as stream:
            reader=csv.DictReader(stream)
            require(tuple(reader.fieldnames or ())==columns, name+": column contract")
            rows=[]
            for raw in reader:
                row={}
                for key,value in raw.items():
                    if key in strings:
                        row[key]=value
                    elif key in boolean:
                        require(value in ("True","False"), name+": invalid boolean")
                        row[key]=value=="True"
                    else:
                        row[key]=None if value=="" else float(value)
                        require(row[key] is None or math.isfinite(row[key]),name+": non-finite number")
                rows.append(row)
        return rows
    return (read("states.csv",STATE_COLUMNS,("attached",)),
            read("events.csv",EVENT_COLUMNS,("attached_before","attached_after"),("kind",)))


def validate_trace(cfg,rows,events):
    """Independent recurrence: never call simulate/step to generate the oracle."""
    require(len(rows)==cfg.steps+1,"sample count")
    a,b=cfg.cells
    mass=a.mass_kg+b.mass_kg
    x=[a.initial_x_m,b.initial_x_m]
    v=[a.initial_v_m_s,b.initial_v_m_s]
    forces=[a.force_n,b.force_n]
    masses=[a.mass_kg,b.mass_kg]
    attached=cfg.initially_attached
    max_x=max_v=max_com_x=max_com_v=0.
    max_gap=max_dv=max_force_sum=max_link_error=0.
    for k,row in enumerate(rows):
        if k:
            if attached:
                shared=v[0]+cfg.dt_s*(sum(forces)/mass-cfg.drag_per_s*v[0])
                v=[shared,shared]
            else:
                v=[vi+cfg.dt_s*(fi/mi-cfg.drag_per_s*vi)
                   for vi,fi,mi in zip(v,forces,masses)]
            x=[xi+cfg.dt_s*vi for xi,vi in zip(x,v)]
        if k==cfg.detach_step:
            attached=False
        require(row["time_s"]==k*cfg.dt_s,"time grid")
        require(row["attached"]==attached,"post-event link flag")
        expected_tb=b.mass_kg*sum(forces)/mass-b.force_n if attached else 0.
        for i,label in enumerate(("a","b")):
            max_x=max(max_x,abs(row[f"x_{label}_m"]-x[i]))
            max_v=max(max_v,abs(row[f"v_{label}_m_s"]-v[i]))
            require(row[f"force_{label}_n"]==forces[i],"external force log")
            expected_force=(-expected_tb,expected_tb)[i]
            max_link_error=max(max_link_error,abs(row[f"link_force_{label}_n"]-expected_force))
        max_com_x=max(max_com_x,abs(row["center_of_mass_m"]-sum(mi*xi for mi,xi in zip(masses,x))/mass))
        max_com_v=max(max_com_v,abs(row["center_of_mass_velocity_m_s"]-sum(mi*vi for mi,vi in zip(masses,v))/mass))
        max_force_sum=max(max_force_sum,abs(row["link_force_a_n"]+row["link_force_b_n"]))
        if attached:
            gap=row["x_b_m"]-row["x_a_m"]-cfg.length_m
            dv=row["v_b_m_s"]-row["v_a_m_s"]
            require(row["distance_constraint_error_m"]==gap,"distance error log")
            require(row["velocity_constraint_error_m_s"]==dv,"velocity error log")
            max_gap=max(max_gap,abs(gap)); max_dv=max(max_dv,abs(dv))
        else:
            require(row["distance_constraint_error_m"] is None and
                    row["velocity_constraint_error_m_s"] is None,"OFF constraint fields")
    require(max_x<=1e-9 and max_v<=1e-9,"discrete position/velocity oracle")
    require(max_com_x<=1e-9 and max_com_v<=1e-9,"center of mass oracle")
    require(max_gap<=1e-10 and max_dv<=1e-12,"rigid constraints")
    require(max_force_sum<=1e-12 and max_link_error<=1e-12,"internal forces")

    expected=[]
    if cfg.initially_attached:
        expected.append(("attach_initial",0,False,True,0.))
    if cfg.detach_step is not None:
        expected.append(("detach",cfg.detach_step,True,False,b.mass_kg*sum(forces)/mass-b.force_n))
    require(len(events)==len(expected),"event count")
    for ev,(kind,k,before,after,force) in zip(events,expected):
        require(ev["kind"]==kind and ev["time_s"]==k*cfg.dt_s,"event kind/time")
        require(ev["attached_before"]==before and ev["attached_after"]==after,"event flags")
        require(abs(ev["link_force_before_n"]-force)<=1e-12,"event internal force")
        for variable,unit in (("x_a","m"),("x_b","m"),("v_a","m_s"),("v_b","m_s")):
            require(ev[f"{variable}_before_{unit}"]==ev[f"{variable}_after_{unit}"]==rows[k][f"{variable}_{unit}"],
                    "event/CSV continuity")
    return {"discrete_oracle":True,"constraints":True,"internal_forces":True,
            "center_of_mass":True,"event_continuity":True,
            "max_oracle_x_error_m":max_x,"max_oracle_v_error_m_s":max_v,
            "max_com_x_error_m":max_com_x,"max_com_v_error_m_s":max_com_v,
            "max_distance_error_m":max_gap,"max_velocity_error_m_s":max_dv,
            "max_internal_force_sum_n":max_force_sum,"max_link_force_error_n":max_link_error}


def json_input(value):
    """Keep invalid inputs reconstructible in strict JSON (including NaN/inf)."""
    if isinstance(value,float) and not math.isfinite(value):
        return {"nonfinite_float":repr(value)}
    if isinstance(value,dict):
        return {key:json_input(item) for key,item in value.items()}
    if isinstance(value,list):
        return [json_input(item) for item in value]
    return value


def suite(out):
    source=Path(__file__).read_bytes()
    source_sha=hashlib.sha256(source).hexdigest()
    identity=provenance()  # capture before creating output, not once per run
    out.mkdir(parents=True,exist_ok=False)
    (out/"suite_source.py").write_bytes(source)
    settings={"A-free":base("A-free",attached=False),
      "B-pull":base("B-pull"),"C-both":base("C-both",fb=1.),
      "D-cut":base("D-cut",cut=5.),"E-minus":base("E-minus",fa=-1.),
      "F-dt005":base("F-dt005",dt=.005),
      "F-dt0025":base("F-dt0025",dt=.0025)}
    traces={}
    summaries={}
    for name,raw in settings.items():
        cfg=Config.from_dict(raw)
        manifest=save_run(cfg,out/name,provenance_data=identity,suite_sha256=source_sha)
        rows,events=read_evidence(out/name)
        gates=validate_trace(cfg,rows,events)
        for artifact,digest in manifest["artifacts"].items():
            require(checksum(out/name/artifact)==digest,"saved artifact checksum")
        traces[name]=rows
        summaries[name]={
          "final_x_a_m":rows[-1]["x_a_m"],"final_x_b_m":rows[-1]["x_b_m"],
          "final_v_a_m_s":rows[-1]["v_a_m_s"],"final_v_b_m_s":rows[-1]["v_b_m_s"],
          "max_distance_error_m":max(abs(r["distance_constraint_error_m"] or 0) for r in rows),
          "max_velocity_error_m_s":max(abs(r["velocity_constraint_error_m_s"] or 0) for r in rows),
          "max_internal_force_sum_n":max(abs(r["link_force_a_n"]+r["link_force_b_n"]) for r in rows),
          "events":len(events),"artifact_sha256":manifest["artifacts"],"gates":gates}
    for r in traces["A-free"]:
        require(r["x_b_m"]==.5 and r["v_b_m_s"]==0.,"A: free B moves")
    for r in traces["B-pull"]:
        require(abs(r["distance_constraint_error_m"])<=1e-10,"B: distance")
        require(abs(r["velocity_constraint_error_m_s"])<=1e-12,"B: common velocity")
        require(abs(r["link_force_b_n"]-.5)<=1e-12,"B: force")
    require(all(abs(r["link_force_b_n"])<=1e-12 for r in traces["C-both"]),"C: link load")
    require(not traces["D-cut"][500]["attached"] and
      traces["D-cut"][500]["link_force_b_n"]==0.,"D: post-event cut")
    for a,b in zip(traces["B-pull"],traces["E-minus"]):
        for cell,offset in (("a",0.),("b",.5)):
            require(abs(a[f"x_{cell}_m"]+b[f"x_{cell}_m"]-2*offset)<=1e-9,"E: reflection x")
            require(abs(a[f"v_{cell}_m_s"]+b[f"v_{cell}_m_s"])<=1e-9,"E: reflection v")
    exact_x=2.5*(10-(1-math.exp(-2))/.2)
    exact_v=2.5*(1-math.exp(-2))
    errs_x=[];errs_v=[]
    for key in ("B-pull","F-dt005","F-dt0025"):
        last=traces[key][-1]
        errs_x.append(abs(last["x_a_m"]-exact_x))
        errs_v.append(abs(last["v_a_m_s"]-exact_v))
    require(errs_x[0]>errs_x[1]>errs_x[2],"F: position convergence")
    require(errs_v[0]>errs_v[1]>errs_v[2],"F: velocity convergence")
    ratios=[errs_x[i]/errs_x[i+1] for i in range(2)]
    require(all(1.8<=v<=2.2 for v in ratios),"F: first order")
    summaries["theory"]={"continuous_x_m":exact_x,"continuous_v_m_s":exact_v,
      "position_errors_m":errs_x,"velocity_errors_m_s":errs_v,"position_error_ratios":ratios}
    changes=[("zero_mass",("cells",0,"mass_kg"),0),
      ("bad_gap",("cells",1,"initial_x_m"),.8),
      ("bad_velocity",("cells",1,"initial_v_m_s"),.3),
      ("nonfinite_force",("cells",0,"force_n"),float("nan")),
      ("offgrid_cut",("link","detach_time_s"),5.005),
      ("final_cut",("link","detach_time_s"),10.),
      ("offgrid_dt",("dt_s",),.03),
      ("nonboolean_link",("link","initially_attached"),1),
      ("overflow_mass",("cells",0,"mass_kg"),1.7976931348623157e308),
      ("nonfinite_drag",("drag_per_s",),float("inf"))]
    rejections=[]
    for label,path,value in changes:
        raw=copy.deepcopy(settings["B-pull"])
        target=raw
        for part in path[:-1]: target=target[part]
        target[path[-1]]=value
        if label=="overflow_mass":
            raw["cells"][1]["mass_kg"]=value
        invalid_dir=out/("REJECT-"+label)
        try: save_run(Config.from_dict(raw),invalid_dir,
                      provenance_data=identity,suite_sha256=source_sha)
        except ValueError as exc: rejected=True; reason=str(exc)
        else: rejected=False; reason="not rejected"
        valid=rejected and not invalid_dir.exists()
        rejections.append({"case_id":label,"path":list(path),"value":repr(value),
          "input":json_input(raw),"expected_error":"ValueError","actual_error":"ValueError" if rejected else None,
          "reason":reason,"rejected_before_run":not invalid_dir.exists(),"pass":valid})
        require(valid,"F: invalid input accepted "+label)
    (out/"rejections.json").write_text(json.dumps(rejections,indent=2,ensure_ascii=True,allow_nan=False)+"\n",encoding="utf-8")
    cfg=Config.from_dict(settings["B-pull"])
    save_run(cfg,out/"B-pull-replay",provenance_data=identity,suite_sha256=source_sha)
    names=("config.json","states.csv","events.csv","motion.svg","manifest.json")
    replay_rows,replay_events=read_evidence(out/"B-pull-replay")
    validate_trace(cfg,replay_rows,replay_events)
    same=all((out/"B-pull"/f).read_bytes()==(out/"B-pull-replay"/f).read_bytes() for f in names)
    require(same,"F003 replay is not byte-identical")
    result={"schema_version":"f003.comparison.v1",
      "status":"software_checks_passed",
      "scope":"Ideal 1D model; no hardware, adaptive selection or emergence",
      "provenance":identity,"suite_sha256":source_sha,"suite_source_artifact":"suite_source.py",
      "cases":summaries,"rejections":rejections,
      "rejections_sha256":checksum(out/"rejections.json"),
      "gate_checks":{"A_to_F_saved_evidence":True,"E_both_cells":True,
                     "F_convergence":True,"invalid_inputs_rejected":True},
      "replay":{"same_config":True,"byte_identical":same,
                "matching_sha256":{n:checksum(out/"B-pull"/n) for n in names}}}
    (out/"comparison.json").write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf-8")
    return result

def verify_replay(first,second):
    paths=sorted(p.relative_to(first) for p in first.rglob("*") if p.is_file())
    require(paths==sorted(p.relative_to(second) for p in second.rglob("*") if p.is_file()),
            "full suite replay file list")
    for path in paths:
        require((first/path).read_bytes()==(second/path).read_bytes(),"full suite replay: "+str(path))
    proof={"byte_identical":True,"includes_comparison_json":True,
           "matching_sha256":{str(path):checksum(first/path) for path in paths}}
    (first/"full_suite_replay.json").write_text(json.dumps(proof,indent=2)+"\n",encoding="utf-8")
    return proof

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--replay-output-dir",type=Path)
    args=parser.parse_args()
    result=suite(args.output_dir)
    if args.replay_output_dir is not None:
        suite(args.replay_output_dir)
        verify_replay(args.output_dir,args.replay_output_dir)
    print(json.dumps({"status":result["status"],"runs":len(result["cases"])-1,
      "rejections":len(result["rejections"]),
      "replay_identical":result["replay"]["byte_identical"],
      "full_suite_replay_identical":True if args.replay_output_dir is not None else None},indent=2))
if __name__=="__main__": main()
