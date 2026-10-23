---
id: EXP-F020
title: F020 代謝閉ループ・事前登録ドラフト
kind: experimental_plan
status: DRAFT_PREOBS_NOT_FROZEN_UNEXECUTED
updated: 2026-10-23
issue: 67
---
# F020 experiment PLAN — candidate, NOT FROZEN / NOT EXECUTED

[Question](../../topics/F020-metabolic-feedback/SPEC.md) / [Issue #67](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/67) / [append-only findings](../../findings/F020-validation.md).

## Required preregistration freeze before first production world
Treat ALL numbers below as **draft candidates** to be critically checked and frozen in a later design commit before ANY F020 simulation. Do not use outcomes to select seeds or adjust gates. Preserve F019 v1 unchanged.

- F019 field generator unchanged: seeds 0–31 (32 environment blocks), sign {-1,+1}, patch count {2,5}, radius {0.02,0.06} m, 1,000,000µJ per patch, deterministic SHA256 lattice generator, no initial occupancy and no regeneration.
- Initial positions A=0m, B=.1m, zero velocity, mass each 1kg, ideal link .1m if both step-zero intents YY, no link NN; no drag, externally effective motor on **A only** with fixed ±2N. dt=.25s; total 1.0s / four steps (all candidate values inherited from F019).
- Distinct from F019: initial balance for **each** cell in {75,000;250,000;4,000,000} µJ, capacity 20,000,000µJ; per-cell upfront attachment fee in {0;25,000} µJ. Fee cannot borrow from future patches.
- The 4,000,000 µJ group is a **high-budget, harvest-independent F019-trajectory parity control**: four steps of A-only motor work consume exactly 2,000,000 µJ in NN and 1,000,000 µJ in YY without harvest under the ideal zero-drag model. The former 1,000,000 µJ candidate was insufficient for NN and YY-with-fee; corrected **before any F020 world** following [internal audit](../../docs/reviews/2026-10-23-F020-preobservation-audit.md). F005/F007 charge the ceiling of time-integrated positive motor work, **not** force times semi-implicit position difference.
- Candidate factorial 32 seeds × 2 signs × 2 densities × 2 widths × 3 balances × 2 fees = **1536 scenarios**, with exactly four paired forks: YY/NN × `feedback` / `deferred_credit` = **6144 F020 worlds**. Only 32 resource seeds are distinct; repeated factor combinations are correlated, NOT 1536 independent ecological draws.
- No fixed expected count or sign of resource-enabled moves or private bilateral gains; observed zeros remain valid. Calibrations with chosen patches must NEVER enter the random-field primary estimand.

## Per-world order and causal interventions
Initial F002 balances -> consent gate -> upfront fee if YY -> for k=1..4:
1. Based only on A's *currently motor-eligible balance*, F005 candidate positive work for the proposed A-only step and F007 motor acceptance are evaluated; no future patch map enters controller.
2. Advance one F007 step, preserving time, positions, velocities, mechanical diagnostics and externally effective-force limitations; reject motor without inventing collision or zeroing inertia.
3. Apply F019 closed-interval first entry to both path segments, order candidates by (step, fraction, patch_id, cell_id), claim each patch once and mark depleted.
4. In `feedback`, credit acquired µJ to its actual claimant via F002 at end of k. A may use **its own** resulting balance at k+1, not during k. In `deferred_credit`, each claim irreversibly depletes its patch, but remains per-claimant **pending/quarantined**, never available for motor eligibility during steps 1–4; only after step 4, post F002 acquire events in original claim order. Log `available_balance_uj`, `pending_credit_uj` and ledger event indices separately. Never silently transfer B balance to A.
5. Persist detailed pre-motor balance, cost and decision, physical state before/after, chronological resource-entry record, posted/quarantined credit, claimant's balance, and event indices for independent auditing.

Important: F007's static full-episode `simulate` **cannot** be reused as-is then post-hoc supplemented by F019 harvesting: F020 needs a genuine one-step feedback orchestrator with separate versioned output. No mutation of frozen F019 / F007 schemas.

## Calibration-only theoretical control (Wolfram, pre-F020 execution)
For 1kg A and B, A force +2N, dt=1/4s, v0=0, zero drag:
- YY effective mass 2kg: v1=1/4m/s; x1_A=1/16m, first-step positive ideal work **1/16J = 62,500µJ**.
- NN A alone: v1=1/2m/s; x1_A=1/8m, positive ideal work **1/8J = 125,000µJ**.
- The four positive motor work charges are **NN: 125,000, 375,000, 625,000, 875,000 µJ (total 2,000,000)** and **YY: 62,500, 187,500, 312,500, 437,500 µJ (total 1,000,000)** with uninterrupted force. This uses F005 time-integrated power and F007 kinematics, not semi-implicit displacement as motor work. Therefore the 4M initial-budget group has no motor rejection even with a 25k attachment fee and no patches.
- With both at 75,000µJ and fee=0, YY first step affordable and NN first step rejected. For YY A after first step =12,500µJ; second step positive-work request if motor applied **3/16J=187,500µJ**. An artificial A-accessible 1J patch at first step would make that second step affordable; absent that patch it would be rejected. This is a **hand-constructed non-primary calibration**, not evidence of a naturally advantageous coalition.
- Correctness gates include 0 resource, patch reached only by B, fee-boundary, stationary patch, duplicate claimant, capacity, rounding, rejected action, ± sign mirror, large battery reproducing original high-battery trajectories, and positive-work conservative F005 order.

## Main estimands and audits
Motor accepted/rejected per A step and first rejection time; displacement and later patch claims under feedback minus deferred mode; per-cell acquired/spent/join fee/net and total residual (µJ); deterministic claims and resource depletion; per-seed block summaries, many-to-one factor dependence; null and asymmetric outcomes. Independent verifier MUST calculate step-by-step causal events from source-bound saved state, not call producer `soma.f020`, `soma.f019` or F007 simulator. Hash manifests alone are not adequate. Separate rehashed-tamper tests target pre/post balances, motor flags, patch timestamps, claimant, repeat depletion and source file hash.

## Decision
Technical correctness is NOT conditioned on finding self-sustaining behavior or bilateral positive payoff. A limited internal *software measurement instrument* might be adopted after evidence; **self-assembly, organismality, autonomous metabolism, evolutionary fitness and ecological generalization remain unproven**. Reviewers must freeze detailed contract/tolerances as a new append-only revision before first run.
