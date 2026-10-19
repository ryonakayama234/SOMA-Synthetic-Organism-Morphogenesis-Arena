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

## 2026-10-20 independent AI research-audit follow-up — comparison integrity correction (pre-acceptance)

Review scope: Issue #34 / frozen design PR #35 / stacked implementation PR #36. Reviewer is an **AI research auditor**, not an independent human researcher or external peer-review body; different-session reasoning and Wolfram calculations do not confer third-party human approval.

**P1 evidence-integrity finding, post-experiment:** prior `experiments/F011/verify.py` independently checked per-step CSV physics and ground work, but did not recalculate **every** published `comparison.json` numerical metric (e.g. `results/C-directional/0.0025/last_period_m`). Editing that primary outcome and recomputing the file SHA in `manifest.json` would pass the earlier oracle so long as the independently calculated binary `persistent_directional_model_drift` status remained unchanged. This threatens trust in reported effect magnitude even though it is not evidence of an actual historical forgery. Existing CI success and raw/replay byte identity cannot exclude this class of edited-summary attack.

**Correction (new commits after `299eb388`):** verifier independently rederives all complete-case comparison fields from saved CSV (period drift, return displacement, summed motor/ground work, energy/impulse errors, stroke extrema), validates missing/extra fields, and preserves the previous A partial-run check. A new negative test modifies the C period displacement by +0.125m, recomputes manifest SHA and requires verifier rejection. Frozen SPEC/PLAN, runtime forces, initial conditions, numerical integration and all historical raw artifacts remain untouched. No new research hypothesis, model condition or retrospective acceptance threshold was introduced.

**Independent mathematical corroboration:** a new Wolfram Language implementation of the specified velocity-proximal Coulomb update and semi-implicit position step separately reproduced all 15 A–E x 3-grid outcomes: A first invalid steps 210/419/839, C final COM +3.51604145489474/+3.50697388953050/+3.50238193081765 m, D exactly mirrored, B/E COM 0. For finest C the final two period shifts are +0.5093500542m and +0.5003585453m, with terminal stroke return approximately +0.0019165837m. This corroborates the frozen **discrete model**, not real contact physics or an independent human replication.

**Unchanged scientific exception:** A's full 9.6-second no-ground run remains outside preregistered 0.2–0.8m stroke at approximately 2.1s. H1 full-duration gate is INCONCLUSIVE; analytic/valid-prefix COM conservation does **not** retroactively make the required full A run complete. Consequently no unconditional formal adoption is requested. A narrower adoption, if ever considered, requires a separately documented researcher decision without relabeling the frozen gate.

**CI/revalidation gate:** this entry documents the correction, **not a claim** that CI for this new documentation-inclusive HEAD has passed. Verify Python 3.11/3.12 full regression and negative tests, generated 15 runs and raw artifact links against the *new exact commit* before approval. Preserve old `299eb388` CI and ZIP as historical evidence only. PR #35 and PR #36 must remain Draft and Issue #34 open; do not merge into main or declare adopted without explicit researcher authorization. Human external review, hardware ground tests, autonomous invention, morphology, learning and physical power efficiency are still not established.
