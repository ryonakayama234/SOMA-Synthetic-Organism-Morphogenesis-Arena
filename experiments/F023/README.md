# F023.v1 — frozen private-ground-impulse encounter experiment

**Implementation candidate only until source-bound CI, independent audit, reviewer analysis and formal decision.** Exact immutable preregistration: [FROZEN_V1](FROZEN_V1.md) at `76dcc1db7ae12737705da06c155933d0a8251853`; anchor in [Issue #81](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/81).

This is NOT a robot propulsion or self-assembly experiment. Two *unconnected* ideal disks receive optional researcher-prescribed t=0, **ground-reaction-balanced**, privately funded impulses before immutable F022 passive 2D TOI. No sensor, adaptive policy, lifecycle, docking, agent reward, visual UI, continual motor or real contact actuator. Only a new bounded computational instrument.

From project root on Linux / WSL2:
```bash
python -m unittest discover -s tests
python -O -m unittest discover -s tests -p 'test_f023.py'
python -m experiments.F023.run_suite --out /tmp/f023-a
python -m experiments.F023.verify --root /tmp/f023-a --expected-source-sha "$(git rev-parse HEAD)"
python -m experiments.F023.attack_test --root /tmp/f023-a
python -m experiments.F023.run_suite --out /tmp/f023-b
diff -r /tmp/f023-a /tmp/f023-b
```

**Frozen declared outputs** (new target directory only): `scenario.json`, `actions.jsonl`, `ledger.jsonl`, `states.jsonl`, `contacts.jsonl`, `audit.json`, `manifest.json`. `f023.archive.v1` names and typed fields are binding, including 15 scenes / 135 t-grid frames / 30 private actions / 30 ledger balances and five rejected invalid probes. Nine contacts are a preregistered prediction subject to independent validation, not presupposed empirical emergence. World truth never becomes a cell sensor. Corresponding future UI panels are in [ARCHITECTURE](../../docs/ARCHITECTURE.md) and [DATA_CONTRACTS](../../docs/DATA_CONTRACTS.md).

Technical acceptance requires final exact-source cross-Python CI and all inherited F001–F022 regressions, from-disk independent physics/private-charge recomputation, 10 rehashed semantic adversaries, two clean-root byte replay, archived source and interpretation. Same-AI critical review is not external third-party validation. No frozen protocol/previous source may be reinterpreted after results.
