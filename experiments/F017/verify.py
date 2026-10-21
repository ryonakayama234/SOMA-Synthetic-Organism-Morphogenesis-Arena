"""F017 independent SAVED-EVIDENCE validator. Does not import F017 learner or F007.

Same-author dual implementation is not external human peer review.
Verifies complete raw ideal 1D dynamics, F002 accounting, deterministic experiment
allocation, Q learning updates, action RNG, conditional rewards and outcomes.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import random
import subprocess

PHASES=(("train",64),("holdout",32),("probe",16),("adapt",64),("final",32))
ARMS=("I","N","K","S","L","F","R")
SOURCE_FILES={"soma/f002.py","soma/f007.py","soma/f016.py","soma/f017.py",
              "experiments/F017/run_suite.py","experiments/F017/verify.py",
              "experiments/F017/analyze.py","tests/test_f017.py",
              ".github/workflows/f017.yml","topics/F017-signal-action-learning/SPEC.md",
              "experiments/F017/PLAN.md","findings/F017-validation.md",
              "docs/ARCHITECTURE.md","docs/DATA_CONTRACTS.md"}

def require(ok, reason):
    if not ok:
        raise ValueError("F017 independent saved-world rejection: "+reason)

def close(a,b,why):
    require(type(a) in (float,int) and math.isfinite(a) and abs(a-b)<1e-12,why)

def canonical(x):
    return (json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode()

def digest(data):
    return hashlib.sha256(data).hexdigest()

def sha_source(key):
    return hashlib.sha256(key.encode("ascii")).digest()

def permutation(seed, phase, n, kind):
    ranking=sorted(range(n),key=lambda i:(sha_source(f"f017.v1|{kind}|{seed}|{phase}|{i}"),i))
    out=[0]*n
    for i in ranking[:n//2]:
        out[i]=1
    return out

def rng_seed(key):
    return int.from_bytes(sha_source(f"f017.v1|{key}"),"big")

def init_q():
    return {"none":[0.0,0.0],"0":[0.0,0.0],"1":[0.0,0.0]}

def snapshot(q,updates):
    return {"schema":"f017.receiver.snapshot.v1","updates":updates,
            "q":{k:list(v) for k,v in q.items()}}

def same_q(actual, expected, why):
    require(set(actual)==set(expected) and actual["schema"]==expected["schema"],why)
    require(actual["updates"]==expected["updates"],why+" updates")
    require(set(actual["q"])==set(expected["q"]),why+" contexts")
    for k in ("none","0","1"):
        require(len(actual["q"][k])==2,why+" q dimensionality")
        for i in (0,1):
            close(actual["q"][k][i],expected["q"][k][i],why+" q")

def verify_world(row, arm, seed, encoding, phase, i, bit, scrambled, q, updates, rng):
    require(row["schema"]=="f017.episode.v1","schema")
    for key,expected in {"arm":arm,"seed":seed,"encoding":encoding,
                         "phase":phase,"index":i,"target_right":bit}.items():
        require(type(row[key])==type(expected) and row[key]==expected,key)
    target=.625 if bit else -.625
    close(row["target_x_m"],target,"target position")
    sym=None if arm=="N" else (1 if arm=="K" else scrambled if arm=="S"
                              else bit ^ encoding ^ int(phase in ("probe","adapt","final")))
    p=row["packet"]
    require(p is None if sym is None else
            p=={"source_id":"B","step_index":0,"time_s":0.0,"symbol":sym},
            "forged packet")
    label="none" if sym is None else str(sym)
    same_q(row["Q_before"],snapshot(q,updates),"pre-action Q")
    explore=rng.random()<.125
    scores=q[label]
    if explore or scores[0]==scores[1]:
        choice=rng.randrange(2)
    else:
        choice=0 if scores[0]>scores[1] else 1
    force=(-2.0,2.0)[choice]
    close(row["action_n"],force,"A learned action / RNG divergence")
    sign=1 if force>0 else -1
    states=row["states"]
    require(type(states) is list and len(states)==5,"F007 state length")
    fees=0 if sym is None else 50_000
    spend=[62_500,187_500,312_500,437_500]
    for k,s in enumerate(states):
        require(s["step_index"]==k and s["attached"] is True,"state index/connection")
        close(s["time_s"],k*.25,"F007 time")
        close(s["x_a_m"],sign*k*(k+1)/32,"A position")
        close(s["x_b_m"],.1+sign*k*(k+1)/32,"B position")
        close(s["v_a_m_s"],sign*k/4,"A velocity")
        close(s["v_b_m_s"],sign*k/4,"B velocity")
        close(s["motor_command_n"],force,"command")
        close(s["motor_applied_n"],0 if k==0 else force,"applied")
        close(s["link_force_b_n"],0 if k==0 else sign,"link force")
        require(s["spent_a_uj"]==(spend[k-1] if k else 0),"F007 cost")
        require(s["balance_a_uj"]==10_000_000-sum(spend[:k]),"F007 balance")
        require(s["balance_b_uj"]==10_000_000,"F007 B battery")
        if k:
            close(s["motor_positive_work_j"],spend[k-1]/1e6,"work")
            close(s["mechanical_residual_j"],0,"mechanical residual")
    require(len(row["link_events"])==1 and
            row["link_events"][0]["kind"]=="attach_initial","link initialization")
    motor=row["motor_events"]
    require(len(motor)==4 and sum(z["amount_uj"] for z in motor)==1_000_000,
            "motor F007 events")
    reached=sign==(1 if bit else -1)
    acquire=3_000_000 if reached else 0
    require(type(row["reached"]) is bool and row["reached"]==reached,
            "research success truth")
    for key,expected in (("acquired_uj",acquire),
                         ("motor_spent_uj",1_000_000),
                         ("communication_spent_uj",fees),
                         ("net_uj",acquire-1_000_000-fees),
                         ("balance_a_uj",9_000_000+acquire),
                         ("balance_b_uj",10_000_000-fees),
                         ("ledger_residual_uj",0)):
        require(type(row[key]) is int and row[key]==expected,
                "F002 / energy truth "+key)
    exp_events=(([("spend","B",50_000)] if fees else [])+
                [("spend","A",x) for x in spend]+
                ([("acquire","A",3_000_000)] if reached else []))
    evs=row["f002_events"]
    require(len(evs)==len(exp_events),"F002 event length")
    for j,(evt,(kind,who,amount)) in enumerate(zip(evs,exp_events),1):
        require(evt["event_index"]==j and evt["kind"]==kind
                and evt["amount_uj"]==amount and evt["residual_uj"]==0,
                "F002 event sequence")
        require(evt["source_id"]==who if kind=="spend" else
                evt["target_id"]==who,"F002 ledger identity")
    if phase in ("train","adapt") and arm in ("I","N","K","S","R"):
        old=q[label][choice]
        q[label][choice]=old+.25*((acquire-1_000_000)/1_000_000-old)
        updates+=1
    same_q(row["Q_after"],snapshot(q,updates),"post-feedback Q")
    return updates

def calc_probe(q, arm, seed, encoding, phase):
    rand=random.Random(rng_seed(f"causal|{seed}|{encoding}|{arm}|{phase}"))
    count=[0,0]
    for _ in range(256):
        explore=rand.random()<.125
        tie=rand.randrange(2)
        for symbol in (0,1):
            x=q[str(symbol)]
            a=tie if explore or x[0]==x[1] else (0 if x[0]>x[1] else 1)
            count[symbol]+=int(a==1)
    return count

def verify_suite(root: Path) -> dict:
    root=Path(root)
    require(root.is_dir(),"missing evidence")
    manifest=json.loads((root/"manifest.json").read_text())
    require(manifest["schema"]=="f017.evidence.v1","manifest schema")
    src=manifest["source"]
    project=Path(__file__).resolve().parents[2]
    head=subprocess.run(["git","-C",str(project),"rev-parse","HEAD"],capture_output=True,
                        check=True,text=True).stdout.strip()
    require(src["git_commit"]==head and not src["git_dirty"],"wrong or dirty source")
    require(set(src["source_hashes"])==SOURCE_FILES,"source file inventory")
    for p,sha in src["source_hashes"].items():
        require(digest((project/p).read_bytes())==sha,"source altered "+p)
    require(set(manifest["artifacts"])=={"episodes.jsonl.gz","summary.json","allocation.json"},
            "artifact allowlist")
    for name,h in manifest["artifacts"].items():
        require(digest((root/name).read_bytes())==h,"artifact digest "+name)
    summary=json.loads((root/"summary.json").read_text())
    alloc=json.loads((root/"allocation.json").read_text())
    require(summary["schema"]=="f017.suite.v1" and len(alloc)==8,"suite format")
    require(digest(canonical(alloc))==summary["allocation_sha256"],"schedule digest")
    counts={arm:{p:{"count":0,"hits":0,"net_sum_uj":0} for p,_ in PHASES} for arm in ARMS}
    clusters=[]
    probes=[]
    observed=0
    with gzip.open(root/"episodes.jsonl.gz","rt",encoding="utf-8") as data:
        for seed in range(8):
            world={p:permutation(seed,p,n,"world") for p,n in PHASES}
            scramble={p:permutation(seed,p,n,"scramble") for p,n in PHASES}
            require(alloc[seed]=={"seed":seed,"world":world,"scramble":scramble},
                    "world allocation mismatch")
            for encoding in (0,1):
                for arm in ARMS:
                    rng=random.Random(rng_seed(f"policy|{seed}|{encoding}|{arm}"))
                    q=init_q()
                    updates=0
                    for phase,n in PHASES:
                        for i in range(n):
                            if arm=="R":
                                rng=random.Random(rng_seed(f"reset|{seed}|{encoding}|{phase}|{i}"))
                                q=init_q()
                                updates=0
                            line=data.readline()
                            require(bool(line),"missing F017 episodes")
                            row=json.loads(line)
                            updates=verify_world(row,arm,seed,encoding,phase,i,
                                                 world[phase][i],scramble[phase][i],
                                                 q,updates,rng)
                            d=counts[arm][phase]
                            d["count"]+=1
                            d["hits"]+=int(row["reached"])
                            d["net_sum_uj"]+=row["net_uj"]
                            if phase in ("holdout","final"):
                                clusters.append({"arm":arm,"seed":seed,"encoding":encoding,
                                                 "phase":phase,"net_uj":row["net_uj"],
                                                 "hit":int(row["reached"])})
                            observed+=1
                        if phase in ("holdout","final"):
                            probe_count=calc_probe(q,arm,seed,encoding,phase)
                            probes.append({"arm":arm,"seed":seed,"encoding":encoding,
                                           "checkpoint":phase,"plus_counts":probe_count,
                                           "D":(probe_count[1]-probe_count[0])/256,
                                           "snapshot":snapshot(q,updates)["q"],"draws":256})
        require(data.readline()=="","excess F017 episodes")
    for arm in ARMS:
        for phase,n in PHASES:
            d=counts[arm][phase]
            d["hit_rate"]=d["hits"]/d["count"]
            d["mean_net_j"]=d["net_sum_uj"]/d["count"]/1_000_000
    require(summary["episode_count"]==observed==23296,"episode number")
    require(summary["summary"]==counts,"summary forgery")
    require(summary["clusters"]==clusters,"clusters mismatch")
    require(summary["causal_probes"]==probes,"causal listening mismatch")
    return {"episodes":observed,"arms":len(ARMS),"seed_blocks":8,"source":head}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True,type=Path)
    print(json.dumps(verify_suite(p.parse_args().root),sort_keys=True))

if __name__=="__main__":
    main()
