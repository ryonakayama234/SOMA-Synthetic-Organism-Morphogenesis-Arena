# F005 — 1D motor positive-work integration experiments

## Status
Implementation candidate on a separate GitHub PR. It is NOT yet an adopted scientific result. F004 remains the accepted historical baseline. No two-cell mechanical or electrical integration, autonomy, learning, or real battery model is included.

## WSL2/Linux commands
Run from repository root on Python 3.11:

```bash
python -m unittest discover -s tests -v
python -m experiments.F005.run_suite --output-dir runs/F005-manual --replay-output-dir runs/F005-manual-replay
```

Choose unused output directories: evidence is never overwritten. A single case can be replayed:

```bash
python -m soma.f005 --config runs/F005-manual/A-reversal/config.json --output-dir runs/F005-single
```

## Source of truth
`topics/F005-positive-work/SPEC.md` and `experiments/F005/PLAN.md` preregister the ideal assumptions, numeric expectations and rejection criteria. The `run_suite.py` verifier loads saved `states.csv`, `ledger/events.csv`, `manifest.json`, and `config.json`, independently computes Euler motion, signed/positive work, integer microjoule spending and F002 residual, and compares all steps. It does not import the F005 step or positive-work implementation for the oracle.

## Data
- Per run: `config.json`, `states.csv`, `ledger/events.csv`, `motion_energy.svg`, `manifest.json`.
- Suite: `suite_source.py`, `comparison.json`, `rejections.json`, replay runs, optional `full_suite_replay.json`.
- Artifacts include exact per-file SHA256, F001/F002/F005 code SHA256, suite SHA256, Git commit/dirty, event counts, and integer ledger residual.
- `candidate_motor_work_j` and `motor_work_j` are **signed** and used in the mechanical energy identity. `candidate_motor_positive_work_j` and `motor_positive_work_j` are **nonnegative ideal positive-work costs**; only accepted positive costs become F002 spend events. Neither represents electrical draw.
- `decision_reason`, `motor_command_n` and `motor_applied_n` distinguish the proposal from the actual motion. All records are world truth for scientific analysis, not cell perception.

## Interpretations
A (reversal) needs 500000 µJ; B (1 µJ balance) rejects the motor; C (non-reversal acceleration) matches F004; D (braking only) spends nothing; E (external only) spends nothing; F addresses two time grids, asymmetric reversal, microjoule rounding, invalid inputs, saved evidence tampering and deterministic replays. Negative results must be reported in `findings/F005-validation.md`.

See [spec](../../topics/F005-positive-work/SPEC.md), [plan](PLAN.md), [findings](../../findings/F005-validation.md), [architecture](../../docs/ARCHITECTURE.md), [data contracts](../../docs/DATA_CONTRACTS.md).

## PR #14 verifier review follow-up
The suite now includes **13** controls: original 10 plus ordinary reversal at a microjoule ceil boundary, endpoint-power underflow and dt=0.1 splitting. The oracle integrates exact Fraction endpoint powers independently, checks the fixed binary64 cost order separately, and records `quantization` in every comparison case. Exact-endpoint arithmetic is not the exact continuous trajectory. Both candidate fields must be null initially; tiny positive-work fields cannot be zeroed while retaining valid evidence. Optimized-Python regression: `python -O -m unittest discover -s tests -p test_f005.py`.
