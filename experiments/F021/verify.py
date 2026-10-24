"""F021 saved-data independent verifier. Intentionally never import soma.f021.

Recomputes SHA256 field, exhaustive budget gate, independent Euler dynamics,
positive-work charge, local F002-style integer ledger, path depletion, and
all archived fields, including a semantically modified file with a new hash.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

DT = .25
IDS = ("A", "B")
SUBSETS = ((), ("A",), ("B",), ("A", "B"))


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def same(a, b, path="root"):
    if type(a) is not type(b):
        raise AssertionError(f"{path}: type {type(a)} != {type(b)}")
    if isinstance(a, dict):
        if set(a) != set(b):
            raise AssertionError(f"{path}: fields mismatch")
        for key in a:
            same(a[key], b[key], path + "." + str(key))
    elif isinstance(a, list):
        if len(a) != len(b):
            raise AssertionError(f"{path}: length mismatch")
        for i, (x, y) in enumerate(zip(a, b)):
            same(x, y, path + "[" + str(i) + "]")
    elif type(a) is float:
        if not math.isfinite(a) or not math.isfinite(b) or abs(a-b)>1e-11 * max(1, abs(a), abs(b)):
            raise AssertionError(f"{path}: {a} != {b}")
    elif a != b:
        raise AssertionError(f"{path}: {a} != {b}")


def field(seed, count, radius):
    patches = []
    for i in range(count):
        for draw in range(10000):
            blob = f"F019-field-v1|seed={seed}|patch={i}|draw={draw}".encode("ascii")
            idx = int.from_bytes(hashlib.sha256(blob).digest()[:8], "big") % 121
            center = (idx - 60) * .025
            if abs(center) <= radius or abs(center - .1) <= radius:
                continue
            patches.append({"patch_id": f"P{i}", "center_m": center,
                            "radius_m": radius, "initial_available_uj": 1_000_000})
            break
        else:
            raise AssertionError("field sampler failed")
    return {"field_id": f"s{seed:02d}-n{count}-r{int(radius*1000):03d}",
            "generator_version": "sha256-grid-v1", "seed": seed, "patches": patches}


def physical(x, v, arm, forces):
    if arm == "YY":
        accel = (forces["A"] + forces["B"]) / 2.
        velocity = v[0] + accel * DT
        displacement = velocity * DT
        link_b = (forces["A"] - forces["B"]) / 2.
        return ([x[0]+displacement, x[1]+displacement],
                [velocity, velocity], {"A": -link_b, "B": link_b})
    next_v = [v[0]+forces["A"]*DT, v[1]+forces["B"]*DT]
    return ([x[i]+next_v[i]*DT for i in range(2)], next_v,
            {"A": 0., "B": 0.})


def positive_work(force, v0, v1):
    if force == 0:
        return 0.
    p, q = force * v0, force * v1
    if p <= 0 and q <= 0:
        return 0.
    if p >= 0 and q >= 0:
        return DT * (p+q) / 2.
    pos = max(p, q)
    neg = -min(p, q)
    return .5 * DT * pos**2 / (pos+neg)


def hit_fraction(x0, x1, p):
    lo, hi = p["center_m"] - p["radius_m"], p["center_m"] + p["radius_m"]
    if lo <= x0 <= hi:
        return 0.
    if x0 == x1 or max(x0, x1) < lo or min(x0, x1) > hi:
        return None
    return (lo-x0)/(x1-x0) if x1 > x0 else (hi-x0)/(x1-x0)


def expected_world(scene):
    if (scene["schema_version"] != "f021.v1" or scene["seed"] not in range(32)
        or scene["sign"] not in (-1,1) or scene["b_relative"] not in (-1,0,1)
        or scene["arm"] not in ("YY","NN")
        or scene["balance_uj"] not in (80_000,250_000,4_000_000)
        or scene["fee_uj"] not in (0,25_000)
        or scene["count"] not in (2,5) or scene["radius_m"] not in (.02,.06)):
        raise AssertionError("outside frozen protocol")
    fields = field(scene["seed"],scene["count"],scene["radius_m"])
    ref_id = (f"F021-s{scene['seed']:02d}-u{scene['sign']:+d}-b{scene['b_relative']:+d}"
              f"-{scene['arm']}-bal{scene['balance_uj']:07d}-fee{scene['fee_uj']:05d}"
              f"-n{scene['count']}-r{int(scene['radius_m']*1000):03d}")
    if scene["world_id"] != ref_id:
        raise AssertionError("scene ID")
    same(scene["field"],fields,"world.field")
    command = {"A": float(2*scene["sign"]), "B": float(2*scene["sign"]*scene["b_relative"])}
    arm = scene["arm"]
    x, v = [0.,.1],[0.,0.]
    initial = scene["balance_uj"]
    balance = {"A":initial,"B":initial}
    totals = {c:{"acquired_uj":0,"motor_spent_uj":0,"fee_spent_uj":0} for c in IDS}
    steps,harvests,events=[],[],[]
    remaining = {p["patch_id"]:p["initial_available_uj"] for p in fields["patches"]}
    index=0
    def event(k,phase,kind,c,amount):
        nonlocal index
        if not amount:
            return
        if kind == "spend":
            if amount > balance[c]:
                raise AssertionError("spend overdraw")
            balance[c]-=amount
            source,target=c,None
        else:
            balance[c]+=amount
            source,target=None,c
        if not 0 <= balance[c] <= 20_000_000:
            raise AssertionError("ledger capacity")
        index+=1
        events.append({"step_index":k,"phase":phase,"event_index":index,
                       "kind":kind,"source_id":source,"target_id":target,
                       "amount_uj":amount,"eta_bps":None,"received_uj":0,
                       "loss_uj":0,"external_in_uj":amount if kind=="acquire" else 0,
                       "external_out_uj":amount if kind=="spend" else 0,
                       "residual_uj":0})
    if arm=="YY":
        for c in IDS:
            event(0,"fee","spend",c,scene["fee_uj"])
            totals[c]["fee_spent_uj"] += scene["fee_uj"]
    ambiguous=0
    for k in range(1,5):
        before=dict(balance)
        prev_x,prev_v=list(x),list(v)
        candidates=[]
        for subset in SUBSETS:
            force={c:command[c] if c in subset else 0. for c in IDS}
            xx,vv,link=physical(x,v,arm,force)
            w={c:positive_work(force[c],v[i],vv[i]) for i,c in enumerate(IDS)}
            charge={c:math.ceil(w[c]*1_000_000) for c in IDS}
            feasible=all(command[c]!=0. and before[c]>0 and charge[c]<=before[c]
                         for c in subset)
            candidates.append({"subset":list(subset),"feasible":feasible,
                               "work_j":w,"charge_uj":charge,"trial_v_m_s":vv})
        n=max(len(c["subset"]) for c in candidates if c["feasible"])
        maximals=[c["subset"] for c in candidates
                  if c["feasible"] and len(c["subset"])==n]
        if len(maximals)==1:
            selected=maximals[0]
            reason="unique_max_feasible" if selected else "none_feasible"
        else:
            selected=[]
            reason="ambiguous_maximal"
            ambiguous+=1
        force={c:command[c] if c in selected else 0. for c in IDS}
        x,v,link=physical(x,v,arm,force)
        chosen=next(c for c in candidates if c["subset"]==selected)
        decision={"candidates":candidates, "maximal_feasible":maximals,
                  "selected_subset":selected,"reason":reason,"applied_n":force,
                  "next_x_m":x,"next_v_m_s":v,"link_force_n":link,
                  "charge_uj":chosen["charge_uj"],"work_j":chosen["work_j"]}
        for c in IDS:
            spend=chosen["charge_uj"][c]
            if spend:
                event(k,"motor","spend",c,spend)
                totals[c]["motor_spent_uj"]+=spend
        options=[]
        for p in fields["patches"]:
            if not remaining[p["patch_id"]]:
                continue
            for i,c in enumerate(IDS):
                fraction=hit_fraction(prev_x[i],x[i],p)
                if fraction is not None:
                    options.append((fraction,p["patch_id"],c))
        step_claims=[]
        for fraction,patch,c in sorted(options):
            amount=remaining[patch]
            if not amount:
                continue
            remaining[patch]=0
            claim={"step_index":k,"patch_id":patch,"fraction":fraction,
                   "winner":c,"amount_uj":amount}
            harvests.append(claim)
            step_claims.append(claim)
            event(k,"harvest","acquire",c,amount)
            totals[c]["acquired_uj"]+=amount
        dk=.5*sum(v[i]**2-prev_v[i]**2 for i in range(2))
        work=sum(force[c]*DT*(prev_v[i]+v[i])/2 for i,c in enumerate(IDS))
        if abs(dk-work)>1e-10:
            raise AssertionError("energy balance")
        steps.append({"step_index":k,"x_before_m":prev_x,"v_before_m_s":prev_v,
                      "x_after_m":x,"v_after_m_s":v,
                      "balance_before_uj":before,"balance_after_uj":dict(balance),
                      "command_n":command,"decision":decision,"harvests":step_claims,
                      "kinetic_delta_j":dk,"signed_work_j":work})
    net={c:totals[c]["acquired_uj"]-totals[c]["motor_spent_uj"]-
         totals[c]["fee_spent_uj"] for c in IDS}
    for c in IDS:
        if balance[c]!=initial+net[c]:
            raise AssertionError("net balance")
    return {"scene":scene,"steps":steps,"harvests":harvests,
            "ledger_events":events,"totals":totals,"net_uj":net,
            "ambiguous_steps":ambiguous,"final_balance_uj":balance}


def verify_root(root):
    manifest=json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    primary=manifest["mode"]=="primary"
    if manifest["schema"]!="f021.evidence.v1":
        raise AssertionError("manifest schema")
    for fname,key in [("worlds.jsonl","worlds_sha256"),("summary.json","summary_sha256")]:
        actual=hashlib.sha256((root/fname).read_bytes()).hexdigest()
        if manifest[key]!=actual:
            raise AssertionError(fname+" SHA256")
    summary=json.loads((root/"summary.json").read_text(encoding="utf-8"))
    observed=set()
    count=0
    for line in (root/"worlds.jsonl").open(encoding="utf-8"):
        world=json.loads(line,parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))
        expected=expected_world(world["scene"])
        same(world,expected,"world["+str(count)+"]")
        if world["scene"]["world_id"] in observed:
            raise AssertionError("duplicate world")
        observed.add(world["scene"]["world_id"])
        count+=1
    if count != summary["worlds"] or (primary and count != 4608):
        raise AssertionError("world count")
    if primary:
        if summary["paired_yy_nn"]!=2304 or summary["seed_blocks"]!=32:
            raise AssertionError("pair count")
    print(canonical({"verified_worlds":count,"sha256_ok":True,
                     "independent_physics_ledger_patch_oracle":True}))
    return count


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,required=True)
    args=ap.parse_args()
    verify_root(args.root)
