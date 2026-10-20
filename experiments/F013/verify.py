"""Independent F013 saved-data physics and scientific-summary oracle.

NO soma.f013 or experiment-runner imports. All mathematical tests are derived
from immutable saved fields and independent implicit residual/kinematic checks.
Same AI author is NOT independent human peer review.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = ("soma/f013.py", "experiments/F013/run_suite.py",
       "experiments/F013/verify.py", "topics/F013-contact-rectification/SPEC.md",
       "experiments/F013/PLAN.md")
CASES = {
    "B-isotropic": (.04, .04, True),
    "C-directional": (.02, .08, True),
    "D-mirror": (.08, .02, True),
    "E-no-drive": (.02, .08, False),
}
EPS = (.02, .005, .001)
DTS = (.01, .005, .0025)
COLUMNS = (
    "step", "time_s", "x_a_m", "x_b_m", "v_a_m_s", "v_b_m_s",
    "r_m", "x_cm_m", "motor_n", "ground_a_n", "ground_b_n",
    "ground_work_j", "motor_work_j", "kinetic_j", "spring_j",
    "impulse_residual_ns", "energy_defect_j", "expected_defect_j",
)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def eq(a, b, tol=2e-10):
    if not (math.isfinite(a) and math.isfinite(b)) or abs(a-b) > tol:
        raise AssertionError(f"independent numeric comparison mismatch: {a}, {b}, tol={tol}")


def key(case, eps, dt):
    return f"{case}/eps-{eps:g}/dt-{dt:g}"


def read_rows(p):
    with p.open(encoding="utf-8", newline="") as f:
        rdr = csv.DictReader(f)
        if tuple(rdr.fieldnames or ()) != COLUMNS:
            raise AssertionError("changed frozen CSV schema")
        rows = []
        for raw in rdr:
            if set(raw) != set(COLUMNS):
                raise AssertionError("extra or missing CSV fields")
            row = {}
            for col in COLUMNS:
                if col == "step":
                    row[col] = int(raw[col])
                else:
                    row[col] = None if raw[col] == "" else float(raw[col])
                    if row[col] is not None and not math.isfinite(row[col]):
                        raise AssertionError("nonfinite raw record")
            rows.append(row)
    if len(rows) < 2:
        raise AssertionError("inadequate raw evidence")
    return rows


def observe(rows, h):
    last = rows[-1]
    p = round(1.2/h)
    data = dict(
        observed_steps=len(rows)-1,
        complete=len(rows)-1 == round(9.6/h),
        center_final_m=last["x_cm_m"],
        max_abs_impulse_residual_ns=max(abs(x["impulse_residual_ns"]) for x in rows[1:]),
        max_abs_energy_identity_error_j=max(abs(x["energy_defect_j"]-x["expected_defect_j"]) for x in rows[1:]),
        ground_work_total_j=math.fsum(x["ground_work_j"] for x in rows[1:]),
        min_r_m=min(x["r_m"] for x in rows),
        max_r_m=max(x["r_m"] for x in rows),
    )
    if data["complete"]:
        if len(rows) <= 2*p:
            raise AssertionError("inadequate duration")
        prior, before = rows[-1-p], rows[-1-2*p]
        data.update(
            last_period_m=last["x_cm_m"]-prior["x_cm_m"],
            penultimate_period_m=prior["x_cm_m"]-before["x_cm_m"],
            last_period_r_return_m=last["r_m"]-prior["r_m"],
        )
    return data


def verify_one(root, case, eps, h, published):
    folder = root/key(case, eps, h)
    config = json.loads((folder/"config.json").read_text(encoding="utf-8"))
    mp, mm, active = CASES[case]
    expected = dict(case_id=case, eps_m_s=eps, dt_s=h, mu_plus=mp, mu_minus=mm,
                    amplitude_n=1.0 if active else 0.0)
    if any(config.get(k) != v for k, v in expected.items()):
        raise AssertionError("F013 frozen config mismatch")
    if (config.get("duration_s") != 9.6 or config.get("stroke_min_m") != .2 or
            config.get("stroke_max_m") != .8 or
            config.get("ground_model") != "smooth_directional_tanh_implicit_v1" or
            config.get("seed", "missing") is not None):
        raise AssertionError("incompatible F013 numerical world")
    rows = read_rows(folder/"states.csv")
    initial = rows[0]
    for k, v in (("step", 0), ("x_a_m", -.25), ("x_b_m", .25),
                 ("v_a_m_s", 0), ("v_b_m_s", 0), ("x_cm_m", 0),
                 ("r_m", .5), ("time_s", 0)):
        eq(initial[k], v)
    for c in COLUMNS[8:]:
        if c not in ("kinetic_j", "spring_j") and initial[c] is not None:
            raise AssertionError("initial interval force/energy is filled")
    if len(rows)-1 > round(9.6/h):
        raise AssertionError("extra time steps")
    half = round(.6/h)
    for i in range(1, len(rows)):
        old, cur = rows[i-1], rows[i]
        if cur["step"] != i:
            raise AssertionError("nonconsecutive step")
        eq(cur["time_s"], i*h, 1e-11)
        u = (1.0 if ((i-1)//half)%2 == 0 else -1.0) if active else 0.0
        eq(cur["motor_n"], u, 0)
        r0 = old["x_b_m"]-old["x_a_m"]
        internal = u+20*(r0-.5)
        van, vbn = cur["v_a_m_s"], cur["v_b_m_s"]
        vstar_a = old["v_a_m_s"]+h*internal
        vstar_b = old["v_b_m_s"]-h*internal
        # Independent math: directly evaluate the constitutive implicit equation
        # rather than calling the production bisection algorithm.
        for v, vst, f in ((van, vstar_a, cur["ground_a_n"]),
                          (vbn, vstar_b, cur["ground_b_n"])):
            mu = mp if v>0 else mm
            if v==0:
                constitutive = 0.0
            else:
                constitutive = -9.81*mu*math.tanh(v/eps)
            eq(v - vst - h*constitutive, 0.0, 3e-12)
            eq(f, (v-vst)/h, 4e-10)
            if f*v > 1e-11:
                raise AssertionError("positive dissipative-ground work")
        eq(cur["x_a_m"], old["x_a_m"]+h*van)
        eq(cur["x_b_m"], old["x_b_m"]+h*vbn)
        rr = cur["x_b_m"]-cur["x_a_m"]
        eq(cur["r_m"], rr)
        eq(cur["x_cm_m"], (cur["x_a_m"]+cur["x_b_m"])/2)
        eq(cur["kinetic_j"], (van**2+vbn**2)/2)
        eq(cur["spring_j"], 10*(rr-.5)**2)
        gw = h*(cur["ground_a_n"]*van+cur["ground_b_n"]*vbn)
        wm = h*u*(van-vbn)
        eq(cur["ground_work_j"], gw)
        eq(cur["motor_work_j"], wm)
        imp = van+vbn-old["v_a_m_s"]-old["v_b_m_s"]-h*(cur["ground_a_n"]+cur["ground_b_n"])
        eq(cur["impulse_residual_ns"], imp, 5e-12)
        defect = cur["kinetic_j"]+cur["spring_j"]-old["kinetic_j"]-old["spring_j"]-gw-wm
        predicted = 10*(rr-r0)**2-((van-old["v_a_m_s"])**2+(vbn-old["v_b_m_s"])**2)/2
        eq(cur["energy_defect_j"], defect)
        eq(cur["expected_defect_j"], predicted)
        eq(defect, predicted, 2e-9)
        if not .2-1e-12 <= rr <= .8+1e-12:
            raise AssertionError("invalid state retained as valid")
        if (case == "B-isotropic" and abs(cur["x_cm_m"]) > 2e-10):
            raise AssertionError("isotropic COM drift")
        if case == "E-no-drive" and (abs(cur["x_a_m"]+.25) > 2e-10 or
                                     abs(cur["x_b_m"]-.25) > 2e-10):
            raise AssertionError("no-motor drift")
    measured = observe(rows, h)
    for k, v in measured.items():
        z = published.get(k)
        if isinstance(v, bool) or isinstance(v, int):
            if z != v:
                raise AssertionError("invalid published status/count " + k)
        elif z is None:
            raise AssertionError("missing published " + k)
        else:
            eq(v, float(z), 2e-10)
    n_expected = round(9.6/h)
    if published.get("outcome") == "complete":
        if len(rows)-1 != n_expected or published.get("invalid_step") is not None or published.get("attempted_r_m") is not None:
            raise AssertionError("falsely labeled complete")
    elif published.get("outcome") == "stroke_inconclusive":
        if len(rows)-1 >= n_expected or published.get("invalid_step") != len(rows):
            raise AssertionError("bad stroke prefix status")
        # Verify next attempted step actually breaches the frozen stroke, independently.
        old = rows[-1]
        i = len(rows)
        u = (1.0 if ((i-1)//half)%2 == 0 else -1.0) if active else 0.0
        F = u+20*(old["r_m"]-.5)
        nextv = []
        for vs in (old["v_a_m_s"]+h*F, old["v_b_m_s"]-h*F):
            mu = mp if vs>0 else mm
            lo, hi = (0.0, vs) if vs>0 else (vs, 0.0)
            for _ in range(80):
                mid = (lo+hi)/2
                if mid+h*9.81*mu*math.tanh(mid/eps) < vs:
                    lo=mid
                else:
                    hi=mid
            nextv.append((lo+hi)/2)
        attempted = old["r_m"]+h*(nextv[1]-nextv[0])
        eq(float(published["attempted_r_m"]), attempted, 4e-10)
        if .2-1e-12 <= attempted <= .8+1e-12:
            raise AssertionError("false stroke failure")
    else:
        raise AssertionError("unknown outcome")
    if published["complete"] != (published["outcome"] == "complete"):
        raise AssertionError("incoherent completeness")
    return rows


def persistent(z):
    if not z["complete"]:
        return False
    a, b = z["last_period_m"], z["penultimate_period_m"]
    return (a*b>0 and min(abs(a),abs(b))>.001 and
            min(abs(a),abs(b)) >= .5*max(abs(a),abs(b)) and
            abs(z["last_period_r_return_m"])<=.01)


def verify(root: Path):
    root = Path(root)
    manifest = json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "f013.evidence.v1":
        raise AssertionError("wrong evidence version")
    if manifest.get("source_sha256") != {p:sha(REPO/p) for p in SRC}:
        raise AssertionError("source not tied to checkout")
    disk = sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file() and p.name != "manifest.json")
    if manifest.get("files_sha256") != {p:sha(root/p) for p in disk}:
        raise AssertionError("tampered or incomplete raw evidence")
    report = json.loads((root/"comparison.json").read_text(encoding="utf-8"))
    if report.get("schema_version") != "f013.comparison.v1" or report.get("preregistered_runs") != 36:
        raise AssertionError("wrong reported comparison")
    expected_keys = {key(c,e,d) for c in CASES for e in EPS for d in DTS}
    if set(report.get("results", {})) != expected_keys:
        raise AssertionError("missing/unregistered case")
    frames = {}
    for case in CASES:
        for eps in EPS:
            for dt in DTS:
                k=key(case,eps,dt)
                frames[k]=verify_one(root,case,eps,dt,report["results"][k])
    for eps in EPS:
        for dt in DTS:
            cr=frames[key("C-directional",eps,dt)]
            dr=frames[key("D-mirror",eps,dt)]
            if len(cr)!=len(dr):
                raise AssertionError("mirror length discrepancy")
            for x,y in zip(cr,dr):
                for left,right in (("x_a_m","x_b_m"),("x_b_m","x_a_m"),
                                   ("v_a_m_s","v_b_m_s"),("v_b_m_s","v_a_m_s"),
                                   ("ground_a_n","ground_b_n"),("ground_b_n","ground_a_n")):
                    if x[left] is not None and y[right] is not None:
                        eq(x[left],-y[right],2e-9)
                eq(x["r_m"],y["r_m"],2e-9)
                eq(x["x_cm_m"],-y["x_cm_m"],2e-9)
                if x["ground_work_j"] is not None:
                    eq(x["ground_work_j"],y["ground_work_j"],2e-9)
    results = report["results"]
    computed = {}
    for case in CASES:
        for eps in EPS:
            x,y=results[key(case,eps,.005)],results[key(case,eps,.0025)]
            if not x["complete"] or not y["complete"]:
                z="INCONCLUSIVE"
            else:
                a,b=x["center_final_m"],y["center_final_m"]
                z=("SUPPORTED" if abs(a-b)<=max(.002,.1*abs(b)) and
                   (a*b>0 or (abs(a)<=1e-10 and abs(b)<=1e-10)) else "INCONCLUSIVE")
            computed[f"{case}/eps-{eps:g}"]=z
    if report.get("h13b") != computed:
        raise AssertionError("forged timestep classification")
    groups=[]
    for eps in EPS:
        c,d=results[key("C-directional",eps,.0025)],results[key("D-mirror",eps,.0025)]
        if (computed[f"C-directional/eps-{eps:g}"] != "SUPPORTED" or
            computed[f"D-mirror/eps-{eps:g}"] != "SUPPORTED" or not c["complete"] or not d["complete"]):
            groups.append("INCONCLUSIVE")
        elif persistent(c) and persistent(d) and c["center_final_m"]>0 and d["center_final_m"]<0:
            groups.append("SUPPORTED")
        else:
            groups.append("CONTRADICTED")
    decision=("INCONCLUSIVE" if "INCONCLUSIVE" in groups else
              "SUPPORTED" if all(z=="SUPPORTED" for z in groups) else "CONTRADICTED")
    if report.get("h13a") != decision or report.get("per_epsilon_h13a") != groups:
        raise AssertionError("forged persistence statement")
    if report.get("h13c") != "INCONCLUSIVE":
        raise AssertionError("F013 cannot prove physical model equivalence")
    eq(report.get("f011_reference_center_m"),3.50238193081765,0)
    fine=results[key("C-directional",.001,.0025)]
    delta=fine["center_final_m"]-3.50238193081765 if fine["complete"] else None
    if delta is None:
        if report.get("f013_minus_f011_center_m") is not None:
            raise AssertionError("falsified F011 comparison")
    else:
        eq(report["f013_minus_f011_center_m"],delta,1e-11)
    if report.get("h13d") != "SUPPORTED":
        raise AssertionError("forged verification status")
    return dict(h13a=decision,eps_results=groups,h13b=computed,
                c_fine={str(e):results[key("C-directional",e,.0025)] for e in EPS},
                f011_comparison_delta_m=delta)
