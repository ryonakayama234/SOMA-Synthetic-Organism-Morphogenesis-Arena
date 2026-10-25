---
id: EXP-F022
title: 2D接触世界の反証実験計画案
kind: experiment_plan
status: DRAFT_UNFROZEN_UNEXECUTED
updated: 2026-10-25
issue: 77
keywords: [F022, 2D, control, impulse, timestep, falsification, archive]
---

# F022 実験計画案（PRE-REGISTRATION CANDIDATE）

**設計のみ。一次世界を一つも生成していない。凍結済みseed、dt、許容誤差、採用判断は存在しない。**
[仕様](../../topics/F022-2d-encounter/SPEC.md) / [Issue #77](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/77) / [結果ノート](../../findings/F022-validation.md)

## 一つの因果機構
2Dの円盤幾何・接触インパルスが、セル同士が接近/離反する運動状態へ与える効果。外力、制御器、接続判断、資源場は0/なしで固定。2セルのみ。真値と研究者表示を分離。

## 観測前に必ず固定する決定
- 正式な衝突検出時刻の定義（連続 time-of-impact または妥当性を厳密化した別解）と接触判定/初期overlap拒否。
- 質量、半径、反発係数、dtまたはイベント駆動積分方式、総時間、全初期条件、固定シードと対照の繰返し規則、単位・丸め、番号とイベント順序。
- 保存データschema・完全性/インパルス監査の数値許容差、エネルギー散逸許可範囲、独立標本単位。
- 非貫通、数値収束や可能な接触イベントの見逃しに対するフェイル条件。分析計画と閾値の世界結果への後付け適合は禁止。
- V001互換性は別途明示。1D F007の保存ログを書き換えない。

## 反事実/負の対照（各結果は未実施）
| ID | 初期条件の介入 | 予測/棄却基準 |
|---|---|---|
| A | 遠隔・平行/離反・非接触 | impulse=0、各セル等速直線運動、contactイベントなし |
| B | 等質量・正面・弾性衝突 | 法線速度交換、全運動量と運動エネルギーの収支を保存 |
| C | 斜め衝突・接線成分あり | 法線方向の交換/反発・接線方向不変（滑らかな円盤） |
| D | impact parameter を接触から近接未接触へ掃引 | 無接触と接触を幾何により区別。しきい値の恣意的成功を禁じる |
| E | 刻み幅変更、A/B鏡映、座標移動・回転 | 解析解との整合・対称性・不正イベント/トンネリングなし |
| F | 原本の接触法線/時刻/インパルス/速度を改変し再hash | producer独立のsaved-data verifierが偽造を拒否 |
| G | 非弾性衝突（e<1） | 総運動量保存とエネルギー非増加。散逸分を記録 |

「成功した結合回数」や移動距離の最大化を目的関数にしない。接触ゼロ、反証、差なしも研究成果。

## 機械可読の記録候補（未確定）
- scenario.json: study_id, model_version, units, physics_config, initial_states, seed/null, source_sha
- states.jsonl: world_id, step/event index, time_s, A/B (x_m,y_m,vx_mps,vy_mps), energy_kinetic_j
- contacts.jsonl: contact_id, time_s, pair (A,B), normal_xy, impulse_ns, pre/post relative normal speed, restitution, separation, solver_status
- audit.json: conserved_momentum_residual_kg_mps, energy_delta_j, min_separation_m, geometry_class, verifier_status, source/data hashes
- manifest.json: stable schema version, source revision, input/output SHA256, execution environment and evidence provenance
最終schemaは事前凍結で決定し、単位やnull条件、検証関係を[DATA_CONTRACTS](../../docs/DATA_CONTRACTS.md)へ同期。これは仕様提案であり実データの存在証明ではない。

## 別実装PRと第三者視点の審査
実装は他のFxxxを修正しない隔離モジュール/実験スイートとする。解析的校正、保存原本の再演算可能性、モデル実装に依存しない検証器、再hash改竄負例、2つのclean root byte replay、Python 3.11/3.12テストと既存全回帰、正確な最終HEAD CIを要求。同じAIの批判チェックを外部査読と呼ばない。

## 科学判定のスロット
- H22a: **未実施**
- H22b: **未実施**
- H22c: **未実施**
- R22a/R22b反証検査: **未実施**
- 技術的採用: **未採用**
- main統合: **未実施**
