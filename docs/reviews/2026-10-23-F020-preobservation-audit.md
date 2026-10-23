---
id: REVIEW-F020-20261023
title: F020 事前観測レビュー：高電池対照と資源クレジット時刻
kind: design_review
status: PREOBS_DESIGN_CORRECTION_NO_WORLD_EXECUTION
updated: 2026-10-23
issue: 67
---

# F020 pre-observation design audit — 2026-10-23

Review scope: draft PR #68, issue #67, the F005/F007 positive motor work implementation and existing F019 resource sampler. **This is an internal computational critique, NOT external scientific peer review, NOT a F020 simulator observation, and NOT a frozen protocol.**

## Blocking defect caught before the first F020 world

The draft PLAN called **1,000,000 µJ** a "high-battery F019-parity control." This amount is *not* sufficient to reproduce the nonlinked four-step (NN) fixed A-only motor world without harvest. F005 and F007 charge `ceil(1e6 × positive_motor_work_J)`, where positive work integrates motor power using midpoint velocity under linearly interpolated velocity; it is **not** `force × semi-implicit displacement`.

For force magnitude 2 N, dt=0.25 s, zero initial velocity, zero drag, no resource:
- NN, effective mass 1 kg: expected positive motor work [1/8, 3/8, 5/8, 7/8] J = total **2 J = 2,000,000 µJ**.
- YY, effective mass 2 kg: expected work [1/16, 3/16, 5/16, 7/16] J = total **1 J = 1,000,000 µJ**.
- A 25,000 µJ step-zero join fee reduces the usable balance for YY before the first step.

Thus a nominal 1,000,000 µJ high control fails for NN without harvesting (third step; 1.125 J cumulative) and fails YY with 25,000 µJ upfront fee at its fourth step. The PLAN's upper budget was changed **pre-observation** from 1,000,000 to **4,000,000 µJ** while preserving three initial-balance levels, 32 independent resource seeds, the 1536 scenario / 6144 world candidate size, and the declared zero/nonzero controls. This is a *design correction*, not post-outcome tuning. The 4M group is expected to reproduce F019 motor trajectories in all four paired arms, regardless of actual patch availability, subject to source-verified tests.

## Required contract checks before protocol freeze

1. Pre-step F002 available A balance alone gates A's candidate F005 work, using `ceil(positive_motor_work_J × 1_000_000)`; F007 mechanical advance (including inertia when motor rejected) comes after gating. No harvest from step k funds motor of the same step.
2. At step-end, claimant's resource amount is credited to the same cell for next step in feedback. In deferred-credit, claims deplete the same physical resource but remain explicitly quarantined by claimant until after step 4; F002 external acquire is then posted *in original claim order*. Deferred resource is not a spendable phantom balance.
3. Preserve separate `available_balance_uj` and `pending_credit_uj` in saved per-cell snapshots, with paired `claims.csv` and ledger event indices (including post-step settlement). Never allow B-only harvest to authorize an A motor.
4. No-field, B-only-harvest, step-one/step-two timing, 0/25k fee, motor-off, force reflection, rejected-while-inertial, high-budget equality and F019 nonregression must be independently replayed from files.
5. Predeclare integer budget and float tolerance behavior, deterministic event-order tie breaking, source-hash binding, primary per-seed ecological block unit, and rejection of rehashed semantic tamper.

## 2026-10-23 exact-rational artificial patch calibration — Wolfram, NOT F020 simulation

Construct a **separate calibration-only** field with one 1,000,000µJ patch centered at x=1/16m and radius 1/200m. Initial xA=0m, xB=1/10m, mA=mB=1kg, both balances=75,000µJ, fee=0, +2N A-only effective motor, dt=1/4s, 4 steps, zero drag. The patch is not a frozen F019 sampled-field draw; never include this case in the primary 32-seed ecological estimand.

The first linked A step costs 62,500µJ, then A crosses the patch (first-entry fraction 23/25 within step1 using 1D linear segment) and claims 1J at **the end of step1**. Same-step motor eligibility must remain independent of this credit. Wolfram exact rational recurrence yields:

| Arm | xA(k=0..4) in meters | A applied motor k=1..4 | step-4 spendable A balance before deferred final settlement |
|---|---|---|---|
| YY feedback | [0, 1/16, 3/16, 3/8, 5/8] | [yes,yes,yes,yes] | 3/40 J = 75,000µJ |
| YY deferred_credit | [0, 1/16, 1/8, 3/16, 1/4] | [yes,no,no,no] | 1/80 J = 12,500µJ, plus 1J pending |
| NN feedback | [0,0,0,0,0] | [no,no,no,no] | 3/40 J = 75,000µJ |
| NN deferred_credit | [0,0,0,0,0] | [no,no,no,no] | 3/40 J = 75,000µJ |

In YY deferred, A's k=2 motor is rejected but its previously acquired v=1/4 m/s remains; coasting gives xA=1/8 m at k=2. Every A-centered endpoint and motor boolean is a **future F020 implementation assertion**, not an observed simulator output or demonstration of autonomous joining. The delta xA at k4 from enabling same-cell feedback is 3/8m; this isolated calibrated effect is engineered and not ecological inference.

## Open blockers

This review does **not** freeze the draft. Before F020 v1 freeze and implementation: finalize exact saved CSV/JSON columns, conflict/tie semantics, quantized work rule, first-entry interpolation, deferred-acquire bookkeeping and thresholds. F020 should remain **UNEXECUTED / NOT ADOPTED** until separate experimental data, independent verifier, CI and a reasoned verdict exist.

Navigation: [F020 PLAN](../../experiments/F020/PLAN.md), [SPEC](../../topics/F020-metabolic-feedback/SPEC.md), [architecture](../ARCHITECTURE.md), [data contract](../DATA_CONTRACTS.md), [unexecuted findings](../../findings/F020-validation.md), [Issue #67](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/67).
