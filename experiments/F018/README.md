---
id: EXP-F018-RUN
title: F018 再現と反証の手順
kind: experiment_howto
status: implementation_candidate
updated: 2026-10-22
issue: 61
---

# F018 630-world frozen assay — implementation candidate

[Design freeze](PLAN.md) / [Hypothesis](../../topics/F018-attachment-value/SPEC.md) / [Findings](../../findings/F018-validation.md) / [Data contract](../../docs/DATA_CONTRACTS.md).

This module uses **researcher-fixed** YES/NO proposals for two equal initially contact-ready 1D cells. World truth is not delivered to an agent. A motor is externally effective (F007), not internally grounded (F011). Connection is ideal; it does not implement docking, physical latch or power transfer. F018 does not implement a learned or rational consent policy.

## Run on WSL2/Linux, from repo root

~~~bash
python -m unittest discover -s tests -p "test_f018*.py" -q

python -m experiments.F018.run_suite --output-root runs/F018-a
python -m experiments.F018.verify --root runs/F018-a
python -m experiments.F018.attack_test --root runs/F018-a
python -m experiments.F018.analyze --root runs/F018-a

python -m experiments.F018.run_suite --output-root runs/F018-b
python -m experiments.F018.verify --root runs/F018-b
diff -rq runs/F018-a runs/F018-b
~~~

A preexisting output directory is refused. The suite requires a clean Git tree; source SHA and the hashes of all relevant source/experiment/document files are embedded in the manifest. When documentation or code changes, rerun on that exact new source SHA. CI also runs Python 3.11 and 3.12; do not infer green status from this guide.

## Frozen factorial

5 terminal layouts NONE/B_LINK/A_SOLO/DUAL_LINK/DUAL_SOLO × signed motor ±2N × radii 0.01/0.05/0.20m × join fees 0/0.1/0.5J = 90 unique scenes. Four fixed-motor consent arms YY/YN/NY/NN plus three NN outside motor alternatives -2/0/+2N = 7 per scene, **630 deterministic four-step F007 worlds**. Each resource patch awards 3J only at the t=1s terminal state, once to the nearest cell inside radius. A potential collision en route does not harvest a patch; there is no pre-existing docking force. This terminal rule is a declared model abstraction.

## Files and provenance

- `worlds.jsonl`: each world id, frozen scene, chosen arm and A motor, actual link events and terminal patch claims, per-cell net and spending.
- `states.csv`: all F007 per-step physical world-truth states, mechanically auditable.
- `events.jsonl`: F002 step/event-indexed individual spends and acquisitions with running cell balances.
- `ledger.jsonl`: final per-world F002 totals, balances and integer-µJ zero residual.
- `summary.jsonl`: 90 paired scene outcomes, individual `delta_fixed_uj` and `delta_outside_uj` over the restricted A-only action menu, plus Pareto indicators.
- `manifest.json`: run count, code/source SHA256, commit identity, artifact hashes and deterministic status. No seed clusters or inferential P-values because this is a complete deterministic enumeration.

`verify.py` **does not import the F018 producer or F007**. It recomputes physical trajectories, per-step motor work, terminal patch claims, chronological per-cell integer-µJ ledgers, outside best values and the full 90-condition grid from saved file contents. `attack_test.py` alters raw score, physics, and F002 ledger evidence, rehashes the manifest, and requires semantic rejection. A clean hash alone never proves physical truth.

## What success means

A scenario where both `delta_outside_i>0` shows a **conditional ex-post resource/effort participation opportunity** within the fixed restricted menu, not learned/voluntary simultaneous agreement or body emergence. If no such scenario exists, report negative evidence without adding a bonus for attachment. Important asymmetry: the old single-patch B_LINK example improves A versus forced solo drive but makes A worse off than idle.

**Implementation branch creation and tests are not scientific validation.** Report actual observed values and exact source CI in the append-only findings *only after CI and artifacts have been inspected*.
