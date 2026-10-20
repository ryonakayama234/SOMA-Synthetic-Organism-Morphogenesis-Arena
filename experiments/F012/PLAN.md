---
id: EXP-F012
kind: experiment_plan
status: preregistered_not_executed
updated: 2026-10-20
---
# F012 A–F frozen study design (before implementation)

[NORMATIVE SPEC](../../topics/F012-finite-energy/SPEC.md) precedes any experiment. The following is a proposal/forecast, **no F012 results observed yet**.

| Condition | Passive ground per cell | Internal command | Purpose |
|---|---|---|---|
| B:isotropic | mu+=.04; mu-=.04 | prescribed ±1N | no COM under reflected symmetry |
| C:directional | mu+=.02; mu-=.08 | prescribed ±1N | energy-limited candidate directional drift |
| D:mirror | mu+=.08; mu-=.02 | prescribed ±1N | mirror and **same spent µJ** |
| E:no-drive | mu+=.02; mu-=.08 | 0N | no-drive/no-work negative |
| F:invalid | malformed inputs/CSV/summary/rehashed manifest | N/A | refuse wrong scientific evidence |

48 *normal* combinations: B/C/D/E × budgets [0,1000000,3000000,10000000] µJ × dt [.01,.005,.0025]s. No random seed. Each separate run restarts xA=-.25,xB=.25, vA=vB=0, k=20N/m, L=.5m, mass=1kg each, g=9.81m/s2, 8 cycles of period 1.2s, full T=9.6s. A:no-contact is **not a valid full-duration F011 baseline**, remains explicitly OUT OF SCOPE; Issue #37 preserved.

## Independent predictions made now
1. At 0J, gate prohibits all commands: cells initially static at spring rest => no motion or positive work at any dt for all B/C/D/E.
2. With E:no-drive, no physical motion/positive work at any budget; residual budget identical to initial.
3. For isotropic B, the symmetric ground law + equal/opposite internal forces leaves COM zero at each step under symmetric initial state, independent of budget.
4. For C/D with paired budget/dt, under reflection xA ↔ -xB and vA ↔ -vB, same candidate work, accepted motor, spending and separation, but opposite COM drift. Their signed displacements need **not** be assumed >0 at each finite budget.
5. The first step at dt=.01, C, u=+1N, with enough budget, gives ground-limited velocities vA=.008038m/s and vB=-.002152m/s, ground forces -.1962N and +.7848N, COM shift +.00002943m, signed motor work .0001019J, and **linear-interpolation positive mechanical work .00005095J, ceil charge 51µJ**. This first-step reference is the model's discrete prediction, NOT an observed F012 trajectory. This step must be rejected for 0J; accepted for 1J/3J/10J.
6. Under accepted actuation, negative signed work may coexist with nonzero positive-work cost if relative power crosses zero; do not charge signed work as a surrogate.
7. Quantization difference and timestep acceptance changes are acknowledged potential confounds; no locked prediction for 1/3/10 J final displacement or persistence.

## Primary measures, classification
For each run: all-state time series, commands/applied, candidate/accepted positive work, cost/balance and reasons, signed motor and ground work, momentum/energy identity, r min/max, drift per last 2 periods, quantization excess, accepted/rejected counts. Save exact configuration and code identity.

Persistence classification per-budget follows the quantitative SPEC thresholds. Report SUPPORTED, CONTRADICTED, INCONCLUSIVE, UNEXECUTED per scientific hypothesis, **not** only pass/fail tests. Any stroke violation is negative evidence and must remain; no parameter respecification after viewing data.

## Verification and provenance
Independent saved-CSV physics/arithmetic replay (different implementation than F012 production), source-file hashes and SHA256 of outputs bound to externally trusted checkout, no self-trusting manifests, random mutation/rehash and missing source negatives. Two fresh output directories should be byte-identical; no overwrite of earlier evidence. 3.11 and 3.12 workflow, inherited regression and optimized tests, explicit final HEAD checks; no claim of external peer review. Numerical or physics issues may trigger audited implementation correction, but not retroactive hypothesis/threshold tuning.
