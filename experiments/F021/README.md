# F021 two-owner motor experiment

Frozen research design: [FROZEN_V1](FROZEN_V1.md); current accepted baseline is F001–F020 only.

From WSL2/Linux repository root:

```bash
python -m experiments.F021.run_suite --out /tmp/f021-a
python -m experiments.F021.verify --root /tmp/f021-a
python -m experiments.F021.run_suite --out /tmp/f021-b
diff -r /tmp/f021-a /tmp/f021-b
python -m unittest discover -s tests
```

Output directories must not already exist. Each 4,608-world primary suite is paired YY/NN over identical 32 finite-resource field seed blocks. Raw worlds, summary, manifest are saved as JSONL/JSON. GitHub Actions separately executes source-bound verification and byte replay on Python 3.11 and 3.12.

The primary model contains externally prescribed motor commands and initial attachment, NOT endogenous joining, grounded electric actuation, autonomous learning, survival, biological evolution or external peer review.

For any selected world, `worlds.jsonl` contains every step, motor subset candidate/choice, A/B private balance and own debit, link dynamics, patch claim, and source-bound provenance. Do not treat 4,608 correlated factorial runs as 4,608 independent ecological samples.
