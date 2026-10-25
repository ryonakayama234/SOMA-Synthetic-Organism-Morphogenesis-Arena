> **Status as of 2026-10-25:** F022.v1 is now a technically adopted, **bounded passive two-body measurement instrument**, following 22/22 merged-main GitHub Actions green. Earlier "(implementation PR candidate)" heading below is the historical build-stage title. [Adoption decision](../../docs/decisions/2026-10-25-F022-limited-admission.md) / [saved scientific summary](../../findings/F022-ci-summary-2026-10-25.json). No robot autonomy, organismality, attachment or 2D viewer.

# F022.v1 — frozen 2D passive Encounter Lab (implementation PR candidate)

Research Issue [#77](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/77), design [Draft PR #78](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/78), [FROZEN_V1.md](FROZEN_V1.md) at protocol SHA `3984e9dcb2cb420abab5ca92b4d029b31b5173f8`. The implementation is an ideal two-body verification instrument, not voluntary docking, drive/ground dynamics or bio-inspired morphology.

From WSL2/Linux repository root:

```bash
python -m unittest discover -s tests
python -m experiments.F022.run_suite --out /tmp/f022-run-a
python -m experiments.F022.verify --root /tmp/f022-run-a --expected-source-sha "$(git rev-parse HEAD)"
python -m experiments.F022.attack_test --root /tmp/f022-run-a
python -m experiments.F022.run_suite --out /tmp/f022-run-b
diff -r /tmp/f022-run-a /tmp/f022-run-b
```

Outputs cannot overwrite. Bundle: `scenario.json`, exactly 117 sampled states in `states.jsonl`, full pre/post events in `contacts.jsonl`, `audit.json`, and source-bound hash manifest. Verifier imports neither physics producer nor producer scenario generator. Same-AI code-path auditing is **not** external peer review.
