---
id: EXP-F011
kind: experiment_plan
status: preregistered_not_executed
updated: 2026-10-20
---
# Frozen F011 A–F experiment plan (before ANY F011 runs)

The [SPEC](../../topics/F011-grounded-internal-drive/SPEC.md) is normative. This plan freezes each comparison and prohibits tuning a favorable locomotion result after observing data.

| Case | Passive ground law for both identical cells | Motor | Intended discrimination |
|---|---|---|---|
| A:no_contact | mu+=0, mu-=0 | ±1N open-loop | H1: internal force alone cannot displace COM |
| B:isotropic | mu+=.04, mu-=.04 | ±1N | H3: reflection symmetry blocks COM drift |
| C:directional | mu+=.02, mu-=.08 | ±1N | H2: possibility of passive environmental rectification |
| D:mirror | mu+=.08, mu-=.02 | ±1N | H2/H4: sign reversal and A/B swap mathematical mirror |
| E:no_motor | mu+=.02, mu-=.08 | zero | H4: no drift driven by ground-law bias without motion |
| F:negative | malformed configs, missing files, altered raw csv + recomputed manifest SHA, false comparison, deterministic replay, dt/stroke boundary | varied invalid | Do not publish fabricated science |

Common values: `mA=mB=1 kg; xA0=-0.25 m; xB0=0.25 m; vA0=vB0=0; L0=.5m; k=20 N/m; g=9.81m/s²; u=+1N for half 0.6s then -1N for next 0.6s; 8 periods T=9.6s; dt=.01,.005,.0025 seconds; allowable 0.2<=r<=0.8m`. Each case/dt run starts fresh; `seed=null`. Run no parameter search. Ground is an ideal **velocity-implicit** directional Coulomb threshold with mu_stick=mu_slide (numerical approximation). No role labels and no sensor/controller learning.

For H1/H3/E: analytical `COM(t)=0`; H2 C/D **mirror** analytic `COM_C(t)=-COM_D(t)` and same separation `r_C(t)=r_D(t)`. The true sign/magnitude of C drift is NOT predicted by these conservation/symmetry checks; measure it and honestly reject/inconclusive if needed.

### Primary outcomes
- `Xcm(T)-Xcm(0)` (m); `Xcm(T)-Xcm(T-1.2)` and `Xcm(T-1.2)-Xcm(T-2.4)` (m), `r(T)-r(T-1.2)` (m).
- Per-step `ΔP-ground impulse` (N·s); friction dissipation (J), motor work (J), spring+kinetic energy and **explicit** semi-implicit energy defect identity. Ground work must not be positive, including static intervals.
- Each frozen run has 960/1920/3840 intervals respectively. Same parameter sequence across independent replay, CSV/summary/manifest integrity, non-finite/incompatible input rejection.
- Quantitative H2 thresholds, exclusion rules and reflection precision are in SPEC; do not postselect the best-looking interval or coefficient.
- Support/contradicted/inconclusive/unexecuted must be kept distinct from CI PASS. Broken code is not evidence for or against natural locomotion.

### Wolfram theory prior to software experiment
Two 1kg masses with `F_A=u+k(r-L)+f_A`, `F_B=-u-k(r-L)+f_B` obey `a_cm=(f_A+f_B)/(2kg)`; if both ground forces zero, `a_cm=0`. Motor power is `u(v_A-v_B)`, spring power cancels through potential. Directional ground forces are dissipative. These are mathematical predictions, not F011 observations.
