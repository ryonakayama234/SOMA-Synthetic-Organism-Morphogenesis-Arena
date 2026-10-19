---
id: FIND-F011
kind: validation
status: preregistered_not_executed
updated: 2026-10-20
---
# F011 research record

## Preregistered BEFORE F011 code and experimental runs
**UNEXECUTED:** There is no F011 simulator output, test run, CI, measured COM displacement, real hardware evidence, reviewer acceptance, or main integration at the time of this entry. [Issue #34](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/34) / [SPEC](../topics/F011-grounded-internal-drive/SPEC.md) / [PLAN](../experiments/F011/PLAN.md).

Predictions from Newtonian COM momentum and ideal semi-implicit discretization are in SPEC and PLAN, with fixed controls A–F and `dt=.01,.005,.0025`. Neither an expected positive displacement nor any neural/morphological emergence has been established. Friction is a simplified ideal Coulomb law with static=kinetic threshold, not measured contact, battery or autonomous choice.

| Gate | At design-time freeze |
|---|---|
| Frozen hypothesis/controls and falsifiers | PREREGISTERED |
| F011 code/tests/experiment output | UNEXECUTED |
| Independent raw arithmetic replay | UNEXECUTED |
| Exact-HEAD CI and inherited regression | UNEXECUTED |
| Independent external human peer review | UNEXECUTED / unavailable |
| Researcher acceptance/main merge | NOT AUTHORIZED |

Append subsequent evidence with exact code SHA, CI run URL, observed negative cases, numerical errors, unsupported and inconclusive decisions. Never overwrite this preregistered history to make predictions appear observed.


## 2026-10-20 initial local candidate experiment (NOT formal adoption)

After the design-only PR #35 preregistered the A–F controls and stroke gate, a local Python 3 runtime model run was executed on the proposed F011 code. These are *software-model observations*, not Wolfram predictions or hardware data. Local exact-SHA GitHub CI and independent external human review were **not yet completed** at this point. Original design-time UNEXECUTED section above remains unchanged.

**Scientifically significant negative result:** case A (no ground) exceeds the preregistered 0.80m separation bound before reaching T=9.6s. First out-of-stroke step: dt=.01 → step 210 (attempted 0.806184929 m), dt=.005 → step 419 (attempted 0.800908020 m), dt=.0025 → step 839 (attempted 0.801788104 m). Up to that boundary, zero COM and zero total momentum are upheld. **H1 complete-duration comparison is INCONCLUSIVE; a finite-stroke internal oscillator without grounding is not viable for the preregistered duration.** Do not silently extend the stroke or change the drive period to manufacture a full negative-control success. The runner archives the valid prefix, attempted invalid state and status.

| Case | dt=.0025s local proposed-model observation | Decision at this stage |
|---|---|---|
| A no contact | full 9.6s blocked by upper stroke; partial COM 0 | H1 **INCONCLUSIVE for full duration**; conservation supported only on valid prefix |
| B equal-direction friction | final COM 0m; ground work negative | H3 SUPPORTED within frozen model |
| C directional friction +.02/-.08 | final COM **+3.5023819308m**; last two periods **+0.5003585453m, +0.5093500542m**, terminal r-period difference +0.0019165837m | H2 SUPPORTED **model-only**, under frozen criteria |
| D mirror friction +.08/-.02 | final COM **-3.5023819308m**, mirrored r exactly to float tolerance | mirrored counterfactual SUPPORTED within model |
| E no motor | final COM=0m and no ground work | no-actuation negative control SUPPORTED |

For C, final COM at dt=.01/.005/.0025 is 3.5160414549/3.5069738895/3.5023819308 m respectively. The medium/fine difference ~0.004592m satisfies the **predefined** max(0.002m,10% final displacement) criterion. C's ground work at finest is -1.8229002583J and motor signed work +2.2103937855J; maximal stored-scheme energy-identity error approximately 1.7e-15J. A continued no-ground run would require **new, separately preregistered model validation scope**; that task is not silently added here. The positive directional drift arises in a specially direction-dependent ground law; it **does not establish general emergent locomotion** on isotropic real floors, learning, or spontaneously formed organs.

The initially discovered stroke-boundary failure was not hidden or adjusted away. All local new F011 tests after that discovery passed (5/5 in an isolated Python environment); full-repo inherited tests and final-head GitHub Actions are separate subsequent gates. Preserve source-level scientific interpretation and tamper-negative evidence; exact authoritative HEAD CI must be appended after observed.

## 2026-10-20 exact GitHub CI #39286372313 and cross-Python forensic audit (BEFORE numerical-output hardening)

**Implementation SHA `d10a86930131871efbde8a273fc7822ff1d1add8`** passed [F011 GitHub Actions #39286372313](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39286372313) on Python 3.11 and 3.12 with full inherited unit discovery, optimized F011 tests and saved A–E×3 independent CSV oracle/two-root same-byte replay. Artifacts: [3.11 #12203601741](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39286372313/artifacts/12203601741), [3.12 #12203955657](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39286372313/artifacts/12203955657), each covering 32 original + 32 replay files (64 ZIP entries).

**Independent ZIP cross-version inspection:** all 60 original/replay non-aggregate raw-state/config files and other identical elements byte-match. **Four of 64 entries differ**: `F011-ci/comparison.json`, its `manifest.json`, and the two replay copies. Only floating `sum_ground_work_j`/`sum_motor_work_j` aggregation differed at floating roundoff (order ~1e-14J), producing corresponding SHA differences. No raw `states.csv` bytes diverged; the frozen scientific classification and stroke failure agree. This is **not** new physical variability. It exposes a reproducibility limitation of naive floating `sum` across Python 3.11/3.12. Preserve both original archives and failure-to-byte-match as genuine audit evidence, not a scientific contradiction.

**Separate correction, after above audit and without changing frozen hypotheses/parameters/physical row updates:** `soma/f011.py` accumulates recorded work with `math.fsum`, `experiments/F011/run_suite.py` uses `math.fsum` for scientific summary, `verify.py` independently checks with `math.fsum`. This only alters summary rounding, **not** ground friction, actuator update, controls, predeclared effect threshold or raw trajectories. Commits a1f036a → e320576 → a5b6e04. Fresh CI on the eventual documentation-inclusive HEAD and freshly downloaded 3.11/3.12 artifacts must be inspected; original `d10a869` success **does not** verify the corrected code yet. No formal adoption/merge authorization. Full-duration A remains INCONCLUSIVE.
