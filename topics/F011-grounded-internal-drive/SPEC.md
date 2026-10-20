---
id: F011
kind: research_spec
status: preregistered_not_executed
updated: 2026-10-20
issue: 34
---
# F011 — Two-cell passive grounded locomotion: one falsifiable capability

**2026-10-20 DESIGN FREEZE, before any F011 simulation.** Researcher authorized work, not acceptance or main merge. Baseline main `0e01b68cd15795b1d152d56967909dfa27f283e8`. Related: [Issue #34](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/34), [PLAN](../../experiments/F011/PLAN.md), [unexecuted findings](../../findings/F011-validation.md).

## Scientific question and competing mechanisms
Can two *identical* 1D masses, connected only by an internal equal-and-opposite periodic actuator plus passive spring, acquire persistent center-of-mass drift through *passive* ground interaction, without a cell-specific role or prescribed anchor switching? Is drift absent without contact or with symmetric friction? Do mirrored directional friction laws reverse drift? Distinguish finite transient deformation, physical momentum exchange, and timestep artifact from repeatable locomotion. This does **not** test self-organized choice, autonomous actuation or invented organs.

### Frozen ideal model
- A,B each mass `m=1 kg`. Initial `xA=-0.25 m, xB=+0.25 m, vA=vB=0`. Relative separation `r=xB-xA`, rest length `L=0.5 m`, spring `k=20 N/m`. Interior motor force on A `F_int=u(t)+k(r-L)`; on B `-F_int`, no externally specified propulsive force.
- `u(t)=+1 N` for phase `[0,0.6 s)` and `-1 N` for `[0.6,1.2 s)`, repeated 8 periods; duration `T=9.6 s`, chosen BEFORE execution. Case E uses 0. Researcher prescribes identical open-loop waveforms; cells do not select it.
- Both cells have the same passive idealized ground law using `mu_plus`, `mu_minus` and `g=9.81 m/s²`. **Static threshold equals kinetic threshold** for each direction (deliberately simplified Coulomb stick/slip). No ground contact means both coefficients zero. To avoid unstable explicit friction overshoot use a backward-velocity proximal step: `vstar_i=v_i + dt*Fint_i/m`; if vstar>0 `vnext=max(0,vstar-dt*mu_plus*g)`; if vstar<0 `vnext=min(0,vstar+dt*mu_minus*g)`; else 0. The resulting ground impulse is `m*(vnext-vstar)`; `f_ground=impulse/dt`. Update `xnext=x+dt*vnext` (semi-implicit Euler). This is a specified **numerical discretization** of passive ground forces, not a validated 2D contact solver.
- No roles assigned to A/B: same masses, passive law and actuator endpoints. Fixed allowed separation `0.20 m <= r <= 0.80 m` is an **applicability gate**, not a mechanical collision solver; if exceeded, case is INCONCLUSIVE/model invalid rather than silently clipping, rescoring, or changing stroke after seeing the result.
- No floating loss of scope: existing F001–F010 physics, source and historical artifacts frozen; F009 ground traction is researcher-prescribed and is **not** reused as if passive ground friction; F007 effective world motor force is not internal propulsion. No F002 microjoule ledger or real battery/powertrain here.

## Preregistered H1–H4 and falsifiers
- **H1 conservation:** in case A, `P=m(vA+vB)=0` and `Xcm=(xA+xB)/2=0` at every grid point, though r changes. Any discrepancy beyond 1e-10 SI units fails integrity.
- **H3 symmetric control:** B with `mu_plus=mu_minus=0.04` for each cell and otherwise identical parameters has `P=0,Xcm=0` each grid point to 1e-10. A genuinely larger drift contradicts symmetry or numeric contract.
- **H2 exploratory locomotion:** C with `mu_plus=.02,mu_minus=.08` may produce drift; D interchanges these coefficients. Mirror requirement is `Xcm_D(t)=-Xcm_C(t)` and `r_D(t)=r_C(t)` at every grid point to 1e-9. If no significant repeatable drift: H2 unsupported in the frozen parameter set, **not** tune the coefficients post hoc.
- **H4 artifacts/confounds:** E C friction with `u=0` remains static. Friction's discretized ground work `dt*(fA*vA_next+fB*vB_next)<=0`. Each step momentum `ΔP=dt*(fA+fB)`. Energy identity using `K=m(vA²+vB²)/2`, `S=k(r-L)²/2`, `Wmotor=dt*u*(vA_next-vB_next)`, `Wground=dt*(fA*vA_next+fB*vB_next)`: `(Knext+Snext)-(K+S)-Wmotor-Wground = (k/2)*(Δr)^2-(m/2)*((ΔvA)^2+(ΔvB)^2)` for this semi-implicit scheme. Do **not** claim zero residual of a discrete identity whose truncation error is nonzero.
- Failure mode: sample-grid endpoint direction/phase, coefficient reversal, initial state, guard breach or physical balance nonconformance; preserve raw negative evidence.

## Frozen quantitative classification
For each of A–E at `dt=0.01,0.005,0.0025 s`: require valid finite run, exact step counts 960/1920/3840, all physical/replay/guard checks. H2 **persistent directional drift** is SUPPORTED *in this ideal model only* if at finest dt: final TWO period displacements each have the same nonzero sign; each magnitude >0.001m; each differs by <=50% of the larger; `|r(T)-r(T-1.2)|<=0.01m`; and `|Xcm_T(dt=.005)-Xcm_T(dt=.0025)|<=max(0.002 m,0.1*|Xcm_T(.0025)|)`. If valid but conditions fail, H2 NOT SUPPORTED/CONTRADICTED **for these controls**, not a universal impossibility. If numerical convergence, end-shape recurrence, evidence or stroke condition fails, INCONCLUSIVE; never claim autonomous locomotion. Require C↔D mirror and A/B/E negative controls independently even if H2 fails. `dt=0.01` is a diagnostic coarse value, not required to be monotonic near stick/slip discontinuities.

## Integrity and completion gates
- Preregistration saved in design-only Draft PR before implementation or model outcomes.
- Implementation PR stacked on design, separate new F011 code, tests, A–E × 3 dt raw traces, F negative input/rehash/tamper, deterministic replay, independent saved-file arithmetic oracle (no production simulator import), SHA manifest; versioned schema/figure/readme/AGENTS updated together.
- Python 3.11 and 3.12 CI on exact final implementation HEAD, existing regressions, failure artifacts preserved, independent alternative math (Wolfram + separate code), no fabrication. Reviewer by same assistant or different AI is not independent human review.
- Actual model data and adoption are **different**: no merge, formal acceptance, deletion or changes to main without researcher's explicit approval. External human peer review and real-world contact validation remain unperformed.
