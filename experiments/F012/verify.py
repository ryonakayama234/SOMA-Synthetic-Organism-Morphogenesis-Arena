"""Researcher-only independent raw F012 oracle; NO production simulator imports."""
import csv
import hashlib
import json
import math
from pathlib import Path

CASES={"B-isotropic":(.04,.04,1),"C-directional":(.02,.08,1),
       "D-mirror":(.08,.02,1),"E-no-drive":(.02,.08,0)}
BUDGETS=(0,1000000,3000000,10000000)
DTS=(.01,.005,.0025)
SOURCES=("soma/f012.py","soma/f011.py","soma/f005.py",
         "experiments/F012/verify.py","experiments/F012/run_suite.py",
         "tests/test_f012.py",".github/workflows/f012.yml",
         "topics/F012-finite-energy/SPEC.md","experiments/F012/PLAN.md")
KEYS=("step","time_s","x_a_m","x_b_m","v_a_m_s","v_b_m_s",
      "r_m","x_cm_m","motor_command_n","motor_applied_n",
      "motor_candidate_positive_j","motor_positive_j","motor_signed_j",
      "spent_uj","balance_uj","decision","ground_a_n","ground_b_n",
      "ground_work_j","kinetic_j","spring_j","impulse_residual_ns",
      "energy_defect_j","expected_defect_j")


def near(a,b,tol=3e-9):
    if not (math.isfinite(a) and math.isfinite(b)) or abs(a-b)>tol:
        raise ValueError("independent arithmetic disagreement: %s %s"%(a,b))


def positive_area(u,a,b,h):
    p,q=u*a,u*b
    if p>=0 and q>=0: return h*(p+q)/2
    if p<=0 and q<=0: return 0.
    return (h/2)*max(p,q)**2/abs(p-q)


def step(xa,xb,va,vb,h,u,mp,mm):
    internal=u+20*(xb-xa-.5)
    av,bv=va+h*internal,vb-h*internal
    def contact(v):
        if v>0: return max(0.,v-h*mp*9.81)
        if v<0: return min(0.,v+h*mm*9.81)
        return 0.
    an,bn=contact(av),contact(bv)
    return xa+h*an,xb+h*bn,an,bn,(an-av)/h,(bn-bv)/h


def metrics(rows):
    h=rows[1]["time_s"]; per=round(1.2/h)
    z,p,q=rows[-1],rows[-1-per],rows[-1-2*per]
    pos=math.fsum(v["motor_positive_j"] for v in rows[1:])
    spent=sum(v["spent_uj"] for v in rows[1:])
    return dict(center_final_m=z["x_cm_m"],
        last_period_m=z["x_cm_m"]-p["x_cm_m"],
        penultimate_period_m=p["x_cm_m"]-q["x_cm_m"],
        stroke_return_m=z["r_m"]-p["r_m"],
        accepted_steps=sum(x["motor_applied_n"]!=0 for x in rows[1:]),
        rejected_steps=sum(x["decision"] in ("zero_balance","insufficient_balance") and x["motor_command_n"]!=0 for x in rows[1:]),
        spent_uj=spent,balance_uj=z["balance_uj"],positive_work_j=pos,
        quantization_excess_j=spent/1e6-pos,
        signed_motor_work_j=math.fsum(x["motor_signed_j"] for x in rows[1:]),
        ground_work_j=math.fsum(x["ground_work_j"] for x in rows[1:]),
        min_stroke_m=min(x["r_m"] for x in rows),
        max_stroke_m=max(x["r_m"] for x in rows))


def audit_rows(case,budget,h,rows):
    if case not in CASES or budget not in BUDGETS or h not in DTS or len(rows)!=round(9.6/h)+1:
        raise ValueError("wrong study design or incomplete full trace")
    mp,mm,active=CASES[case]
    xa,xb,va,vb=-.25,.25,0.,0.
    balance=budget
    for index,row in enumerate(rows):
        if set(row)!=set(KEYS) or row["step"]!=index: raise ValueError("bad CSV schema/step")
        if index==0:
            for k,v in (("time_s",0.),("x_a_m",xa),("x_b_m",xb),("v_a_m_s",va),
                        ("v_b_m_s",vb),("r_m",xb-xa),("x_cm_m",(xa+xb)/2)):
                near(row[k],v)
            if row["balance_uj"]!=balance: raise ValueError("initial ledger mismatch")
            if any(row[k] is not None for k in ("motor_command_n","motor_applied_n","spent_uj","decision")):
                raise ValueError("initial event not empty")
            continue
        cmd=(1. if (index-1)//round(.6/h)%2==0 else -1.) if active else 0.
        cand=0.
        if cmd==0:
            applied,cost,reason=0.,0,"zero_command"
        elif balance==0:
            applied,cost,reason=0.,0,"zero_balance"
        else:
            trial=step(xa,xb,va,vb,h,cmd,mp,mm)
            cand=positive_area(cmd,va-vb,trial[2]-trial[3],h)
            cost=math.ceil(cand*1e6)
            if cost<=balance:
                applied=cmd
                reason="accepted_positive_work" if cost else "accepted_nonpositive_work"
            else:
                applied,cost,reason=0.,0,"insufficient_balance"
        for k,v in (("motor_command_n",cmd),("motor_applied_n",applied),
                    ("motor_candidate_positive_j",cand)):
            near(row[k],v,2e-9)
        if row["spent_uj"]!=cost or row["decision"]!=reason: raise ValueError("false budget gate")
        nx,ny,nv,nw,ga,gb=step(xa,xb,va,vb,h,applied,mp,mm)
        if not (.2-1e-12<=ny-nx<=.8+1e-12): raise ValueError("stroke failure")
        wplus=positive_area(applied,va-vb,nv-nw,h)
        ws=h*applied*(nv-nw)
        wg=h*(ga*nv+gb*nw)
        e0=(va*va+vb*vb)/2+10*(xb-xa-.5)**2
        e1=(nv*nv+nw*nw)/2+10*(ny-nx-.5)**2
        imp=(nv+nw-va-vb)-h*(ga+gb)
        defect=e1-e0-ws-wg
        expected=10*((ny-nx)-(xb-xa))**2-((nv-va)**2+(nw-vb)**2)/2
        for k,v in (("motor_positive_j",wplus),("motor_signed_j",ws),
                    ("ground_a_n",ga),("ground_b_n",gb),("ground_work_j",wg),
                    ("kinetic_j",(nv*nv+nw*nw)/2),
                    ("spring_j",10*(ny-nx-.5)**2),
                    ("impulse_residual_ns",imp),
                    ("energy_defect_j",defect),("expected_defect_j",expected)):
            near(row[k],v,4e-9)
        if wg>1e-11 or abs(imp)>1e-10 or abs(defect-expected)>1e-9:
            raise ValueError("physics invariant failed")
        balance-=cost
        xa,xb,va,vb=nx,ny,nv,nw
        for k,v in (("time_s",index*h),("x_a_m",xa),("x_b_m",xb),
                    ("v_a_m_s",va),("v_b_m_s",vb),("r_m",xb-xa),
                    ("x_cm_m",(xa+xb)/2)):
            near(row[k],v)
        if row["balance_uj"]!=balance: raise ValueError("post-step ledger mismatch")
    if balance<0 or balance+sum(x["spent_uj"] for x in rows[1:])!=budget:
        raise ValueError("budget not conserved")
    return metrics(rows)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_csv(path):
    with Path(path).open(encoding="utf-8",newline="") as f:
        rd=csv.DictReader(f)
        if tuple(rd.fieldnames)!=KEYS: raise ValueError("wrong header")
        rows=[]
        for item in rd:
            row={}
            for k,v in item.items():
                if k=="decision": row[k]=v or None
                elif k in ("step","spent_uj","balance_uj"): row[k]=int(v) if v else None
                else: row[k]=float(v) if v else None
            rows.append(row)
        return rows


def verify_suite(root,checkout):
    root,checkout=Path(root),Path(checkout)
    manifest=json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    actual_files={str(p.relative_to(root)) for p in root.rglob("*") if p.is_file() and p.name!="manifest.json"}
    if set(manifest)!=set(("schema","files","source_hashes")) or manifest["schema"]!="f012.evidence.v1":
        raise ValueError("manifest schema")
    if set(manifest["files"])!=actual_files: raise ValueError("artifact inventory")
    if set(manifest["source_hashes"])!=set(SOURCES): raise ValueError("source inventory")
    for k,v in manifest["files"].items():
        if sha(root/k)!=v: raise ValueError("artifact corruption: "+k)
    for k,v in manifest["source_hashes"].items():
        if sha(checkout/k)!=v: raise ValueError("trusted source mismatch: "+k)
    comp=json.loads((root/"comparison.json").read_text(encoding="utf-8"))
    if set(comp)!=set(("schema","baseline","outcomes")) or comp["schema"]!="f012.comparison.v1" or comp["baseline"]!="F011 fixed model; F012 ideal energy gate":
        raise ValueError("comparison contract")
    expected={("%s__%suj__dt%s"%(c,b,str(h))) for c in CASES for b in BUDGETS for h in DTS}
    if set(comp["outcomes"])!=expected: raise ValueError("missing or extra experiment")
    checked={}
    for c in CASES:
        for b in BUDGETS:
            for h in DTS:
                label="%s__%suj__dt%s"%(c,b,str(h))
                cfg=json.loads((root/label/"config.json").read_text(encoding="utf-8"))
                mp,mm,active=CASES[c]
                if cfg.get("schema_version")!="f012.energy.v1" or cfg.get("case_id")!=c or cfg.get("budget_uj")!=b or cfg.get("dt_s")!=h or cfg.get("seed") is not None or cfg.get("mu_plus")!=mp or cfg.get("mu_minus")!=mm or cfg.get("motor_amplitude_n")!=(1. if active else 0.) or cfg.get("duration_s")!=9.6 or cfg.get("spring_n_m")!=20.:
                    raise ValueError("wrong experiment input")
                measured=audit_rows(c,b,h,read_csv(root/label/"states.csv"))
                advertised=comp["outcomes"][label]
                if set(advertised)!=set(measured): raise ValueError("false science summary keys")
                for k,val in measured.items():
                    if k in ("accepted_steps","rejected_steps","spent_uj","balance_uj"):
                        if advertised[k]!=val: raise ValueError("false science summary count")
                    else: near(advertised[k],val,2e-8)
                checked[label]=measured
    for b in BUDGETS:
        for h in DTS:
            x=checked["C-directional__%suj__dt%s"%(b,str(h))]
            y=checked["D-mirror__%suj__dt%s"%(b,str(h))]
            near(x["center_final_m"],-y["center_final_m"],1e-9)
            if x["spent_uj"]!=y["spent_uj"] or x["balance_uj"]!=y["balance_uj"]:
                raise ValueError("cost mirror broken")
    return checked
