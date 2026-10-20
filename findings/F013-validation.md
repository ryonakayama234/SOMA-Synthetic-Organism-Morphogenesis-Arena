---
id: FIND-F013
kind: validation
status: preregistered_not_executed
updated: 2026-10-20
---
# F013 experimental record

## 2026-10-20 design-only preregistration — no F013 run
**UNEXECUTED**. F013 hypothesis, controls and acceptance rules are recorded before writing F013 simulation code or observing any F013 output. See [SPEC](../topics/F013-contact-rectification/SPEC.md), [PLAN](../experiments/F013/PLAN.md), Issue #42. Baseline main `004d4dcf045bbea42a6b2aa2ecbe6c125f7881bf`.
Existing F011 result (+3.5023819308m C at dt=.0025) is a prior observation under *another friction model*, not an F013 prediction/observation. F011 no-contact A full 9.6s remains INCONCLUSIVE. The predetermined eps values are research choices, not realistic measured friction smoothing parameters.
| Gate | At design-only checkpoint |
| --- | --- |
| Frozen hypotheses and 36 controls | PREREGISTERED |
| F013 implementation / 36 runs / tests | UNEXECUTED |
| Independent math / saved-data verification | UNEXECUTED |
| Python3.11/3.12 CI exact HEAD | UNEXECUTED |
| Independent human/external scientific review | NOT PERFORMED |
| Researcher adoption and main merge | NOT AUTHORIZED |

Append observed results and failures with code SHA/CI links without rewriting this section or silently moving thresholds.

## 2026-10-20 initial F013 numerical experiment and AI/mathematical audit — CANDIDATE, NOT ADOPTED

**Chronology and source of observations:** frozen design-only preregistration commit `7dd962d183b3382761c1a809142b2a1effc031dd`, [design Draft #43](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/43), strictly before any F013 implementation. New source on separate [implementation Draft #44](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/44). First documentation-complete experimental source HEAD `26af40f7cd2e377355b8ef86ba40f79a7c16b3af`, [F013 push Actions #39419760994](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39419760994) and [F013 PR Actions #39419768678](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39419768678) both succeeded for Python 3.11 and 3.12. **13 PR-triggered F001–F013 workflows succeeded on this SAME commit**, independently of the 3.11/3.12 push F013 execution. Each F013 version ran 178/178 full regressions and 5/5 optimized tests; 36 frozen cases, independently checked raw constitutive equation/energy/momentum, pointwise 3eps×3dt mirrored controls, hash-bound source plus semantic summary, 74 raw files ×2 byte-identical output roots *within each Python version*. Archived runner ZIPs: [3.11 artifact #12263362217](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39419760994/artifacts/12263362217), [3.12 artifact #12263671732](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39419760994/artifacts/12263671732). **Cross-version byte identity was not independently established**. Historical evidence was not rewritten. These CI claims refer to `26af40f` only; later commits must be rechecked.

### Actual C-directional values, 9.6 s, dt=0.0025 s (F013 model outputs, NOT Wolfram forecasts or hardware)

| Width eps (m/s) | COM displacement (m) | Final period (m) | Previous period (m) | End r return (m) | Sum passive ground work (J) |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0.020 | +3.3930258156 | +0.4878535893 | +0.4808874919 | +0.0038809328 | −1.8095100523 |
| 0.005 | +3.4822192017 | +0.5054167459 | +0.4967332067 | +0.0022456459 | −1.8202479214 |
| 0.001 | +3.4996816262 | +0.5089431831 | +0.4999078368 | +0.0018476001 | −1.8227914032 |

All 36 runs B/C/D/E × 3 widths × 3 timesteps completed 9.6s without the frozen 0.2–0.8m relative stroke guard being violated. B isotropic COM remained zero, E no-drive static, D opposite-sign mirror of C at **every saved timestep**, and friction work was nonpositive with recorded momentum/energy identities. At finest C width 0.001, independent raw-CSV audit found max momentum residual `2.776e-16 N*s` and max discrete energy-identity defect mismatch `1.689e-15 J`; these are numerical model consistency, not real-world accuracy.

**H13a SUPPORTED within three frozen alternative model configurations:** each finest-grid C+D pair satisfied preregistered last-two-period same-sign, >1mm, >=50% relative magnitude, r-period return <=1cm and numerical gate. Positive sign C, negative D. This cannot imply robust locomotion for ALL contact models, nor make the direction coefficient self-selected.

**H13b SUPPORTED against the preregistered, intentionally limited 2mm/10% final-COM timestep gate** for ALL 12 case×eps comparisons of 0.005 vs 0.0025s. This does NOT demonstrate a continuous-time limit, strict monotonic refinement, or solver independence in the *entire* integration loop. The new F013 solver uses a separate implicit bisection friction substep but retains F011's semi-implicit position update and identical springs. A broader independent simulation architecture was NOT tested.

**H13c INCONCLUSIVE on physical-model equivalence**, although numeric model discrepancy is measured: at eps=0.001, dt=0.0025, F013 C = +3.4996816262m and accepted F011 original C = +3.5023819308m, giving **−0.0027003046m** at the specified finite epsilon. F013 eps=0.020 differs more. Three finite widths do not prove eps→0 convergence or that the real contact law is correct.

**H13d SUPPORTED for the frozen numerical identity/negative controls conditional on successful independent raw audit:** 36-case row-by-row verifier passed under two Python versions. The first output schema at commit `26af40f` still names this field `INCONCLUSIVE_UNTIL_INDEPENDENT_RAW_AUDIT` as a pre-audit publication state; later code changes clarify this classification after verify. The source-bound rehash-forged scientific comparison negative was detected. Neither author authentication nor maliciously modified Python runtime can be excluded.

### Independent Wolfram arithmetic cross-check (NOT a second F013 simulation / human review)

Using high-precision `FindRoot` independently for the **first** C interval at h=.01s, eps=.02m/s, u=+1N, the alternative implicit contact equation yields:
`vA=+0.009159421988891862m/s`, `vB=-0.007267468045899013m/s`, `fA=-0.08405780111081378N`, `fB=+0.27325319541009866N`, `ΔXcm=+0.00000945976971496424m`, `Wground=-0.0000275577973791498J`, momentum residual zero. This is a computation for the mathematical F013 rule, not independent physical confirmation. A post-experiment unit test pins these values with stated tolerances; it was **not** a preregistered empirical forecast. F011's corresponding step differs because its contact law is different.

### Important retrospective audit correction: friction is continuous but NOT globally smooth

The original frozen SPEC describes a "smooth" tanh friction, but `mu_dir(v)` changes discontinuously at the sign crossing when mu_plus != mu_minus. Because `tanh(v/eps)→0` at v→0, `f_eps(v)` is **continuous (C0)**. Its one-sided derivatives at zero are `-mg mu_plus/eps` and `-mg mu_minus/eps`, so it is **NOT C1** for directional C/D. This does NOT invalidate the monotone implicit bisection solver or passivity, but strictly limits claims of smooth dynamical regularization. **No frozen equation, width, hypothesis or observed data is changed after this audit.** Later prose should call it a *continuous tanh-regularized direction-dependent contact law*, not a globally differentiable smooth law. In isotropic B, the one-sided derivatives coincide.

This distinction is relevant to the numerical-contact literature, including [Areias et al., 2019, regularized friction and inertial contact](https://doi.org/10.1016/j.finel.2019.103321), and [Acary, 2013, projected event-capturing nonsmooth friction integration](https://doi.org/10.1016/j.cma.2012.12.012). Those sources are PRIOR WORK, not SOMA experimental data, and do not prove F013's hardware relevance.

### Independence, publication and decision

The independently coded saved-CSV oracle, independent Wolfram first step and two interpreter versions are distinct computational checks but were all orchestrated by the same AI assistant. **Independent external human scientific peer review NOT PERFORMED** and cannot be claimed. GitHub Actions artifacts have finite retention: exact source, pinned SHA, reproduction commands and scientific summary remain in repository, but full raw CSV persistence beyond artifact retention is NOT guaranteed. No actual robot/surface friction, force-feedback policy, self-body model, energy budget, morphology optimization or human visual browser test. F011's full no-contact 9.6s control stays INCONCLUSIVE under Issue #37. Formal research adoption and merging BOTH PR #43 / #44 are expressly withheld for researcher decision.
