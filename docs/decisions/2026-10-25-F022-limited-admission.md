---
id: DECISION-F022-ADMISSION-2026-10-25
title: F022.v1 限定技術採用と科学判定
kind: research_decision
status: TECHNICALLY_ADOPTED_MODEL_BOUNDED
updated: 2026-10-25
related: [F022, ISSUE-77, PR-78, PR-79]
keywords: [F022, physics, collision, admission, evidence, science_boundary]
---

# F022.v1 limited technical adoption — 2026-10-25

## Decision
**ADOPT the versioned passive 2D two-disk continuous-collision instrument as a bounded computational research baseline only.** [Design PR #78](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/78) then [implementation PR #79](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/79) manually merged. Preregistered exact scientific protocol SHA `3984e9dcb2cb420abab5ca92b4d029b31b5173f8` precedes F022 primary observations; implementation merge main SHA `824a8621944ea438388c54949a2b65719be2e419`.

## Evidence and gates
At merged-main source SHA, [F022 CI #40176213718](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/40176213718) **succeeded in Python 3.11/3.12** with inherited full unit regressions, optimized F022 tests, source-bound producer, separate on-disk analytic verifier, eight rehashed semantic forgery tests and byte-identical two-root replay. **22/22 merged-main workflows passed**: F001–F021 and F022. 13 fixed worlds, 117 2D sample records, 10 contacts (9 impulse, 1 geometric zero impulse), 3 no-contact worlds, 5 invalid-input rejections. [Full append-only findings](../../findings/F022-validation.md) / [machine-readable summary](../../findings/F022-ci-summary-2026-10-25.json) / [frozen original contract](../../experiments/F022/FROZEN_V1.md).

Local Python3.13 post-implementation audit observed max momentum residual 0 kg·m/s, max KE-budget residual 1.1102230246251565e-16 J, max contact penetration 1.1102230246251565e-16 m. In merged-main CI Python3.11/3.12 those metric gates passed preregistered 1e-9 SI criterion; raw per-version exact residual floats have not been independently extracted for this note. CI artifacts may expire after 30 days, source and compact summary persist.

## Separate scientific verdict (do not overstate)
- H22a: **SUPPORTED under this prechosen ideal two-disk physics**; no unexplained momentum or energy contribution.
- H22b: **SUPPORTED under tested geometry**; miss, glancing, tangent, head-on, symmetry and fast collision distinguishable.
- H22c: **SUPPORTED for frozen archived evidence and tested forgeries**; source-independent mathematical re-derivation and eight forged/rehashed negatives.
- Rivals R22a/R22b: challenged by analytic high-speed and conservative-energy controls; not proof against untested solver regions.
- No external human peer review obtained; separate-code-path verifier and assistant self-criticism must not be called third-party peer review.

The above is **not** 2D grounded autonomous locomotion, real battery energetics, joining, attachment, consent, learned local body knowledge, cooperative payoff, self-assembly, organismality or open-ended evolution. No statistical biological significance claimed from 13 selected deterministic cases. V001 remains a separate unadopted 1D viewer Draft.

## Research process disposition and next boundary
Technical adoption gate satisfied without retroactively changing F001–F021 or rewriting the preregistered protocol; version and SHA remain discoverable. Issue #77 may close after the adoption record is merged and documented. The next research selection should isolate **a separate single capability** (e.g., physically meaningful 2D actuator/ground reaction or persistent attachment) with its own preregistration and independent acceptance; adding join behavior directly into F022.v1 would destroy scientific identifiability. [Original selection history](2026-10-25-F022-selection.md) remains immutable.
