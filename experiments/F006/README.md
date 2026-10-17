# F006 — fixed-control timestep diagnostics (v2, limited research adoption)

## Scope

F006 runs the *unchanged* accepted F005 1D single-cell motor-battery simulator
under identical physical parameters and different time steps. It reads the
persisted evidence, verifies every step/event using F005's independent
saved-file oracle, and measures motion integration differences,
all-or-nothing battery acceptance, and integer-µJ quantization.

This does NOT introduce a new physical solver, repair F005, validate real
electrical consumption, test multicellular assembly, or prove emergence.

## WSL2/Linux commands

From the repository root, Linux/WSL2 and Python 3.11 or 3.12:

    python -m unittest discover -s tests -v
    python -O -m unittest discover -s tests -p test_f005.py -v
    python -O -m unittest discover -s tests -p test_f006.py -v
    python -m experiments.F006.run_suite --output-dir runs/F006-local --replay-output-dir runs/F006-replay

Output paths must be unused and disjoint. Evidence files are not overwritten.
A successful CLI prints:

    {"diagnosis": "supported", "independent_saved_log_audit": true, "replay_bytes_identical": true, "runs": 15, "schema_version": "f006.v2"}

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
- comparison.csv (observed and discrete reference values, expected_classification,
  signature_matches_reference);
- diagnostics.json (cross-dt diagnosis and original artifact hashes);
- comparison.svg (display only, not numeric evidence);
- suite_source.py (exact runner source copy);
- manifest.json (suite hashes, source_hashes for the nine trusted dependency/
  reference paths, and pinned suite/run identity).

The replay directory produces the same complete file tree. The suite refuses existing outputs (including dangling symlinks), resolves both
paths before disjointness checks, and independently rebuilds all summaries from
saved files. It generates both suites in private sibling staging directories,
audits them and compares every byte before no-replace publication. Ordinary
exceptions roll back only outputs published by this invocation; existing and
concurrently created paths are preserved. Empty newly created parent directories
may remain. Linux renameat2 is required; unsupported platforms fail without
publishing evidence. Two directory renames are not crash-atomic as a pair: an
uncatchable crash between renames may leave the complete audited primary only. The comparison and diagnostic files are themselves audit targets.

## Research status

Research decision 2026-10-17: fixed A-E/15run diagnostic only is formally adopted
on the basis of preregistered references, independent saved-log auditing,
Python 3.11/3.12 CI and explicit user acceptance. Design PR #17 merged to main;
implementation/adoption record are tracked in PR #18. Historical v1 candidate
reports and failure reviews remain in findings. GitHub Actions F006 runs all
historical regressions, optimized Python oracle tests, 15 sweeps plus replay,
and uploads the evidence. This acceptance is not a GitHub third-party APPROVE.

## v2 trust and interpretation contract (2026-10-17)

The v2 schema intentionally rejects historical v1 artifacts; preserve those in
their original archive. Numeric A-E references are unchanged. The auditor compares
source_hashes to its trusted checkout, including diagnostics.py, the reused F005
saved-file oracle, simulator sources, and reference PLAN/SPEC. It checks suite
model/sweep/seed/reference IDs and all run provenance against an independent
expected identity, not against expectations copied from the manifest.

By default audit_suite(directory, build_settings()) pins provenance from the
auditor's checkout. For an archived CI artifact, first check out its audited
source revision, then pass expected_identity from independently inspected CI
checkout logs (the PR merge SHA can differ from its head SHA):

    from soma.f005 import provenance
    from experiments.F006.diagnostics import audit_suite
    from experiments.F006.run_suite import build_settings
    expected = provenance()
    expected.update(git_commit=ci_checkout_sha, git_dirty=False)
    audit_suite(directory, build_settings(), expected_identity=expected)

Never read the expected identity or settings from the evidence being audited.
The optional run/run_pair identity is also a trusted caller input frozen before
any staging; it must use actual source hashes. Null Git fields mean unknown
origin. A successful audit proves consistency with this trust anchor and the
saved numeric evidence; it does not attest who historically executed the code.

Labels are preregistered expected_classification values. Observed numeric
signatures and signature_matches_reference are separate. causal_attribution is
null, with a reason: this is a fixed-control verification suite, not a general
causal classifier. B retains Euler position error alongside battery gating.
A reference mismatch raises an exception before publication.
