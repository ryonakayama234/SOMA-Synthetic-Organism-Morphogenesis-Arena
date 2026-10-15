---
id: DATA
title: データの構造と流れ
kind: contract
status: partially_implemented
updated: 2026-10-13
related: [ARCHITECTURE, F001, F002, F003]
---

# データの構造と流れ

「どんな情報が、どこからどこへ移るか」を図で保持するための、最小限の約束。**F001・F002は実装済みの契約を含み、F003は提案中。** 状態を節ごとに区別する。

## 三つに分けて考える
~~~mermaid
flowchart LR
  I["① 設定\n実験条件"] --> E["② 実行中の状態\n刻々と変化"]
  E --> O["③ 記録\n再解析できる保存物"]
~~~

| 種別 | 意味 | F001の例 |
| --- | --- | --- |
| 設定（input） | 何を固定して試すか | 質量 kg、力 N、抵抗 1/s、刻み s、総時間 s |
| 状態（state） | いまどうなっているか | 時刻 s、位置 m、速度 m/s |
| 記録（output） | 実験後にも調べられる証拠 | 時系列CSV、設定JSON、要約と図 |

## 一個のセルの状態（F001）
~~~mermaid
flowchart TD
  ID["Cell-001"] --> X["位置 x [m]"]
  ID --> V["速度 v [m/s]"]
  ID --> M["質量 m [kg]\n変更しない設定値"]
  ID -. "未導入・将来" .-> E["電力量 [J]"]
  ID -. "未導入・将来" .-> B["接続情報"]
~~~

## 仮の入力形式例
~~~json
{
  "schema_version": "0.1-proposal",
  "experiment_id": "F001-run-001",
  "seed": 1,
  "model": "1d_linear_drag",
  "mass_kg": 1.0,
  "drag_per_s": 0.2,
  "force_n": 1.0,
  "dt_s": 0.01,
  "duration_s": 10.0
}
~~~
**数値は実験準備の例で、確定仕様ではない。**

## 仮の時系列記録
~~~csv
time_s,x_m,v_m_s,force_n
0.00,0.0,0.0,1.0
0.01,0.0001,0.01,1.0
~~~
これは説明用の2行。実験結果を示すものではない。F001の仕様が承認されたら正式な列を固定する。

## 研究の再現性に必要な紐づけ
- 実験識別子 → 設定 → 乱数シード → 実行コードのコミットID → 生ログ → 図 → 解釈
- 記録は追記または新規作成。別条件の結果を同じファイルに上書きしない。
- 物理エンジン用の真の状態ログと、セルが実際に知覚した観測ログを分ける。

[システム図鑑](ARCHITECTURE.md)

## F001で確立した入出力（2026-10-13）
- 設定は `schema_version=f001.v1` を使用。 `model=1d_linear_drag`。
- `initial_x_m`、`initial_v_m_s` も入力として追加。
- 時系列 `states.csv` の列順は `time_s,x_m,v_m_s,force_n` で確定。
- 各実験に `config.json`、`manifest.json`（コードコミットIDとチェックサム）、`motion.svg` を出力。
- 実行結果の上書きを禁止し、出力先には未使用のディレクトリを指定。
- 詳細： [F001の再現方法](../experiments/F001/README.md)。

## F002 エネルギー台帳のデータ契約【実装済み・v1】

~~~mermaid
flowchart TB
  CFG["① config.json\nセルID / 容量・初期残量 µJ\nイベント順・効率 bps"] --> CORE["② LedgerState\nセル別残量と累計入力・支出・損失"]
  CORE --> EV["③ events.csv\n取引イベントと収支残差"]
  CORE --> BAL["③ balances.csv\n各セルの残量・容量"]
  EV --> M["manifest.json / energy.svg"]
  BAL --> M
~~~

| 区分 | カラム・フィールド案 | 注意 |
| --- | --- | --- |
| 入力 | `schema_version=f002.v1`, `experiment_id`, `seed`, `cells`, `events` | 取引順序を使い、時間刻みはまだ定義しない |
| セル | `cell_id`, `capacity_uj`, `balance_uj` | 整数µJ、範囲検証 |
| イベント | `event_index`, `kind=acquire/spend/transfer`, `source_id`, `target_id`, `amount_uj`, `eta_bps` | 無効時は原子的に拒否 |
| 記帳 | `received_uj`, `loss_uj`, `external_in_uj`, `external_out_uj`, `residual_uj` | 内部移送は外部流入・外部流出と別 |
| 証拠 | `config.json`, `events.csv`, `balances.csv`, `energy.svg`, `manifest.json` | 設定・SHA・シード・checksumの対応を残す |

保存会計は `初期残量合計 + 外部取得 = 最終残量合計 + 支出 + 移送損失`。有効イベントの残差は整数で厳密0 µJ。移送の到着量は `floor(amount_uj * eta_bps / 10000)`、送出と受領の差を損失に計上する。丸めによりイベント分割の結果が変わる可能性も記録する。

**数値台帳の電力量とF001の運動モデルを勝手に接続しない。** 電池から運動へ仕事を供給するための効率や回生モデルは未定義。実装済みのデータとして扱わない。

[詳細仕様](../topics/F002-energy-ledger/SPEC.md) / [実験計画](../experiments/F002/PLAN.md)。

### 実装された正式なF002ログ仕様（v1）

- `config.json`：`schema_version=f002.v1`、`experiment_id`、`seed`、`cells` (各 `cell_id`, `capacity_uj`, `balance_uj`) と `events` (kind, amount_uj、種別に応じて source_id, target_id, eta_bps)。未知フィールドは禁止。
- `events.csv` 列順：`event_index,kind,source_id,target_id,amount_uj,eta_bps,received_uj,loss_uj,external_in_uj,external_out_uj,residual_uj`。受理されたイベントだけを記録。
- `balances.csv` 列順：`event_index,cell_id,balance_uj,capacity_uj`。0番目は初期状態。その後、受理したイベントごとに全セル1行ずつ記録。
- `energy.svg`：全セルのイベントごとのセル残量推移と初期量・外部入力・最終残量・支出・損失の収支内訳を可視化。最大400程度のプロット点に間引くため、全イベントの整数値はCSVを一次証拠とする。
- `manifest.json`：`schema_version`、`experiment_id`、`model`、`python_code_git_commit`、`python_code_git_dirty`、`python_code_sha256`、`seed`、`seed_note`、`event_count`、`final_balances_uj`、`acquired_uj`、`spent_uj`、`loss_uj`、`residual_uj`、成果物のSHA256。
- `comparison.json`：A/B/C/D/F-bulk/F-splitの各runに `event_count`, `final_balances_uj`, `acquired_uj`, `spent_uj`, `loss_uj`, `residual_uj` を記録し、全項目を事前予測と厳密照合したうえで生成する（最適化実行 `python -O` でも検査を省略しない）。`E-invalid-events.json`：不正入力の拒否テスト13件（小数値・非有限値も含む）の結果。どちらもF002スイート全体の保存物。
- 電力量・容量・イベント額は1〜10^15 µJ（残量は0も許す）。セル数は1〜100、イベント数は最大10,000。最大値を超える入力は拒否。効率は0〜10,000 bps。
- `event_index` はイベント順序（F001の秒ではない）。状態は不変オブジェクトであり、不正なイベントは例外となり状態が不変。
- git情報は実行モジュールが属するリポジトリから取得する。変更されたワークツリーを実行した場合、`python_code_git_dirty=true` と実行モジュールのSHA256を記録する。Git管理外の場合はSHAとdirty値をnullとし、CIに保存したartifactを再現性の基準とする。

[F002検証結果](../findings/F002-validation.md) / [再現手順](../experiments/F002/README.md)。

### XML出力可能な実験識別子（PR #6 レビュー対応）

`experiment_id` はUnicode文字列（1〜120文字）だが、`energy.svg` のテキストにも使うので**XML 1.0で許容される文字のみ**受け付ける。`\u0000` のような禁止制御文字、Unicodeサロゲート、U+FFFE／U+FFFFは入力検証で拒否する。通常の日本語・絵文字、`&`・`<`・`>`などの文字は許容し、SVG生成時にXMLエスケープする。無効なIDは成果物ディレクトリ作成前に拒否する。詳細は`test_svg_experiment_id_xml10_character_contract`と`soma/f002.py`。

### 同一取引列の再実行データ（F：P1レビュー対応）
F-bulk、F-splitの各configを一切変更せずに再実行し、`F-bulk-replay/` と `F-split-replay/` に別々の証拠を保存する。各初回runとreplayで`config.json`、`events.csv`、`balances.csv`、`energy.svg`、`manifest.json`の生バイトをSHA256照合し、相違があればスイートを失敗させる。`comparison.json.f_replay_checks`に、元run名をキーとして`replay_run`、`same_config`、`byte_identical`、`matching_artifact_sha256`（5ファイルの一致SHA256）を保存する。この観測は同一設定での決定性の根拠であり、物理的な妥当性の根拠ではない。

### F002スイートのGit出自スナップショット（2026-10-15）

`experiments.F002.run_suite` は出力ディレクトリ作成前にGit SHAとdirty値を一度取得し、A/B/C/D/FとFの再実行の計8 manifestへ同じ値を渡す。生成物が未追跡ファイルとしてGit statusに現れても、スイートの実行前コード状態を汚れと誤認しない。実行前からある未コミット変更は引き続きdirty=trueとして記録する。`save_run`単独呼び出しは各runの保存前に取得する。Git出自は開始時のスナップショットであり、並行したソース編集を監視する機能ではない。JSONのフィールド名・会計値は不変。

### 実験スクリプトの出自（2026-10-15）

スイート開始時に`experiments/F002/run_suite.py`のバイト列を取得する。`comparison.json.python_suite_sha256`にSHA256、`suite_source_artifact`に保存先`suite_source.py`を記録し、そのバイト列を出力ルートに保存する。各manifestの`python_code_sha256`は引き続き台帳モジュール本体の識別子。これにより同じHEAD・dirty=true・同じ台帳モジュールでも、条件生成と合否判定の異なるローカル版を区別し、保存ソースを監査できる。会計値とrun単位のスキーマは不変。

## F003の提案データ構造（2026-10-14、未実装）
F001が確立した単一セルの位置・速度・外力を二セルに拡張する。**以下は仕様案であり、動作するAPIや保存済み実験データではない。**

~~~mermaid
flowchart LR
  INPUT["設定JSON\n2セルの初期状態\n各セルの外力・リンクON/OFF"] --> WORLD["世界の真の状態\nCell A / Cell B / Link"]
  WORLD --> TRACE["states.csv\n位置・速度・外力\n内部力・拘束誤差"]
  WORLD --> EVENT["events.csv\n結合・切断・拒否"]
  TRACE --> META["manifest.json\n設定・commit・各成果物ハッシュ"]
  EVENT --> META
  INPUT --> META
  TRACE --> REVIEW["対照比較・図・判断"]
~~~

~~~json
{
  "schema_version": "f003.v0-proposal",
  "experiment_id": "F003-B-planned",
  "seed": null,
  "dt_s": 0.01,
  "duration_s": 10.0,
  "drag_per_s": 0.2,
  "cells": [
    {"id": "A", "mass_kg": 1.0, "initial_x_m": 0.0, "initial_v_m_s": 0.0, "force_n": 1.0},
    {"id": "B", "mass_kg": 1.0, "initial_x_m": 0.5, "initial_v_m_s": 0.0, "force_n": 0.0}
  ],
  "link": {"initially_attached": true, "length_m": 0.5, "detach_time_s": null}
}
~~~

- 実行状態：時刻、各セルの位置・速度、外部指定力、結合ON/OFF、各セルに作用するリンク内部力。
- 記録：拘束誤差や重心の解析値との差分も追加して、間違った内部力や数値積分の劣化を発見可能にする。
- イベント：接続/切断/拒否を理由とともに記録。無理な初期接続を黙って修正しない。
- 境界：すべて**世界の真値を用いる研究用データ**であり、セルが知覚できる情報とは異なる。セル観測ログはセンサー能力を別途実装するまで作らない。
- 再現性：F001と同じく設定・コードSHA・生ログ・SHA256と図を関連づける。乱数を使用しなければ seed は null と記録する。

列名・厳密な許容誤差は実装前の仕様レビューで決定し、実験データに合わせて後付けしない。
[設計仕様](../topics/F003-attachment/SPEC.md) / [実験計画](../experiments/F003/PLAN.md)。

## F003 切断イベント／不正入力のデータフロー（2026-10-15提案・未実装）

~~~mermaid
flowchart TD
  C["config.json 2セル・力・リンク"] --> V{"事前検査"}
  V -->|有効| W["F003 worldの真値"]
  V -->|無効| R["suiteのrejections.json"]
  W --> S["states.csv：時刻毎のpost-event状態"]
  W --> E["events.csv：正常な結合／切断"]
  S --> J["comparison.json・SVG"]
  E --> J
  R --> J
  J --> M["manifest：Git版・suite/モジュール/成果物SHA256"]
~~~

- states.csv：最小列time_s、attached、x_a_m、x_b_m、v_a_m_s、v_b_m_s、force_a_n、force_b_n、link_force_a_n、link_force_b_n、distance_constraint_error_m、velocity_constraint_error_m_s。各時刻の**イベント適用後**の状態を1行だけ記録する。OFF時リンク力0、拘束誤差空欄。
- events.csv：切断イベントはtime_s、kind、attached_before/after、x_a_before_m、x_a_after_m、x_b_before_m、x_b_after_m、v_a_before_m_s、v_a_after_m_s、v_b_before_m_s、v_b_after_m_s、link_force_before_nを持つ（この必須列名を事前固定）。切断の位置・速度before/afterは完全一致する。時刻0の初期結合も有効な場合だけ記録。
- rejections.json：Fスイートの各case_id、入力、expected_error、actual_error、reason、rejected_before_run、pass。無効runのstates/events出力を作らない。
- 研究用world真値とセルの局所知覚を隔離し、F002台帳とは未接続。列順・型の確定は実装PRで検証する。この節はまだ動作していない提案契約。
