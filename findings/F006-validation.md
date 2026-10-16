---
id: FIND-F006
title: F006 時間刻み依存の検証ノート
kind: experiment_finding
status: implementation_candidate
updated: 2026-10-16
feature: F006
issue: 16
---

# F006検証記録 — 実装候補（未採用）

## 問い
dtの違いに伴うF005の運動・駆動受否・整数µJ支出の変化を別々に検証できるか。

## 事前仮説
[H006、対立仮説、受入条件](../topics/F006-timestep-diagnostics/SPEC.md)。
[実験A〜F計画](../experiments/F006/PLAN.md)。

## 現時点の証拠区分
| 対象 | 状態 |
| --- | --- |
| Wolfram厳密有理数によるdt=1,1/2,1/4の参照例 | **理論検算済み（SOMA実験ではない）** |
| F006コード、単体・回帰テスト | **実装候補／初回CI成功** |
| F006 A〜F実行・保存ログ・比較図 | **A〜E: 15run実行・保存成功。F: 負例・改変テストを実施** |
| F006 CI・artifact・完全再実行 | **初回CI success／生証拠162ファイル／再実行バイト一致** |
| 独立監査、採否 | 未実施・未判断 |

## 実験後に埋める欄
- 実行日時、最終HEAD、Git dirty、Python版、環境、seed、suite/コードSHA。
- A〜Fそれぞれの入力・全試行・理論参照・binary64参照・保存ログ、比較CSV、図、差分と不確実性。
- 行動受否による不連続、軌道の誤差、正仕事の積算誤差、µJ切上げ誤差の別々の推定。
- 正常な負の結果と失敗の理由、ソフトウェア欠陥とモデル意味論の境界。
- 別視点レビュー、修正履歴、CI artifact、採用判断、既存F005との互換性。

**禁止**：診断に成功したことを、F005の刻み幅収束・実機のエネルギー妥当性・身体機能の創発が成立した証拠として扱わない。後続の数値改善は別Issueで設計する。

[Issue #16](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/16)


## 2026-10-16 詳細設計時の追加Wolfram検算（F006実験は引き続き未実施）

1kg/1N/総試行時間1秒/外力・抵抗なし・初速0。厳密有理数で時間刻みを1,1/2,1/4とした独立反復では、**電池十分**：最終位置1,3/4,5/8m、速度は全1m/s、全正仕事費用500000µJ。連続運動の参照位置1/2mに対する差は1/2,1/4,1/8m。

**電池400000µJ**：最終(x,v,spent_uj)は(0,0,0)、(1/2,1/2,125000)、(9/16,3/4,281250)、駆動受理/拒否ステップは0/1,1/1,3/1。微小モーターと逆方向外力で正仕事合計1µJの対照Cは1/10/100分割に対して切上げ支出1/10/100µJ。反転Dは正仕事1/2J、符号付き仕事0J、有理数参照の支出500000µJ。

**証拠種別**：Wolframによる事前理論検算。実装したF006のソフトウェア観測・CI・実測の成功は一切示さない。F006の達成目標は差の測定・分類・追跡であり、時間刻み不変性の証明ではない。[事前登録の詳細](../experiments/F006/PLAN.md)。

## 2026-10-16 初回F006実装CI観測（実装Draft PR #18、正式採用前）

- **commit**: `d279472f7d1eb3c6a7a9121bb86d6518e25451b0`（実装ブランチの**初回**CI対象、最終HEADではない）。
- **workflow**: [F006 Action #38916091762](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38916091762)、結論`success`。Python 3.11.17、Linux runner。
- **検証**：F001〜F006全体で**100テスト成功**。`python -O`のF005 20テスト、F006 7テスト成功。A〜Eをそれぞれ3刻みで**合計15 run**、各原本を独立検査。`{"diagnosis":"supported","independent_saved_log_audit":true,"replay_bytes_identical":true,"runs":15,"schema_version":"f006.v1"}` とCIログで確認。
- **証拠**：[artifact 12052835687](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38916091762/artifacts/12052835687)。再実行分を含む**162ファイル**。config、state CSV、ledger events、run manifests、suite manifest、比較表、可視化、診断JSON、suite source snapshot。
- **A〜Eの観測**：初回CIで`tests/test_f006.py`による参照照合成功。Aの位置`1, .75, .625m`、Bの適用回数`0,1,3`、Cの支出`1,10,100µJ`、比較誤差比率`2,2`をテストが保存値から照合。その他の物理・仕事・イベントはF005の全ステップ保存証拠オラクルとF006の比較器で照合。Wolfram有理数参照とCIでのPython binary64観測を区別する。
- **発見・修正**：初回成功ログにCSVハンドル閉じ忘れによる`ResourceWarning`があったため、テストでコンテキストマネージャによる閉鎖に変更。これは物理モデルの変更ではない。
- **独立性・限界**：F005と異なる数式の保存証拠オラクルを通すが、別の人によるコード監査・他環境での再現・一般dt格子への収束保証は未了。`verdict=supported`は事前登録された限定対照に関する診断機能の成否のみ。

**必要な次ゲート**：最終HEADのCI success、原本・表・図・仕様の整合性監査、外部／独立レビュアーの確認、ユーザーによる正式採否。それまでは`main`未統合。

