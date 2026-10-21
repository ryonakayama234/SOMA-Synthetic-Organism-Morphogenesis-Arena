---
id: FIND-F017
kind: validation
status: proposed_unexecuted
updated: 2026-10-21
issue: 57
---

# F017 検証台帳 — 実験未実施

**最新状態: DESIGN PROPOSAL ONLY. NO F017 SOURCE, SIMULATION, SCIENTIFIC RESULTS, CI OR ADOPTION.**
[Issue #57](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/57) / [candidate SPEC](../topics/F017-learned-signal/SPEC.md) / [candidate PLAN](../experiments/F017/PLAN.md).

## 事実と仮説を分離
- **既存F016で観測済み**: [F016 findings](F016-validation.md) にある固定解読規則での A0=0.50J、T=1.95J、I=-1.05J（各4episode）、Python3.11/3.12とpost-main CI。これはF017のエージェント学習の実験ではない。
- **Wolfram理論のみ**: pを資源への正確な到達確率とすると固定費用下の平均netは `3p-1.05J`、A-only平均0.5Jとの等価閾値は`p=31/60`。独立bandit learning結果ではない。
- **F017仮説（未検証）**: 同じF007資源世界で、Aはbit→motor対応を事前に知らずに自己のエネルギー結果だけから条件付き行動を学べる。反転した意味への再適応は別判定。

## ゲート記録
| gate | present state |
|---|---|
| 科学的問い／主要な反証可能性 | 提案済み、未凍結 |
| 世界/入力/feedback/学習器データ隔離の独立監査 | 未実施 |
| seed/系列・学習algorithm・閾値の実験前凍結 | 未完 |
| F017 source / unit tests / CI | **NONE** |
| F017 raw episodes / policy traces / auditor | **NONE** |
| 数値効果・不確実性・反転後の回復 | **UNEXECUTED** |
| 限定採用・main統合 | **NOT AUTHORIZED** |

今後はここに日付・source SHA・設計凍結hash・CI link・raw artifact hashes・陰性結果・独立監査・判定を**追記**し、先行する未実施表記を歴史的証拠として保存する。負の結果も保管し、F016成果をF017として転記しない。
