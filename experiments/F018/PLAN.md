---
id: EXP-F018
title: F018 事前設計 — 接続要求と反事実的個体利得
kind: experiment_plan
status: frozen_v1
updated: 2026-10-22
issue: 61
---

# F018 experiment plan — FROZEN v1 / UNEXECUTED

[Hypotheses](../../topics/F018-attachment-value/SPEC.md) / [Issue #61](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/61) / [findings](../../findings/F018-validation.md).

## Research separation
Step 1: prove the selection gate, invariant mechanics and per-cell accounting under **researcher-fixed** requests (F018). Step 2 (future distinct experiment): can two cells with local observation/learning independently choose attachment and detachment when favorable? Do not merge these claims. No new simulation or formal adoption occurs in this design PR.

## Candidate factorial treatments (to review and freeze; counts not final)
- Attach intents: [yes,yes], [yes,no], [no,yes], [no,no].
- Local energy/resource: neither resource, reachable-by-linked-passive patch, reachable-by-solo-driver patch, a fixed *spatial grid/width sweep* to detect dependence on arbitrarily narrow/handpicked rewards; mirror x -> -x.
- Fee cost per joining cell: zero, moderate, high. As an explicit F002 numerical debit, not a validated connector mechanism. No phantom fee on refused attachment unless separately stipulated and preregistered.
- Identical cell motor ownership swapped, motor sign mirrored, unpowered/no-motor and no-resource conditions; same physics/effective external motor semantics in all paired forks.
- Initial geometry F003-eligible at step0 and invalid off-manifold rejection controls. Later detach is F003-known but not part of this initial-choice experiment.

## Run / evidence process
1. Design-stage Wolfram arithmetic: F003/F001 mass combination, 4 steps × .25s, force+2N, midpoint work, per-cell 0.1J fee and 3J resource. This is a **feasibility demonstration only** and produced no SOMA world trajectories.
2. Before execution, independently audit physical motor/energy integration boundaries, enumerate grid/seeds, prespecify collision/patch sampling tolerance, fixed test gates, source SHA and true sampling independence. Freeze SPEC+PLAN in design PR and merge design **before** implementation evidence.
3. Implementation (separate branch/PR): source code module + tests + paired raw `states.csv`, `events.jsonl`, `ledger.jsonl`, `worlds.jsonl`, `summary.json`, `manifest.json` and independent saved-data calculator. Source-bound two-root deterministic replay; malformed ledger/rehashed-score/invalid geometry negatives; Python3.11+3.12 regression.
4. Analyze signed `delta_i_uj` at **cell level**, Pareto region, summed net, group-level seed clusters if stochastic. Any support/contradiction specific to the frozen physical/resource conditions only.
5. Scientific decision append-only in findings. No merge/adoption until *final documentation-inclusive* exact-SHA CI and verifiable artifacts; check main CI if eventually merged. Outcomes cannot be backfilled into this design text.

## Test labels / inference protection
- baseline NO/NO vs YES/YES is not by itself proof of consent learning; YES/NO and NO/YES are needed to verify mutual gating.
- Natural variance due to resource jitter is an investigator-only factor. A policy should never receive scene ID, full trajectories, winner label or `delta`.
- Swap cell/motor assignment to prevent an accidental permanently privileged sender/driver. Separate `net_A`, `net_B` and `net_A+net_B` even when only one gains.
- Jointly favorable conditions do not prove a viable *multi-agent decision equilibrium* without training both agents and testing incentives against unilateral deviation, which is out of scope.


## Pre-execution reviewer addendum: outside-option control required (2026-10-22)

The original engineered 'B near' resource patch gives a positive fixed-action fork delta for both cells **while driver A's absolute joined return is negative**. If the agent can decline motion, it could avoid the loss altogether; therefore no voluntary attachment incentive has been established even in the theoretical example.

Before freezing, explicitly include `no_motor` and available non-joined motor actions in the counterfactual menu, and compute two separate tables:
- `DeltaFixed_i`: hold same motor effort fixed, change physical link only.
- `DeltaOutside_i`: join-protocol individual return minus best feasible unjoined *individual* option including idle.

A positive fixed-action delta but a negative outside-option delta is **not** an indication of self-interested joining. Compare both cells' outside options, not just sum. Optimizing independent actions across both cells is a bounded additional model/experiment design choice and must not use future information unavailable to local controllers. True strategic equilibrium and learned policies remain out of F018 scope.

## F018 v1 preregistration freeze — 2026-10-22 (before first F018 code/world)

The preceding sections preserve candidate history. **The following precise protocol supersedes their candidate scopes**; implementation must not silently extend or tune it after inspecting experiment outputs.

- Fixed two-cell world: A at x=0m, B at x=0.1m, mA=mB=1kg, vA=vB=0; rigid link length=0.1m; dt=0.25s, duration=1s (four F007 semi-implicit steps), drag=0, external forces=0. Initial energy 10,000,000µJ and capacity 20,000,000µJ for each; zero baseline/idle upkeep. Only A has an externally effective motor (F007), fixed force f = 2*s N for s in {-1,+1}; no transmitted electric energy.
- Exogenous terminal-harvest resource patches: exactly one harvest at t=1s, not first passage; each patch has integer 3,000,000µJ, a center and closed radius, can be collected at most once by the nearest eligible cell at the terminal observation (ties to A); neither receives value for a link itself. This artificial terminal interaction is an explicit model assumption, not general biological foraging.
- Theoretical geometry for motor sign s (NOT measured data): joined endpoints A=0.625*s, B=0.1+0.625*s; solo fixed-action endpoint A=1.25*s, idle B=0.1. Define five predeclared resource layouts: NONE=[], B_LINK=[joined B endpoint], A_SOLO=[solo A endpoint], DUAL_LINK=[joined A endpoint, joined B endpoint], DUAL_SOLO=[solo A endpoint, idle B endpoint]. All patch awards are per-cell and never transferred.
- Fully cross 5 layouts × 2 signs × 3 terminal patch radii {0.01,0.05,0.20} m × 3 joining fees {0,100000,500000} µJ per consenting/attached cell = **90 deterministic scenarios**. For EACH scenario run researcher-imposed 4 consent arms {YY,YN,NY,NN}, all with the same fixed motor force 2*s: **360 primary worlds**. In addition, run 3 separately held outside-option worlds with NN consent and motor force {-2,0,+2} N for each scenario: **270 outside worlds**; **630 total recorded 4-step worlds** (some deliberately identical). No random seed/sample inference; exact finite-factorial enumeration.
- Initial joining fees are F002 per-cell spends at t=0 before F007 motion and never charged to rejected link requests. F007 is called with the corresponding post-fee balances so work acceptance is battery-correct. Motion motor spend is charged to cell A only; F002 accounts terminal acquisition per winning cell. Positive motor work is F005 per-step integral/ceil rule through F007, not a separate hand-imposed motion cost.
- Per-cell net = acquired - motor_spent - join_spent (µJ). `delta_fixed_i=net_i(YY,fixed_motor)-net_i(NN,fixed_motor)`. `delta_outside_i=net_i(YY,fixed_motor)-max_{u in {-2,0,+2}} net_i(NN,u)`. The outside max is a **researcher-only, omniscient ex-post benchmark over a declared restricted A-motor menu**, NOT a proof that a local cell can know/implement the optimal action, and NOT a Nash solution. Retain winning outside motor actions and ties as raw record fields.
- Frozen numeric expectations for sign +, radius 0.01m, fee 100000µJ: DUAL_LINK has joined (net_A,net_B)=(1,900,000,2,900,000) µJ and `delta_outside=(1,900,000,2,900,000)` µJ (outside both have zero best net); B_LINK has joined (-1,100,000,+2,900,000) µJ, `delta_fixed=(+900,000,+2,900,000)` µJ but `delta_outside_A=-1,100,000` µJ. Exact F007 outputs must independently confirm or contradict these before conclusions.
- Acceptance checks: all primary YES-only gating and exact initial constraints; no attachment on unilateral/no requests; zero F002 conservation residual for 630 worlds; no secret cross-world input; independent from-disk saved-state mechanical/work/resource and ledger audit; all 90 summaries independently reconstructed; forced falsification through modified/rehash-invalid raw data; byte-for-byte two-root replay; Python3.11+3.12 exact-source CI. No Monte Carlo confidence interval for a deterministic 90-world grid. Classify positive fixed delta/negative outside delta as insufficient for a self-interested join.
- Out of F018 v1 scope by *explicit pre-run restriction*: motor-B-only owner-swap physical trials (current frozen F007 only supports A-driven motor), internal F011 drive, spontaneous approach, 2D, actual contact/collision/latch, online consent learning and strategic bargaining. A motor sign reflection +/- tests signed direction; it does NOT constitute an owner-swap control. Do not claim owner-exchange invariance; add a separately frozen follow-up if warranted. Spatial widths do not establish environment-general incentives.
- Archive `worlds.jsonl`, `states.csv`, `events.jsonl`, `ledger.jsonl`, `summary.jsonl`, `manifest.json` with exact source-hash inventory and raw-data verifier. Negative tests must tamper with scores and mechanical/ledger fields and recompute artifact hashes to test semantic auditing, not only checksum rejection.
- Decision: technical selection gate and conditional value-landscape may be *limited adopted* only if all tests and exact-SHA CI verify. Even if theoretical positive regions occur, NO claim of voluntary informed consent, self-sustaining body, natural ecology, or emergence.
