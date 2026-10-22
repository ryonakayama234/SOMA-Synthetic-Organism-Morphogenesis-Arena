---
id: EXP-F019-RUN
title: F019 source-bound experiment instructions
kind: experiment_howto
status: IMPLEMENTATION_CANDIDATE_NOT_ADOPTED
updated: 2026-10-22
issue: 64
---

# F019 frozen v1 execution (researcher-only)

[Freeze](PLAN.md) / [Specification](../../topics/F019-resource-ecology/SPEC.md) /
[Findings](../../findings/F019-validation.md) / [Architecture](../../docs/ARCHITECTURE.md).

Requires clean Git checkout, Python 3.11 or 3.12, and git. No network, learner,
sensor, docking, B motor, tools, energy transfer, mid-run topology change, or dynamic controller.
Patch fields are exogenous, independent of both joined and solo trajectories.

From repository root on WSL2/Linux:

~~~bash
python -m unittest discover -s tests -p 'test_f019*.py' -q
python -m experiments.F019.run_suite --output-root runs/F019-a
python -m experiments.F019.verify --root runs/F019-a
python -m experiments.F019.attack_test --root runs/F019-a
python -m experiments.F019.analyze --root runs/F019-a
python -m experiments.F019.run_suite --output-root runs/F019-b
python -m experiments.F019.verify --root runs/F019-b
diff -rq runs/F019-a runs/F019-b
~~~

The run refuses dirty source trees, embeds source SHA256 hashes and commit identity,
and never overwrites an existing output directory. Source changes require a new
SHA-scoped run. Exactly 512 conditions and 3584 counterfactual worlds are evaluated,
without cherry-picking. Mutually positive or negative outcomes are both legitimate.

Outputs:
- worlds.jsonl: full pristine scene/field, linkage, claims and per-cell nets.
- states.csv: complete F007 physical state columns for each of five time samples.
- harvests.jsonl: path-first entry and unique winner in each world.
- events.jsonl: exact F002 chronological fee/motor/harvest ledger entries.
- ledger.jsonl: final energy stores/conservation per world.
- summary.jsonl: per-patch YY vs NN winner/time and individual payoff comparisons.
- manifest.json: all raw artifact and source hashes, counts and Git commit.

All outputs are OFF-WORLD investigator truth; no future cell policy sees whole fields or
outside payoff maxima. Independent verify.py recalculates fields, physics, chronology
and counterfactuals using only stdlib and saved data, no soma.f019/F007 imports.
The adversarial runner modifies and rehashes evidence before rejection checks.
Software independence is NOT independent external scientific peer review.
