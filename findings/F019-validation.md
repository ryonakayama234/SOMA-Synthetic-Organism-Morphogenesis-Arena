---
id: FINDINGS-F019
title: F019 経路資源生態系・研究証拠台帳
kind: scientific_findings_append_only
status: UNEXECUTED
updated: 2026-10-22
issue: 64
---

# F019 validation — UNEXECUTED / UNFROZEN / NOT ADOPTED (2026-10-22)

[Issue #64](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/64) / [draft preregistration](../topics/F019-resource-ecology/SPEC.md) / [PLAN](../experiments/F019/PLAN.md).

## Current state
**No F019 simulator exists, no F019 world has been executed, and no result, effect size or scientific acceptance is asserted.** Documentation in the F019 draft PR is a proposed study design, not an implementation or experimental observation. F001–F018 main evidence is separate and unchanged.

## Reason to run
In [F018 limited-adoption evidence](F018-validation.md), only 18 of 90 conditions had both individuals' restricted outside-option deltas positive, and **all 18 belong to the hand-tailored DUAL_LINK terminal-patch layout**. Other 72 conditions had no bilateral outside-positive region. That is a bounded verified precedent, not evidence that untuned ecological resource encounters will induce linking.

## Wolfram precheck (theoretical only, independent of F019)
With mA=mB=1kg, force 2N on A, dt=1/4s, four ideal semi-implicit steps and zero drag: linked positions of A: 0, 1/16, 3/16, 3/8, 5/8m; linked B: A+1/10m; unlinked A: 0, 1/8, 3/8, 3/4, 5/4m. This matches the F018/F007 displacement assumptions. **No resource first-entry/depletion results have been computed in Wolfram or SOMA for F019.**

## Required append-only table (do not fill before actual run)
| Gate | Actual observation | Status |
|---|---|---|
| H19a first-entry and depletion uniqueness | NONE | UNEXECUTED |
| H19b untuned resources and individual outside deltas | NONE | UNEXECUTED |
| H19c no-resource/drive-off/refusal/mirror controls | NONE | UNEXECUTED |
| H19d saved-data oracle, forgery rejection and replay | NONE | UNEXECUTED |
| Frozen preregistration commit and exact-source CI | NONE | NOT STARTED |
| Independent scientific decision and final main CI | NONE | NOT AUTHORIZED |

## Decision rule
A negative Pareto region under valid untuned worlds is a **valid negative scientific result**. Adopt a bounded resource/harvest measurement API only when technical invariants hold, even if the scientific incentive hypothesis fails; keep the substantive "emergent morphology" claim unapproved. Later investigators append source SHA, exact sample universe, raw artifact identifiers, statistical aggregation rule, verdict, limitations and reviewer objections without replacing these pre-experiment entries.

## 2026-10-22 — pre-freeze research-question refinement (no observations)

The previous framing highlighted whether untuned patches reproduce F018's bilateral positive link benefit. Before any F019 freeze or world run, the study's **primary** question was broadened to *connectivity-dependent resource encounter, claimant identity/ownership, depletion sequence and individual net energy*. Both-cell positive outside-option deltas remain a **secondary, exploratory** observation. Neither winner switches nor bilateral gains are required for technical adoption. No physical mechanics, candidate generator, sampling count, or data-safety gates were changed; the earlier rationale and UNEXECUTED entries are preserved above as history. See [current SPEC](../topics/F019-resource-ecology/SPEC.md), [PLAN](../experiments/F019/PLAN.md) and [future-only research memo](../docs/research-notes/2026-10-22-temporary-morphology-and-resource-access.md).

## 2026-10-22 preregistration freeze — before first F019 world (append-only)

Committed design commits freeze the previously ambiguous generator and edge semantics in [PLAN](../experiments/F019/PLAN.md), with exactly 512 candidate main scenarios / 3584 counterfactual worlds. This entry records **no execution, evidence, positive effect, or acceptance**. A separate implementation PR will be required, and review beyond same-assistant computational auditing remains outstanding. Frozen technical criteria do **not** require any positive link or owner-switch result.

## 2026-10-22 implementation-candidate source addition — before CI verification

Separate implementation branch adds F019 patch-field sampling, within-step harvest, same-field paired outcomes, raw evidence producer, independent verifier, 10 deliberately rehashed corruption cases, unit tests, workflow and source/architecture/contracts documentation. **These are proposed source capabilities; no GitHub Actions result, numeric outcome, effect-size claim, independent external review or scientific adoption is asserted here.** The preregistered 512 worlds? No: 512 independent-parameter *scenarios*, seven arms each, 3584 worlds. This corrects any accidental conflation of conditions and counterfactual worlds. On successful exact-source CI, append observed counts and reviewer notes; do not overwrite this entry.

## 2026-10-22 initial PR #66 CI: failed, preserved (before first F019 world)

At implementation HEAD `ca24e4461393744fc298e308171dd1a525b26562`, [F019 run #39794847004](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39794847004) executed Python 3.11/3.12 full regression. Each failed **1 out of 227 tests**: a semantic-equivalent but byte-different float lattice coordinate `-0.9500000000000001` from `n * .025` versus `-0.95` from `n / 40` in the independently implemented sampler's direct-equality test. No frozen F019 world generation or adoption claim occurred (workflow skipped suite stage). The verifier is corrected to use the frozen preregistration's `* 0.025` serialization convention while retaining separate SHA256/hash-to-grid implementation. No seeds, protocol gates, geometry or outcomes were changed after observation, because no F019 suite observation had yet executed. Retest on next exact source SHA.
