---
id: F006
title: 時間刻みによる運動・電力結果の変化を分離診断する
kind: feature_spec
status: proposed
updated: 2026-10-16
related: [F001, F002, F004, F005, ARCHITECTURE, DATA, EXP-F006, FIND-F006]
issue: 16
---

# F006 — Timestep Convergence Diagnostics【設計提案・未実装・未実施】

## 唯一の新能力
**同じ物理・電池条件で dt だけを変えた複数の F005 実行を比較し、運動の積分誤差・ステップ丸ごとの駆動拒否・整数µJ切上げを区別して記録する。** 既存 `f005.v1` の運動計算、台帳、歴史的データには手を入れない。

## 研究上の問い
現状は `dt` の変更で速度・位置・仕事・駆動受否・最終電池残量が変わりうる。どの変化が積分方式に、どの変化が全区間受否に、どの変化が毎ステップ切上げに由来するか、第三者が生ログから再現できるか。

## H006（事前仮説）
A: 電池十分ではF001半陰的Eulerの位置誤差を参照解に対して分離可能。B: 電池閾値下では同一指令が時間刻みにより採否される履歴を特定可能。C: 同じ理想正仕事でも、各刻みごとの `ceil` が総支出の差を生むことを独立に再構成可能。これらの観測を混同しなければ、F005の適用範囲を科学的に明示できる。

## 代替・反証
- 実験条件で dt 以外が変化する、参照式と保存ログが一致しない、丸め誤差と物理積分誤差を分離できない、受否履歴が再計算できない。
- 生ログを改変してハッシュを更新した場合に独立検証が見逃す、同条件の完全バイト再実行が一致しない。
- 期待が外れた場合はモデル改変で隠さず、`findings`へ反証または不明を報告する。

## 入力・出力
- `sweep.json`: `schema_version=f006.v1`, `sweep_id`, `seed`, `source_model=f005.v1`, `case_id`, `common_parameters`, `dt_s_values`, `reference_id`。各既存F005設定に展開する際はT/dtの格子妥当性、質量・力・電池上限を既存契約で検証。
- `comparison.csv`: `case_id,dt_s,steps,final_x_m,final_v_m_s,positive_work_j,spent_uj,balance_uj,accepted_steps,rejected_steps,reference_x_m,reference_v_m_s,classification` を最低限持たせる。参照値の種類（連続系、厳密有理数離散、binary64実装参照）を `diagnostics.json` で区別する。
- 各試行の生 `states.csv`, `events.csv`, `config.json`, `manifest.json` は既存F005仕様に従う。追加成果物は `diagnostics.json`, `comparison.svg`, 総合 `manifest.json`、suiteスクリプトSHA。
- 真の世界状態は研究用ログにのみ渡し、将来のセル制御器や局所知覚に渡さない。

## 判定基準
1. [実験計画](../../experiments/F006/PLAN.md) のA〜F対照を実装前に凍結し、数式理論値とSOMA実行値を別欄に保存する。
2. `f005.v1` の各ログとイベントを独立の式・整数会計で検査し、比較行から原本へ遡れる。
3. 結果のdt依存が残っても、測定と原因の区分が再現可能であればF006の**診断能力**として採用可能。現行シミュレーターの収束が証明されたとは主張しない。
4. 無効入力拒否、保存証拠のハッシュ・改変検出、Python `-O`も含む検証、同設定の完全再実行一致、F001〜F005の回帰、最終HEAD CI、独立監査。
5. コード／テスト、Mermaidシステム図、データ契約、findings、READMEを**同一の実装PR**で同期して正式採否を判断。

## 非目標
部分時間駆動、残り端数の繰越、位置と仕事の軌道統一、保持電力、接地・反作用、2セル電池統合、局所学習、身体創発、実機妥当性。収束性の診断ができてから、対処を一つずつ別課題にする。

## 状態
**proposed**。数値は理論予測であり、新しいF006コード・CI・実験観測は存在しない。正式採用・main統合は別の意思決定。

[Issue #16](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/16) / [研究記録](../../findings/F006-validation.md) / [研究運営](../../docs/RESEARCH_PROCESS.md)
