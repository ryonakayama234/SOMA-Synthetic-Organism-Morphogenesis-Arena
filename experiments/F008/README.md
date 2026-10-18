# F008 v1 — local A-only response anomaly (implementation candidate)

**Not adopted; do not merge before review and the researcher's explicit decision.**

The design is preregistered at [Issue #22](../../issues/22) and design PR #23.
It reuses the unchanged, limited-adoption F007 numerical model and its saved-data
oracle. It does **not** model a real actuator's ground reaction, real propulsion,
online learning, body-schema topology, or emergent morphology.

From repository root on WSL2/Linux (Python 3.11 or 3.12; no third-party packages):

```bash
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -p test_f008.py -v
python -m experiments.F008.run_suite \
  --output-dir runs/F008-ci --replay-output-dir runs/F008-replay
```

Both output directories must not exist. Successful execution prints a JSON summary
with `cases=5`, `observations=20`, `linked_external_indistinguishable=true`,
and `byte_equal_files` for a complete two-directory same-byte replay.

Each case saves an immutable F007 source under `CASE/F007/` plus the derived
`CASE/local.csv`. The latter has only A's own time, velocity, command, applied
motor force and battery, plus its own residual and status. It never contains
`attached`, partner state, link force, unknown external forces or case truth.
`comparison.json` contains **researcher-only** planned references.
`manifest.json` contains source/checkout origin and all artifact SHA256 values.

The independent `experiments/F008/verify.py` re-reads persisted F007 traces,
calls F007's independent numerical evidence audit, and computes expected A-local
fields without importing `soma.f008`. It checks the true physical difference
between B-linked and D-hidden-force while their entire A-local time series is
identical. Changes to F007 source or to F008 local.csv must be rejected even if
a corresponding artifact manifest hash is recalculated.

A–E conditions are unchanged from `PLAN.md`: A free; B linked; C detach at
0.5 s; D free with hidden external force −1 N on A; E free with depleted A
battery. F is the information boundary, negative and reproducibility checks.
No noisy sensor or randomized trial is claimed: F007 requires seed=null.
A "supported" label, if produced, refers only to exact *discrete-software*
controls and is not a researcher adoption decision.

The stored intervals represent the force applied **before** any event at the
interval endpoint. For C, t=0.5 s is already post-cut in F007's world truth,
but the interval ending at 0.5 s still exhibits linked dynamics; the next
interval exhibits free dynamics.

A's nominal mass 1 kg is a supplied prior calibration. Applied motor force is
treated as permitted *A-local feedback*, not as the commanded force and not as
a secret world-state label. No unique connection state or apparent mass is
inferred. When the actual applied motor force is zero, status=`not_excited`
and the model returns null for predicted acceleration and residual; observed
acceleration may still be nonzero from unknown external forces.

See `topics/F008-local-load-detection/SPEC.md`,
`docs/ARCHITECTURE.md`, `docs/DATA_CONTRACTS.md` and
`findings/F008-validation.md` for preregistration and research status.
