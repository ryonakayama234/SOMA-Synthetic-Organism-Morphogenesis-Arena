---
id: EXP-F009
status: preregistered_not_executed
updated: 2026-10-18
---
# F009 A〜F事前登録（SOMA観測前）
**理論値はWolfram/数学モデルの予測。SOMA F009未実施。**
共通：1D、mA=mB=1kg、xA0=0,xB0=.5m、v=0、dt=1/4s、T=1s、drag=0、command=2N。

| 対照 | 作用の源泉 | 結合 | 理論(xA,xB;vA,vB) at 1s |
| --- | --- | --- | --- |
| A | legacy external effective +2N to A | ON | (5/8,9/8;1,1) |
| B | internal pair A+2N/B−2N; external 0 | ON | (0,1/2;0,0) |
| C | ground traction +2N / reaction ground −2N; limit≥2 | ON | (5/8,9/8;1,1) |
| D | ground contact OFF, traction 0 | ON | (0,1/2;0,0) |
| E | ground traction +2N to A | OFF | (5/4,1/2;2,0) |
| F | ground ON, limit 1N; plus malformed/tampered inputs | ON | (5/16,13/16;1/2,1/2) |

Theory: linked common acceleration Fext/(mA+mB); semi-implicit Euler xA[n]=h² Fext n(n+1)/(2(mA+mB)). External impulse over 1s = +2Ns in A/C/E, +1Ns in F, 0 in B/D. Ground receives -2Ns for C/E, -1Ns F, 0 for A/B/D. Closed internal pair has zero center of mass momentum change. Continuous-time displacement for A/C would be 1/2m, not 5/8m: time-discrete values must be used. E nonlinked center motion is different.
Independent Wolfram exact arithmetic predictions are not SOMA measurements.

F negative acceptance: +2N commanded with max 1N produces exactly 1N traction; contact OFF means 0; invalid limit/mass/dt/mode/position constraint, boolean input, NaN/Inf, altered CSV/manifest (even rehashed), duplicated/nonmonotone steps must be rejected. Stored external_impulse_ns equals timestep sum of **external force on cells only**; internal A+u/B-u cancels. Ground reaction is a distinct field.
Every saved step (including t=0) must be present and checked independently, old F007 unaffected, same input and code exact byte replay. Tolerances: 1e-12 in each stated SI quantity for these fixed controls; source SHA must be checked against trusted checkout, not a self-described manifest. Negatives and failures retained.

Result status: supported if all frozen predictions, conservation, provenance and regression checks hold; contradicted if physical budget/ground reaction or reference fails; inconclusive if missing evidence; not executed before actual run. No hardware or emergence claim.
