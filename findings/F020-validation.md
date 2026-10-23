---
id: FINDINGS-F020
title: F020 代謝閉ループ・実験証拠（追記専用）
kind: scientific_findings_append_only
status: UNEXECUTED
updated: 2026-10-23
issue: 67
---
# F020 validation — UNEXECUTED / DESIGN DRAFT / NOT ADOPTED

**Current truth:** No `soma.f020` implementation, no F020 world, no F020 saved artifact, no model outcome, and no formal adoption. The design on [Issue #67](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/67) is **NOT frozen**, and cannot be represented as a finished preregistered test. [SPEC](../topics/F020-metabolic-feedback/SPEC.md) / [candidate PLAN](../experiments/F020/PLAN.md).

## Parent result (NOT F020 evidence)
F019 main commit `7de755c79fed3b806417da5c15f0115ea7ac04c8` merged 2026-10-23; 19/19 post-main workflows succeeded. F019 froze 32 environmental seeds, 512 scenarios, 3,584 worlds and observed 580 of 1,792 owner-status changes, **0/512** bilateral-positive cases; fixed high starting batteries prevented harvest affecting motor trajectories. Those observations belong exclusively to [F019 findings](F019-validation.md).

## Independent Wolfram theory precheck (NOT simulation)
+2N, dt=1/4s, no drag, initial v=0, masses 1+1kg: linked first-step energy `1/16J = 62,500µJ`; unlinked A first-step `1/8J = 125,000µJ`. For A with 75,000µJ and fee0, the linked first move is affordable; its next motor candidate at v=1/4m/s needs `3/16J = 187,500µJ` and therefore needs resource A actually acquired in a previous step. A chosen patch in this demonstration is calibration only, never part of random-field inference.

## Required evidence to append, without rewriting negative outcomes
| Item | Observed F020 data | Gate |
|---|---|---|
| Exact freeze SHA / source and sample plan | NONE | NOT FROZEN |
| Feedback versus deferred-credit causal forks | NONE | UNEXECUTED |
| A/B individual net and rejected/accepted step timeline | NONE | UNEXECUTED |
| Boundary, no-resource, B-only, high-budget and mirror controls | NONE | UNEXECUTED |
| Independent saved-data verification and rehashed tamper detection | NONE | UNEXECUTED |
| Python 3.11/3.12, source-bound SHA, two-root replay and post-merge CI | NONE | UNEXECUTED |
| Critical review, bounded adoption decision | NONE | NOT AUTHORIZED |

Scientific labels: SUPPORTED / REFUTED / INCONCLUSIVE / UNEXECUTED, separate from software technical acceptance. No external human peer review is claimed.

## 2026-10-23 pre-observation design audit (NOT F020 world evidence)

An internal independent-formula review of F005/F007 and Wolfram exact fractions revealed that the initial 1,000,000 µJ "high-battery" candidate cannot run four nonlinked ±2N 0.25s steps without energy stalls. Expected positive motor work (linear-velocity integral with F005 ceil µJ gate) is NN **2,000,000 µJ**, YY **1,000,000 µJ**, in contrast to the larger motor-force × semi-implicit displacement product. High-budget candidate revised to **4,000,000 µJ pre-observation**, while preserving the 32-seed, 1536 proposed scenarios/6144 candidate worlds factorial. Detailed critique and contract timing: [design review](../docs/reviews/2026-10-23-F020-preobservation-audit.md). F020 is still **NOT FROZEN / UNEXECUTED / NOT ADOPTED**; no real F020 trajectory or positive result has been observed.
