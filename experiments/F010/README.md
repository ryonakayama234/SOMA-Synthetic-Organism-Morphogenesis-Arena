# F010 reproduction — active local response identifiability

Status: implementation candidate **NOT ADOPTED**, separate design Draft PR #32 / Issue #31. Requires Python 3.11 or 3.12 and standard library. No modifications to adopted F007/F008/F009 or V001.

Run from repository root:

```bash
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -p test_f010.py -v
python -m experiments.F010.run_suite --output-dir runs/F010-ci --replay-output-dir runs/F010-replay
```

Output directories must not exist, overlap or nest. Every case generates three *independently initialized* F007 `config.json`, `states.csv`, `link_events.csv`, `ledger/events.csv`, `motion.svg`, `manifest.json` subdirectories, plus `local.csv`; top level has `comparison.json` and `manifest.json`. Frozen references and science limits: [PLAN](PLAN.md), [SPEC](../../topics/F010-local-identifiability/SPEC.md), [FINDINGS](../../findings/F010-validation.md). Distinct A-local force probes are arranged by the *researcher* offline; no cell-autonomous probing, learned body schema or topology detection. A linked case and an input-dependent unknown-force case are observably identical.

Do not delete previous evidence or conflate generated files with Git-tracked historical scientific results. CI artifacts, identified by job/run HEAD SHA, provide raw data for replay.
