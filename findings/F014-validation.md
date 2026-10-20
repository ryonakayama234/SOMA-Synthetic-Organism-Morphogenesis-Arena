---
id: FIND-F014
kind: validation
status: preregistered_not_executed
updated: 2026-10-20
issue: 45
---
# F014 — one-bit peer response research log

## 2026-10-20: design-only preregistration / no F014 simulator runs

**UNEXECUTED.** The [SPEC](../topics/F014-peer-body-observability/SPEC.md) and [PLAN](../experiments/F014/PLAN.md) were written ahead of any new F014 implementation or experiment. The research objective and restrictions are tracked in [Issue #45](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/45).

Existing accepted F010 findings established indistinguishable A-only linked vs input-dependent-hidden-force histories in **the earlier F010 experiment**; do not relabel them as F014 results.

### Mathematical precheck only — Wolfram 2026-10-20
An exact rational Wolfram Language evaluation for masses 1 kg, dt=1/4 s, u∈{2,1,1/2} N gave:

| u (N) | A acceleration L/G/C (m/s²) | B Δv L (m/s) | B Δv G (m/s) | B Δv C (m/s) |
|---:|---:|---:|---:|---:|
| 2 | 1 | 1/4 | 0 | 1/4 |
| 1 | 1/2 | 1/8 | 0 | 1/8 |
| 1/2 | 1/4 | 1/16 | 0 | 1/16 |

Prediction: a B-local binary moved-bit separates linked L from unlinked ghost G, but not from unlinked co-forced C. **Neither the symbolic output nor a Draft PR establishes a demonstrated F014 software capability**. The result depends on F007's 1D external effective motor model and researcher-selected disturbances. This is not a statistical noise model or an information theoretic lower bound on all possible sensors.

### Evidence gate
| Gate | State on design preregistration |
|---|---|
| Hypotheses H14a–e and frozen control matrix | PREREGISTERED |
| F014 runtime implementation / F014 empirical trial data | UNEXECUTED |
| Independent saved-data oracle / tamper / byte replay | UNEXECUTED |
| Exact SHA Python3.11/3.12 CI | UNEXECUTED |
| External independent human reviewer | NOT PERFORMED |
| Formal scientific adoption / main merge | NOT AUTHORIZED |

When F014 is actually implemented, **append** numerical observations, failures, source hashes and CI URL in a dated later section; do not edit away this design-only snapshot or retrospectively modify threshold, cases, and hypotheses. Observe L/C observational equivalence as negative scientific evidence; do not claim this sensor proves mechanical coupling.


## 2026-10-20 — implementation proposal created; awaiting exact-HEAD GitHub CI evidence

Separate stacked branch `feat/F014-peer-body-observability-20261020` adds isolated typed F014 inferencer, the F007 frozen 15-run producer, researcher-only B velocity-bit projection, independent saved-data oracle, tests, byte replay and Python 3.11/3.12 workflow. Original F014 mathematical forecasts, thresholds and fixed cases are unchanged. This section is an **implementation milestone, not an observed F014 result**. Before any support claim, inspect a successful exact implementation SHA's CI log/artifacts, falsified-data tests, all regression suites and compare raw 60 peer observations; append a dated observed evidence and counterexample table. No external independent human review, real sensor, autonomy, topology identification or formal scientific adoption has occurred at this writing.


## 2026-10-20 — first *observed* F014 simulator run (before final config-envelope hardening)

**Observed in GitHub Actions, distinct from preregistered Wolfram theory.** Stacked implementation PR #47 at source commit `35469a1bcbb82bae8d49001a7fa44e0919155d28` passed [run #39445358867](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39445358867) with Python 3.11 and 3.12 both successful.

| Evidential gate | Actual CI observation, both Python versions |
| --- | --- |
| Inherited and added full regression | **186** tests pass per version |
| Optimized F014 boundary tests | **5** tests pass per version |
| Frozen F007 world trials | **15** of 15 simulated runs |
| A-local and B-peer interval rows | **60** each, all independently checked |
| Controlled step-2 missing B packet | **3** cases inconclusive |
| L vs G | B movement bit differs despite exact A local match |
| L vs C | All A-local and B packet rows byte-equal; structural counterexample survives |
| Two-root replay | **122** identical evidence files; success |
| Tamper / forged scientific summary rejection | negative tests passed |
| Exact source evidence artifacts | [Python 3.11 artifact #12277140197](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39445358867/artifacts/12277140197) / [Python 3.12 artifact #12277410021](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39445358867/artifacts/12277410021) |

CI stdout: `{"L_C_indistinguishable": true, "L_G_separated": true, "byte_replay": true, "cases": 15, "dropout_controls": 3, "evidence_files": 122, "local_intervals": 60, "peer_bits": 60, "replay_files": 122, "topology_identified": false}`.

**Science interpretation: SUPPORTED within frozen ideal F007 conditions**, conditional L/G peer-response discrimination *and* genuine L/C observational nonidentifiability; **not a proof of connected topology**. No human peer review, noise model, cryptographically authenticated sender, physical propulsion or organism autonomy. The reviewer must distinguish this real first successful SHA from later commits.

### Follow-up evidence-integrity hardening (post-initial-run, not changed hypotheses)

After the successful run, add one explicit `f014.config.v1` researcher-only envelope per world run and audit the frozen threshold/case/force identity against a freshly SHA-rehashed forgery. These changes do not alter the preregistered physical conditions. **Do not apply the preceding #39445358867 success to subsequent source hashes.** The final new SHA requires its own CI evidence and verified artifact count before scientific acceptance or any merge.
