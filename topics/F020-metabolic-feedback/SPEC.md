---
id: F020
title: 代謝閉ループ：有限資源の取得が次の運動を変えるか
kind: capability_proposal
status: DESIGN_DRAFT_NOT_FROZEN_UNEXECUTED
updated: 2026-10-23
issue: 67
predecessors: [F002, F005, F007, F018, F019]
---
# F020 — Metabolic Closure (design draft; NOT implemented or adopted)

[Issue #67](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/67) / [experiment draft](../../experiments/F020/PLAN.md) / [unexecuted findings](../../findings/F020-validation.md) / [research decision](../../docs/decisions/2026-10-23-F020-selection.md).

## Scientific question
Can **path-acquired** finite external energy at the end of step k make the SAME cell's **next** motor step feasible, causing an altered subsequent motion path or another resource encounter, relative to a matched delayed-credit counterfactual? F019's initial motor energy was sufficient and its acquired resource had no within-world motor effect. F020 changes only that causal connection.

## H20 and rival explanations
- **H20a (timing/energy)**: acquisition into A at end of k may authorize A's motor at k+1, never retrospectively at k; a motor action is rejected whenever the candidate F005 positive-work charge exceeds the available F002 A balance. Rejection does not eliminate passive/inertial motion.
- **H20b (ecological intervention)**: for matched trajectory-blind fields and initial conditions, feedback versus deferred-credit can change A's first motor rejection, motion and subsequent A/B patch ownership; a zero effect and all benefit signs are legitimate outcomes, not gate failures.
- **H20c (non-transfer)**: B's acquired energy changes B's own F002 balance only; it cannot energize A. Fixed YY/NN (not autonomously chosen), no-resource, motor-off, high-battery F019-parity and artificial boundary calibration controls must expose leakage and rounding mistakes.
- **H20d (evidence)**: producer's trajectories, claims, ledger and summaries must be re-derived from saved data by a separate no-producer-import verifier; forged/rehashed data rejected, two clean-root byte replay, SHA manifest, Python 3.11/3.12 full regressions and exact SHA workflows.
- **Rivals**: apparent benefit from F018-style endpoint tuning, cherry-picked seeds, accidental B→A transfer, post-hoc threshold alteration, same-step backdating, field lookahead, or incorrect positive-work/quanta.

## Scope and model limitations
Keep F007's one-dimensional ideal effective A motor (not physical ground reaction), F018 step-0 bilateral consent, ideal fixed connection, F019 SHA256 trajectory-blind patches and first-claim depletion. No B motor, no dynamic reconnection or actual approach/contact, no policy learning, no energy transfer, no chemical metabolism, no organism or evolutionary claims. Existing f001–f019 v1 data and frozen protocols remain unchanged. F020 is a **new versioned orchestrator**, not a modification of F019 historical semantics.

Cell-local action input consists only of a fixed experimental motor command and the cell's permitted balance; patch positions, linked-vs-unlinked fork outcomes and future events are **researcher-only truth**. All joined/nonjoined assignments are investigator-specified. Direct joint reward is never introduced.

## Decision gates
1. Freeze exact seeds, samples, event order, expected calibration and negative tests in a separate **pre-first-world design commit**; this document is currently a reviewable DRAFT.
2. Implement one-step ledger→F007→first-entry→F002 loop in a **separate implementation PR**, with complete architecture, contracts, tests, source-bound artifacts and append-only findings.
3. Compare signed results, nulls and per-seed dependencies without reward shaping; make scientific interpretation separately from the technical acceptance of a limited measurement instrument.
4. No adoption or main merge before exact-source CI, adversarial audit and critical review. Internal AI role-switching is NOT external peer review.
