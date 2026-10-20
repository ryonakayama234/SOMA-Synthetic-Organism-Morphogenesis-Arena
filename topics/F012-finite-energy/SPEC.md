---
id: F012
kind: research_spec
status: preregistered_not_executed
updated: 2026-10-20
issue: 38
---
# F012 — Finite ideal positive-work budget for a prescribed two-cell ground-driven motion

**DESIGN FREEZE before any F012 simulation or source implementation.** Researcher authorized work (2026-10-20), NOT adoption or main merge. Reference main `c8992a0236177c4ce3c8de71db09c78c755b05b7`. [Issue #38](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/38). F011's conditional limited adoption and its failed 9.6-second no-contact A are not repaired or reclassified here; A is explicitly excluded. V001 Draft and F001–F011 remain unchanged.

## Question, competing interpretations
How does a bounded **ideal positive mechanical motor-work** allowance affect repeatability of prescribed two-cell 1D internal-drive locomotion against a passive direction-dependent ground law? Does motion persist within finite cost or become short-lived? Could a reported change be an artifact of timestep, integer microjoule ceil, gating rule, transient deformation, or an imposed directional ground law rather than a self-created physical capability?

**Not tested**: electrical motor efficiencies, genuine power sources, physical contact, autonomous phase selection, self-assembled morphology, local agent knowledge, survival, actual robotics.

## Immutable physical and energy semantics
- Two cells identical masses 1 kg, initial xA=-.25m,xB=.25m and vA=vB=0; spring natural .5m, stiffness k=20 N/m, r=xB-xA in [.2,.8]m. 1D, duration T=9.6s, no external injected propulsion force.
- Internal command u=+1N for 0-.6s, -1N for .6-1.2s, repeat eight periods. Case E is zero command. On a step motor may be rejected; spring remains active. Internal equal/opposite forces +[u+k(r-L)] on A and negative on B.
- Cases B isotropic mu+=mu-=.04; C directional mu+=.02,mu-=.08; D mirror mu+=.08,mu-=.02; E directional mu+=.02,mu-=.08 with no motor. Identical passive ground law per cell, g=9.81m/s^2. F011 velocity-implicit Coulomb shrink: v*_A=vA+h Fint, v*_B=vB-h Fint; v'=max(0,v*-h mu_plus g) for v*>0, v'=min(0,v*+h mu_minus g) for v*<0; x'=x+h v'. fground=(v'-v*)/h. This is a *numerical idealization*.
- Budgets exactly 0,1,3,10 J => 0,1000000,3000000,10000000 **integer microjoules**; dt 0.01,0.005,0.0025 s; 4 cases x 4 budgets x 3 grids = **48 predeclared cases**. seed=null. No adaptive search or post-hoc tuning.
- Compute **candidate** step with prescribed u. Signed discrete motor work used for mechanical identity is `h*u*(vA_next-vB_next)`, matching F011. Compute budget-relevant **positive motor work** as `Integral_0^h max(0,u*(vA(t)-vB(t))) dt` under *linear interpolation of endpoint relative velocities*. For force of constant sign, apply F005's already-adopted `positive_motor_work(u, vA0-vB0, vA1-vB1,h)` algebra; charge `ceil(1000000 * Wpositive)` whole microjoules per *accepted* interval.
- **All-or-none gate**: zero balance rejects motor regardless of zero candidate positive work; with positive balance, if candidate positive-work microjoule charge <=balance, accept the whole command, otherwise reject it and recalculate the step with **u=0** (same spring/ground). Rejected steps spend 0, passive mechanics continue. This gate is intentionally noncontinuous in dt and carries a free-negative/zero-positive-work idealization. No regeneration, idle draw, electric efficiency or cell-local battery allocation. This differs from unbounded F011 and is separately versioned.
- On an attempted r outside [.2,.8], retain valid-prefix and mark INCONCLUSIVE, never clip or silently extend. Exact energy balance `E0=Efinal+sum(spent_uj)`; quantization overhead = spent_uj/1e6 minus total accepted positive work J. Distinguish signed work from positive work, and both from actual electrical energy.
- Preserve world-truth observations exclusively in researcher evidence. No F008/F010 local API changes and no cell autonomous controller.

## Preregistered hypotheses, controls, and falsifiers
- **H12a (accounting)**: no negative balance, no motor with E0=0, and exact integer balance; rejected motor leaves passive motion. If these fail, software/measurement integrity contradicts model, *not* new physics.
- **H12b (budget causality)**: C/D with a sufficiently generous budget may retain last-two-period nonzero drift; low budgets may lose drive. Per budget classify persistence separately; **no preclaim that 1,3 or 10 J reaches particular distances or even succeeds**. Comparing same-condition 0 and high budget identifies the intervention within this fixed model.
- **H12c (symmetry)**: all B COM at every grid <=1e-10m; all E zero velocity/drift. Large drift without anisotropy/motor violates symmetry under this model.
- **H12d (mirror)**: every C/D paired by budget and dt has COM_C=-COM_D and r_C=r_D, and applied-command/charge sequences equal; max absolute position mirror residual <=1e-9m; cost/balance exactly same in µJ. This is conditional on *pairwise unchanged identical rules*.
- **H12e (exploratory efficiency)**: distance / accepted positive-work J or / charged J need not be monotone in nominal budget. Report without favorable sign selection. For zero spent, efficiency is undefined (not zero/infinite).
- **H12f (artifacts)**: all numerical steps satisfy `Delta P=h*(groundA+groundB)`, nonpositive ground work, and `Delta(K+S)-Wmotor_signed-Wground = k/2*(Delta r)^2 - 1/2*((Delta vA)^2+(Delta vB)^2)`; the nonzero semi-implicit defect is *not* erased. Candidate and applied work must not be conflated.

## Frozen evidence gates and distinct conclusions
- No case expected to exceed stroke: if one does, preserve prefix, classify that case INCONCLUSIVE and do not claim all 48 complete. Need exactly 960,1920,3840 intervals for completed cases. Normality finite throughout; ledger exactly zero residual; abs(momentum defect)<=1e-10 Ns, abs(energy identity defect difference)<=1e-9 J, ground work<=1e-11 J.
- **Persistent directional locomotion per budget**: at dt=.0025, BOTH last two 1.2s period COM increments same nonzero sign and >.001m magnitude each; their magnitudes differ by <=50% of larger; `abs(r(T)-r(T-1.2))<=.01m`; `abs(Xcm(dt=.005)-Xcm(dt=.0025))<=max(.002m, .1*abs(Xcm fine))`. As in F011, dt=.01 is diagnostic, not necessarily monotone. Low budget loss of persistence is a valid negative outcome; input starvation means condition may be NOT SUPPORTED, not incorrectly labeled a model failure.
- For a proposed cross-budget trend, compare displacement and accepted positive work at each dt, explicitly separate dt differences in motion from changes in accept/reject events and <=N microjoule ceiling overhead (ideal exact arithmetic).
- Negative input / missing/tampered CSV / rehashed comparison / conflicting source manifest must be rejected by an **independent saved-data oracle** that does not import production F012 physics. Byte-exact double replay, full inherited unittest suite with Python 3.11/3.12, optimized assertions-off tests, and CI for final SHA. A failed or unobserved CI must remain NOT VERIFIED.
- **SUPPORTED** only for frozen model claims actually demonstrated with evidence. **CONTRADICTED** for valid model-case observation conflicting with predeclared scientific prediction. **INCONCLUSIVE** for stroke violation, insufficient numerical convergence, unidentifiable mechanism, or failed/missing evidence. **UNEXECUTED** before any actual F012 run.
- External independent *human* review, autonomous discovery, actual electrical efficiencies, 2D/3D contact and hardware are outside this study. User's fresh explicit approval is mandatory for formal adoption and main merge.
