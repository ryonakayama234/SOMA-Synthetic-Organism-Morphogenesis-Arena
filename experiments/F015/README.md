# F015 — preregistered active-body probing (implementation candidate)

Tracks [Issue #48](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/48), design [Draft PR #49](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/49), [SPEC](../../topics/F015-active-body-probing/SPEC.md), [PLAN](PLAN.md), [FINDINGS](../../findings/F015-validation.md).

One frozen question: held exogenous forces versus input-tracking confound after 2/1/0 N full-reset probes in a fixed F007 1D world. Five cases × three independent trials × four steps = **15 runs / 60 A-local + 60 B-bit observations**, no learned policy. Compare A-only and A+boolean additional discrimination; NEVER output a verified mechanical attachment classification.

From repository root (Python 3.11 or 3.12; no third-party Python packages required):

```bash
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -p test_f015.py -v
python -m experiments.F015.run_suite --output-dir runs/F015-ci --replay-output-dir runs/F015-replay
```

Unmodified F007 engine stores raw physical truth under each case/force in `F007/`. Researcher-only adapter writes `a_local.csv` (strict F008 allowlist), `b_packets.csv` (strict F014 1-bit sensor and packet time/source framing). `probe_schedule.json`, `comparison.json`, `manifest.json` bind frozen experimental identity and source/file SHA256. The separate `verify.py` never imports F015 producer/inference; every raw row is audited using the existing F007 independent arithmetic verifier and separate exact rational references, then local and packet projections and hypothesis outputs are independently reconstructed. Two fresh output roots must be byte identical; refusals and tamper negatives are tested.

**Before successful exact-HEAD CI and human research interpretation this is CANDIDATE ONLY.** Wolfram theoretical predictions are not observed trial data. No external peer review, noisy sensor, online control, autonomy, 2D world, or physical coupled robot implied.
