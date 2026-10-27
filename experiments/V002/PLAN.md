---
id: PLAN-V002
title: V002 observable and falsifiable replay controls
status: PROPOSED_UNFROZEN
updated: 2026-10-26
issue: 86
---

# V002 preregistration candidate — design / NO V002 RUNS

Parent: https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/86; [SPEC](../../topics/V002-counterfactual-observatory/SPEC.md), [view contract](../../docs/DATA_CONTRACTS.md), [findings](../../findings/V002-validation.md). This is not frozen and is not an executed experiment. Observer-only projection and audit, **not** a new robotic-science simulation. Reference originals must be independently validated, source-bound, immutable and individually admissible.

## Universe and baseline inputs
- **Initial executable fallback:** F022.v1 main accepted `f022.archive.v1` suite C01–C13 (13 deterministic worlds; 9 archived sample rows each; contact file includes off-grid events). Each case is a distinct deterministic calibration scenario, **not** an independent biological replicate.
- **Conditional extension:** F023.v1 Q01–Q15 **only after** F023 technically accepted/merged at an exact trusted SHA. Otherwise mark all F023 tests **BLOCKED_BY_SOURCE_GATE**, never pass or silently substitute hand-crafted F023 worlds.
- Both sides explicitly identify source family/version, world IDs, expected immutable source SHA, frozen protocol SHA, hashes and verifier result. Renderer accepts only archives the separate source-independent verifiers have confirmed. Neither trust anchor is inferred from the archive's own manifest.
- Two independent output directories for canonical view artifacts; source archives mounted/read in immutable or verified read-only fashion. Do not overwrite existing output. UI is not an archive editor.

## Fixed design controls (anticipated behavior, not observations)
| ID | Archived pair/control | Required interpretation and visualization |
| --- | --- | --- |
| A | F022 C01 vs C02 | central contact in both, different restitution; show full input difference; precise t=.5s event pre/post and post sample |
| B | F022 C05 vs C06 | near miss vs actual impact; field-level changed offset; null contact remains empty |
| C | F022 C07 vs C08 | grazing zero impulse vs separation; no “bond” label; multi-field flag where appropriate |
| D | F022 C13 solo or C13 vs C01 | event at .095s before first .25s frame; never fabricate sample at .095s on other side |
| E | F022 C01 vs itself | identical canonical projection and zero differences, but still two independently referenced archives |
| F* | F023 Q02 vs Q04 | **CONDITIONAL:** same nominal +Y action but 200 vs 199µJ A private budget; accept/reject separately |
| G* | F023 Q02 vs Q03 and Q02 vs Q05 | **CONDITIONAL:** steering direction; B private budget does not pay A action |
| H* | F023 Q02 vs Q07 | **CONDITIONAL:** elasticity changes saved post-contact energy; no real battery efficiency inferred |
| I | F022 original invalid probes excluded | reject malformed input/archive *before* view bundle publication, never render physical repairs |
| J | F022 source viewer vs V001 | **NON-GOAL:** separate 1D unmerged viewer not imported into 2D data truth |

*Conditional tests are not V002 results and are BLOCKED until F023 gate passes.*

## Fault injection / rejection tests
1. Missing, duplicate, out-of-order `states.jsonl` row, reordered IDs, invalid/missing event, malformed sample phase, changed off-grid contact timestamp, injected phantom miss-contact.
2. Semantically edited AND SHA-rehashed `states.jsonl` or `contacts.jsonl`; independently audit physics not merely manifest checksums.
3. A well-formed-looking view bundle whose cell positions/contact markers do not match saved source; independent projector-vs-source oracle rejects.
4. An archive with self-consistent manifest but wrong externally expected trusted source SHA, unsupported schema, or F023 not adopted must be refused.
5. Substituting nonexistent F022 ledger/actions with zeros, merging private A/B balance, swapping A and B without metadata — reject or explicit N/A as contract prescribes.
6. Selecting an off-grid event time must show own archived event pre/post, **OTHER_WORLD_NO_SNAPSHOT**, never interpolate or pretend both worlds sampled simultaneously.
7. Null/miss/graze remain semantically different; reject a contact animation injected by the UI without an archival event.
8. Filesystem check: original bytes/hashes unchanged across every build and browsing session; publishing existing output path fails safely.

## Measurable acceptance gates (planned)
- **Numerical/data fidelity:** compare **every** saved sample field used by the UI to the exact archived source value (no float relaxation for source-to-view copies), **every** contact/action event, exact row provenance and phase. For any intentionally formatted decimal display, retain original numeric value and disclose formatting; do not round source evidence in the canonical bundle.
- **Timing fidelity:** all F022 selected controls preserve exact event timestamps (including C13 0.095s) and sample 0..2s in 0.25s steps. Contact at a sample time has post-event sample; event pre/post are separately selectable. Unobserved-other-world placeholders enforced.
- **Source fidelity:** verify all required input files, schema, trusted source/protocol identity and saved physical/accounting semantics prior to displaying values. Independent archive verifiers and distinct view-oracle path, with negative forged/rehashed tests.
- **Reproducibility:** two clean roots from same externally checked source+archive yield byte-identical canonical view JSON; Python 3.11/3.12; current exact final source SHA CI; inherited tests remain green. No implementation results invented here.
- **Visual comprehension:** hands-on browser inspection verifies legible same-scale X/Y axes, units, A/B identity, sample vs event distinction, F022 N/A cells and refusing unverified input. Capture screenshot/test notes with browser+OS, treat screenshots as illustration **not** physical evidence. This gate is untested today.
- **Research inference:** input field-by-field diff is complete; label “single field changed” only when demonstrably so; no universal counterfactual-causality claim from visual proximity alone.
- **Boundaries:** UI cannot send state into `LocalObservation`, `LocalPolicy`, F022/F023 producers or mutate original archives. New panels or changed ownership fail the contract gate.

## Decision and records
Technical verdict = PASS/FAIL/INCONCLUSIVE; H-V002 verdict = SUPPORTED/REFUTED/INCONCLUSIVE/UNEXECUTED, separately, with evidence SHA and explicit negative cases. V002 projection count and scenario coverage are **not yet observed**. [Append-only findings](../../findings/V002-validation.md) must record failed browser/manual checks, source rejections and dependency blocks, not only positive screenshots. Do not integrate without explicit user adoption decision.


## 2026-10-27 design correction for schema review (NOT V002 execution)
- Proposed machine-checkable JSON Schema: [`contracts/v002.view.v1.schema.json`](../../contracts/v002.view.v1.schema.json). Replaces the loose `object`/`any` proposal during review, not a freeze.
- Check **actual** archived event kind `"impulse"` or `"grazing_zero_impulse"` against source `contacts.jsonl`; `"motor_action"` belongs only to F023 `actions.jsonl`, not a contact-kind variant.
- `source_row` must be 0-based **full JSONL file index**, not a per-world sample index. Each `WorldProjection` remains one of two distinct sides, allowing C01 vs C01 with separate independently verified source bundle identities.
- Only same-family two-world pairs for v1; unsupported cross-F022/F023 mixed comparisons fail closed. Cross-source provenance must not be conflated with same-world identities.
- Cross-field/trust/semantic checks remain separately preregistered; passing structural JSON Schema alone is never sufficient. After F023 formal admission update trust anchors before freezing.
