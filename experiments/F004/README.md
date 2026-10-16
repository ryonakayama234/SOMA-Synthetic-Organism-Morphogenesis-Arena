# F004 reproducible motor/battery A-F experiment

## Status
Implementation candidate, not yet formally adopted. Independent review and PR #11 approval are separate from CI success. F003 coupling and real hardware are out of scope.

## Run in WSL2/Linux bash from repository root
```bash
python -m unittest discover -s tests -v
python -m experiments.F004.run_suite --output-dir runs/F004-manual --replay-output-dir runs/F004-manual-replay
```
Do not reuse the output paths: results are deliberately not overwritten. GitHub Actions workflow `.github/workflows/f004.yml` runs the same commands on Python 3.11 and uploads the raw A-F evidence.

For an individual run, pass a valid `f004.v1` JSON file:
```bash
python -m soma.f004 --config runs/F004-manual/B-full/config.json --output-dir runs/F004-single
```

## Evidence
- Each run saves `config.json`, `states.csv`, `ledger/events.csv`, `motion_energy.svg`, and `manifest.json`.
- Suite saves `suite_source.py`, `comparison.json`, `rejections.json` (17 invalid cases after review), ten A-F controls, a B replay and optional full-suite `full_suite_replay.json`.
- `comparison.json.cases` is constructed from **saved files** with an independent stepwise Euler and F002 accounting oracle. It checks time, force provenance, position, velocity, battery gating, energy rounding, event references, conservation and per-artifact hashes.
- F004 has no random process; `seed: null`. Each manifest records Git revision, dirty status, F001/F002/F004 SHA256, suite source SHA256, all raw artifact SHA256. Freeze provenance before making output folders.
- `B-full` preregistered binary64 final balance 499995 µJ (rational ideal 500000); `D-low` 54996 µJ (rational ideal 55000). Tolerances for 1D baseline positions/velocities: 1e-12.
- A zero-balance and zero candidate work cancellation counterexample is explicitly checked. A positive-balance zero-work motor is **free only in the ideal model**, not in a real motor.
- A successful suite only establishes software consistency under its idealized assumptions, not emergent morphology, evolution, real battery behaviour or independent external review.

Reference: [F004 specification](../../topics/F004-actuation-energy/SPEC.md), [A-F preregistration](PLAN.md), [finding log](../../findings/F004-validation.md), [architecture](../../docs/ARCHITECTURE.md), [data contracts](../../docs/DATA_CONTRACTS.md), [PR #11](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/11).

## Review hardening (2026-10-16)
All Config constructors validate inputs, including direct construction and `dataclasses.replace`. The exact decimal time ratio must remain unchanged after float normalization; unrepresentable grids are rejected rather than truncated. Plot coordinates normalize before large products/subtractions. The saved-run verifier requires the exact four-artifact inventory and checks zero work/energy delta at the initial row independently of updated CSV hashes. Existing A-F predictions and the binary64 motor-work formula are unchanged. See the finding log for review counterexamples and current validation evidence.
