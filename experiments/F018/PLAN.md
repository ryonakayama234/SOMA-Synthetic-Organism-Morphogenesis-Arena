---
id: EXP-F018
title: F018 事前設計 — 接続要求と反事実的個体利得
kind: experiment_plan
status: design_unfrozen
updated: 2026-10-22
issue: 61
---

# F018 experiment plan — UNEXECUTED / UNFROZEN

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
