# F012 — reproducible finite mechanical-work experiments

**Implementation candidate only. NOT formally adopted or merged.** Related Issue #38, preregistered design PR #39 and stacked implementation Draft PR #40. The design [SPEC](../../topics/F012-finite-energy/SPEC.md) and [PLAN](PLAN.md) were committed before implementation. Prior F001–F011 and their original evidence remain unchanged; F011 A full-duration no-contact remains INCONCLUSIVE.

```bash
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -p test_f012.py -v
python -m experiments.F012.run_suite --output-dir runs/F012-first --replay-output-dir runs/F012-replay
```

The runner refuses preexisting, overlapping and nested output roots. It generates B/C/D/E × 0/1/3/10 J × dt=.01/.005/.0025 (48 independently initialized full 9.6s simulations), each with frozen config.json and complete world states.csv. Two generated roots are byte compared and independently verified. `comparison.json` contains per-case numeric outcomes; `manifest.json` hashes raw artifacts and selected trusted source files. The verification module does **not** import F012/F011/F005 production simulators; it separately reconstructs mechanics, gating, budget and all summary metrics from saved data. File hashes alone are not science nor human identity attestation.

World truth is researcher-facing only. Ideal positive mechanical work and integer microjoule charging do not imply electrical battery fidelity. No real friction, autonomous body controller, learning, real hardware or independent human review is claimed. Negative observations, gate failure or timestep-sensitive comparisons belong in [findings](../../findings/F012-validation.md).

The two-directory publication is deliberately not power-loss atomic; CI ZIP retention is provider-bounded. To audit, use a trusted checkout of the recorded SHA and verify saved raw artifact paths/hashes plus the independent oracle.
