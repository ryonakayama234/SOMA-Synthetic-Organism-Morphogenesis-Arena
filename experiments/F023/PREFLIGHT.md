---
id: F023-PREFLIGHT
title: F023 独立有理数計算の事前校正
kind: theory_only
status: MATHEMATICAL_PREFLIGHT_NOT_SIMULATION
updated: 2026-10-25
---
# F023 theory-only analytic canary — NOT A SIMULATOR EXPERIMENT
Illustrative calculations independent of any future F023 program. They do not freeze the trial grid, support H23a/b/c empirically, verify float quantization or authorize formal admission.

For A/B unit masses and radii=0.5m, pA=(-1,0), pB=(1,101/100) m, pre-vA=(1,0), pre-vB=(-1,0) m/s; restitution e=1. At t=0 pulse A by J=(0,1/50) N·s, while B has no command.

General r=pB-pA, w=vB-vA, a=w·w, b=2r·w, c=r·r-1, D=b²-4ac.

| Candidate intervention | a | b | c | D | Mathematical classification |
| --- | --- | --- | --- | --- | --- |
| J_A=(0,0) | 4 | -8 | 40201/10000 | -201/625 | miss |
| J_A=(0,+1/50) | 10001/2500 | -20101/2500 | 40201/10000 | 8/25 | first contact predicted, t≈0.9342458972916169s |
| J_A=(0,-1/50) | 10001/2500 | -19899/2500 | 40201/10000 | -608/625 | miss |

For J=(0,+1/50), post-actuation vA=(1,1/50), kinetic increment ΔKA=(1/2)*(1/50)²=1/5000 J = **200 ideal positive-work µJ**, and ground reaction vector (0,-1/50) N·s. B owns no payment. In the budget-rejected branch, actual J=(0,0) and the original miss persists. The exact integer-µJ feasibility boundary must use a separately frozen quantization algorithm, not a floating comparison that could inadvertently round 200 into 201.

This is a **closed-form preflight prediction**, not an observed F023 trajectory, CI outcome, real-world thruster/ground test, self-selected steering policy, or attachment. Even if a future simulator matches this result, this establishes only the specified ideal model.