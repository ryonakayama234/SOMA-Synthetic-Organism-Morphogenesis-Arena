**Current status (2026-10-21): F016 LIMITED ADOPTED in fixed ideal F007 1D task scope; actual design #54 and implementation #55 merged, post-main [Actions #39582766235](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39582766235) 16/16 SUCCESS.** See [final append-only findings](../../findings/F016-validation.md) and frozen [SPEC](../../topics/F016-communication-value/SPEC.md). Subsequent 'candidate' wording below is historical. This is not a hardware communication or spontaneous semantic evolution claim.

# F016 — 1bit communication net physical-action value

**IMPLEMENTATION CANDIDATE / NOT SCIENTIFICALLY ADOPTED.** Do not treat this page as observed F016 simulator results until exact-HEAD CI passes and source-bound artifacts are audited.

Study: [Issue #52](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/52) / [frozen SPEC](../../topics/F016-communication-value/SPEC.md) / [preregistered PLAN](PLAN.md) / [append-only findings](../../findings/F016-validation.md).
The older ±0.5m continuous-time feasibility idea was corrected to ±0.625m before implementation. Motor positive work remains 1J.

Implemented candidate:
- `soma/f016.py`: typed B-local 1bit projector, A fixed 2N sign policy, reused F007 ideal linked physics, F002 sidecar with B-sender fee, A recorded motor expenses and A end-position-dependent resource gain.
- `run_suite.py`: 6 frozen groups ×4 independent full resets =24 runs, CSV+JSON raw world truth per episode and source-bound SHA256 manifest, no source alteration.
- `verify.py`: separate source- and saved-world-data verifier with independent dyadic Euler recurrence, event/ledger arithmetic, per-step physics, behavior outcomes, truth boundary and rehashed false-science rejection.
- `tests/test_f016.py`: observations, 24 frozen controls, sender insufficiency, packet forgery, two-root byte replay and rehashed outcomes/positions.
- `.github/workflows/f016.yml`: Python 3.11/3.12 entire inherited unittest suite + F016 -O, saved-evidence generation, full independent audit and two-root directory diff.

WSL2/bash usage from checked-out **implementation branch**:
```bash
python -m unittest discover -s tests -p test_f016.py -v
python -m experiments.F016.run_suite --output-root runs/F016-ci
python -m experiments.F016.verify --root runs/F016-ci
python -m experiments.F016.run_suite --output-root runs/F016-replay
diff -rq runs/F016-ci runs/F016-replay
```

Outputs must not preexist; `runs/` is ignored. Manifest git SHA/dirty and source file hashes are captured before run. Cross-root byte identity is audited, not inferred.

**Boundary:** B bit's resource-side meaning is researcher specified; F007 motor is ideal external effective force; 1D resource sensing is an exogenous visibility mask, not a physical camera/optical simulation; communication has positive sender energy fee but is ideal instantaneous/delay-free. No radio, true self-organized signal, body-topology recognition, shape morphogenesis or external human peer review.
