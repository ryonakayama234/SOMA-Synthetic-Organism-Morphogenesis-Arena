---
id: FINDING-V002
title: V002 2D Counterfactual Observatory — append-only evidence
kind: append_only_findings
status: UNEXECUTED
updated: 2026-10-26
issue: 86
---

# V002 validation — APPEND ONLY

## 2026-10-26 — researcher authorized design; no experiment

**STATUS: SELECTED FOR DESIGN / UNFROZEN / NO V002 CODE / NO VIEW ARTIFACTS / NO V002 PRIMARY TEST RUNS / NOT ADOPTED.** Issue [#86](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/86) authorizes only a versioned read-only side-by-side F022/F023 archive observer UI **design**, not implementation. The prior UI V001 #24/#25/#26 is an unrelated, unmerged 1D viewer. F022 is limited adopted; F023 implementation PR #83 was unmerged/unadopted at design initiation.

**Question:** Can independent source-verified saved 2D archives be projected into a synchronized exact-sample/event comparison without loss of original meaning, altered data or truth feedback to an agent? This is a hypothesis about research *measurement infrastructure*, not about new physics, voluntary rendezvous, autonomous morphology, organism formation or scientific emergence.

**Predictions and calibration sources (not new observations):** F022 C01/C02 same-time elastic/dissipative contacts, C05/C06 miss/impact, C13 off-grid .095s event, and conditional F023 Q02/Q04 private µJ rejection, Q02/Q03 steering, Q02/Q05 budget separation, Q02/Q07 dissipation. F023 controls are blocked until the F023 source admission gate independently succeeds. Every input-field difference and provenance must be preserved.

**No results yet:** no V002 byte-identical replay claim, no V002 viewer CI, no changed source archives, no browser screenshots, no adoption verdict. [SPEC](../topics/V002-counterfactual-observatory/SPEC.md) / [PLAN](../experiments/V002/PLAN.md) / [ARCHITECTURE](../docs/ARCHITECTURE.md) / [DATA_CONTRACTS](../docs/DATA_CONTRACTS.md).

### Next evidence entries (add; never rewrite the original note)
- Protocol freeze SHA, source/manifest/trusted checkout SHA and exact view-contract version.
- Each control case PASS/FAIL/BLOCKED, complete field diffs, event timing, missing/null semantics, source verification.
- Rehashed semantic archive attacks, independent view-projection audit, F022/F023 source verifiers.
- Python 3.11/3.12 exact-head CI, two-root byte replay, no-source-mutation proof, browser/manual comprehension evidence.
- Critical counteranalysis and scoped technical admission; separate scientific support/refutation/inconclusive verdict and user decision.

## 2026-10-27 — type-contract correction, source dependency unblocked; NO V002 RUN
F023 main merge `6ca8c9db2b29ca87a70eebc0c2c139681ca67d6e` and 22/22 exact merge push CI satisfy V002's prerequisite **source-admission** condition. [Exact-field candidate JSON Schema](../contracts/v002.view.v1.schema.json) proposed with 16/22 scenario fields, 13 sample fields, 20 contact fields and 18 action/5 ledger fields, proper `impulse` event semantics and required 5/7 file hashes. The original informal `object/any` view model has been replaced in `docs/DATA_CONTRACTS.md`. Neither archive display, browser experiment, JSON Schema validator execution, review freeze nor V002 adoption has occurred. Next: critical design review and frozen SHA before implementation.

## 2026-10-27 — independent Codex draft-review P2 issues and design corrections (NO V002 EXPERIMENT)
At old design SHA `26b2b34d0048af1ca050a8f4461b498324cfcf1b`, critical [Codex review on PR #87](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/87) identified two **P2 pre-freeze** defects: (1) Setup's archived scenario diff requires read-only `command_*_ns` values, but architecture incorrectly stated "not action commands"; (2) PLAN called `motor_action` an F023 source kind even though the exact `actions.jsonl` has **no `kind` field**. Corrections explicitly distinguish archived input inspection versus live command submission, and derive `TimelinePointer.kind="action"` **only in the viewer** from the unmodified action-row source. Contact source `kind` remains `impulse|grazing_zero_impulse`. These are design repairs, **not implementation success or a frozen contract**. Request follow-up critical review on exact repaired HEAD before freezing.

## 2026-10-27 — design freeze (no V002 experiments performed)
V002 one-ability scope, fixed six-panel ownership, accepted F022/F023 source families and source-independent SHA-bound evidence gate, exact archive sample/TOI/action semantics, strict `v002.view.v1` schema and controls were preregistered in [V002/FROZEN_V1.md](../experiments/V002/FROZEN_V1.md). Codex re-review of the corrected prefreeze design at `995acc96c3d9124ec7a8beadd7e593234156f7f0` reported no fresh major issues; earlier two P2 defects/fixes are preserved above and in Issue/PR review history. Freeze commit SHA is anchored to Issue #86 separately. **No implemented V002 reader, no browser result, no source/view artifact, no V002 test run, no V002 admission.**


## 2026-10-27 — V002 first implementation slice on isolated Draft PR #89, CI initially queued

After the V002.v1 design freeze at `4ba05357a426edaa7ec6e9d1d5f905ad64893de8` and design merge #87, the researcher authorized delegated implementation subject to stop gates. New **Draft PR #89** implements a candidate archived-source verifier → two-world canonical projection (`experiments/V002/project.py`) with frozen-view JSON Schema validation, exact saved-source row copying, scenario input diffs and ordered sample/event/action pointers. Dedicated Python 3.11/3.12 CI and limited source projection tests have been added. F022/F023 source simulators, frozen source protocols and V001 1D proposals are unchanged.

**No V002 empirical outcome is asserted at this entry.** CI was queued/in progress at initial note, no offline browser UI, human browser inspection, full adversarial view-bundle independent oracle, V002 final evidence qualification or main integration has occurred. Original archive verifier runs before either view record is issued; standalone projection-origin authentication beyond a trusted caller-supplied SHA remains a security boundary requiring audit. Further entries must report exact HEAD/CI/test results and failures rather than retroactively rewriting this note. Pair controls A–H remain frozen and mandatory for acceptance.


## 2026-10-27 — V002 dedicated CI failure, two new review defects and candidate repairs (append-only)

**First measured failure, not an adoption result:** V002 PR head `4440ffeffd6784386e62a2067abd145007d753ab` completed 23 successful inherited Actions workflow instances but failed its separate dedicated V002 workflow [40431485526](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/40431485526) in **both Python 3.11 and 3.12**. Actual logs show `test_invalid_trust_and_immutable_output` ended with `TypeError: publish() missing 6 required keyword-only arguments`; subsequent tests did not execute in that failed workflow. This must not be counted as a passed V002 run.

**Independent Codex latest exact-head findings at `4440ffe`:** [missing source anchors in existing-output test](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/89#discussion_r4384195818) (P1) and [false rendered disk overlap due to a three-pixel radius floor at large C13 scale](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/89#discussion_r4384195822) (P2). Historical P1/P2 findings from the prior review were retained, not erased.

**Code amendments in separate implementation PR #89 only:** supply all immutable-source arguments even in the expected existing-output refusal path; draw disk radii from actual archived scenario radius (metres) at a single XY scene scale **without** minimum screen-pixel inflation, and distinguish symbolic centre crosshairs/text from physical disks. Keep all frozen Setup input fields, precise event vs post-event sample classification, and the independent on-disk view oracle **before** publication. Expand tests to cover frozen F022 controls C01/C02, C05/C06, C07/C08, C13/C01, C01/C01 and F023 Q02/Q04, Q02/Q03, Q02/Q05, Q02/Q07, immutable source bytes, unsupported cross-family pair and edited derived sample refused before publication. Add Playwright Chromium automated DOM/SVG smoke and illustrative screenshot CI; no independent human browser acceptance is claimed.

**Outcome of changes at note:** newer V002 source includes these repairs; **the final documentation-inclusive SHA and its source-bound Python 3.11/3.12, browser and review results are not yet known.** Earlier green runs on earlier SHAs do not count toward final acceptance. V002 status remains **CANDIDATE / NOT ADOPTED / NOT MERGED**. Frozen `FROZEN_V1.md` and `contracts/v002.view.v1.schema.json` were not edited; F022/F023 producers and V001 source remain untouched.
