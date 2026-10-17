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

## 2026-10-17 V001 初回実装候補のGitHub CI観測（限定結果、採用前）

- 実装Draft PR #26（設計Draft #25にstack）。F007本体/旧証拠は不変。視覚化は研究者の世界真値の読み取り専用。
- **実際の初回HEAD `3012e2e0314ddfad09406adfa130113b8c666162`**： [Actions run #39036627646](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39036627646)。
- Python 3.11 **135テスト OK**、V001最適化実行 **9テスト OK**。Python 3.12も**135テスト OK**＋**9最適化 OK**。
- 採用済みF007の9ケース（A-free/B-linked/C-zero/D-external/E-cut/F-01/F-02/F-03/F-04）から、合計**42保存フレーム**を投影・原本数値再照合。E-cutのt=0.5s post-event=OFF、最終xA=0.8125m・xB=0.9375m（Wolfram事前離散参照と一致）。F-01で電池0後のモーター停止と残量推移を確認。
- 9ケース×（F007原本6点＋V001フレーム/HTML/manifest3点）＋comparison1点＝82ファイルを同一checkoutで**2回生成してbyte一致**。Python間でもsuiteログのframesとHTMLのshaが同一。
- CI artifactを**正常終了時のみ**公開： [3.11 evidence](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39036627646/artifacts/12102104092)／[3.12 evidence](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39036627646/artifacts/12102336494)。
- 位置・速度・電池は元CSVの型付き投影、視覚フレーム上で物理計算を再実行しない。初回負例：CSV改変、viewer frame改変＋manifest再hash、HTML改変＋manifest再hash、入力欠損、既存出力上書き拒否、成功前の公開防止。
- **観測の解釈**：H-V001a〜dは凍結済み9条件と初回検査の範囲で**支持候補**。初回CI通過は画面操作/見やすさが評価済みという意味ではない。
- 初回HEAD以降、さらにhash付替え負例の補強とNode.jsによるブラウザJavaScript構文検査を追加。**追加HEADの最終CI確認前に合格と呼ばない**。外部人間による独立レビュー、実ブラウザ操作試験、明示的な採否、main統合は未了。
