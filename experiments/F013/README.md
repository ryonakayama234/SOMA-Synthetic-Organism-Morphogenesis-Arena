# F013 — contact-rectification robustness (research-only, NOT ADOPTED)

Related [Issue #42](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/42) / [frozen SPEC](../../topics/F013-contact-rectification/SPEC.md) / [PLAN](PLAN.md) / [findings](../../findings/F013-validation.md).

Research question: does accepted F011's prescribed internally-driven two-identical-cell COM drift persist in a **different smooth, passive friction constitutive model**? A numerical change in this model is not automatically a F011 bug. No F011/F012 code or historical evidence is modified. World-state trajectories are **researcher-only**, never local knowledge available to cells.

## Reproduction (Python 3.11 or 3.12, WSL2 bash)

```bash
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -p test_f013.py -v
python -m experiments.F013.run_suite --output-dir runs/F013-ci --replay-output-dir runs/F013-replay
```

The last command refuses replacing either output directory; use two new empty pathnames for a fresh run. The generated 36 configs and per-timestep states.csv, comparison.json and manifest.json are independently verified against an actually checked-out source tree; both output roots must match byte-for-byte. The verifier does **not** import the F013 simulation. A common AI implementer, Wolfram and a separately written code verifier are distinct methods, not independent human scientific review.

`states.csv` fields are specified in [docs/DATA_CONTRACTS.md](../../docs/DATA_CONTRACTS.md) with SI units. F013 has no rechargeable electrical budget or autonomous controller. F011's original no-contact full-period A issue #37 remains INCONCLUSIVE. The result cannot demonstrate real friction, robust gaits in new terrains, self-organization or discovered organs.

Do not merge to main or declare formal adoption without the researcher's explicit approval. CI success means the frozen computer model and evidence path passed checks; it does not prove H13a or real-world validity.

## Post-registration independent whole-trajectory audit

The research director found that a separate friction root bisection plus semi-implicit Euler was not a fully independent *time integration method* for F013. The review corrected this missing audit with `experiments/F013/ode_audit.py` — a standalone explicit **coupled 4D RK4** integrator of the same continuous C0 force law, **without importing any `soma/` simulation**. It uses two independent, event-aligned integration steps (0.001s and 0.0005s). All 12 case/epsilon alternative references and their difference from F013 at 0.0025s are archived in `ode_audit.json`; the run verifier independently recomputes them, in addition to normal raw-CSV checks.

This is a **POST-preregistration** review audit, not a rewrite of the 36 frozen experiment conditions, H13a, H13b or H13c. For the alternate integrator, checking difference of its two step resolutions <=0.002m is an implementation consistency gate introduced during review, **not** a preregistered scientific hypothesis success threshold. Report and retain every discrepancy. Its stable drift is evidence the result is not merely the frozen semi-implicit Euler velocity update, but all approaches still assume *the same* researcher's 1D directional-friction physics.

Note: coefficient `mu_dir(v)` switches sign at zero; therefore the original preregistration's adjective **smooth** is mathematically imprecise. The force is continuous C0 and dissipative but not globally C1 for directionally asymmetric friction. The frozen equation itself was **not** changed. Version identifiers using `smooth` are historical schema labels only.
