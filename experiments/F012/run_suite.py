"""Frozen 48 F012 cases, independently audited raw evidence and replay."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from soma.f012 import CASES,BUDGETS_UJ,DTS,Config,COLUMNS,simulate,measurements
from experiments.F012.verify import verify_suite,SOURCES


def write_json(path,obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(root,checkout):
    root.mkdir()
    outcomes={}
    for case in CASES:
        for budget in BUDGETS_UJ:
            for h in DTS:
                config=Config(case,budget,h)
                label="%s__%suj__dt%s"%(case,budget,str(h))
                p=root/label
                p.mkdir()
                write_json(p/"config.json",config.as_dict())
                rows=simulate(config)
                with (p/"states.csv").open("w",newline="",encoding="utf-8") as f:
                    wr=csv.DictWriter(f,fieldnames=COLUMNS,lineterminator="\n")
                    wr.writeheader()
                    wr.writerows(rows)
                outcomes[label]=measurements(rows)
    write_json(root/"comparison.json",{
        "schema":"f012.comparison.v1",
        "baseline":"F011 fixed model; F012 ideal energy gate",
        "outcomes":outcomes})
    write_json(root/"manifest.json",{
        "schema":"f012.evidence.v1",
        "files":{str(p.relative_to(root)):sha(p) for p in sorted(root.rglob("*")) if p.is_file()},
        "source_hashes":{path:sha(checkout/path) for path in SOURCES}})
    verify_suite(root,checkout)


def run_pair(first,second,checkout):
    first,second=first.resolve(),second.resolve()
    if first==second or first in second.parents or second in first.parents:
        raise ValueError("overlapping destinations")
    if first.exists() or second.exists():
        raise ValueError("evidence destination already exists")
    first.parent.mkdir(parents=True,exist_ok=True)
    second.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="f012-",dir=first.parent) as a:
        with tempfile.TemporaryDirectory(prefix="f012-",dir=second.parent) as b:
            x,y=Path(a)/"study",Path(b)/"study"
            build(x,checkout)
            build(y,checkout)
            aa={str(p.relative_to(x)):sha(p) for p in x.rglob("*") if p.is_file()}
            bb={str(p.relative_to(y)):sha(p) for p in y.rglob("*") if p.is_file()}
            if aa!=bb: raise ValueError("two research outputs do not byte match")
            shutil.copytree(x,first)
            shutil.copytree(y,second)
            return len(aa)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",required=True,type=Path)
    parser.add_argument("--replay-output-dir",required=True,type=Path)
    args=parser.parse_args()
    checkout=Path(__file__).resolve().parents[2]
    n=run_pair(args.output_dir,args.replay_output_dir,checkout)
    checked=verify_suite(args.output_dir,checkout)
    print("F012 48/48 runs: independent saved-data oracle; %d files byte-matched x2"%n)
    for budget in BUDGETS_UJ:
        for h in DTS:
            item=checked["C-directional__%suj__dt%s"%(budget,str(h))]
            efficiency=(abs(item["center_final_m"])/(item["spent_uj"]/1e6)
                        if item["spent_uj"] else None)
            print("GRID C budget=%suj dt=%s final=%.10fm spent=%suj positive=%.8fJ accepted=%s rejected=%s abs_cm_per_charged_j=%s"%
                  (budget,h,item["center_final_m"],item["spent_uj"],
                   item["positive_work_j"],item["accepted_steps"],
                   item["rejected_steps"],str(efficiency) if efficiency is not None else "undefined"))
        fine=checked["C-directional__%suj__dt0.0025"%budget]
        medium=checked["C-directional__%suj__dt0.005"%budget]
        last,prior=fine["last_period_m"],fine["penultimate_period_m"]
        period_ok=(last*prior>0 and min(abs(last),abs(prior))>.001
                   and abs(abs(last)-abs(prior))<=.5*max(abs(last),abs(prior))
                   and abs(fine["stroke_return_m"])<=.01)
        convergence=abs(fine["center_final_m"]-medium["center_final_m"])<=max(.002,.1*abs(fine["center_final_m"]))
        print("OBSERVED C budget=%s uj, final_cm=%.10f m, last=%.8f m, prior=%.8f m, stroke_return=%.8f m, spent=%s uj, positive=%.8f J, accepted=%s, rejected=%s, persistence=%s, dt_convergence=%s"%
              (budget,fine["center_final_m"],last,prior,fine["stroke_return_m"],
               fine["spent_uj"],fine["positive_work_j"],fine["accepted_steps"],
               fine["rejected_steps"],period_ok,convergence))


if __name__=="__main__":main()
