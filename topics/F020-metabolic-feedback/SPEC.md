---
id: F020
title: 代謝閉ループ：有限資源の取得が次の運動を変えるか
kind: capability_proposal
status: LIMITED_SIMULATION_MEASUREMENT_INSTRUMENT_MERGED
updated: 2026-10-23
issue: 67
predecessors: [F002, F005, F007, F018, F019]
---
# F020 — Metabolic Closure (historical design + frozen implementation draft; NOT adopted)

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

## Pre-observation quantitative audit (2026-10-23; NOT simulation)
The [internal design review](../../docs/reviews/2026-10-23-F020-preobservation-audit.md) found that 1,000,000 µJ cannot serve as F019-parity for the nonlinked 4-step world (2,000,000 µJ positive motor work). The unfrozen high-budget candidate is now 4,000,000 µJ; same 32 seeds/1536 proposed scenarios/6144 worlds. Timing must honor F005 `ceil(1e6 × positive motor work)` and quarantine delayed claimant credits until after step 4. This revision is **pre-F020 observation**, not evidence or an adoption verdict.

## Decision gates
1. Freeze exact seeds, samples, event order, expected calibration and negative tests in a separate **pre-first-world design commit**; this document is currently a reviewable DRAFT.
2. Implement one-step ledger→F007→first-entry→F002 loop in a **separate implementation PR**, with complete architecture, contracts, tests, source-bound artifacts and append-only findings.
3. Compare signed results, nulls and per-seed dependencies without reward shaping; make scientific interpretation separately from the technical acceptance of a limited measurement instrument.
4. No adoption or main merge before exact-source CI, adversarial audit and critical review. Internal AI role-switching is NOT external peer review.


## 2026-10-23 implementation branch update — protocol frozen, not main

The earlier headings/gates above document the **pre-execution** stage. Protocol `f020.v1` was separately frozen at commit `f3e3a4de4ff47677db575efaafe342655dede6c2` in [FROZEN_V1.md](../../experiments/F020/FROZEN_V1.md) **before the first F020 world**. Stacked [implementation PR #69](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/69) contains the causal `soma/f020.py`, source-bound 6144-world suite, independent source/physics/energy reconstruction, synthetic positive controls and seed-block outcomes. No F001–F019 semantics changed. This is **not** autonomy, actual metabolism, a decision-learning loop or a main-branch accepted research conclusion. Refer to append-only [findings](../../findings/F020-validation.md) and exact-head CI for empirical results.


## 2026-10-23 formal scope update — limited F020 tool integrated into main

2026-10-23 formal bounded integration: [design #68](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/68) merged to main at `2d2ae185d428a4dfb685c22b7b9cfcbca2214b79`; [implementation #69](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/69) merged to main at `562dfc163791ffb68aa52e8b12c3fa2e33ada9c7` preserving first-world freeze `f3e3a4de4ff47677db575efaafe342655dede6c2`. **Adopted scope: 1D F020 same-cell k-end resource→k+1 motor eligibility simulation/measurement instrument ONLY**; not self-assembly, independently acting B, metabolic biology, learned consent or fitness. 1,536 primary scenes/6,144 worlds/3,072 timing contrasts; 321 motor/trajectory effects, 64 claimant-map changes (74 additional 1J A claims), of 321 changed-trajectory contrasts 263 A-net-negative, 36 equal, 22 A-net-positive; B net identical across modes. [Exact checked-out final implementation-head F001–F020 20/20 workflow success](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39966063549); [internal critical interpretation](../../docs/decisions/2026-10-23-F020-limited-acceptance.md). Post-main **all-workflow gate is tracked separately** and should not be asserted complete solely from the PR-head run. Internal AI review and code-independent auditor are NOT external human peer review.

H20a (causal k+1 motor eligibility) and H20d (archived independent source-bound software reproduction) are supported **within the fixed simulation**; H20b (resource access consequences) is supported descriptively only for 64 matched pairs under 32 reused field seed blocks. H20c (B cannot energize A) passed. Autonomously self-chosen morphological coalition value and survival benefit were not demonstrated; motor-work costs often outweigh additional resources. Historical draft assertions above reflect earlier stages.
