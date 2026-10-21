"""F017 frozen 23,296-episode ideal-F007 source-bound producer.

Scientifically limited: predefined B sensor, externally imposed B mapping, 1D
terminal task. NEVER expose investigator labels to Receiver.
"""
from __future__ import annotations
import argparse
import copy
from dataclasses import asdict
import gzip
import hashlib
import json
from pathlib import Path
import random
import subprocess

from soma.f002 import Cell, Event, apply_event, new_ledger
from soma.f007 import Config, simulate
from soma.f017 import RawPeerSymbol, Receiver

PHASES = (("train",64),("holdout",32),("probe",16),("adapt",64),("final",32))
ARMS = ("I","N","K","S","L","F","R")
SOURCE_FILES = ("soma/f002.py","soma/f007.py","soma/f016.py","soma/f017.py",
                "experiments/F017/run_suite.py","experiments/F017/verify.py","experiments/F017/attack_test.py",
                "tests/test_f017.py","tests/test_f017_experiment.py",".github/workflows/f017.yml",
                "topics/F017-signal-action-learning/SPEC.md",
                "experiments/F017/PLAN.md","findings/F017-validation.md",
                "docs/ARCHITECTURE.md","docs/DATA_CONTRACTS.md")

def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def digest(text: str) -> bytes:
    return hashlib.sha256(text.encode("ascii")).digest()

def schedule(seed: int, phase: str, length: int, kind: str) -> tuple[int,...]:
    ranked = sorted(range(length), key=lambda i: (digest(f"f017.v1|{kind}|{seed}|{phase}|{i}"),i))
    bits = [0]*length
    for i in ranked[:length//2]:
        bits[i] = 1
    return tuple(bits)

def rng_seed(label: str) -> int:
    return int.from_bytes(digest("f017.v1|"+label),"big")

def physical_config(key: str, action: float) -> Config:
    return Config.from_dict({
        "schema_version":"f007.v1","experiment_id":key,"seed":None,
        "dt_s":.25,"duration_s":1.0,"drag_per_s":0.0,
        "cells":[
            {"id":"A","mass_kg":1.0,"initial_x_m":0.0,
             "initial_v_m_s":0.0,"external_force_n":0.0,
             "capacity_uj":20_000_000,"initial_balance_uj":10_000_000},
            {"id":"B","mass_kg":1.0,"initial_x_m":0.1,
             "initial_v_m_s":0.0,"external_force_n":0.0,
             "capacity_uj":20_000_000,"initial_balance_uj":10_000_000}],
        "motor_force_n":action,
        "link":{"initially_attached":True,"length_m":0.1,"detach_time_s":None},
    })

def canonical(obj) -> bytes:
    return (json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode()

def provenance() -> dict:
    root=Path(__file__).resolve().parents[2]
    sha=subprocess.run(["git","-C",str(root),"rev-parse","HEAD"],
                       check=True,capture_output=True,text=True).stdout.strip()
    dirty=subprocess.run(["git","-C",str(root),"status","--porcelain","--untracked-files=all"],
                         check=True,capture_output=True,text=True).stdout.strip()
    return {"git_commit":sha,"git_dirty":bool(dirty),
            "source_hashes":{p:hash_bytes((root/p).read_bytes()) for p in SOURCE_FILES}}

def causal_probe(receiver: Receiver, seed: int, encoding: int, arm: str, phase: str) -> dict:
    """Off-world matched common uniform/tie draws; no A/world state mutation."""
    q=receiver.snapshot()["q"]
    rng=random.Random(rng_seed(f"causal|{seed}|{encoding}|{arm}|{phase}"))
    pos=[0,0]
    for _ in range(256):
        explore=rng.random()<receiver.epsilon
        tie=rng.randrange(2)
        for symbol in (0,1):
            scores=q[str(symbol)]
            ix=tie if explore or scores[0]==scores[1] else (0 if scores[0]>scores[1] else 1)
            pos[symbol]+=int(ix==1)
    return {"checkpoint":phase,"plus_counts":pos,"D":(pos[1]-pos[0])/256,
            "snapshot":q,"draws":256}

def episode(arm: str, seed: int, encoding: int, phase: str, i: int,
            target_right: int, scrambled: int, receiver: Receiver) -> dict:
    if arm=="R":
        receiver=Receiver(exploration_seed=rng_seed(f"reset|{seed}|{encoding}|{phase}|{i}"))
    inverted=int(phase in ("probe","adapt","final"))
    symbol=(None if arm=="N" else
            (1 if arm=="K" else scrambled if arm=="S"
             else target_right ^ encoding ^ inverted))
    packet=None if symbol is None else RawPeerSymbol("B",0,0.0,int(symbol))
    before=receiver.snapshot()
    action=receiver.observe(packet)
    key=f"F017-{arm}-{seed}-{encoding}-{phase}-{i}"
    rows,motor_events,link_events,f007ledger=simulate(physical_config(key,action))
    side=new_ledger([Cell("A",20_000_000,10_000_000),
                     Cell("B",20_000_000,10_000_000)])
    events=[]
    fee=0 if symbol is None else 50_000
    if fee:
        side,en=apply_event(side,Event(kind="spend",amount_uj=fee,source_id="B"))
        events.append(asdict(en))
    motor=0
    for row in rows[1:]:
        amount=row["spent_a_uj"]
        if amount:
            side,en=apply_event(side,Event(kind="spend",amount_uj=amount,source_id="A"))
            events.append(asdict(en))
            motor+=amount
    if motor != 1_000_000 or f007ledger.cell("A").balance_uj != side.cell("A").balance_uj:
        raise ValueError("F007/F002 motor ledger mismatch")
    target=.625 if target_right else -.625
    reached=abs(rows[-1]["x_a_m"]-target)<=1e-12
    acquired=3_000_000 if reached else 0
    if acquired:
        side,en=apply_event(side,Event(kind="acquire",amount_uj=acquired,target_id="A"))
        events.append(asdict(en))
    if side.residual_uj!=0:
        raise ValueError("F002 residual")
    if phase in ("train","adapt") and arm in ("I","N","K","S","R"):
        receiver.learn(own_action_n=action,own_acquired_uj=acquired,own_motor_spent_uj=motor)
    else:
        receiver.end_without_learning()
    after=receiver.snapshot()
    return {"schema":"f017.episode.v1","arm":arm,"seed":seed,"encoding":encoding,
            "phase":phase,"index":i,"target_right":target_right,"target_x_m":target,
            "packet":None if packet is None else asdict(packet),"action_n":action,
            "Q_before":before,"Q_after":after,"states":rows,
            "motor_events":motor_events,"link_events":link_events,
            "f002_events":events,"motor_spent_uj":motor,
            "communication_spent_uj":fee,"acquired_uj":acquired,
            "reached":reached,"net_uj":acquired-motor-fee,
            "balance_a_uj":side.cell("A").balance_uj,
            "balance_b_uj":side.cell("B").balance_uj,
            "ledger_residual_uj":side.residual_uj}

def suite(root: Path) -> dict:
    root=Path(root)
    if root.exists():
        raise FileExistsError("F017 evidence root exists")
    src=provenance()
    root.mkdir(parents=True)
    summary={a:{p:{"count":0,"hits":0,"net_sum_uj":0} for p,_ in PHASES} for a in ARMS}
    clusters=[]
    causal=[]
    allocations=[]
    with (root/"episodes.jsonl.gz").open("wb") as raw:
        with gzip.GzipFile(filename="",fileobj=raw,mode="wb",mtime=0,compresslevel=6) as gz:
            for seed in range(8):
                world={p:schedule(seed,p,n,"world") for p,n in PHASES}
                scramble={p:schedule(seed,p,n,"scramble") for p,n in PHASES}
                allocations.append({"seed":seed,"world":world,"scramble":scramble})
                for encoding in (0,1):
                    for arm in ARMS:
                        learner=Receiver(exploration_seed=rng_seed(f"policy|{seed}|{encoding}|{arm}"))
                        for phase,n in PHASES:
                            for i in range(n):
                                rec=episode(arm,seed,encoding,phase,i,world[phase][i],scramble[phase][i],learner)
                                gz.write(canonical(rec))
                                d=summary[arm][phase]
                                d["count"]+=1
                                d["hits"]+=int(rec["reached"])
                                d["net_sum_uj"]+=rec["net_uj"]
                                if phase in ("holdout","final"):
                                    clusters.append({"arm":arm,"seed":seed,"encoding":encoding,
                                                     "phase":phase,"net_uj":rec["net_uj"],
                                                     "hit":int(rec["reached"])})
                            if phase in ("holdout","final"):
                                causal.append({"arm":arm,"seed":seed,"encoding":encoding,
                                               **causal_probe(learner,seed,encoding,arm,phase)})
    for arm in ARMS:
        for phase,_ in PHASES:
            d=summary[arm][phase]
            d["hit_rate"]=d["hits"]/d["count"]
            d["mean_net_j"]=d["net_sum_uj"]/d["count"]/1_000_000
    report={"schema":"f017.suite.v1","design":"F017-2026-10-22-pre-run-freeze",
            "episode_count":sum(summary[a][p]["count"] for a in ARMS for p,_ in PHASES),
            "summary":summary,"causal_probes":causal,"clusters":clusters,
            "allocation_sha256":hash_bytes(canonical(allocations)),
            "claims_excluded":["spontaneous_sender_code","body_morphogenesis",
                               "physical_radio","general_meaning","human_peer_review"]}
    (root/"summary.json").write_bytes(canonical(report))
    (root/"allocation.json").write_bytes(canonical(allocations))
    names=("episodes.jsonl.gz","summary.json","allocation.json")
    manifest={"schema":"f017.evidence.v1","source":src,
              "artifacts":{n:hash_bytes((root/n).read_bytes()) for n in names}}
    (root/"manifest.json").write_bytes(canonical(manifest))
    from experiments.F017.verify import verify_suite
    verify_suite(root)
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-root",required=True,type=Path)
    args=p.parse_args()
    result=suite(args.output_root)
    print(json.dumps({"episodes":result["episode_count"],
                      "phase_summary":{a:{p:{"hit_rate":v["hit_rate"],
                          "mean_net_j":v["mean_net_j"]} for p,v in ph.items()}
                          for a,ph in result["summary"].items()}},sort_keys=True))

if __name__=="__main__":
    main()
