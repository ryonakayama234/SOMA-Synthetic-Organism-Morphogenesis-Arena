---
id: EXP-F021
title: 双駆動・因果対照実験 設計ドラフト
kind: experimental_plan
status: UNFROZEN_UNEXECUTED
updated: 2026-10-24
issue: 72
---
# F021 Experimental Plan — DESIGN ONLY / no simulation executed

[Issue #72](../../issues/72) · [SPEC](../../topics/F021-bilateral-actuation/SPEC.md) · [findings](../../findings/F021-validation.md).

## Main question
For the SAME precommitted trajectory-blind resource field and action schedules, how does enabling B's own, independently billed effective motor change (a) the 1D ideal mechanics and (b) each individual's net energy, own resource claims and outside-option value, in joined versus separate states?

## Design method
1. Pre-observation Wolfram mechanics sanity check for equal 1kg masses and three signed force pairs: A+2/B0 => linked a+1; A+2/B+2 => linked a+2; A+2/B−2 => linked a0. This is **pure algebra**, not an F021 run.
2. Design an independent per-cell motor positive-work and motor refusal law with NO A-before-B priority. Audit energy conservation in the stated toy-model sense. Treat co-opposition stationary/zero positive mechanical work as a special modeling limit where electrical holding work is not represented.
3. Freeze primary resource fields independently of linked/unlinked outcomes. Reuse documented F019/F020 field construction as feasible while recording new F021 version and freeze SHA. Do not pick fields because they deliver desired bilateral benefit.
4. Compare signed B inputs absent/with A, same/opposite direction, NN/YY, high/low/zero battery, idle/negative controls, both own outside options; predeclare seed blocks, analysis unit, sample count and thresholds in a **new FROZEN_V1 document before any run**. Numerical grid, sample counts and tolerances are **not yet fixed**.
5. Implement a separate f021 orchestrator, not a mutation of F020 semantics. Collect per-step state, effective applied forces by cell, rejected requests, each positive motor work estimate, ledger and patch events, and linked internal constraint accounting.
6. Run physical oracle + tamper-resistant independent archive verifier, 2-root replay, Python 3.11/3.12 all regression Actions. Record EVERY null and negative. Analyze per seed block to avoid pseudoreplication.
7. Judge mechanics H21a separately from ecological effects H21b; **do not condition software correctness on finding a cooperative body**.

## Hard stop before implementation
Unresolved nonlocal interdependence of simultaneous battery-limited motor admission. Must critically review and independently solve without silently giving B an omniscient A observation channel. No automatic issue closure, main merge or science adoption by creating this draft.
