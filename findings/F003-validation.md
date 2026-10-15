---
id: FIND-F003
title: 二セル1D機械結合の検証記録
kind: experiment_finding
status: not_run
updated: 2026-10-15
feature: F003
issue: 3
---

# F003 検証記録 — 事前登録（未実施）

**現状：実装なし・実験なし・実測値なし。** 以下の期待値は理想モデルの解析予測であり、SOMAコードによる観測ではない。

- [仕様／仮説／許容差](../topics/F003-attachment/SPEC.md)
- [対照実験A〜F](../experiments/F003/PLAN.md)
- [Issue #3](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/3) / [設計PR #7](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/7)

| 条件 | 事前仮説と評価点 | 実測 | 証拠URL | 判定 |
| --- | --- | --- | --- | --- |
| A 未結合 | F001系列一致・B静止 | 未実施 | 未生成 | 未実施 |
| B 片側駆動 | 共通速度・リンク力と拘束 | 未実施 | 未生成 | 未実施 |
| C 双側駆動 | 内部力0 | 未実施 | 未生成 | 未実施 |
| D 中途切断 | 位置・速度の連続 | 未実施 | 未生成 | 未実施 |
| E 符号反転 | 変位・速度対称 | 未実施 | 未生成 | 未実施 |
| F 刻みと不正 | 誤差収束・明示拒否 | 未実施 | 未生成 | 未実施 |

## 実行後の保存義務
設定JSON、世界の真値CSV、イベントCSV、比較結果、SVG、manifest、Git SHA・dirty・モジュールとsuiteのハッシュ、CI Actions artifact、同条件再実行の一致検査、否定的結果を一組にして記録する。

## 独立監査と採否
研究対象は**1D・二セル・理想リンクON/OFF**のみ。F002は連携しない。解析式・世界真値と局所観測の境界・回帰試験・図とログの一致を第三者視点で検査する。支持／反証／不明は実行後に判断し、レビュー承認まで正式採用としない。
