# V002 workspace layout contract — DESIGN candidate (2026-10-27)

**Status:** proposed in response to researcher usability rejection; **not an adopted UI, not a change to frozen `v002.view.v1`**. Source design freeze `4ba05357a426edaa7ec6e9d1d5f905ad64893de8` and original [PR #89](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/89) remain unchanged until separate acceptance. Owner map machine-readable: [`contracts/v002.workspace.layout.v1.json`](../../contracts/v002.workspace.layout.v1.json). Only layout/presentation/selection state may change. No seventh panel, no new world physics, no new evidence schema, no learning/truth feedback.

## Thesis: architecture FIRST, evidence inside fixed sockets
**One workstation, one dominant physical Arena.** The operator should infer actions from placement and interaction rather than read instruction paragraphs. No lower-growing content regions. The old long stacked six panels with verbose text are rejected as a usability failure, regardless of passing CI. The **main document viewport stays fixed** at the 1500×950 reference size; each pane is an explicit bounded scroll owner. Sub-1000px responsive adaptations need separate review, never silently hide sources.

## Fixed desktop wireframe (six existing owners)
~~~text
┌─ SOMA  /  F022:F023 pair identification ─────────────────────────────┐
│ Setup (read-only pair + input diff) │       ARENA A  |  ARENA B     │ Evidence (audit) │
│ scroll details in same pane        │  dominant metric XY viewport │ compact + scroll│
│────────────────────────────────────│                             │─────────────────│
│ Cells (A/B private ledger)         │  no painted-in physics       │ System/Data     │
│ F022 NOT MODELED; F023 values      │  no new panes               │ contract + future│
├───────────────────────────────────────────────────────────────────────┤
│ TIMELINE fixed-height: sample time / exact event + scrollable past event log │
└───────────────────────────────────────────────────────────────────────┘
~~~
The bottom Timeline is an existing sixth panel, **not** a new Console/Logs panel. Log entries are original saved `timeline[]` pointers; changing saved sample time changes the selected/visible history window **within the same fixed-height scroller**. No live sensor, unrecorded time, log fabrication, automatic simulator updates, polling or websocket is implied.

## Explicit owned data / responsibility mapping
| Owned region | Existing data owners | Allowed interactions | No authority over |
| --- | --- | --- | --- |
| Setup / left-top | `worlds[].scenario`, `parameter_diff[]`, `pair_inference` | see frozen pair and scroll complete field diff, equal fields included | scene selection from absent files, submit actions |
| Arena / centre | exact `worlds[].samples` and contact annotations | side-by-side orthographic metric XY at common SAVED sample time | invent off-grid samples or alter physical sizes |
| Cells / left-bottom | `worlds[].cell_model` | view original F023 separate A/B private actions/ledgers, F022 NOT MODELED | synthetic power, agent controls |
| Timeline / bottom | `joint_sample_times_s`, source-indexed `timeline[]` | step/select saved sample, scroll bounded chronological log, select source event with exact time | mutate times or convert event into sample |
| Evidence / right-top | `evidence.*` | inspect pass/reject source/projection audit, reveal SHA on demand | grading truth from pixels |
| System/Data / right-bottom | `schema_version`, frozen contract references | display schema, allowed routes and disabled future-slot legend | policy input, new panel or module |

## Visual / behaviour contract
1. Neutral grayscale (light, medium, dark) only. Use contrast, whitespace and borders, not saturated categorical colors. Valid/invalid indicated in words/icons in addition to contrast.
2. Dominant centre must *feel recessed*, with vignetting/inset shadows and layered grid, **but the scientific projection stays 2D orthographic**. No perspective distortions or radius clamping. Symbolic crosshairs clearly distinct from physical circles.
3. Header carries only research identity and readonly status. Zero explanatory paragraphs in initial viewport. Expand details in panels rather than add rows below.
4. Timeline owns both archive time navigation and historical event log. Log is bounded to Timeline and independently scrollable. Choosing a saved time filters history to original pointers at or before that time; a selected off-grid event preserves its own exact timestamp and does not move either Arena to fabricated positions.
5. Every future capability first receives a **reserved slot within an existing panel owner** (unless a new schema/owner version is independently approved). Placeholder says NOT IMPLEMENTED rather than zero, fake value, or inert active control.
6. If a region needs more data, **it gains internal scroll or disclosure, never increases page height or creates a seventh panel**. Narrow screens cannot claim desktop acceptance without a separate responsive evaluation.
7. Review actual browser DOM dimensions / no document scroll at 1500×950, full input table, exact C13 .095s marker, F022 N/A, F023 Q02/Q04 ledger, and compare available archive results. Automated checks are not human usability assessment.
8. One-way graph preserved: `verified F022/F023 archive → externally anchored independent source verifier → v002.view.v1 projector → independent derived verifier → six owned UI slots`. `Timeline.selectedSample` and `Timeline.selectedEvent` are *UI transient state*, never an archive row or a LocalPolicy input.

## Sequence / gates
A. Freeze **only the proposed workspace mapping for experimental implementation** after critical review; code must use a named layout contract and preserve old source v1. B. Build a candidate fixed workspace on an isolated implementation branch; do not overwrite or merge older frozen evidence. C. Run source/derived verification, desktop DOM geometry + bounded scroller interactions, Chromium screenshots and independent critique. D. Human researcher decides usability; only then admit/merge. Do not mistake earlier 24/24 *old UI* CI as acceptance of this UI.

## Architecture (same six panels, no new logic owner)
~~~mermaid
flowchart LR
  SRC["F022 / F023 immutable archives"] --> OR["Source-independent verification + trusted SHA"]
  OR --> PR["Immutable v002.view.v1 projector"]
  PR --> OV["Independent derived-view verifier"]
  OV --> WS["Bounded workspace shell"]
  WS --> SET["Setup: pair + full diff"]
  WS --> AR["Arena: saved XY x2"]
  WS --> CE["Cells: private ledger / N.A."]
  WS --> TL["Timeline: clock + bounded history"]
  WS --> EV["Evidence: provenance"]
  WS --> SY["System/Data: versions + future reserved"]
  WS -. "FORBIDDEN" .-> AG["Agent policy / source writes"]
~~~
