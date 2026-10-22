---
id: FIND-F018
title: F018 分離／結合の価値地図 — 設計時点の研究記録
kind: validation
status: not_executed
updated: 2026-10-22
issue: 61
---

# F018 validation — UNEXECUTED (2026-10-22)

[Issue #61](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/61) / [SPEC](../topics/F018-attachment-value/SPEC.md) / [PLAN](../experiments/F018/PLAN.md).

## What is observed?
**No F018 simulation, raw `states`, F018 code, Actions results, hypotheses gate tests, scientific adoption or main merge exist at this design checkpoint.** A theorist can demonstrate a sign-changing incentive with imposed patches; this does not imply natural morphogenesis.

## Independent Wolfram rational feasibility PRECHECK — theoretical prediction only
For two identical 1kg cells, F=+2N applied to only one, 4 semi-implicit intervals dt=.25s, initial v=0:
| pure-theory calculation | link on (2kg) | link off (1kg driver) |
|---|---:|---:|
| driven displacement (m) | 0.625 | 1.25 |
| final driven speed (m/s) | 1 | 2 |
| midpoint-positive motor work (J) | 1 | 2 |
| passive cell displacement (m) | 0.625 | 0 |

Model-dependent spatial patch gain =3J at the matching terminal position; attachment fee =0.1J per cell:
| deliberately constructed patch | join (A,B net J) | free (A,B net J) | counterfactual join-minus-free (A,B J) |
|---|---|---|---|
| near passive B when connected | (-1.1, +2.9) | (-2, 0) | (+0.9, +2.9) |
| near solo driver A when disconnected | (-1.1, -0.1) | (+1, 0) | (-2.1, -0.1) |

These calculations were evaluated by Wolfram Language on 2026-10-22; **NOT extracted from SOMA code**. They assume externally imposed fixed motor action even if it causes personal loss, no energy sharing, ideal zero-drag joint, perfect first/final patch registration, and no alternate do-nothing choice. They are a *construction*, not experimental confirmation or a stochastic estimate. The forthcoming design review must reject claims of robust incentive changes based solely on these two hand-selected resource positions.

## F018 research ledger (append later, without overwriting design stage)
| Gate | Current |
|---|---|
| H18a consent / physical eligibility | UNEXECUTED |
| H18b signed per-cell benefit crossover over frozen grid | UNEXECUTED |
| H18c no explicit link reward or information leakage | UNEXECUTED |
| H18d independent saved-world and accounting audit | UNEXECUTED |
| Exact implementation-source CI / actual raw artifacts | NONE |
| Research acceptance, merged PR, post-main CI | NOT AUTHORIZED / NONE |
| Independent human physics review | NONE |

Potential confounders to investigate: nominal contact precondition (not discovered approach), free vs linked numerical-work convention, resource patch discretization, individual sacrifice masked by group net, actuator ownership asymmetry, selective cost accounting, game-theoretic mutual consent and absent learning.
