---
id: FIND-F006
title: F006 時間刻み依存の検証ノート
kind: experiment_finding
status: proposed
updated: 2026-10-16
feature: F006
issue: 16
---

# F006検証記録 — 未実施

## 問い
dtの違いに伴うF005の運動・駆動受否・整数µJ支出の変化を別々に検証できるか。

## 事前仮説
[H006、対立仮説、受入条件](../topics/F006-timestep-diagnostics/SPEC.md)。
[実験A〜F計画](../experiments/F006/PLAN.md)。

## 現時点の証拠区分
| 対象 | 状態 |
| --- | --- |
| Wolfram厳密有理数によるdt=1,1/2,1/4の参照例 | **理論検算済み（SOMA実験ではない）** |
| F006コード、単体・回帰テスト | 未実装 |
| F006 A〜F実行・保存ログ・比較図 | 未実施 |
| F006 CI・artifact・完全再実行 | 未実施 |
| 独立監査、採否 | 未実施・未判断 |

## 実験後に埋める欄
- 実行日時、最終HEAD、Git dirty、Python版、環境、seed、suite/コードSHA。
- A〜Fそれぞれの入力・全試行・理論参照・binary64参照・保存ログ、比較CSV、図、差分と不確実性。
- 行動受否による不連続、軌道の誤差、正仕事の積算誤差、µJ切上げ誤差の別々の推定。
- 正常な負の結果と失敗の理由、ソフトウェア欠陥とモデル意味論の境界。
- 別視点レビュー、修正履歴、CI artifact、採用判断、既存F005との互換性。

**禁止**：診断に成功したことを、F005の刻み幅収束・実機のエネルギー妥当性・身体機能の創発が成立した証拠として扱わない。後続の数値改善は別Issueで設計する。

[Issue #16](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/16)
