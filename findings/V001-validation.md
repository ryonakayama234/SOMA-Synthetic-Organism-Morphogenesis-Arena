---
id: V001-validation
kind: research_findings
status: not_executed
updated: 2026-10-17
related: [V001, F007]
---

# V001 — 研究用1D再生ビューア検証記録

## 2026-10-17 設計時の記録
- 対象：F007採用済み保存実験の読み取り専用フレーム再生。
- 研究仮説：H-V001a〜dは [SPEC](../topics/V001-readonly-replay/SPEC.md) に事前固定。
- A〜F対照・成功条件： [PLAN](../experiments/V001/PLAN.md) に事前登録。
- 実装：**未実施**。
- V001の再生・UI実行：**未実施**。
- V001のテスト・CI・原本照合：**未実施**。
- 研究判断：**未評価／未採用**。
- F007の過去の9条件・CIはF007自身の限定的採用の証拠であり、V001の観測ではない。

## 今後、実験後に追記する欄（空欄を成功扱いしない）
- 原本：保存run ID、元コミットSHA、各artifact SHA256
- ビューア：コードSHA、schema、描画環境/OS
- A〜F：観測、支持/反証/不明、計測差、最小反例
- データ：canonical frames、拒否ログ、スクリーンショット（補助）、再実行証拠
- 監査：別視点レビューの対象・結果・未解消点
- 採否：研究者の明示判断と限定条件

[Issue #24](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/24)

## 2026-10-17 実装方針・合格定義の事前固定（V001結果は未実施）

設計Draft PR #25でPython標準ライブラリによる**F007原本監査 → frame投影 → 単独HTML/SVG再生**を実装案とした。A〜F対照、端点値と切断イベント、パース値厳密一致、canonical byte再生、改変拒否、F007既存回帰を採用ゲートとする。物理計算を変えず、ブラウザ側にシミュレーションを再実装しない。F007の既存Wolfram計算とは別にE-cut理論時系列をWolframで確認したが、**V001の実装/画面実行/CI/ユーザビリティ試験/採否はすべて未実施**。観測結果が出るまで数値・合否欄を埋めない。
