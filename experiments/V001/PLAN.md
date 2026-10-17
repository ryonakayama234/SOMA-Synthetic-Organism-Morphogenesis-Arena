---
id: V001-PLAN
kind: preregistered_plan
status: not_executed
updated: 2026-10-17
related: [V001, F007]
---

# V001: 1D実験再生の事前登録

**全ケース未実施。F007の既存CI合格をV001の実験成功に読み替えない。**

## 比較対象
F007の検証済み保存 `config.json`・`states.csv`・`link_events.csv`・`ledger/events.csv`・`manifest.json` を読んだ**研究者ビューアのフレーム**を、元CSVの各行および既存F007原本独立照合と比較。コントローラ/運動エンジンは変更しない。

| 対照 | 固定する条件 | 合格とする観測 | 明示的な反証 |
| --- | --- | --- | --- |
| A 非接続 | F007 A-free | Aの各保存x/vが一致。リンクOFF | 元にないBの共同運動やリンク描画 |
| B 結合 | F007 B-linked | A/Bの保存位置とリンクON・距離が正確 | 両位置差が描画内で一貫しない |
| C 切断 | F007 E-cut | イベント直前/直後の保存行を正しい順で提示 | 未記録のジャンプ、接続ラベルずれ |
| D 電池 | F007 F-01等 | 残量とmotor applied/deniedを別表示 | 指令と実適用を混同、負残量の捏造 |
| E 負例 | 改変CSV/manifest・欠損カラム・逆順時刻・改変リンクイベント | 表示前に拒否し原因を記録 | 原本改変でも表示を続行 |
| F 再現 | 同じ原本、同じ投影仕様 | 正規化frame recordsの逐語/byte一致。F007テスト不変 | フレーム不一致、原本変更 |

## 計測指標（実装前に凍結）
- source_to_frame_coverage：元CSVの有効な全 `step_index` と表示フレームが一対一対応する割合。期待100%。
- max_frame_numeric_error：位置・速度・電池・motor appliedを原本数値と比較。元CSVの数値解釈上は完全一致を要求し、画面ピクセルの丸めと分離。
- link_event_mismatch_count：F007イベント/状態と表示ラベルの不一致件数。期待0。
- bad_input_accepted_count：E負例の受容件数。期待0。
- replay_byte_match：canonical frame exportを同条件で二度作った際の完全一致。期待true。
- provenance：source SHA、viewer source SHA、設定、計測コード版、Python/OS、実験ID。

## 禁止する主張
初期図形は1D記録を表示する記号。実機の身体形状、2D衝突、摩擦、結合の適応利益、セルの認識、人工生命の創発を示さない。図だけで物理モデルが正しいと証明しない。

## 実施・判断
設計時：**全未実施**。採用はPRのCIだけでは決定しない。実施時は未変更の原本/ログ、失敗例、反証を `findings/V001-validation.md` に追記する。後付けの閾値変更は禁止。
