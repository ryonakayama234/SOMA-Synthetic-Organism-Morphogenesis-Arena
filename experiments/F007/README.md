# F007 v1：2セル片側駆動の実験と再実行

**2026-10-17 限定的正式採用：** 9条件の離散モデル照合・保存証拠の独立監査・Python 3.11/3.12各126回帰と14最適化を通過。[採否と制限](../../findings/F007-validation.md#2026-10-17-f007-限定的正式採用--最新の研究判断)を優先。直下のDraft等の表記は実装候補時点の履歴。

**Draft / not yet formally adopted**. Issue #19, design PR #20; implementation is reviewed separately. Python 3.11/3.12, WSL2/Linux. No external Python dependencies.

From the repo root:

    python -m unittest discover -s tests -v
    python -O -m unittest discover -s tests -p test_f007.py -v
    python -m experiments.F007.run_suite --output-dir runs/F007-ci --replay-output-dir runs/F007-replay

9 saved scenarios: A-free, B-linked, C-zero, D-external, E-cut, F-01 midrun depletion, F-02 uncharged holding, F-03 external-only with A battery empty, F-04 velocity reversal.

F-05: twelve invalid input cases must be rejected. F-06: saved CSV tamper detection, SHA and complete per-step numerical oracle, full-file byte replay. PLAN values are **Wolfram preregistration**, not observations until CI evidence is independently reviewed.

Per run: config.json, states.csv, ledger/events.csv, link_events.csv, motion.svg, manifest.json. Suite: comparison.json, suite_source.py, oracle_source.py, manifest.json with SHA-256 listing. The verifier reads persisted CSV/events and independently reconstructs per-step equations without importing F007 simulate/step or F005 positive work. This is a separate numerical algorithm by the same assistant, **not a human third-party review**.

Model boundaries: F005 motor is an external effective force with no ground reaction for real propulsion; F003 semi-implicit positions and F005 velocity-interpolant positive work refer to different trajectories; per-step ceil/motor rejection depends on dt. No survival, novelty, physical realism, or advantage of joining is demonstrated. History is preserved and assumptions are explicit.

Do not merge to main before independent design/code/evidence review and researcher's explicit adoption decision.
