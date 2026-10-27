# V002 critical preimplementation self-audit — 2026-10-26

**Review kind:** same-assistant preliminary design challenge; **NOT independent third-party peer review** and **NOT an executed acceptance test**. Source: [#86](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/86) and F022/F023/V001 contracts.

## Identified failure mechanisms and design stops

| Threat | Counterexample | Required control / unresolved decision |
| --- | --- | --- |
| Event hidden in sampling | F022 C13 collides at 0.095s, before .25s frame | Preserve exact off-grid contact event; other world unavailable at that instant rather than inventing XY |
| Fake simultaneity | A event at t when B only has bracketing samples | Shared cursor selects jointly recorded samples; event inspection is per-world and B gets explicit no-record placeholder |
| Candidate source promoted to truth | F023 branch PR #83 green CI but review/adoption unfinished | require trusted exact source and explicit F023 limited admission/main integration before V002 F023 viewing |
| Modified manifest passes | rehash a forged F022/F023 event or state | independent saved-data verifier before rendering, plus projection cross-check against verified source |
| False F022 sensor budget | F022 has no actions/ledger but UI shows 0 µJ | `not_modeled` typed state, not zero-valued model |
| Unjustified “only steering changed” | baseline comparisons differ in commands AND budgets | diff complete input map, label multi-dimension contrasts as descriptive rather than causal proof |
| Renderer leaks global truth | Arena world state wired into future `LocalObservation` | explicit one-way researcher-only observation boundary and rejection in architecture/code review |
| Visual chart ungrounded | invented smooth paths/extra collisions displayed as true | only point/event snapshots authoritative; stylistic trails, if used, must derive from saved samples and marked illustrative |
| V001 inadvertently included | 1D replay merged/reinterpreted under V002 | no V001 code changes or dependencies without distinct approval |
| UI responsibility creep | new comparison/results panel added casually | retain existing six panels; contract version/review required before new panels or ownership changes |

## Audit finding / open items before freeze
- **Unresolved implementation-specific**: canonical sorting/event identity, exact archive record key inspection, trustworthy external expected Git SHA inputs, browser accessibility and operating environment. These need independent design review and freeze before code.
- **No acceptance claimed**: quality of archive verify, viewer replay and user understanding remain untested.
- **Required next audit**: independent reviewer should challenge every displayed claim against immutable F022 source logs and separately adopted F023 if available. Same-AI checklist does not substitute for external review.

**Design verdict:** candidate ready for **Draft PR review only**. STOP before viewer implementation, protocol freeze or main merge until gaps/risks are addressed.

## 2026-10-27 external-tool critical Codex re-review: two P2 corrections requested
- **P2 Setup read-only archived command fields:** `scenario.json` necessarily contains researcher-prescribed `command_ay_ns` etc used by Q02/Q03; forbid **new command dispatch** but permit read-only field diff. Reworded both architecture and SPEC. Existing six panel responsibilities unchanged.
- **P2 fake action source kind:** `actions.jsonl` has exact 18 fields with `decision`, not `kind`. Do not invent `motor_action`; derive viewer-only `TimelinePointer.kind="action"` from the source file and row. Corrected PLAN and data contracts; see typed draft JSON Schema.
- This is an **AI code review**, not a human independent academic referee. Resolution remains subject to exact-head re-review, machine-schema tests and a separate immutable preimplementation freeze. No V002 UI or experiment exists.
