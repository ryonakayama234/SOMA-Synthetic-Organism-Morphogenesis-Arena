---
id: EXP-F010
status: preregistered_not_executed
updated: 2026-10-19
---
# F010 A–F fixed controls — before F010 software execution

**Wolfram exact rational mathematical predictions, not F010 software observations.**
F007 v1 unchanged, independent zero-initial-state runs. mA=mB=1 kg; initial x=(0,0.5)m; h=0.25s; T=1s; drag0; motor u=(2,1,0.5)N, each as separate trial; A battery 3,000,000 µJ, B balance zero. All applied force must equal commanded force or mark inconclusive.

| Group | A/B physics / hidden A force | a at u=(2,1,.5) m/s² | alpha kg^-1; beta m/s² | xA(T) m at u=(2,1,.5) |
| --- | --- | --- | --- | --- |
| A linked | ideal mechanical link, no hidden force | 1, 1/2, 1/4 | 1/2;0 | 5/8, 5/16, 5/32 |
| B constant | detached, external A force -1 N constant across trials | 1,0,-1/2 | 1;-1 | 5/8,0,-5/16 |
| C adaptive | detached, external A force -u/2 (researcher intervention, NOT A input) | 1,1/2,1/4 | 1/2;0 | 5/8,5/16,5/32 |
| D free | detached, external A force 0 N | 2,1,1/2 | 1;0 | 5/4,5/8,5/16 |
| E no excitation | detached, A battery 0, u commands 2,1,.5 | 0,0,0; motor applied 0 | INCONCLUSIVE | 0,0,0 |
| F integrity | bad local field/type, wrong order, duplicate input, missing row, altered SHA+summary, tampered output, exact replay | reject/INCONCLUSIVE | none | n/a |

For A=C, equality extends to all 4 intervals of A-local velocity, applied motor force, battery balances and F008 detection, for each chosen u. This is **non-identifiability**, not classifier failure. For B at u=1 expected acceleration 0 **with motor applied 1**, so zero acceleration alone is not grounds for rejecting a run. For E motor applied 0 is a diagnostic; do not fit using commanded force.
Response fit uses u2=2,u1=1, and u=.5 only as reserved holdout. Require all four dt=.25 acceleration intervals, exact time order, constant applied input within trial, stable acceleration, no F007 motor rejection. Tolerance 1e-12 for these rational controls only. `not_excited` and `insufficient_excitation` are conclusive *inconclusive* statuses, not evidence for a topology.

Wolfram reference: a=(u+d)/1 if unattached, a=u/2 if attached; x_final=(5/8)a via semi-implicit Euler with 4 steps; exact rational 2x2 design matrix rank 2 for distinct inputs. Alpha/beta are descriptive coefficients; an adversarial input-dependent disturbance generates the same alpha and beta as added inertia.
F010 issue #31 -> design Draft PR -> separately stacked implementation Draft PR. Save all negative tests and known limits; never relabel these mathematical predictions as SOMA observations before an actual CI run.
