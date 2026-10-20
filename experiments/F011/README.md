# F011 reproducibility guide (research candidate; NOT ADOPTED)

**Baseline:** main `0e01b68cd157`; implemented exclusively in the F011 stacked Draft PR. Does not change accepted F001–F010 or V001. The [frozen SPEC](../../topics/F011-grounded-internal-drive/SPEC.md) and [preregistered A–F](PLAN.md) were committed in design PR #35 **before** any new F011 code was executed.

Run from repository root on Python 3.11 or 3.12:

```bash
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -p test_f011.py -v
python -m experiments.F011.run_suite --output-dir runs/F011-first --replay-output-dir runs/F011-second
```

The runner refuses existing, overlapping, or nested output destinations and does not overwrite old data. Remove only YOUR own temporary output dirs manually before rerunning; never delete historical evidence. Exact 15 configurations: 5 frozen conditions x 3 dt values. A:no-contact triggers the preregistered 0.8m stroke failure before full 9.6s and is retained as a **partial negative trace**; do not report that A completed. Cases B–E have full 960/1920/3840 interval traces. F comprises invalid configs, tampered source/summary/CSV negatives, rehashed science claim and replay.

Each `case/dt/` has `config.json` and raw SI `states.csv`, the root has `comparison.json` and `manifest.json`. The verifier rederives Newtonian update, exact step-to-step external ground impulse, signed motor work, dissipative friction work, spring energy and expected **nonzero discrete integration defect** directly from saved CSV. It does not import the production F011 simulator. SHA binds generated artifacts and trusted checkout source; SHA is **not** identity attestation.

The full experiment is deterministic (`seed=null`); 2 outputs have identical raw bytes under the same code and Python platform. Two-directory publication is not crash/power-loss-atomic. GitHub Actions artifacts hold full raw evidence for auditing and have finite retention. See [findings](../../findings/F011-validation.md) for exact CI HEAD/run and provenance after CI completion.

No controller, sensor-local body schema, real grounding, real battery, active attachment selection or physically emergent morphology has been demonstrated.
