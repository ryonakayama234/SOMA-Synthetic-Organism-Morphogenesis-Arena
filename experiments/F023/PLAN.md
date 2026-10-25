---
id: EXP-F023
title: Active Encounter 対照実験の計画案
kind: experiment_plan
status: CANDIDATE_NOT_FROZEN_NOT_EXECUTED
updated: 2026-10-25
issue: 81
---
# F023 hypothesis → causal contrast → archive → verdict (UNFROZEN)
No primary F023 worlds are run in this design PR. No numeric simulation evidence, technical qualification, or scientific admission.
[SPEC](../../topics/F023-active-encounter/SPEC.md) / [Issue #81](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/81) / [mathematical preflight](PREFLIGHT.md) / [findings](../../findings/F023-validation.md).

## Main contrast family (candidates; not yet a frozen grid)
| Contrast | Changed factor | Why / falsifier |
| --- | --- | --- |
| M0 vs M1 | same separated initial positions/velocity, no action vs A pulse steering toward B | exact TOI appears ONLY if geometry permits |
| M1 vs M2 | reverse A transverse pulse | directional control vs mere actuation |
| M1 vs M3 | adequate vs below-required A private balance | rejected command acts as no impulse |
| M1 vs M4 | identical A action but B budget changed | no covert B-funded A propulsion |
| M0/M1 mirrored & rotated | transform full scene and commands | covariance of event classification, time and work |
| null parallel / separating / outside horizon | geometry only | preserve no-contact |
| elastic / inelastic | restitution 1 vs 0.5 | check impact KE budget independently |
| invalid & forged | malformed, overlap, source/ledger/normal/event corruption with rehashed manifest | fail before publication / audit rejection |

Core independent unit = one preregistered paired deterministic scene, **not an independent animal**. Matched paired contrasts share initial states; avoid pseudo-statistical replication. No reward for collision or link. Force zero/unaffordable and no-contact legitimate findings.

## Experiment sequence
1. Critical review: scrutinize ideal ground model, action timing, absence of local observations, signed W vs charged W+, input validity, float quantization near µJ.
2. **Pre-observation freeze**: exact collision horizon/sample grid, scene IDs and all initial states, accepted command vectors, fixed e, independent unit count, rejected inputs, energy and momentum numeric tolerances, deterministic serialization/schema, PR/commit freeze SHA. Use F023/FROZEN_V1.md as a new immutable record only after this review.
3. Only then implement isolated F023 producer and saved-data verifier; no F022 source/evidence mutation.
4. Run fixed grid and archive all negatives; compare with independent analytic TOI and per-cell private ledger, environmental impulse, exact frame semantics. Reject falsified-rehash and null corruption.
5. Run clean roots twice, Python3.11/3.12 source-bound CI and all old workflows; append findings and conduct critical review; accept bounded instrument only if technical gates pass; scientific hypotheses may be supported/refuted/inconclusive.
6. A separate implementation PR and adoption decision precede main merge; this design PR does **not** authorize an implementation or claim an observation.

## Panel-to-artifact consistency
- Setup → scenario.json
- 2D Arena → states.jsonl + contacts.jsonl (read-only)
- Cells → actions.jsonl + ledger.jsonl
- Timeline → ordered t=0 action and later TOI (null explicitly displayed)
- Structure → docs/ARCHITECTURE.md + docs/DATA_CONTRACTS.md
- Evidence → audit.json + manifest.json + findings/F023-validation.md
Local Observation/agent training UI is **future only**, no environment truth access. Viewer and physics must never be conflated.


## 2026-10-25 pre-observation freeze update
Binding experiment protocol: [FROZEN_V1](FROZEN_V1.md), commit `76dcc1db7ae12737705da06c155933d0a8251853`, Issue #81 SHA anchor. Earlier illustrative scene comparisons are superseded by the fixed 15-world/5-invalid trial roster. **No F023 worlds executed yet**. Design freeze and implementation/adoption remain separate.
