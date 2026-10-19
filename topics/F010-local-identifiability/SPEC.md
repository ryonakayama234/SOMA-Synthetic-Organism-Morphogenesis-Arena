---
id: F010
kind: research_spec
status: preregistered_not_executed
updated: 2026-10-19
issue: 31
---
# F010 — Active local response identifiability, with an indistinguishability counterexample

**Researcher authorized starting this study, NOT adoption or main merge.** Preregistered BEFORE new F010 implementation runs. Issue [#31](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/31) / [PLAN](../../experiments/F010/PLAN.md) / [findings](../../findings/F010-validation.md).

## One question and decision
Can independently chosen, distinct **motor applied** force levels identify the response slope of an A-local 1D motion trace and distinguish added inertial load from an unknown *constant* exogenous force? Can a force which depends on the motor input render those causes indistinguishable? The output is **a response signature, never a connection label or full body schema**.

## Frozen hypotheses / rival hypotheses (Wolfram exact fractions, NOT SOMA data)
- H010a linked 1 kg A + 1 kg B: a=u/2; for u=2,1,0.5 N, a=[1,1/2,1/4] m/s², response (alpha,beta)=(1/2 kg^-1,0 m/s²).
- H010b free 1 kg A, force d=-1 N constant across trials: a=u-1; a=[1,0,-1/2], response=(1,-1). The u=2 observation agrees exactly with H010a; a second distinct force breaks this equivalence **only under the invariant-disturbance assumption**.
- H010c free 1 kg A, force d(u)=-u/2: a=u/2; a=[1,1/2,1/4] and **entire A-local time, applied force, motor command and battery traces agree with linked**. Distinct input levels cannot decide topology.
- H010d free 1 kg A, d=0: a=u; a=[2,1,1/2], response=(1,0).
- H010e applied force rejected or only one distinct applied input: *inconclusive*; do not substitute commanded force for applied.
- H010f corrupted local fields, world truth leak, hash-consistent forged results or non-reproducible outputs must be rejected.
Strictly A-local F008 `LocalObservation` inputs; cases, B, attached, external forces, source world configuration are not accepted by `soma.f010`. Researcher-only oracle sees world truth separately.
For independent trials fixed: `mA=mB=1 kg; xA=0,xB=.5 m; vA=vB=0; h=.25 s; T=1 s; drag=0; A initial battery=3,000,000 µJ; B balance=0; u in (2,1,.5) N`. High A capacity is an experimental control, not a validated real battery model. `motor_force_n` is F007 external *effective* motor force; no validated ground reaction/powertrain.

## Estimator definition frozen in advance
Each run starts from identical zero-velocity initial conditions. For each accepted, nonzero applied-force step, derive a=(v_current−v_previous)/dt (m/s²) from F008 fields. Require all 4 steps, strictly increasing time, a constant *applied* force across steps, strictly repeated nonzero applied force per trial, an internally constant observed acceleration, no rejected motor step, and at least two **different** applied forces; malformed or underexcited input is inconclusive/error rather than attachment. Fit alpha=(a(u=2)−a(u=1))/(2−1), beta=a(u=1)−alpha·1. The third predeclared `u=.5` is strictly held out and compared with alpha·.5+beta. The response class for the frozen controls is `inertia_like`, `offset_like`, `nominal_like` or `unclassified` with **no connection/topology inference**. Reject inconsistent third response; preserve it as negative evidence. If only one input (or no applied input), do not estimate a slope.

## Frozen expected discrete trajectories
For each constant a, `v_A(1s)=a (m/s)`, `x_A(1s)=5a/8 (m)` under F007 semi-implicit Euler, which differs from continuous `a/2`. Expected listed in PLAN. All comparisons fixed to **absolute 1e-12** for only these rational small synthetic controls. No distributional confidence or real noisy sensor claims. Derived response signature must be checked by a separate Fraction oracle over immutable saved `states.csv` and independently recomputed A-local columns, without importing `soma.f010`.

## Support / contradiction / inconclusive
SUPPORTED if frozen A–D response slopes, holdout, A=C identical local streams, E inconclusive, F tamper/byte reproducibility and full regressions pass, with preserved raw artifacts. CONTRADICTED if fixed model conditions and evidence are valid but theoretical predictions fail; investigate model/implementation rather than changing thresholds. INCONCLUSIVE if motor rejected, insufficient excitation, broken or missing evidence, or topologies generate same A-local stream; record and preserve.
No claims of real contact, electric motor efficiency, continuous-time invariance, online learning, multi-cell emergence, or discovering topology. AI arithmetic audits are not independent human/academic peer review.
