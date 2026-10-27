---
id: V002
title: Counterfactual Observatory — verified 2D archive comparison
kind: design_specification
status: PROPOSED_UNFROZEN
updated: 2026-10-26
issue: 86
depends_on: [F022, F023]
related: [PROJECT, RESEARCH_AGENDA, V001]
---

# V002 — Two-world Counterfactual Observatory (DESIGN ONLY)

**Researcher approval on 2026-10-26** authorizes this design phase. https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/86. No V002 implementation, browser result, saved display bundle, CI, technical adoption or main merge has occurred. Schema identifiers and tests below are candidates until independently reviewed and frozen **before** implementation. The user authorized the *direction*, not bypassing review or acceptance.

## The single ability / why now
Turn **independently verified, already saved** F022/F023 two-disk 2D experiment archives into a researcher-only, read-only **side-by-side synchronized comparison**, exposing what inputs differed, what archived contacts occurred and what evidence supports each visible measurement. A visually persuasive animation with invented physics or missing contact events is a failure.

F022.v1 is a technically limited **passive** 2D contact instrument on main. F023's frozen design and implementation candidate are tracked at #81, design PR #82 merged, implementation PR #83 still **unadopted/unmerged at design selection**. Never accept F023 as a qualified source before a **separate** source-bound critical/adoption gate and main merge. If that is still pending, implement/review an explicitly restricted F022-only V002 or postpone the F023 path; never quietly relax the accepted-source gate. V001 #24/#25/#26 is separate, unmerged 1D replay and must remain untouched.

## Question, hypothesis and alternatives
**H-V002**: an accepted F022/F023 immutable archive can be deterministically projected to a versioned, traceable shared-observation display without modifying its physical/numerical/event meaning, rewriting evidence, or supplying researcher-only world truth to a cell policy.

Rivals: a missing off-grid TOI is hidden by interpolation; an internally consistent SHA-rehashed forged archive is displayed; a null/missing F022 private ledger is rendered as real zero; two frozen scenarios change more fields than advertised; renderer runs its own simulation; a shared time cursor silently extrapolates the other world; an F023 implementation candidate is mistaken for adopted evidence.

Support **only if** canonical projection is byte-identical across two clean roots with the same trusted source/archives; independent projector-vs-source auditor reconstructs each visible value, each event and each paired condition difference; altered/missing/rehash attacks fail closed; no source mutation; browser inspection confirms legible distinction among exact event, sample, null and unavailable data.
Refute/stop for a dropped/contact-overwritten event, fabricated sampled coordinates at an unsampled time, forged archived facts passing, source truth crossing into LocalObservation/Policy, or unversioned/undeclared panel responsibility change. Mark usability **inconclusive** until actual human/browser review; technical correctness does not prove research comprehension.

## Scope and forbidden changes
- Two **already saved** archives/world IDs, initially identical simulator-family/version at approved trust anchors. Read-only offline study view.
- Existing panel responsibilities only: **Setup, Arena, Cells, Timeline, Evidence, System/Data**; two Arenas are repeat instances inside the **existing Arena panel**, not a new panel. No direct user UI editing of original data. No novel panel, changed ownership, new physical meaning, action input or privileged export to agents.
- No new physics, no integration of F001–F021 distinct worlds, no body attachment, no motor design, no resource ecology, no autonomous controller, sensors, learning, reward or robot-body/emergence claim.
- Viewer is measurement infrastructure; the system may *display* existing physical data, but it must not produce any new F022/F023 simulation or generate new experiment outcomes for comparison.

## Supported source / state boundary
- **F022:** `f022.archive.v1`: `scenario.json`, `states.jsonl`, `contacts.jsonl`, `audit.json`, `manifest.json`; **there are no actions/ledger files**. Cells must say **N/A (not modeled)**, never “0 spent” or “0 motor”.
- **F023 conditional:** `f023.archive.v1`: the five files above **plus** `actions.jsonl`, `ledger.jsonl`; per-cell private balance, prescribed t=0 action, charged/rejected status displayed ONLY after the separate F023 admissibility decision.
- Source schema must be explicitly supported. Independently verify archives and external expected source/freeze identities before projection. SHA digest self-consistency alone is not trusted.
- **Time:** matched sample time `t` is browsable only if both archives hold samples at that exact time. A contact's exact TOI is an event (pre/post) and is **not** itself a sampled frame. When selected, show the owning world's archived event record; for the other world, if no exact stored record exists at that time show **NO_RECORDED_SNAPSHOT_AT_TIME**, not interpolated positions. F022 C13 has impact at 0.095s before 0.25s sample. F023 t=0 acts before t=0 post sample. Zero-contact worlds have no phantom contact.
- **Comparisons:** differences are computed from the complete frozen initial input fields, not just a human label. Report number and identity of different fields, distinguish one-field contrast from multi-field descriptive comparison; no inferred automatic causal attribution.

## UI panel contract (all six existing responsibilities; zero extensions)
| Panel | Sole rendering responsibility | Source-bound projection | Forbidden |
| --- | --- | --- | --- |
| Setup / Scenarios | select two verified saved IDs; full initial-field diff | verified scenario world records **including read-only prescribed command input fields** | send live settings or command changes to simulator, mutate archive |
| Arena | render two read-only 2D XY scenes + actual exact contact annotations | saved samples and event pre/post snapshots | synthesize new physics, own new panel |
| Cells | per-cell private action/balance, or explicit N/A for F022 | F023 actions/ledger; F022 absent | pool A/B balance, invent missing values |
| Timeline | common sample cursor, per-world off-grid event markers, ordered action/contact phases | exact sample/event times and kind | interpolation posing as evidence |
| Evidence | independent archive result, provenance and reason for refusal | verifier result, audit and trusted source SHA | accept manifest-only proof |
| System/Data | schema/version, ownership, read-only boundary and provenance model | contract/architecture IDs | reveal truth to LocalObservation/Policy |

Detailed prospective `v002.view.v1` typed schema in [DATA_CONTRACTS](../../docs/DATA_CONTRACTS.md); corresponding Mermaid diagram in [ARCHITECTURE](../../docs/ARCHITECTURE.md). Any new/merged panel, semantic ownership shift or new source/feedback route requires a **new explicit contract review and approval before UI code**. Style-only tweaks may remain within this contract.

## Preimplementation and implementation gates
1. **This design PR only:** Issue + SPEC + PLAN + architecture + data contracts + UNEXECUTED findings + README/AGENTS + critical self-audit. Do **not** mark view-v1 frozen or implemented merely from publication.
2. Reviewer verifies complete schema, event ordering and error semantics; issue a separately identifiable **immutable design-freeze SHA** before code/first V002 archived display projection. Amend before any primary projection if errors are found; after freeze use new version.
3. Separate implementation PR, F022-only if needed. Source-independent verification **must precede** display. Test exact time, null, F023 conditional gate, attacks after rehash, missing files/event/ledger, byte replay, Python 3.11/3.12 regression, browser operation, no mutation.
4. Researcher receives screenshots + comparison interpretation + source-linked findings; adopts or rejects bounded viewer **explicitly** before main integration. Same-AI self-audit is not third-party peer review.

**Status: SELECTED / DESIGN PROPOSAL ONLY / ZERO V002 EXECUTIONS.**

## 2026-10-27 design status update — new accepted 2D source
F023.v1 [PR #83](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/83) has now merged on main and passed 22/22 exact-merge push workflows, so the **source-admission dependency is satisfied for eligible F023 archives**. Viewer evidence **still** requires per-archive independently verified saved content plus trusted expected SHA/protocol identities. F023 scenarios are never UI-generated, and V002 continues to require a reviewed/frozen machine-readable [JSON Schema](../../contracts/v002.view.v1.schema.json) before code. The October 26 historical “F023 unmerged” passages above describe the original selection checkpoint, not the current state. F022-only fallback remains valid if specific F023 archives fail verification. No V002 runs or implementation have occurred.
