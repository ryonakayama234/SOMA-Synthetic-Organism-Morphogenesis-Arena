---
id: F023
title: Active Encounter — 2D私有駆動による出会いの因果可能性
kind: feature_specification
status: SELECTED_DESIGN_UNFROZEN_UNEXECUTED
updated: 2026-10-25
issue: 81
related: [PROJECT, RESEARCH-AGENDA, F002, F005, F021, F022, ARCHITECTURE, DATA]
---
# F023 — Active Encounter（設計案・観測前）
**Status: selected for DESIGN, UNFROZEN. No F023 source code, primary simulator observations, CI, or adoption.**
[Issue #81](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/81) / [PLAN](../../experiments/F023/PLAN.md) / [theoretical preflight](../../experiments/F023/PREFLIGHT.md) / [findings](../../findings/F023-validation.md).

## One question / why now
F022.v1 limited adopted passive two-disk 2D continuous-TOI contact, but no 2D action or source-of-momentum model. F021 separately measured private bilateral 1D motor economics, and its idle-inclusive bilateral payoff gate found 0 strict dual positives / 4,608 contrasts in that *different* 1D model. F023 asks: **when does one prescribed battery-bounded 2D action change an otherwise missed encounter into true physical contact, and how does action feasibility affect that difference?**

This **does not** test autonomous approaching, learned steering, negotiation, attachment, self-assembly, realistic tires, closed ecological survival, perception, body schema or organismality.

## Bounded addition / physical honesty
Two ideal identical 1kg/0.5m-radius disks, no spin, unbounded planar horizontal world; F022-style free flight + continuous quadratic TOI + ideal frictionless normal restitution. One **externally scheduled time-zero** actuator command per cell, a vector impulse J=(Jx,Jy) N·s, with opposite **environment/ground reaction** -J. Only the accepted impulse changes that cell's velocity v_after=v_before+J/m. All subsequent t>0 behavior is ballistic except contact; no ongoing drive or policy. Contact is NOT an attachment edge.

For each cell, signed instantaneous mechanical work W_i = v_before·J + |J|²/(2m), corresponding exactly to post-minus-pre kinetic energy. Battery debit uses **ideal positive work only**, ceil(max(0,W_i)*1e6) integer µJ, with explicit rounding excess; W<0 is dissipated (no credit). A rejected private-budget command applies zero impulse and has zero charge; another cell's battery is never borrowed. The environment receives equal/opposite impulse; **cell-only total momentum need not remain fixed during actuation**. The battery-to-work conversion, zero idle cost, infinite-inertia fixed ground and perfect instantaneous traction are idealized assumptions, **not measured hardware efficiency**.

**Important prefreeze numeric hazard:** floating rounding close to an integer-µJ boundary must be resolved via exact-rational/safeguarded audit, not a naive floating ceil that switches a 200µJ candidate into 201µJ because of binary noise. Freeze deterministic quantization, strict validation, command bounds, ordering, and tolerances before primary simulations. The preflight values below are theory-only.

## Hypotheses, alternative explanations and nulls
- H23a steering-in: admissible time-zero transverse impulse can move a preregistered fixed near-miss from no contact to a continuous-TOI impulse event.
- H23b private budget + direction: forbidden/underfunded/steering-away command cannot be misreported as the same causal approach. Per-cell debits and the environment reaction must reconcile.
- H23c source-independent archives: physical event, energy bookkeeping and source-bound hashes can be reconstructed by an implementation-independent verifier, including rehashed semantic attack rejection.
- R23a: any apparent contact comes from discrete-frame overlap / contact-epsilon bias.
- R23b: hidden external kinetic supply, cross-cell budget transfer, or arbitrary action arbitration.
- R23c: coordinate rotation / swapping identities changes predictions where symmetry requires invariance.
Report missed encounters, rejected commands, no-change and negative energy effects as evidence.

## Input/outputs and prospective module boundary
Future candidate `soma/f023.py` exposes a versioned, immutable `Scenario` and pure `simulate(scenario)->(states,actuation_events,contacts,ledger)` or equivalent tested API; exact names **not frozen**. Do not alter `soma/f022.py` or `f022.archive.v1`. Preserve own-arm private battery, F002 integer-µJ semantics where applicable; unit conversion and event ordering deliberately require preregistration.

Candidate archive: `scenario.json` (initial truth, J command, per-cell budget), `states.jsonl` (world XY truth), `actions.jsonl` (pre/post impulse, ground counter-impulse, W, decision), `contacts.jsonl`, `ledger.jsonl` (private µJ), `audit.json` (momentum incl. ground, KE, collision loss, nulls, flags), `manifest.json` (freeze/implementation SHA, input/output digests). No agent-local input API.

## UI-panel traceability, strictly read-only
| Event or data | Proposed future panel | Authority |
| --- | --- | --- |
| Scenario + chosen contrasts | Setup / Scenarios | experimenter only |
| Two disks, paths, contact normal | 2D Arena | world truth replay, not agent input |
| Commands, accepted/rejected impulse, private balance | Cells | experimenter replay; individual balance is private if a future controller exists |
| T=0 action / exact TOI / null misses | Timeline | recorded event order |
| Schema arrows, physical vs information connection | System / Data | explanatory read-only schema |
| Ground reaction, conservation, source hashes | Evidence / Audit | verifier / experimenter |
Future `LocalObservation` and `Policy` ports are explicitly absent; a viewer will be separate V00x work. Existing V001 1D draft PRs #25/#26 are not modified/merged.

## Technical admission gates
Freeze full prospective independent unit set and tests before F023 primary run. New implementation PR, independent physics/ledger saved-file recomputation without importing producer, forged-rehash adversaries, two clean-root byte-identical replay, Python3.11+3.12, all F001–F022 regressions and final exact-SHA CI. Record numerical ambiguity and source of momentum and work. Strictly separate *bounded technical adoption* from scientific H23a/b/c results; no merge/close in this design PR.

[Research charter](../../docs/PROJECT.md) / [agenda](../../docs/RESEARCH_AGENDA.md) / [study process](../../docs/RESEARCH_PROCESS.md).