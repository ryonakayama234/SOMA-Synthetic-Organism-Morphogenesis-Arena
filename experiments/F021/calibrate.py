"""F021 off-primary ambiguity counterfactuals (calibration ONLY, no ecology)."""
from __future__ import annotations
import json
import math
from soma.f005 import positive_motor_work
from soma.f021 import _motion, motor_gate, DT


def arbitration_fixture():
    x,v=[0.,.1],[0.,0.]
    command={"A":2.,"B":2.}
    balances={"A":80_000,"B":80_000}
    actual=motor_gate(x,v,"YY",command,balances)
    alternatives=[]
    for label,applied in (("both",{"A":2.,"B":2.}),
                          ("A_only",{"A":2.,"B":0.}),
                          ("B_only",{"A":0.,"B":2.}),
                          ("off",{"A":0.,"B":0.})):
        nx,nv,link=_motion(x,v,"YY",applied["A"],applied["B"])
        charges={c:math.ceil(positive_motor_work(applied[c],v[i],nv[i],DT)*1_000_000)
                 for i,c in enumerate(("A","B"))}
        alternatives.append({"branch":label,"applied_n":applied,
                             "x_a_m":nx[0],"x_b_m":nx[1],
                             "v_end_m_s":nv[0], "charge_uj":charges,
                             "affordable":all(charges[c]<=balances[c]
                                                for c in ("A","B"))})
    return {"kind":"off_primary_calibration_not_ecology",
            "actual_predeclared_arbitration":actual["reason"],
            "selected":actual["selected_subset"],
            "alternatives":alternatives}


if __name__=="__main__":
    print(json.dumps(arbitration_fixture(),sort_keys=True,indent=2))
