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


## 2026-10-22 pre-execution feasibility falsification insight (still NO F018 simulation)

The worked Wolfram near-B case (`Δ_A_fixed=+0.9J`) **fails a voluntary-action sanity check**: A receives `net_A(join)=-1.1J`, whereas a feasible no-motor individual outside option would return 0J under zero baseline upkeep, hence `Δ_A_outside=-1.1J`. This is a *theoretical counterexample to equating fixed-action improvement with voluntary self-interest*. It does not falsify H18 in an unrun SOMA world; the experiment must pre-register outside options and test whether any positive individual participation region truly exists.

**Status remains UNFROZEN/UNEXECUTED**, no simulation or empirical evidence. The negative observation is about the *model interpretation of the theory*, and is preserved for audit before creating motor/attachment decision modules.


## Implementation candidate checkpoint — 2026-10-22 (NOT A SCIENCE RESULT)

Frozen 90-scenario / 630-world protocol is now explicitly published in the design PLAN before any F018 simulator run; prior free-form proposals and their Wolfram values are retained above as historical research motivation. The new implementation branch proposes `soma/f018.py`, saved-raw `run_suite.py`, independent `verify.py`, `attack_test.py`, `analyze.py`, two-Python test/CI and synchronized system/data diagrams.

**At this checkpoint, CI and actual F018 experiment data have NOT been inspected or accepted.** The Wolfram new dual-terminal-patch rational precheck gives A=+1.9J and B=+2.9J versus restricted unjoined A-motor {-2,0,+2} outside choices at radius .01m, fee .1J, +2N. This is a **theoretical/engineered terminal-resource example only**, separate from any future simulated measurement. Same original B-only patch theory gives A joined -1.1J, fixed-action delta +.9J, but outside delta -1.1J. Both must be verified on exact saved-world data.

Follow-up science decision must classify whether the built system satisfies all saved-world gates and whether any Pareto-positive region survives predeclared widths and sign reversal. Do not infer policy incentive discovery, Nash equilibrium, stable morphology, environmental generalization or physical power conservation from synthetic F002 bookkeeping.

## 2026-10-22 first F018 executed candidate evidence — NOT ADOPTED

**Actual implementation source SHA `26160c5155d4954b07505f65960acb2e1cd62da2`** and [GitHub Actions #39737330499](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39737330499): frozen F018 CI **SUCCESS on Python 3.11 AND 3.12**. Both ran inherited regression tests, optimized F018 negatives, 90 deterministic factorial scenes / 630 four-step F007 worlds (360 primary consent and 270 NN outside options), 630 saved-data mechanical/resource/F002 integer-ledger audits with zero µJ residual, three rehashed score/physics/ledger tampering negatives, and byte-identical two-root replay. GitHub evidence: [3.11 raw archive](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39737330499/artifacts/12408055374), [3.12 raw archive](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39737330499/artifacts/12408035550).

| Resource layout, 18 deterministic scenes each | Both `Δfixed >0` | Both `Δoutside >0` |
|---|---:|---:|
| NONE | 0/18 | 0/18 |
| B_LINK | 18/18 | **0/18** |
| A_SOLO | 0/18 | 0/18 |
| DUAL_LINK | 18/18 | **18/18** |
| DUAL_SOLO | 0/18 | 0/18 |
| **Total** | **36/90** | **18/90** |

**Actual measured individual examples at +2N, 0.01m patch radius, 0.1J fee per cell:** `DUAL_LINK` joined net A=+1,900,000µJ/B=+2,900,000µJ, `Δfixed` A=+3,900,000µJ/B=+2,900,000µJ, and `Δoutside` A=+1,900,000µJ/B=+2,900,000µJ. `B_LINK` joined net A=-1,100,000µJ/B=+2,900,000µJ, `Δfixed` A=+900,000µJ/B=+2,900,000µJ, but `Δoutside_A=-1,100,000µJ`. These are **SOMA F018 observed saved-world results**, numerically consistent with the separate Wolfram rational theory.

The 18 dual-benefit cases are **only** the deliberately engineered DUAL_LINK resource positions crossed with force sign, radius, and fee; they are not 18 independent random discoveries or ecological generalization. Terminal harvest, omniscient restricted A-only outside menu, no approach, no B motor, no learned consent, no equilibrium, no real physics hardware or spontaneous persistent body. The mechanism merely permits and measures prescribed connection. This was audited by code written by the same assistant, **not external human peer review**.

**Provenance:** observations above belong to SHA `26160c5`; the current hardening/docs commit changes source hashes. A final exact-SHA CI and independent adoption judgment are still required. No F018 main merge or formal research acceptance is claimed.
 
## Independent code-review correction before adoption — 2026-10-22

The GitHub Codex automated review on implementation PR #63 at `c5045da` identified a **P1 semantic evidence-auditor gap**: some archived F007 `states.csv` fields (`decision_reason`, `ledger_event_index`, nullable candidate motor-work fields, and initial diagnostic values) were not checked, so rehashed forgeries in those fields could pass verification even while score and trajectory totals stayed unchanged. **This is a real issue**, not a counterexample to the physical payoff estimates. The adoption requirement H18d includes trustworthy archived evidence, so it must be corrected before merge.

Correction: `verify.py` now requires exact initial nullable/zero fields, F007-only motor event indices (distinct from F018 upfront-join-fee F002 indices), per-step motor decision reasons, and nullable zero-command candidate work. `attack_test.py` additionally alters these fields with SHA hashes rebuilt and requires semantic rejection. `test_f018_experiment.py` checks this expanded attack suite. The code review thread must be resolved only after exact revised-source Python3.11/3.12 CI confirms.

The original 630-world observations at `26160c5` and corrected-source replays must be separately attributed; never present a pre-fix verification as evidence of the stronger post-fix claim.

## 2026-10-22 internal scientific decision — F018 v1 LIMITED ADOPTION APPROVED

**Decision subject:** one narrow research capability only: a fixed, researcher-imposed pair of step-0 attachment requests for two F003-eligible 1D cells, an ideal link/no-link gate reusing F007 A-only externally effective drive, per-cell resource-and-motor F002 accounting, and paired **investigator-only** fixed-action/outside-option value estimates. **This does NOT approve spontaneous voluntary joining or any body emergence claim.**

The decision is based on the separately merged frozen protocol PR #62 (`0cab39b`), the executed independent saved-world evidence and **review-hardened source SHA `f8dd2b6b4eb41364c75adbb6b224088df3a4775b`**: [Actions #39758187922](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39758187922) confirms **18/18 inherited and F018 workflows SUCCESS**, including 3.11/3.12 full + `-O` unit tests, independent 630-world oracle, 90 scenario summaries, 8 SHA-rehashed semantic forgery negatives (score/physics/ledger plus five Codex P1 uncovered state-field defects), double-byte replay and artifact upload. The earlier P1 review concern at PR #63 about unchecked archived diagnostic columns was **confirmed and fixed** before adoption, with the original review thread resolved only following exact-source green tests.

Scientific judgment by frozen gate:
- **H18a: supported within this ideal contact-ready F003/F007 1D contract.** Strict mutually-YES initial attachment, nonconsent remains unlinked, invalid initial distance/relative speed rejects without a snap; no mechanical/electric benefit from nonexistent links.
- **H18b: supported narrowly as an investigator-measured conditional payoff landscape**, NOT generalized emergent incentive: full 90 predeclared deterministic scenarios × 7 causal/outside worlds each; 36/90 both `Δfixed>0`, only **18/90** both `Δoutside>0`, all latter in engineered `DUAL_LINK` geometry, no positives in other 72. At DUAL_LINK +2N/0.01m/0.1J cost, own joined net A+1.9J, B+2.9J and own outside deltas +1.9/+2.9J; at B_LINK, `Δfixed_A=+0.9J` but `Δoutside_A=-1.1J`. Signed direction, three radii and three costs covered, **but B motor-owner exchange and natural ecology NOT tested**.
- **H18c: supported within explicit synthetic bookkeeping semantics.** No direct join score and no implicit A-to-B energy transfer; only geometrically sampled *terminal* exogenous patches plus F007 positive mechanical motor spending and declared F002 initial join fee. A B-resource capture does not automatically become A's payoff.
- **H18d: supported technically following P1 audit correction**, but not external human peer review: integer µJ residual zero for each of 630 runs, complete independent recomputation of saved F007 diagnostic/physics/ledger columns, replay consistency and source/artifact SHA controls, 8 rehashed negative attacks rejected and 18/18 exact-SHA CI green.

**Conclusions NOT approved:** an agent actually selecting YES on the basis of its own sensor/history; the ex-post outside max being locally knowable or strategically stable; equilibrium/partner negotiation, spontaneous spatial approach/docking, persistent/reconfigurable bodies, arbitrary resources/collisions, B-motor identity symmetry, 2D/3D, hardware energy/electrical conservation, or general ecological robustness. The model deliberately places resource patches at theoretical terminal positions, and the 18 outside-positive conditions are structurally correlated (force-sign/radius/fee replicates of one chosen layout, not random independent trials).

**Adoption/merge rule:** The *limited functionality and scoped finding* are accepted for SOMA's research toolkit, not its ultimate emergence claim. Integrate PR #63 only after the **documentation-inclusive final source SHA** runs the same inherited+F018 tests fully green and provenance is preserved, then separately inspect post-main Actions. PR/Issue comments retain exact merge and post-main SHA/links without rewriting earlier evidence. Further studies must use separately frozen plans for learned choices, B-owned motors or non-tailored environments.
