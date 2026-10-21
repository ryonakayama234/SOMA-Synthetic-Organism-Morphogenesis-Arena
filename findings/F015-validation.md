---
id: FIND-F015
kind: validation
status: preregistered_unexecuted
updated: 2026-10-21
issue: 48
---
# F015 — active body probing evidence ledger

## 2026-10-21 — DESIGN ONLY / NO F015 SIMULATOR RUNS
[Issue #48](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/48) / [SPEC](../topics/F015-active-body-probing/SPEC.md) / [PLAN](../experiments/F015/PLAN.md).

**UNEXECUTED.** Frozen design and theoretical Wolfram computation were prepared ahead of any F015 code, saved F015 world traces, independent F015 auditor or GitHub CI. F014 acceptance and 14/14 green main workflows establish only the prior F014 capability; they do not validate the new hypotheses.

### Wolfram Language exact rational PRECHECK, not empirical observation
For equal masses m=1kg, dt=1/4s, u=2,1,0N, prior mA=mB, zero drag, rest/reset:

| applied command u N | Linked L (aA,aB) m/s² | Unlinked fixed F (aA,aB) | Unlinked tracking T (aA,aB) | B moved L/F/T |
|---:|---|---|---|---|
| 2 | (1,1) | (1,1) | (1,1) | 1/1/1 |
| 1 | (1/2,1/2) | (0,1) | (1/2,1/2) | 1/1/1 |
| 0 | (0,0) | (-1,1) | (0,0) | 0/1/0 |

Analytical B increment each step: L/T = u/8 m/s; F = 1/4 m/s. Thus at u2 F and L are indistinguishable; holding hidden forces fixed across u reveals a discrepancy, while tracking external forces remain perfectly indistinguishable. At u1 B one-bit has no incremental discrimination (all 1), while A-only local data already differs for fixed F. Interpret B incremental utility *separately* from A-only. No noise, authenticated packet, human external review or software outcome is inferred.

### Prospective evidence gate — all unexecuted
| Gate | State |
|---|---|
| Frozen H15a-e / 15×4 matrix and counterexamples | PREREGISTERED |
| F015 module and simulation outputs | UNEXECUTED |
| Independent world-truth CSV audit + contamination negatives | UNEXECUTED |
| Byte replay and source/manifest hashes | UNEXECUTED |
| Exact implementation SHA CI Python3.11/3.12 | UNEXECUTED |
| Scientific adoption / merged main | NOT AUTHORIZED |

When execution is separately undertaken, **APPEND** real outcomes with dates, SHA, CI, independent audit findings and interpretation. Do not replace this preregistration or hide falsification/counterexample.

## 2026-10-21 — F015 implementation PR milestone (NOT YET OBSERVED)

A separate implementation branch, stacked on the frozen F015 design PR, introduces `soma/f015.py`, dedicated 15-trial F007 producer, an independently coded F007 saved-file oracle + F015 projection/science re-derivation, negative/tamper tests, and Python 3.11/3.12 inherited CI. The immutable H15a–e preregistered hypotheses and force schedule are unchanged. This is **code creation and a review gate, not measured evidence**. The exact final implementation commit, actual Actions runs, per-step observations, false-science rejection and byte replay must be separately checked before status can change. No external human peer review claimed.

**Nuanced prediction to test:** F-fixed and L differ already in the A-only local trajectory at u=1 and u=0; the B one-bit at u=0 differs too, but may provide **zero unique additional discrimination** given the entire A-only schedule. The negative result must be retained even if the primary held-force identification is supported. T-tracking remains fully non-identifying for topology.

## 2026-10-21 — FIRST OBSERVED F015 RESULT / exact source HEAD 9725c556741b373184a53e6a407644644ff75952

**This section reports real model results, not the earlier Wolfram preregistration.** [GitHub Actions #39538071630](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39538071630) completed successfully on the implementation HEAD `9725c556741b373184a53e6a407644644ff75952`.

| Gate | Actual execution (each of Python 3.11 + 3.12) |
|---|---|
| Full inherited + F015 unit regression | **191 tests PASS** |
| Python `-O` optimized F015 control/tamper tests | **5 tests PASS** |
| Frozen world cases | **5 × 3 = 15** independent 1s F007 runs |
| Strict A-local / B moved one-bit rows | **60 / 60** verified against raw source |
| Tamper/forged-science negative controls | **PASS** (rehashed B bit, topology claim, invented B value) |
| Step-2 B-packet dropout | **3** cases => augmented INCONCLUSIVE, A-only retained |
| Two-root byte-identical replay | **138 evidence files** per root, **PASS** |
| Exact-HEAD inherited and new workflow status | **15/15 success** |
| Raw evidence | [Python 3.11 artifact #12317458441](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39538071630/artifacts/12317458441) / [3.12 #12317403514](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39538071630/artifacts/12317403514) |

CI result JSON: `{"L_F_A_only_separated":true,"L_T_indistinguishable":true,"a_local_intervals":60,"b_packet_intervals":60,"byte_replay":true,"cases":15,"dropout_controls":3,"evidence_files":138,"peer_incremental_discrimination":false,"replay_files":138,"topology_identified":false}`.

### Scientific H15 interpretation — model-only, not general topology
- **H15a SUPPORTED:** At u=2N L-linked / F-fixed / T-tracking produce identical full A-local and B-onebit traces; independent saved-file byte comparison checks this.
- **H15b SUPPORTED with *important narrower inference*:** At u=1N F-fixed A acceleration is 0 vs reference L +0.5 m/s²; u=0N F-fixed A acceleration -1 vs reference L 0, and B bit F=1 vs L=0. A-only data **already separates** the held-force mimic after intervention. Therefore the 1-bit B channel has **zero unique additional discriminatory value** for these exact cases. Detection is relative to the preregistered ideal linked response, not evidence that the robot learned a true linkage model.
- **H15c SUPPORTED as negative identification result:** T-tracking and L are entirely indistinguishable across all u, even with peer bits; *physical linkage cannot be certified* on this observation channel.
- **H15d SUPPORTED (fixed tests):** Battery-rejected E remains INCONCLUSIVE; deliberate 0N trial is used only as an episode in the full 2/1/0 sequence, not alone to infer detachment; corrupt time/source, missing peer packets, full-reset violations rejected or appropriately unknown.
- **H15e SUPPORTED (software evidence integrity):** Trusted checkout source hashes and all artifact SHA256, existing independent F007 full dynamics/ledger oracle, separately coded F015 exact-reference verifier, all 15×4 row projections, tamper negatives with recomputed manifest hashes and independent deterministic replay passed.

### Independently checked exact Wolfram relations (not a separate experimental replicate)
For `u={2,1,0}N`, `(a_A(L),a_A(F),a_A(T))=({1,1,1},{1/2,0,1/2},{0,-1,0}) m/s²`. First-step B velocity increments are respectively `({1/4,1/4,1/4},{1/8,1/4,1/8},{0,1/4,0}) m/s`; the B movement bits are `(1,1,1),(1,1,1),(0,1,0)`. Observed source behavior matches these values under the frozen ideal discretization, *not* a general physics identification theorem.

## 2026-10-21 — Formal scope judgment: LIMITED ADOPTION APPROVED, final-HEAD gate remains

Based on observed experimental evidence, frozen test criteria, Wolfram precheck, complete two-version CI and distinct saved-data audit, recommend/authorize **limited scientific adoption** of the `f015.comparison.v1` *ideal F007 model response-signature comparison* and documented non-identifiability counterexample only. Do **not** adopt any `connected`, `attached`, `topology_verified` output, autonomous active experimentation, physical robot sensing, causal identification for unrestricted external forces, grounded propulsion, general energy-efficient gait, self-formed body schema or human independent peer review. This is an authorization for design+implementation integration **only after this documentation-inclusive final source SHA passes exact-head CI and source/artifact audit**, followed by actual GitHub merge and post-main workflow verification. Keep any contrary results or red CI permanently; do not rewrite pre-experiment design sections.

The identical assistant authored the main implementation and its distinct verifier: it is independent code path, **not independent human scientific review**. The truth labels belong only to researcher-side raw and audit; A's typed estimator cannot use them. Retain F011 Issue #37 and V001 #24/#26 unchanged.

