"""F010: fixed A-E independent F007 trials, immutable saved evidence + replay.

Researcher-only adapter sees F007 world; soma.f010.estimate sees solely
ordered tuples of adopted F008 LocalObservation. No online active controller.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from soma.f007 import Config, STATE_COLUMNS, provenance, publish_dir, save_run
from soma.f008 import COLUMNS, analyze, project_local
from soma.f010 import estimate
from experiments.F007.run_suite import baseline
from experiments.F007.verify import read_csv
from experiments.F010.verify import verify_suite

GROUPS = ("A-linked","B-constant","C-adaptive","D-free","E-empty")
FORCE_TAGS = ((2.0,"u2"),(1.0,"u1"),(.5,"u05"))
SOURCE_FILES = (
    "soma/f010.py", "experiments/F010/run_suite.py",
    "experiments/F010/verify.py", "tests/test_f010.py",
    ".github/workflows/f010.yml",
    "topics/F010-local-identifiability/SPEC.md",
    "experiments/F010/PLAN.md", "experiments/F010/README.md",
    "findings/F010-validation.md", "docs/ARCHITECTURE.md",
    "docs/DATA_CONTRACTS.md", "README.md", "AGENTS.md",
    "library/INDEX.md",
)


def cases() -> tuple[str,...]:
    return GROUPS


def origin_snapshot() -> dict:
    root=Path(__file__).resolve().parents[2]
    return {"f007": provenance(), "f010_source_hashes": {
        p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in SOURCE_FILES
    }}


def configuration(group: str, force: float) -> dict:
    if group not in GROUPS or force not in (2.,1.,.5) or type(force) not in (float,int):
        raise ValueError("non-preregistered case/force")
    cfg=baseline("B-linked")
    tag={2.:"u2",1.:"u1",.5:"u05"}[force]
    cfg["experiment_id"]="F010-"+group+"-"+tag
    cfg["motor_force_n"]=force
    if group!="A-linked":
        cfg["link"]["initially_attached"]=False
    if group=="B-constant":
        cfg["cells"][0]["external_force_n"]=-1.
    elif group=="C-adaptive":
        cfg["cells"][0]["external_force_n"]=-force/2.
    elif group=="E-empty":
        cfg["cells"][0]["initial_balance_uj"]=0
    return cfg


def make_run(location: Path, group: str, force: float, origin: dict):
    src=location/"F007"
    location.mkdir(parents=True)
    save_run(Config.from_dict(configuration(group,force)),src,identity=origin["f007"])
    raw=read_csv(src/"states.csv",STATE_COLUMNS,
                 strings=("decision_reason",),flags=("attached",),
                 integers=("step_index","spent_a_uj","balance_a_uj",
                           "balance_b_uj","ledger_event_index"))
    local=analyze(raw)
    with (location/"local.csv").open("w",newline="",encoding="utf-8") as fp:
        writer=csv.DictWriter(fp,fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(local)
    return tuple(project_local(previous,current)
                 for previous,current in zip(raw,raw[1:]))


def _json(path: Path, payload: dict):
    path.write_text(json.dumps(payload,sort_keys=True,indent=2,allow_nan=False)+"\n",
                    encoding="utf-8")


def build(stage: Path, origin: dict) -> dict:
    comparison={}
    for group in GROUPS:
        trials=[]
        for force,tag in FORCE_TAGS:
            trials.append(make_run(stage/group/tag,group,force,origin))
        comparison[group]=estimate(tuple(trials))
    _json(stage/"comparison.json",{
        "schema_version":"f010.evidence.v1",
        "science_status":"software_model_candidate_not_adopted",
        "question":"A-local force-response identifiability; no topology identification",
        "fixed_cases":list(GROUPS),
        "force_levels_n":[2.,1.,.5],
        "signatures":comparison,
        "counterexample":"A-linked and C-adaptive have identical A-local time/battery histories",
        "researcher_truth_only":True,
    })
    files={p.relative_to(stage).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
           for p in sorted(stage.rglob("*")) if p.is_file()}
    _json(stage/"manifest.json",{
        "schema_version":"f010.evidence.v1",
        "origin":origin, "cases":list(GROUPS),
        "artifacts":files,
    })
    return verify_suite(stage,origin)


def _check_pair(a: Path, b: Path):
    a,b=a.resolve(),b.resolve()
    if a==b or a in b.parents or b in a.parents:
        raise ValueError("same or nested output destinations")
    if a.exists() or b.exists():
        raise FileExistsError("existing evidence destination")


def suite(destination: Path, replay_destination: Path, *, origin: dict|None=None) -> dict:
    a,b=Path(destination),Path(replay_destination)
    _check_pair(a,b)
    a.parent.mkdir(parents=True,exist_ok=True)
    b.parent.mkdir(parents=True,exist_ok=True)
    ident=origin_snapshot() if origin is None else origin
    stagea=Path(tempfile.mkdtemp(prefix=".f010-A-",dir=a.parent))
    stageb=Path(tempfile.mkdtemp(prefix=".f010-B-",dir=b.parent))
    try:
        result=build(stagea,ident)
        verify_suite(stageb,ident) if False else None
        build(stageb,ident)
        first={p.relative_to(stagea).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
               for p in stagea.rglob("*") if p.is_file()}
        second={p.relative_to(stageb).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                for p in stageb.rglob("*") if p.is_file()}
        if first!=second:
            raise AssertionError("different bytes in identical run/replay")
        _check_pair(a,b)
        publish_dir(stagea,a)
        publish_dir(stageb,b)
        return {**result,"byte_replay":True,"replay_files":len(first)}
    finally:
        for stage in (stagea,stageb):
            if stage.exists():
                shutil.rmtree(stage)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",required=True)
    p.add_argument("--replay-output-dir",required=True)
    args=p.parse_args()
    result=suite(Path(args.output_dir),Path(args.replay_output_dir))
    print(json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
