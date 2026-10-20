"""Post-preregistration independent whole-trajectory ODE integration audit.

Alternative classical explicit RK4, not the F013 split implicit Coulomb step:
integrates dx=v, dv=+/-[u+k(r-L)]+f_eps(v) as a coupled 4D
continuous-time ODE. Reproduces separate 0.6s drive phase boundaries.
Does not import soma.f013, run_suite, or its saved-data verifier.

The direction-dependent tanh ground rule is C0 but not globally C1; high-order
asymptotic RK4 convergence is NOT asserted around v=0.
"""
from __future__ import annotations
import math

CASES = {
    "B-isotropic": (.04,.04,True),
    "C-directional": (.02,.08,True),
    "D-mirror": (.08,.02,True),
    "E-no-drive": (.02,.08,False),
}
EPS = (.02,.005,.001)
REF_DT = (.001,.0005)


def independent_ode_rk4(case: str, epsilon: float, h: float):
    """Independent continuous-time 4D solver, seconds/metres/SI units."""
    if case not in CASES or epsilon not in EPS or h not in REF_DT:
        raise ValueError("non-preregistered ODE audit control")
    mp,mm,motor = CASES[case]
    y = (-.25,.25,0.,0.)
    n_half, n_period, n_end = (round(x/h) for x in (.6,1.2,9.6))
    for steps,t in ((n_half,.6),(n_period,1.2),(n_end,9.6)):
        if abs(steps*h-t)>1e-12:
            raise AssertionError("ODE independent solver phase not aligned")

    def field(x, drive):
        xa,xb,va,vb = x
        shared = drive+20.0*(xb-xa-.5)
        ga=-9.81*(mp if va>0.0 else mm)*math.tanh(va/epsilon)
        gb=-9.81*(mp if vb>0.0 else mm)*math.tanh(vb/epsilon)
        return (va,vb,shared+ga,-shared+gb)

    def add(x,k,scale):
        return tuple(a+scale*b for a,b in zip(x,k))

    record = [(0.0,.5)]
    rmin = rmax = .5
    for i in range(n_end):
        drive = ((1.0 if (i//n_half)%2==0 else -1.0) if motor else 0.0)
        k1=field(y,drive)
        k2=field(add(y,k1,h/2),drive)
        k3=field(add(y,k2,h/2),drive)
        k4=field(add(y,k3,h),drive)
        y = tuple(v+h*(a+2*b+2*c+d)/6
                  for v,a,b,c,d in zip(y,k1,k2,k3,k4))
        rr=y[1]-y[0]
        rmin=min(rmin,rr)
        rmax=max(rmax,rr)
        if i%n_period==n_period-1:
            record.append(((y[0]+y[1])/2,rr))
        if not all(math.isfinite(z) for z in y):
            raise ArithmeticError("non-finite alternate ODE solution")
        if not .2-1e-12<=rr<=.8+1e-12:
            raise ArithmeticError("alternate ODE violated frozen stroke")
    if len(record)!=9:
        raise AssertionError("wrong number of whole-period snapshots")
    return dict(
        center_final_m=record[-1][0],
        last_period_m=record[-1][0]-record[-2][0],
        penultimate_period_m=record[-2][0]-record[-3][0],
        last_period_r_return_m=record[-1][1]-record[-2][1],
        min_r_m=rmin,max_r_m=rmax,
    )


def independent_ode_audit(production_summary):
    """Post-experiment audit; no adjustment of registered H13 thresholds."""
    cases={}
    for case in CASES:
        for epsilon in EPS:
            record={}
            for h in REF_DT:
                record[f"{h:g}"] = independent_ode_rk4(case,epsilon,h)
            coarse=record["0.001"]["center_final_m"]
            fine=record["0.0005"]["center_final_m"]
            # This check is a POST-REGISTERED implementation audit gate,
            # not a retroactive change to preregistered H13b.
            if abs(coarse-fine)>.002:
                raise ArithmeticError("independent ODE resolution mismatch")
            if case in ("B-isotropic","E-no-drive") and abs(fine)>1e-10:
                raise ArithmeticError("independent ODE negative control drift")
            prod=production_summary[f"{case}/eps-{epsilon:g}/dt-0.0025"]
            if not prod["complete"]:
                raise AssertionError("F013 production model incomplete")
            record["relative_to_implicit_euler_m"]=fine-prod["center_final_m"]
            cases[f"{case}/eps-{epsilon:g}"]=record
    for epsilon in EPS:
        c=cases[f"C-directional/eps-{epsilon:g}"]["0.0005"]
        d=cases[f"D-mirror/eps-{epsilon:g}"]["0.0005"]
        for k in ("center_final_m","last_period_m","penultimate_period_m"):
            if abs(c[k]+d[k])>2e-9:
                raise AssertionError("alternative integrator mirror mismatch")
        if (c["center_final_m"]<=0 or d["center_final_m"]>=0
                or min(c["last_period_m"],c["penultimate_period_m"])<=0
                or max(d["last_period_m"],d["penultimate_period_m"])>=0):
            raise AssertionError("alternative integrator fails qualitative robust drift")
    return dict(
        schema_version="f013.postregistered_ode_audit.v1",
        method="fully-coupled 4D continuous-time classic explicit RK4; steps 0.001 and 0.0005 s",
        interpretation="post-preregistration independent method check, NOT part of frozen H13a/H13b gates",
        tests="separate ODE numerical consistency <=0.002m; pointwise mirror and B/E negative controls",
        cases=cases,
    )
