---
id: FINDINGS-F020
title: F020 代謝閉ループ・実験証拠（追記専用）
kind: scientific_findings_append_only
status: PRELIMINARY_SOURCE_BOUND_EVIDENCE_UNADOPTED
updated: 2026-10-23
issue: 67
---
# F020 validation — proposal history and source-bound first observation / NOT ADOPTED

**Current truth:** No `soma.f020` implementation, no F020 world, no F020 saved artifact, no model outcome, and no formal adoption. The design on [Issue #67](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/67) is **NOT frozen**, and cannot be represented as a finished preregistered test. [SPEC](../topics/F020-metabolic-feedback/SPEC.md) / [candidate PLAN](../experiments/F020/PLAN.md).

## Parent result (NOT F020 evidence)
F019 main commit `7de755c79fed3b806417da5c15f0115ea7ac04c8` merged 2026-10-23; 19/19 post-main workflows succeeded. F019 froze 32 environmental seeds, 512 scenarios, 3,584 worlds and observed 580 of 1,792 owner-status changes, **0/512** bilateral-positive cases; fixed high starting batteries prevented harvest affecting motor trajectories. Those observations belong exclusively to [F019 findings](F019-validation.md).

## Independent Wolfram theory precheck (NOT simulation)
+2N, dt=1/4s, no drag, initial v=0, masses 1+1kg: linked first-step energy `1/16J = 62,500µJ`; unlinked A first-step `1/8J = 125,000µJ`. For A with 75,000µJ and fee0, the linked first move is affordable; its next motor candidate at v=1/4m/s needs `3/16J = 187,500µJ` and therefore needs resource A actually acquired in a previous step. A chosen patch in this demonstration is calibration only, never part of random-field inference.

## Required evidence to append, without rewriting negative outcomes
| Item | Observed F020 data | Gate |
|---|---|---|
| Exact freeze SHA / source and sample plan | NONE | NOT FROZEN |
| Feedback versus deferred-credit causal forks | NONE | UNEXECUTED |
| A/B individual net and rejected/accepted step timeline | NONE | UNEXECUTED |
| Boundary, no-resource, B-only, high-budget and mirror controls | NONE | UNEXECUTED |
| Independent saved-data verification and rehashed tamper detection | NONE | UNEXECUTED |
| Python 3.11/3.12, source-bound SHA, two-root replay and post-merge CI | NONE | UNEXECUTED |
| Critical review, bounded adoption decision | NONE | NOT AUTHORIZED |

Scientific labels: SUPPORTED / REFUTED / INCONCLUSIVE / UNEXECUTED, separate from software technical acceptance. No external human peer review is claimed.

## 2026-10-23 exact-rational positive control (THEORY ONLY; not F020 execution)

Wolfram verified a separate hand-placed x=1/16m, radius 1/200m, 1J patch fixture (75,000µJ initially each, zero join fee, +2N, four 0.25s steps). After A's first-step claim, YY feedback predicts xA(1s)=5/8m versus YY deferred xA(1s)=1/4m; both NN forks predict xA(1s)=0m. YY deferred retains vA=1/4m/s after motor refusal; 1J is pending only until post-episode settlement. Exact details and limits in [internal audit](../docs/reviews/2026-10-23-F020-preobservation-audit.md). These numbers are **theoretical expectations for a calibration fixture**, **not** F020 simulator results; primary random-field evidence remains NONE.

## 2026-10-23 pre-observation design audit (NOT F020 world evidence)

An internal independent-formula review of F005/F007 and Wolfram exact fractions revealed that the initial 1,000,000 µJ "high-battery" candidate cannot run four nonlinked ±2N 0.25s steps without energy stalls. Expected positive motor work (linear-velocity integral with F005 ceil µJ gate) is NN **2,000,000 µJ**, YY **1,000,000 µJ**, in contrast to the larger motor-force × semi-implicit displacement product. High-budget candidate revised to **4,000,000 µJ pre-observation**, while preserving the 32-seed, 1536 proposed scenarios/6144 candidate worlds factorial. Detailed critique and contract timing: [design review](../docs/reviews/2026-10-23-F020-preobservation-audit.md). F020 is still **NOT FROZEN / UNEXECUTED / NOT ADOPTED**; no real F020 trajectory or positive result has been observed.


## 2026-10-23 F020 FIRST SOURCE-BOUND PRIMARY OBSERVATION — exact-head CI, not adopted

**Evidence status:** The historical headings and "Current truth: no F020 world" paragraphs ABOVE were valid at the proposal stage and remain **append-only historical notes**. They are superseded by this dated, later source-bound observation. F020 remains **implementation PR only, NOT MERGED TO MAIN, NOT FORMALLY ADOPTED**. This is an engineering-supported result in a fixed 1D investigator-controlled model, not an autonomous body/metabolism finding.

- Design was frozen **before any F020 world** by [FROZEN_V1 protocol](../experiments/F020/FROZEN_V1.md) in Git commit `f3e3a4de4ff47677db575efaafe342655dede6c2`; parameters fixed: original F019 32 SHA256 environment seeds × 2 motor signs × 2 densities × 2 patch radii × 3 balances × 2 joining fees = **1,536 canonical scenarios**, each `YY/NN × feedback/deferred_credit` = **6,144 archived worlds** and **3,072 direct feedback-vs-deferred paired comparisons**. Calibration fixtures excluded.
- [GitHub Actions full reproducible run #39950334330](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39950334330) passed on **Python 3.11 and Python 3.12** at the **exact checked-out PR head/source SHA `80ca70d95c2a870a357a12c449b10f0109cb8686`**: 239 full F001–F020 regression tests per interpreter; 6,144 simulated worlds per clean producer root, two roots per interpreter; source-bound no-producer-import from-disk verifier; **9/9 on-disk semantic forgeries rejected even after replacing artifact SHA256**; exact byte comparison of the two complete output roots; uploaded archived `f020-worlds-py3.11` and `f020-worlds-py3.12` evidence artifacts. This source SHA is a *passing baseline*. Later documentation-only commits must earn a separate exact-head passing CI before final PR acceptance.
- **Primary observed paired result:** feedback vs deferred credit changed **A's final trajectory in 321 / 3,072** paired contrasts. In the same **321** contrasts the feedback arm authorized ≥1 step of A motor that the deferred arm refused. Directional displacement along the prescribed ±2N command was positive in those 321 and negative in zero of the fixed matched conditions. This is a conditional within-simulator mechanism, **not** a policy/fitness result.
- **Claimant-map changed in 64 / 3,072 pairs** (at least one patch's claimed/unclaimed or claimant-A/B map differed); this is a pair count, **not** 64 independently sampled patches or an independent causal body-benefit endpoint.
- For descriptive ecological uncertainty, **only 32 externally generated environment seed blocks** are distinct; **27/32** have at least one nonzero trajectory response, five have none. The 3,072 pairs are correlated factorial reuse and must NEVER be reported as independent replications. There is no inferential p-value or observed spontaneous joining.

| Initial energy per cell | Fixed joined YY: changed / 512 | Fixed unjoined NN: changed / 512 | Claimant-map-changed YY / NN |
|---|---:|---:|---:|
| 75,000µJ | 33 / 512 | 0 / 512 | 2 / 0 |
| 250,000µJ | 82 / 512 | 206 / 512 | 6 / 56 |
| 4,000,000µJ | 0 / 512 | 0 / 512 | 0 / 0 |
| **Total** | **115 / 1,536** | **206 / 1,536** | **8 / 56** |

**Mechanistic interpretation:** at low NN energy (75kµJ), A cannot afford its first 125kµJ step and therefore cannot reach a new field patch under this initially stationary topology; at 75kµJ YY A can afford the first 62.5kµJ step, potentially acquire its own resource and drive again. At high 4MµJ neither topology depends on newly acquired energy within four steps, agreeing with the Wolfram positive-work upper-bound control. With medium energy, some NN worlds obtain enabling resource and thus exhibit more feedback-sensitive paths than YY. All geometrical field placements are frozen F019 fields, not individually tuned to these outcomes. The separate hand-placed Wolfram technical positive control (YY A position 5/8m vs deferred 1/4m at 1s) also passed unit assertions; it was **not** counted as ecological evidence.

**Falsifiers and scope:** F002 integer energy residual always zero and no A↔B transfer; a B-only resource does not authorize A; no same-step retroactive credit; motor refusal does not cancel inertia; no-field and motor-off controls; high-battery F007 motion parity; independent field/ledger/motion rederivation. Tested rehashed attacks: physical position, applied motor, claimant, harvest timestamp, retroactive energy eligibility, pending amount, spend source, field geometry, falsified manifest count. Independent auditing is **source-code independence** (verifier deliberately does not import producer/`soma`); it is NOT external human peer review. No actual ground reaction, docking, learner, dual drive, dynamic topology, autonomous joining, chemical metabolism, fitness, organismality or ecological generalization has been shown.

**Reproduction (WSL2/Linux, clean PR head)**:
```bash
python -m unittest discover -s tests -p 'test_*.py' -q
python -m experiments.F020.run_suite --output-root runs/F020-a
python -m experiments.F020.verify runs/F020-a
python -m experiments.F020.attack_test --root runs/F020-a
python -m experiments.F020.analyze --root runs/F020-a
python -m experiments.F020.run_suite --output-root runs/F020-b
diff -rq runs/F020-a runs/F020-b
```

**Verdict at this stage:** technical evidence supports the existence of the requested next-step feedback in the 1D toy simulator, subject to current documented-source CI and review; **implementation remains a Draft PR #69 stacked on design PR #68; no main merge and no formal instrument adoption.** Preserve this observation, including null seeds and zero-effect high battery, even if future studies find no robust coalition benefit.


## 2026-10-23 deeper raw-world reanalysis and internal conditional adoption review (APPENDED; NOT post-main)

This addendum does not replace the previously timestamped first observation or preregistration. Read the detailed [internal critical-review and conditional decision](../docs/decisions/2026-10-23-F020-limited-acceptance.md), based on an **actually downloaded** Python 3.11 GitHub Actions artifact `12501545195`, `worlds.jsonl` SHA256 `8972ab33ef8429b9c605a38aac7f12bfb2ec10ebbbdf7c2d9e570d3475b31c7a`, source SHA `e32ae59bfeee321fc76c3bc9ccd3e9bf65781ccf`, [complete current-source run #39951381134](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39951381134): Python 3.11/3.12 239 regression tests each, full 6,144-world independent archive verification, 9/9 rehashed disk forgeries rejected and two-root byte replay. **All 20 workflow types passed on the same exact source SHA.** External human peer review has **not** been obtained.

**Exploratory subgroup results, not predeclared acceptance thresholds:** 321/3072 feedback-vs-deferred pairs changed A motion; 27/32 reused field seed blocks had ≥1 effect. Among *those 321 changed pairs*, A terminal **net µJ was smaller in 263**, equal in 36, greater in 22; **B net was identical in all 3,072 pairs**. Distinct future resource claimant-map differences occurred in 64 pairs, representing 74 additionally captured 1J A patches; B acquisition maps did not change. All 64 were in the 5-patch fields (2-patch cases produced zero changes). Median A directional displacement among the 321 changed pairs was 0.1875m (range .0625–.75m). At 75k initial balance and YY fee 25k A cannot afford its first 62.5k step, whereas YY fee0 yielded 33/256 movement-changing pairs; NN 75k cannot afford its 125k initial move regardless of fee. These patterns underscore that **movement enablement is not positive net energy, bilateral surplus, learned joining, or viability**.

**Representative observed path, independently confirmed with Wolfram exact recurrence:** canonical primary scene `s01-n5-r060-sign-1-bal0250000-fee00000`, NN; A acquires a 1J patch near x=−0.175m during step1. In feedback, A motors steps 1–3, reaches −1.125m at k4 and discovers an additional P4 patch; in deferred credit, A motors step1 only, coasts to −0.5m at k4, P4 remains unclaimed. This is *post-observation illustrative selection* and should not be treated as preregistered independent validation.

**Internal conditional decision:** The requested resource→same-cell next-step motor causal mechanism is supported **within the frozen ideal 1D simulator**. Approve only its potential integration as a **limited, source-verifiable software measurement instrument** if the final doc-inclusive head CI and then post-main F001–F020 CI pass; never attach autonomous metabolism, fitness optimization, self-assembly or ecological-generalization claims. Preserve historical outcomes and all nulls. Status at this append: **CONDITIONALLY_APPROVED_NOT_YET_MERGED**.
