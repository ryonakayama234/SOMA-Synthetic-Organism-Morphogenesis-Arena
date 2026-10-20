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
