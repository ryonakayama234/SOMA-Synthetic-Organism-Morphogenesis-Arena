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
