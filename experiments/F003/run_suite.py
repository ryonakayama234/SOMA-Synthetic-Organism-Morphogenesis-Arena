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
from soma.f003 import Config,provenance,save_run,simulate

def base(label,*,attached=True,fa=1.,fb=0.,dt=.01,cut=None):
    return {"schema_version":"f003.v1","experiment_id":"F003-"+label,"seed":None,
      "dt_s":dt,"duration_s":10.,"drag_per_s":.2,
      "cells":[{"id":"A","mass_kg":1.,"initial_x_m":0.,"initial_v_m_s":0.,"force_n":fa},
               {"id":"B","mass_kg":1.,"initial_x_m":.5,"initial_v_m_s":0.,"force_n":fb}],
      "link":{"initially_attached":attached,"length_m":.5,"detach_time_s":cut}}

def checksum(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def require(value,why):
    if not value: raise AssertionError(why)

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
        rows,events=simulate(cfg)
        traces[name]=rows
        manifest=save_run(cfg,out/name,provenance_data=identity,suite_sha256=source_sha)
        summaries[name]={
          "final_x_a_m":rows[-1]["x_a_m"],"final_x_b_m":rows[-1]["x_b_m"],
          "final_v_a_m_s":rows[-1]["v_a_m_s"],"final_v_b_m_s":rows[-1]["v_b_m_s"],
          "max_distance_error_m":max(abs(r["distance_constraint_error_m"] or 0) for r in rows),
          "max_velocity_error_m_s":max(abs(r["velocity_constraint_error_m_s"] or 0) for r in rows),
          "max_internal_force_sum_n":max(abs(r["link_force_a_n"]+r["link_force_b_n"]) for r in rows),
          "events":len(events),"artifact_sha256":manifest["artifacts"]}
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
        require(abs(a["x_a_m"]+b["x_a_m"])<=1e-9,"E: reflection x")
        require(abs(a["v_a_m_s"]+b["v_a_m_s"])<=1e-9,"E: reflection v")
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
      ("nonboolean_link",("link","initially_attached"),1)]
    rejections=[]
    for label,path,value in changes:
        raw=copy.deepcopy(settings["B-pull"])
        target=raw
        for part in path[:-1]: target=target[part]
        target[path[-1]]=value
        invalid_dir=out/("REJECT-"+label)
        try: save_run(Config.from_dict(raw),invalid_dir,
                      provenance_data=identity,suite_sha256=source_sha)
        except ValueError as exc: rejected=True; reason=str(exc)
        else: rejected=False; reason="not rejected"
        valid=rejected and not invalid_dir.exists()
        rejections.append({"case_id":label,"path":list(path),"value":repr(value),
          "expected_error":"ValueError","actual_error":"ValueError" if rejected else None,
          "reason":reason,"rejected_before_run":not invalid_dir.exists(),"pass":valid})
        require(valid,"F: invalid input accepted "+label)
    (out/"rejections.json").write_text(json.dumps(rejections,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    cfg=Config.from_dict(settings["B-pull"])
    save_run(cfg,out/"B-pull-replay",provenance_data=identity,suite_sha256=source_sha)
    names=("config.json","states.csv","events.csv","motion.svg","manifest.json")
    same=all((out/"B-pull"/f).read_bytes()==(out/"B-pull-replay"/f).read_bytes() for f in names)
    require(same,"F003 replay is not byte-identical")
    result={"schema_version":"f003.comparison.v1",
      "status":"software_checks_passed",
      "scope":"Ideal 1D model; no hardware, adaptive selection or emergence",
      "provenance":identity,"suite_sha256":source_sha,"suite_source_artifact":"suite_source.py",
      "cases":summaries,"rejections":rejections,
      "replay":{"same_config":True,"byte_identical":same,
                "matching_sha256":{n:checksum(out/"B-pull"/n) for n in names}}}
    (out/"comparison.json").write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf-8")
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    result=suite(args.output_dir)
    print(json.dumps({"status":result["status"],"runs":len(result["cases"])-1,
      "rejections":len(result["rejections"]),
      "replay_identical":result["replay"]["byte_identical"]},indent=2))
if __name__=="__main__": main()
