# F006 — time-step dependence diagnostics (implementation candidate, not adopted)

## Scope

F006 runs the *unchanged* accepted F005 1D single-cell motor-battery simulator
under identical physical parameters and different time steps. It reads the
persisted evidence, verifies every step/event using F005's independent
saved-file oracle, and measures motion integration differences,
all-or-nothing battery acceptance, and integer-µJ quantization.

This does NOT introduce a new physical solver, repair F005, validate real
electrical consumption, test multicellular assembly, or prove emergence.

## WSL2/Linux commands

From the repository root, Python 3.11:

    python -m unittest discover -s tests -v
    python -O -m unittest discover -s tests -p test_f005.py -v
    python -O -m unittest discover -s tests -p test_f006.py -v
    python -m experiments.F006.run_suite --output-dir runs/F006-local --replay-output-dir runs/F006-replay

Output paths must be unused and disjoint. Evidence files are not overwritten.
A successful CLI prints:

    {"diagnosis": "supported", "independent_saved_log_audit": true, "replay_bytes_identical": true, "runs": 15, "schema_version": "f006.v1"}

The status is the outcome of this frozen set of diagnostic controls, **not**
a generic convergence guarantee.

## Preregistration and cases

- A: positive constant-force motion, no battery gate. Reference Euler terminal x: 1, .75, .625 m for dt 1, .5, .25; continuous reference .5 m.
- B: same motion, initial battery .4 J. Observed acceptance patterns and spent µJ must match independent Wolfram discrete references.
- C: balanced tiny motor / external forces, one ideal µJ total, yields expected per-step ceiling spend of 1, 10, 100 µJ.
- D: reversal motor command, positive work .5 J versus net signed work zero.
- E: external force only, nonzero displacement, zero motor spend.
- F: invalid inputs, forged/hash-updated evidence, record tampering, and byte replay live in tests/test_f006.py (not extra physical sweep rows).

See PLAN.md for the preregistered full expected values and interpretation boundaries.

## Evidence

Every individual run gets its original F005 config.json, states.csv,
ledger/events.csv, motion_energy.svg and manifest.json. Each has its own hashes
and F005 source provenance. The F006 suite additionally emits:

- sweep.json (15 complete, frozen f005.v1 configs; seed=null);
- comparison.csv (observed and discrete reference values);
- diagnostics.json (cross-dt diagnosis and original artifact hashes);
- comparison.svg (display only, not numeric evidence);
- suite_source.py (exact runner source copy);
- manifest.json (suite hashes and provenance).

The replay directory produces the same complete file tree. The suite refuses
an existing output directory and independently rebuilds all summaries from
saved files. The comparison and diagnostic files are themselves audit targets.

## Research status

Implementation PR #18 is a draft stacked on design PR #17; neither is adopted
or merged to main. GitHub Actions F006 runs all historical regressions, optimized
Python oracle tests, 15 sweeps plus replay, and uploads source evidence. A
separate research audit and formal adoption decision are required.
