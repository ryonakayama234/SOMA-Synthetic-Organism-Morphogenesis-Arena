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

## 2026-10-15 受入ゲート事前登録（実測ではない）

Wolframで検算した連続解：Bの10秒後に共通速度2.1616617919084682703 m/s、共有変位14.191691040457658649 m。
同じ名目条件の半陰的Euler法（dt=0.01）での離散基準：速度2.162338693883290987 m/s、共有変位14.209929917522377975 m。
dtを0.005／0.0025へ半減した位置誤差の事前期待：0.009118027943618595／0.004558661430422564 m。
切断t=5 sのstates.csvはイベント後1行、イベント前後の位置・速度はevents.csvで同値検証。不正設定はrejections.jsonへ別保存。数値・再実行・回帰・CI・独立監査の採用条件はSPECとPLANを正本とする。

**F003のコード・実験・実測値は依然として存在しない。支持・反証の判定は全て未実施。**

## 実装候補の検証状態（2026-10-15）

- **コード**：専用実装ブランチにF003計算、A〜F実験スイート、9件の単体検査、およびCI workflowを追加。
- **設計側の予測**：連続系 v(10)=2.161661791908468... m/s、変位14.191691040457659... m；dt=.01の離散系 v(10)=2.162338693883291... m/s、変位14.209929917522378... m。Wolframで独立に再確認。Bの内部力 +0.5 N、不等質量2kg/1kgのB内部力 +1/3 N。
- **ローカル試作の検査**：モデル等価なF001小関数を用いたローカル試作では9件の検査とA〜F（7正常run／8拒否ケース）、B再実行のバイト一致が成功。ただしGitHubにある実装そのものとmainの既存F001/F002の回帰を確認したものではなく、**GitHub Actionsでの正式な検証証拠として扱わない**。
- **GitHub CI**：以下の2026-10-15の最新CI証拠を確認。
- **独立監査**：未完了。主張できるのは理想1D力学ソフトウェアの検証候補まで。実機接続や創発を示さない。

**ゲート**：CI結果・SHA照合・第三者視点のレビューを確認してから採否を記録する。失敗・修正履歴は削除しない。

[実験スイート](../experiments/F003/run_suite.py) / [CI workflow](../.github/workflows/f003.yml)。

## F003 GitHub CI 確認（2026-10-15）

- 実装HEAD: 1512206596ca8939705e6e1ab603e9aa1bbd626d
- F003 Actions: https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38731190546 — success。Python 3.11で合計44テスト（F001 17、F002 16、F003 11）合格。
- A〜F正常7run、不正入力8件を拒否、B同条件再実行の生バイト一致。artifact: F003-A-F-evidence（ID 11970235937）。
- F001既存ワークフロー: https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38731190562 — success。
- F002既存ワークフロー: https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38731190549 — success。
- 以上は1D理想モデル・ソフトウェアの整合性を示す。実機による結合、エネルギー相互作用、身体創発を示さない。
- 独立第三者の監査は未了。PR #7の設計レビューと、PR #8の正式採用判断を区別する。

| 種別 | 現時点の判定 |
| --- | --- |
| Wolfram理論値 | 事前予測として固定 |
| ソフトウェア試験 | 44テスト・A〜F・再現性支持 |
| 独立監査 | 未実施 |
| 正式採用 | 保留 |
