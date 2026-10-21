"""Frozen F017 analysis; only read independently verified saved evidence."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from experiments.F017.verify import verify_suite

ARMS=("I","N","K","S","L","F")

def bootstrap(clusters, reference, arm, phase):
    blocks=[]
    for seed in range(8):
        a=[z["net_uj"] for z in clusters if z["arm"]==reference and z["phase"]==phase and z["seed"]==seed]
        b=[z["net_uj"] for z in clusters if z["arm"]==arm and z["phase"]==phase and z["seed"]==seed]
        if len(a)!=64 or len(b)!=64:
            raise ValueError("unbalanced bootstrap seed blocks")
        blocks.append((sum(a)-sum(b))/64/1_000_000)
    draws=[]
    for rep in range(10000):
        ix=[int.from_bytes(hashlib.sha256(
            f"f017.v1|bootstrap|{rep}|{draw}".encode()).digest(),"big")%8
            for draw in range(8)]
        draws.append(sum(blocks[i] for i in ix)/8)
    draws.sort()
    return {"point_j":sum(blocks)/8,
            "ci95_j":[draws[250],draws[9749]],
            "independent_world_seed_clusters":8}

def analyze(root: Path):
    audited=verify_suite(root)
    report=json.loads((root/"summary.json").read_text())
    summary=report["summary"]
    first=summary["I"]["holdout"]["hit_rate"]
    final=summary["I"]["final"]["hit_rate"]
    immediate=summary["I"]["probe"]["hit_rate"]
    deltas={arm:bootstrap(report["clusters"],"I",arm,"holdout") for arm in ARMS if arm!="I"}
    differences={arm:first-summary[arm]["holdout"]["hit_rate"] for arm in ARMS if arm!="I"}
    enc={}
    for encoding in (0,1):
        rows=[z for z in report["clusters"] if z["arm"]=="I" and z["phase"]=="holdout" and z["encoding"]==encoding]
        enc[str(encoding)]=sum(z["hit"] for z in rows)/len(rows)
    intervention={}
    for arm in ("I","L","F"):
        for phase in ("holdout","final"):
            for encoding in (0,1):
                rows=[z for z in report["causal_probes"] if
                      z["arm"]==arm and z["checkpoint"]==phase and z["encoding"]==encoding]
                intervention[f"{arm}/{phase}/encoding{encoding}"]=sum(z["D"] for z in rows)/len(rows)
    h17a=first>=.70 and all(differences[a]>=.20 and deltas[a]["ci95_j"][0]>0 for a in differences)
    h17b=all(z>=.65 for z in enc.values()) and intervention["I/holdout/encoding0"]*intervention["I/holdout/encoding1"]<0
    reset=summary["R"]["holdout"]["hit_rate"]
    h17c=all(differences[a]>=.20 for a in ("N","K","S","L","F")) and first-reset>=.20
    h17d=final>=.70 and final-immediate>=.20
    h17f=(all(abs(intervention[f"I/{phase}/encoding{encoding}"])>=.50
              for phase in ("holdout","final") for encoding in (0,1))
          and all(abs(intervention[f"{arm}/{phase}/encoding{encoding}"])<=.10
                  for arm in ("L","F") for phase in ("holdout","final")
                  for encoding in (0,1))
          and all(intervention[f"I/{phase}/encoding0"]*
                  intervention[f"I/{phase}/encoding1"] < 0
                  for phase in ("holdout","final"))
          and all(intervention[f"I/holdout/encoding{encoding}"]*
                  intervention[f"I/final/encoding{encoding}"] < 0
                  for encoding in (0,1)))
    return {"schema":"f017.analysis.v1","auditor":audited,
            "holdout_I_hit_rate":first,"holdout_by_encoding":enc,
            "reversal_immediate_hit_rate":immediate,
            "reversal_final_hit_rate":final,
            "reset_holdout_hit_rate":reset,
            "holdout_hit_rate_differences":differences,
            "paired_seed_bootstrap":deltas,
            "causal_listening_D":intervention,
            "candidate_gates":{"H17a":h17a,"H17b":h17b,"H17c":h17c,
                               "H17d":h17d,"H17e_saved_evidence":True,"H17f":h17f},
            "scientific_restriction":"frozen ideal 1D receiver learning, not morphological or protocol emergence"}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",required=True,type=Path)
    args=parser.parse_args()
    print(json.dumps(analyze(args.root),sort_keys=True,indent=2))

if __name__=="__main__":
    main()
