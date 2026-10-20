---
id: DATA
title: データの構造と流れ
kind: contract
status: partially_implemented
updated: 2026-10-16
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
  WORLD --> EVENT["events.csv\n正常な結合・切断"]
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
- イベント：正常な接続/切断だけを記録。不正設定はrejections.jsonに別記。無理な初期接続を黙って修正しない。
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

### F003 設計監査の補足契約（2026-10-15、未実装）
保存される真値・派生量はすべて有限、OFF時の拘束誤差だけnull/CSV空欄とする。表現不能な数値は正常run生成前に拒否する。時間格子の整数性は十進有理数として厳密判定し、Decimalの実行時精度から独立させる。比較結果は保存CSVとイベントを読み戻した全ゲート照合から作る。rejections.jsonは入力全体と例外証拠を保持し、comparison.jsonからSHA256で紐づける。F001依存ソースも出自に含める。

## F003 実装候補（2026-10-15）

~~~mermaid
flowchart LR
  C["設定: f003.v1"] --> S["World Truth: A/B/attached"]
  S --> R["states.csv: 1刻み1行 (post-event)"]
  S --> E["events.csv: attach_initial/detach"]
  C --> M["manifest.json"]
  R --> M
  E --> M
  R --> J["comparison.json: A-F照合"]
  E --> J
  I["不正入力"] --> Q["rejections.json: 拒否ケースのみ"]
  J --> M
~~~

- `config.json`: `schema_version=f003.v1`、`experiment_id`、`seed=null`、`dt_s`、`duration_s`、`drag_per_s`、`cells` (A/Bにid, mass_kg, initial_x_m, initial_v_m_s, force_n)、`link` (initially_attached, length_m, detach_time_s)。
- `states.csv` 列順：`time_s,attached,x_a_m,x_b_m,v_a_m_s,v_b_m_s,force_a_n,force_b_n,link_force_a_n,link_force_b_n,distance_constraint_error_m,velocity_constraint_error_m_s,center_of_mass_m,center_of_mass_velocity_m_s`。OFF時の内部力0・拘束誤差は空欄。
- `events.csv`: `time_s,kind,attached_before,attached_after,x_a_before_m,x_a_after_m,x_b_before_m,x_b_after_m,v_a_before_m_s,v_a_after_m_s,v_b_before_m_s,v_b_after_m_s,link_force_before_n`。正常な初期接続・切断のみ。切断瞬間の前後の座標・速度は同値。
- `rejections.json`：無効設定のcase_id、変更した入力、予期/実際の例外、理由、正常runが生成されなかったか。
- `motion.svg` は最大約500点で**表示のみ間引く**。完全な真値はCSVに保存。
- `manifest.json` はGit HEAD/dirty、F003モジュールSHA、suiteソースSHA、4成果物SHA256、シード未使用、積分方式・行数・イベント数を保持。`suite_source.py` は実行開始時のスクリプトそのものを保存。
- 同じ入力・同じソースに対する `B-pull` と `B-pull-replay` はconfig/CSV/SVG/manifestのバイト一致を検査する。GitHub Actionsのartifactへ全runを保管。
- 初期接続の位置差と速度は**厳密一致**を要求し、丸めや自動補正で修復しない。時間格子は `Fraction(str(value))` によって十進数の厳密な有理数として整数ステップを判定する。これらは理想リンクの設計条件であり、衝突時の合体は対象外。

参考：[F003実装スイート](../experiments/F003/run_suite.py) / [SPEC](../topics/F003-attachment/SPEC.md)。

### F003 監査修正後の証拠契約（2026-10-15、実装候補）
- 各真値・派生数値は有限。表現不能な合成量や状態は保存前にValueErrorで拒否し、OFF拘束だけ空欄とする。保存JSONはallow_nan=False。
- `manifest.json.f001_sha256`は再利用するF001コードのハッシュ。保存を伴わないシミュレーションの前にGit/ソース出自を取得する。
- `comparison.json.cases.<case>.gates`は保存CSV/イベントから検査した全時系列の離散参照・拘束・内部力・重心・イベント同値の合否と最大誤差。`gate_checks`は両セル鏡映・収束・拒否等を含む全体ゲート。
- `rejections.json[].input`は無効入力全体。非有限floatを`{"nonfinite_float":"nan"}`等の文字列タグで表し、正常JSONに非標準NaN/Infinityを持ち込まない。`comparison.json.rejections_sha256`で拒否証拠を参照する。
- `--replay-output-dir`指定時は比較JSONを含む全保存物の生バイトを照合し、初回ルートの`full_suite_replay.json`に一致SHAを保存する。CIは初回・再実行の両方をartifactに保存する。

### F003の採用判断（2026-10-15）
監査修正・50テスト・A〜F・再現性・CI検証を経て、記載した1D二セル理想リンクの実装を採用する。設計#7はmain統合済み、実装の統合はPR #8で追跡。既存の図・スキーマ・観測境界は不変で、候補・未統合表記は過去時点の履歴。

## F004：内部駆動・電池の入出力構造【2026-10-15 提案／未実装】

以下は **f004.v0-proposal** の説明用案。まだ有効なAPI・既存CSVではない。F001〜F003の既存契約を変更せず、実装前レビューでフィールドと型を凍結する。

~~~mermaid
flowchart LR
  CONFIG["config.json：1セル・外力／内部力／初期µJ"] --> CAND["F004候補ステップ"]
  CAND --> MOTOR["内部力の正の離散仕事・費用µJ"]
  MOTOR --> LEDGER["F002 LedgerState：spend または無支出"]
  MOTOR --> STEP["F001 step：実際に適用した内部＋外力"]
  LEDGER --> STATES["states.csv：時刻・残高・適用力・仕事"]
  STEP --> STATES
  LEDGER --> EVENTS["events.csv：受理されたF002支出"]
  STATES --> COMP["comparison.json／motion_energy.svg"]
  EVENTS --> COMP
  CONFIG --> META["manifest.json：Git／実装／suite／出力のSHA"]
  COMP --> META
~~~

~~~json
{
  "schema_version": "f004.v0-proposal",
  "experiment_id": "F004-B-planned",
  "seed": null,
  "mass_kg": 1.0,
  "drag_per_s": 0.0,
  "dt_s": 0.1,
  "duration_s": 1.0,
  "initial_x_m": 0.0,
  "initial_v_m_s": 0.0,
  "motor_force_n": 1.0,
  "external_force_n": 0.0,
  "capacity_uj": 1000000,
  "initial_balance_uj": 1000000
}
~~~

| データの種類 | 候補フィールド・単位 | 注意 |
| --- | --- | --- |
| 設定 | 質量kg、抵抗1/s、dt/duration s、内部／外部力N、初期残高・容量µJ | 外力と内部駆動力を分ける。例の値は事前理論比較用 |
| 世界状態 | time_s、x_m、v_m_s、balance_uj、motor_command_n、motor_applied_n、external_force_n | 真値のみ。将来のセル観測ログとは分離 |
| 運動と費用 | proposed_motor_work_j、spent_uj、motor_accepted、拒否理由 | 仕事は台形速度、位置はF001半陰的Euler。1µJ未満正値は切り上げ |
| F002イベント | kind=spend、source_id、amount_uj と残差 | 正の額のみ記帳、残高不足時はspendを発生させない |
| 証拠 | states.csv、events.csv、comparison.json、motion_energy.svg、manifest.json、suite_source.py | Git SHA/dirty、モジュール・suite・保存物SHAを連結。再実行の生バイト一致 |

不変条件：残量は非負の整数µJ、正常支出は常にF002の保存会計残差0。外力のみならspend=0。残高不足時は内部力だけ0として候補を捨て、外力によるF001運動を記録。入力や派生量が無効なら、世界状態と台帳の両方を更新しない。丸め境界の表現方式と最大数値範囲は実装前に仕様レビューで凍結する。

この段階は**仮説と契約案**であり、F004実験ログ・実装の存在を示さない。[仕様](../topics/F004-actuation-energy/SPEC.md) / [A〜F](../experiments/F004/PLAN.md) / [Findings](../findings/F004-validation.md)。

### F004 2026-10-16 事前監査のデータ・数値契約（未実装）
- `states.csv` に`step_index`, `ledger_event_index`（spendなしはnull）、`motor_command_n`, `motor_applied_n`, `external_force_n`, `candidate_motor_work_j`, `spent_uj`, `balance_uj`, `decision_reason`を持たせ、時刻と位置・速度に対応づける。
- `ledger_event_index`によってF002のspendイベントと当該運動ステップを1対0/1で結合する。支出0のステップはF002にイベントを出さない。
- `decision_reason` は `zero_balance`, `zero_command`, `insufficient_balance`, `accepted_positive_work`, `accepted_nonpositive_work` など。残量0でも候補仕事0ならモーターが動く抜け道を防ぐ。
- `candidate_motor_work_j`はステップの仮計算値。電池0の場合は仮計算を行わずnullとする。`spent_uj`は整数、`balance_uj`はF002の厳密整数。外力の仕事をspentへ算入しない。
- 浮動小数点と1 µJ切上げにより、Wolfram理想有理数とbinary64参照はBで5 µJ、Dで4 µJ異なる。理論参照と浮動小数点の合否参照を明確に分離し、どちらも記録する。
- 無効時は台帳と運動を不可分に拒否。入力の時刻格子は十進有理数で厳密判定。F004は最大10000ステップ。全ログと実行スクリプト・Git版・hashを対応づける。設計時点の提案契約であり、実装済みスキーマではない。

## F004 実装候補 f004.v1 の確定予定スキーマ（2026-10-16／PR #11）

\`config.json\` 必須フィールド（未知キー不可）：\`schema_version="f004.v1"\`, \`experiment_id\`（XML1.0有効、長さ1〜120）, \`seed=null\`, \`mass_kg\`, \`drag_per_s\`, \`dt_s\`, \`duration_s\`, \`initial_x_m\`, \`initial_v_m_s\`, \`motor_force_n\`, \`external_force_n\`, \`capacity_uj\`（1〜10^15）, \`initial_balance_uj\`（0〜capacity）。セルIDは内部で"A"固定。時間格子は\`Fraction(str(duration))/Fraction(str(dt))\`が整数1〜10000と一致する条件。有限値、正質量、非負抵抗、dt*drag<=1。

\`states.csv\` 列順（step_index=0が初期状態、その後各ステップ適用後1行）：

~~~text
step_index,time_s,x_m,v_m_s,motor_command_n,motor_applied_n,external_force_n,candidate_motor_work_j,motor_work_j,external_work_j,drag_work_j,kinetic_delta_j,mechanical_residual_j,spent_uj,balance_uj,ledger_event_index,decision_reason
~~~

- \`candidate_motor_work_j\`は電池0または命令0の場合null/空欄。残量不足時は仮計算した値が存在しても\`motor_applied_n=0\`。\`spent_uj\`は非負整数。\`ledger_event_index\`は支出イベントがある時にだけ連続した正整数、他はnull。
- 理想モデルの\`decision_reason\`：\`initial\`, \`zero_balance\`, \`zero_command\`, \`insufficient_balance\`, \`accepted_positive_work\`, \`accepted_nonpositive_work\`。最後のケースは正の残量がある場合のみ。**ブレーキ等の内部力適用回数≠支出イベント数**。
- 各行の\`motor_work_j\`, \`external_work_j\`, \`drag_work_j\`は（符号付き）midpoint-velocity仕事。\`mechanical_residual_j = kinetic_delta_j - (motor_work_j + external_work_j - drag_work_j)\`。世界の真値のみでありセンサー出力ではない。
- \`ledger/events.csv\`：\`step_index,time_s,event_index,kind,source_id,target_id,amount_uj,eta_bps,received_uj,loss_uj,external_in_uj,external_out_uj,residual_uj\`。イベントはF002の既存\`spend\`のみ。支出0なら行は無い。
- \`motion_energy.svg\`：位置・速度・残量の3段表示。間引き表示のみ、生証拠は完全なCSV。\`manifest.json\`：モデル/版/seed/積分方式、Git HEAD・dirty、F001/F002/F004コードSHA256、スイートSHA256、ケースごとのCSV/JSON/SVG SHA256。
- スイート出力：\`suite_source.py\`, \`rejections.json\` (監査後17拒否), \`comparison.json\` (A〜F 10設定・理論参照・binary64参照・CSV独立検算), \`B-full-replay/\`, \`full_suite_replay.json\`。完全な再実行バイト照合が一致しなければテストは失敗。
- 運動と台帳は新しい不変値として不可分commit。不正入力や有限でない派生量はrunフォルダ作成前に拒否。台帳残差は厳密0 µJ。
- \`comparison.json.status=local_software_checks_passed\`はスイート内部のソフトウェア検査を意味し、main統合の承認・実機の裏付けではない。

[実装モジュール](../soma/f004.py) / [再現手順](../experiments/F004/README.md) / [初回CI](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38829244901)。

### PR #11 監査後の補足契約（2026-10-16）
- `Config(**fields)`、`Config.from_dict/from_json`、`dataclasses.replace`の全経路で同じ型・範囲・時間格子検証を行う。数値フィールドはfloatに正規化するが、時間比は**生入力と正規化後の両方**で同じ整数1〜10000でなければ`ValueError`。例：dt=`9007199254740992`、duration=`54043195528445952`は入力上6ステップでも正規化後の十進比が変わるため拒否する。ステップ数を切り捨てて実行しない。
- 初期行（step_index=0）の`motor_work_j`、`external_work_j`、`drag_work_j`、`kinetic_delta_j`、`mechanical_residual_j`はすべて厳密0。初期速度が非0でも区間仕事・エネルギー**差**なので0とする。
- `manifest.artifacts`のキーは`config.json`、`states.csv`、`ledger/events.csv`、`motion_energy.svg`の4つと厳密一致させる。空・欠落・余分な一覧を拒否し、すべてのSHA256を照合する。hash一致と独立の意味検証は別の条件であり、hashが更新されても初期行異常を許可しない。manifest自体の真正性を保証する署名方式ではない。
- SVGは有限値の時間比と正規化した状態範囲から座標を計算する。大きい有限状態でも座標を`inf`/`nan`にしない。CSVの物理値や仕事のbinary64演算順序は変更しない。

### F004 採用決定（2026-10-16）
ユーザーの指示で`f004.v1`を正式採用。設計PR #10は先に統合済み、実装・採用記録はPR #11で統合する。採用による列・型・演算順序・既存APIの変更なし。仕事は区間の符号付き仕事であり、速度反転をまたぐ場合も正負を相殺した**後**の正部分を課金する。区間内の正の仕事だけを積分した電力費用とは異なる。`accepted_nonpositive_work`で適用モーター力非0・支出0があり得る。保持/待機消費と実モーター損失は未モデル化。[反転の実行例と後続課題](../findings/F004-validation.md#2026-10-16-採用判断と統合)。


## F005：正仕事と符号付き仕事の分離【2026-10-16 提案・未実装】

`f005.v0-proposal` は **計画用データ契約**であり、現行API・生成物ではない。F004の `f004.v1` は変えない。実装PR前にスキーマと演算順序・許容差をレビューして確定する。

~~~mermaid
flowchart LR
  CJ["config.json 1セル・力・残高・刻み"] --> S["F001仮運動"]
  S --> W["F005 正仕事積分候補（未実装）"]
  W --> L["F002残高／spendまたは内部力拒否"]
  L --> CSV["states.csv：候補値・採用値・世界真値"]
  L --> EV["ledger/events.csv：正額支出"]
  CSV --> COMP["comparison.json：全時刻独立参照"]
  EV --> COMP
  CSV --> SVG["motion_energy.svg：可視化だけ"]
  COMP --> HASH["manifest.json：Git/ソース/成果物SHA"]
  CJ --> HASH
~~~

### 提案設定（読みやすさ優先：項目・版は未確定）
~~~json
{
  "schema_version": "f005.v0-proposal",
  "experiment_id": "F005-A-planned",
  "seed": null,
  "mass_kg": 1.0,
  "drag_per_s": 0.0,
  "dt_s": 1.0,
  "duration_s": 1.0,
  "initial_x_m": 0.0,
  "initial_v_m_s": 1.0,
  "motor_force_n": -2.0,
  "external_force_n": 0.0,
  "capacity_uj": 500000,
  "initial_balance_uj": 500000
}
~~~

### 提案フィールド
| データ | 候補の項目・単位 | 意味・検査 |
| --- | --- | --- |
| `config.json` | F004の構成＋新しいschema版 | 1セル、1D、有限な数値、時間格子整数、seed=null |
| `states.csv` | `step_index`, `time_s`, `x_m`, `v_m_s` | 区間適用後の**世界真値** |
| `states.csv` | `motor_command_n`, `motor_applied_n`, `external_force_n` | 指令と適用を区別。残高不足時は内部のみ0 |
| `states.csv` | `candidate_signed_work_j`, `candidate_positive_work_j`, `motor_signed_work_j`, `motor_positive_work_j` | 候補vs採用／機械収支vs費用を厳密に分離 |
| `states.csv` | `spent_uj`, `balance_uj`, `ledger_event_index`, `decision_reason` | 整数µJ・正額のみspend・拒否理由。候補と実際の課金を同一視しない |
| `ledger/events.csv` | F002の`spend`イベントと各ステップの参照 | 台帳の保存残差は**厳密0** |
| `comparison.json` | A〜F、理想値／独立binary64参照／実測差、改変検査 | 予測と観測・全ステップの判定を分ける |
| `manifest.json` | Git HEAD/dirty、ソース・実験スイート・成果物 SHA256、seed | 証拠の対応付け。署名や改ざん耐性の保証ではない |

**不変条件**：残高は非負整数µJ、正仕事だけを理想エネルギー費用として計上、外力の仕事は電池支出に含めない。モーター力が採用されなければ`motor_positive_work_j=0`だが`candidate_positive_work_j`は正の場合がある。費用計量はF001の速度更新や機械恒等式を変更しない。無効設定・非有限派生量は保存前に拒否する。

[仕様](../topics/F005-positive-work/SPEC.md) / [A〜F](../experiments/F005/PLAN.md) / [未実施の記録](../findings/F005-validation.md)。

### F005 implementation candidate: f005.v1 (2026-10-16; adoption pending)

**Schema `f005.v1` is implemented on the proposed feature branch only**, and does not overwrite historic `f004.v1` CSVs. Config accepts exactly F004's 13 keys, changing only `schema_version` to `f005.v1`; no additional motion/controller/observation state is introduced.

`states.csv` columns are exactly:

~~~text
step_index,time_s,x_m,v_m_s,motor_command_n,motor_applied_n,external_force_n,candidate_motor_work_j,candidate_motor_positive_work_j,motor_positive_work_j,motor_work_j,external_work_j,drag_work_j,kinetic_delta_j,mechanical_residual_j,spent_uj,balance_uj,ledger_event_index,decision_reason
~~~

- The **candidate** positive field is null when the motor is not evaluated (zero battery or zero command), otherwise measures the proposed motor+external candidate. The accepted `motor_positive_work_j` is zero when the motor is rejected or commanded off.
- `candidate_motor_work_j` and `motor_work_j` are still **signed midpoint** mechanical work; neither is the battery expense when a velocity reversal occurs.
- `motor_positive_work_j` integrates only `max(0,motor_force * linearly-interpolated velocity)` in joules. Only `ceil(1e6 * candidate_motor_positive_work_j)` on an accepted step is debited via F002 `spend`. No event for zero cost; rejection recomputes external-force-only F001 motion.
- No real electrical efficiency, holding, waiting, heat, or regeneration. Decimal time-grid strictness, finite numbers, one-cell A, maximum 10000 steps, immutable atomic accounting, XML-safe identifiers and `seed=null` retain F004-style constraints.
- `ledger/events.csv`: same `EVENT_COLUMNS` as F004, accepted positive F002 spend only. The F002 conservation residual must be exactly zero µJ.
- `manifest.json`: `schema_version=f005.v1`, Git commit and dirty flag, F001/F002/F005 code digests, suite SHA256, row/event counts and exact hashes of config, states, ledger events and SVG. `comparison.json` and replay report are suite-level and contain case-specific independent results; initial row must have zero *both signed and positive* interval work.
- Invalid or nonfinite runs do not create valid evidence. Original F004 test suite and `f004.v1` output remain independently repeatable.

### F005 comparisonの独立積分・数量化記録（PR #14監査、2026-10-16）
`f005.v1`の保存列と課金式は維持。初期行では `candidate_motor_work_j` と `candidate_motor_positive_work_j` の両方がnull。候補/採用正仕事の比較には正値性と相対・ULP許容差を使い、1e-100Jを0Jへ改変したログを許容しない。

`comparison.json` の各caseに `quantization` を追加：
- `exact_endpoint_integral_j`：実際に採用された区間のbinary64端点を厳密有理数として積分した総和（分数字列）。理想連続軌跡の積分とは区別。
- `binary64_work_error_j`：binary64正仕事総和−上記厳密積分（J）。
- `exact_ceiled_spent_uj`／`exact_rounding_excess_uj`：各厳密積分をµJ切上げした合計／その数量化差（後者は分数字列）。
- `binary64_spent_uj`／`binary64_minus_exact_ceiled_uj`：実支出合計／厳密切上げ合計との差（整数µJ）。
- `positive_intervals`：採用された正仕事区間数N。厳密数量化差はN=0なら0、N>0なら0以上N未満と検証。binary64演算後の差にはこの厳密不等式を無条件適用しない。
受否はbinary64課金で確定するため、この比較は同じ採用軌跡の評価であり、有理数課金で別の軌跡をシミュレートした結果ではない。


### f005.v1 採用済み契約の適用範囲（2026-10-16）
`f005.v1`の上記列とスキーマは**離散理想正仕事・整数µJ台帳接続用に正式採用**。過去`f004.v1`は不変。仕事`motor_positive_work_j`は位置変位に沿った物理的な電気消費量ではなく、線形補間速度上の正の機械仕事である。時間刻みを変えると運動採否・積分近似・整数切上げ費用が変わる。ゼロ仕事の保持・制動は正残量で無料、`motor_applied_n`は反作用を持たない有効力である。形態・生存・移動効率の比較への転用禁止。[F005正式採用の条件](../topics/F005-positive-work/SPEC.md#2026-10-16-正式採用f005の限定的な研究上の位置づけ)。

## F006：刻み幅比較のデータ構造と流れ（2026-10-16／提案・未実装）

~~~mermaid
flowchart TD
  A["① sweep.json\n1ケースに共通の条件＋dt値一覧"] --> B["② dtごとに独立したF005 config.json"]
  B --> C["③ F005の元データ\nstates.csv / events.csv / manifest.json"]
  C --> D["④ 原本検証・独立参照と突合"]
  A --> D
  D --> E["⑤ comparison.csv\n1行=ケース×dt"]
  D --> F["⑤ diagnostics.json\n参照式・差・分類・判定"]
  E --> G["⑥ comparison.svg / manifest.json\nSHAとGit commitで原本追跡"]
  F --> G
~~~

| 段階 | 最低限のフィールド（案） | 意味 |
| --- | --- | --- |
| 入力 | `schema_version=f006.v1`, `sweep_id`, `case_id`, `seed`, `source_model=f005.v1`, `common_parameters`, `dt_s_values`, `reference_id` | dt以外を固定・版を記録 |
| 元run | f005.v1の`config.json`, `states.csv`, `events.csv`, `manifest.json` | 生ログは改変せず原本を参照 |
| 比較1行 | `case_id`, `dt_s`, `steps`, `final_x_m`, `final_v_m_s`, `positive_work_j`, `spent_uj`, `balance_uj`, `accepted_steps`, `rejected_steps` | m/m·s^-1/J/µJの単位と経過を明示 |
| 比較参照 | `reference_x_m`, `reference_v_m_s`, `classification` | 連続理論／厳密離散／実装参照の区別を必須に |
| 解析 | `diagnostics.json`、原本パス・各SHA、source/suite SHA、許容差、判定 | 相互作用は混合・不明を許容 |
| 表示 | `comparison.svg`, `manifest.json` | 人に読める図＋機械が検証できる出自 |

F006が独自の世界状態を持つことはない。すべての元状態はF005のシミュレーターから取得する。比較層で統合し、**セルの知覚には完全な世界真値を渡さない**。上記フィールドは設計案。実装前に型、厳密な列順、バリデーション、浮動小数点演算順序を凍結する。

[仕様](../topics/F006-timestep-diagnostics/SPEC.md) / [A〜F](../experiments/F006/PLAN.md) / [Findings](../findings/F006-validation.md)


### F006 v2 改訂契約（2026-10-17、設計・未採用）
以下は旧v1フィールド案より優先する。`sweep.json`は完全設定15個を持つ`runs`マップ（キーA-dt-00〜E-dt-02）、`schema_version=f006.v2`, `sweep_id=F006-A-E-v2`, `source_model=f005.v1`, `seed=null`, `reference_id=Wolfram-exact-fractions-2026-10-16`を持つ。

CSV確定列順は`case_id,dt_s,steps,final_x_m,final_v_m_s,positive_work_j,signed_work_j,spent_uj,balance_uj,accepted_steps,rejected_steps,reference_x_m,reference_v_m_s,reference_type,expected_classification,signature_matches_reference,verdict`。dt/位置/速度/仕事/参照はfinite float（単位s,m,m/s,J）、steps/支出/残高/受否は整数、case_id=A〜E。reference_typeはdiscrete_exact_fraction、ラベルは事前登録値、署名一致はbool（CSVはTrue/False）、成功verdictはsupported。不一致は公開前に例外とする。

`diagnostics.json`のラベルはexpected_classification、観測値は比較特徴量・各run原本への相対パス/SHA・受否step一覧・仕事/会計残差として保存する。`classification_scope=fixed_preregistered_controls_only`、`causal_attribution=null`と理由を必須にし、事前ラベルと一般因果判定を区別する。

suite manifestはモデル/seed/sweep/run数/verdict、Git commit/dirty、F001/F002/F005 hash、suite_sha256、artifact hashに加え、`source_hashes`（runner/diagnostics/F005 oracle/soma初期化/F001/F002/F005/PLAN/SPECの9パス→SHA256）を持つ。suite sourceコピー、run manifest、モデルメタデータ、参照IDを照合する。Gitとソースは信頼するcheckoutまたは外部CI記録を期待値とし、manifestから信頼基準を逆算しない。履歴実行の本人性をhashで証明したとはしない。具体的保存・障害契約はF006 SPECのv2改訂節を優先する。

### F006 診断フィールドの意味と整合性ゲート（設計詳細・未実装）

- `accepted_steps`: `motor_applied_n != 0` のステップ数（初期行を除外）。`rejected_steps`: 非ゼロ命令があったにもかかわらず `insufficient_balance` または `zero_balance` により適用されなかったステップ数。`zero_command`は拒否に含めない。
- `positive_work_j`: **適用された**正仕事の全ステップ和。`candidate_motor_positive_work_j`（棄却候補の仕事を含む）と混同しない。
- `spent_uj`: F002の受理された整数支出。イベントの合計、初期残量−最終残量、全状態の`spent_uj`合計の三者を照合。
- `reference_x_m`, `reference_v_m_s`: 必ず参照方式`continuous_analytic`／`discrete_exact_fraction`／`f005_binary64`とペアで格納し、Bの離散仕様と連続物理の真値を取り違えない。
- `classification`: `integration`, `budget_gate`, `quantization`, `positive_work`, `external_only`, `mixed`, `undetermined`の候補。対照A〜Eの事前分類と、実行結果からの帰属を別々のフィールドに保存すること。
- `diagnostics.json`：各run原本への相対パスとSHA、参照の出自・式、正仕事計算誤差・整数丸め超過・受否履歴差・物理量差・許容差・支持／反証／不明を持たせる。検証不能な属性はnullと理由を明記。
- `manifest.json`：Git HEAD / dirty、f005ソースhash、F006スイートhash、各成果物hash、実行環境を記録。再実行比較の可変メタデータは固定化または分離し、履歴出力の書き換えを防止する。

以上は設計上の意味契約。実装前にフィールド型・値域・列順を確定し、出力生ログとの同期を監査する。

## F006 実装候補の確定列・出力物（PR #18、未採用）

| ファイル | 契約・意味 |
| --- | --- |
| `sweep.json` | `schema_version=f006.v1`, `sweep_id=F006-A-E-v1`, `seed=null`, `source_model=f005.v1`, `reference_id`, `runs`。15個のf005.v1完全設定をキー `A-dt-00` ～ `E-dt-02` に保存 |
| `comparison.csv` | `case_id,dt_s,steps,final_x_m,final_v_m_s,positive_work_j,signed_work_j,spent_uj,balance_uj,accepted_steps,rejected_steps,reference_x_m,reference_v_m_s,reference_type,classification,verdict`。全15行。採用前に列名・順番の不変性をテスト |
| `diagnostics.json` | 実行時の分類・参照の種類・刻み間の特徴量・各run原本5ファイルのSHA・採否ステップ一覧・正仕事合計・整数台帳残差・支持状態 |
| `comparison.svg` | 生CSVから独立に再構成可能な表示専用図 |
| `manifest.json` | Git HEAD、実験スクリプトSHA、F001/F002/F005ソースSHA、suiteファイルSHA、実行run数、supported/unsupported、再現性の原資料 |
| `suite_source.py` | 実際に実行したF006実験ドライバのソースコピー。SHAと照合 |
| `A-dt-00/`等の15ディレクトリ | F005の`config.json`、`states.csv`、`ledger/events.csv`、`motion_energy.svg`、`manifest.json`を無変更で保存 |

`F006`の`reference_type=discrete_exact_fraction`はWolframによる**離散モデル参照**であり、連続真値の意味は持たない。`A`の連続参照0.5mは`diagnostics.json`の別フィールド`reference_continuous_x_m`に格納。各runの`quantization_excess_uj`は理想正仕事を区間毎に厳密積分した切上げ超過の分数を文字列で保存する。監査器は元の状態CSVとイベントを再読込し、比較ファイル・表示図を再構成して検証する。

**F対照は15行の物理実験には含めず、負例・改変・再現性テストに実装。**これは事前登録PLANとの対応上、明示的に区別する。


### F006 v2実装対応（2026-10-17）
上の「F006 実装候補の確定列・出力物」はv1履歴であり、v2改訂契約が優先する。ファイル数は1suite81（15run×5＋suite6）、replay込み162で維持。新しいsource_hashesはmanifest内の9パス→hashマップで、各ソースのコピー9ファイルを出す意味ではない。audit_suiteの結果はidentity_matches_trusted_expectation=trueとhistorical_execution_attested=falseを返す。JSONのsignature_matches_referenceはbool、CSVはTrue。Git不明時はnull。一般因果帰属はnull＋理由とする。

## F006 v2 限定的正式採用のデータ契約（2026-10-17）

**現行契約は`f006.v2`、固定`sweep_id=F006-A-E-v2`、`seed=null`。** 上のv1候補列・スキーマは履歴であり採用済み形式ではない。F005の単一run契約・歴史的ログは不変。出力は1suite=15run×5ファイル＋suite6ファイル=81ファイル、replay込み162ファイル。

| ファイル/キー | 採用済みの意味と照合 |
| --- | --- |
| `sweep.json` | 事前凍結A〜Eの15条件。各ケース内で`dt_s`と識別子のみ変化。モデル`f005.v1`、固定参照ID。 |
| `comparison.csv` | 15行。位置・速度・仕事・支出・受理/拒否・参照値に加え、事前ラベル`expected_classification`と観測`signature_matches_reference`を分離する。 |
| `diagnostics.json` | `classification_scope=fixed_preregistered_controls_only`、`causal_attribution=null`。生ログの照合、誤差比・受否・数量化の固定参照と原本hash。 |
| `manifest.json` | suite/run model/sweep/seed/git identity、F001/F002/F005 sha、runner source sha、9依存`source_hashes`、全成果物SHA256。期待identityは未信頼manifest外から指定。 |
| `A-dt-xx/` | 各F005 runのconfig/state CSV/ledger events/SVG/manifest。独立保存オラクルが各ステップ・残差・イベントを検査。 |
| `suite_source.py` / `comparison.svg` | source snapshotのhash照合／SVGは表示専用でCSVに優先しない。 |

**保存ルール**：私有stageで生成/再計算/バイト再生一致を完了し、Linux `renameat2(RENAME_NOREPLACE)`で公開。通常例外ではこの呼出しで公開した成果物だけをrollback。他者の既存証拠は変更しない。2宛先の一括crash-atomicは提供しない。出自hashは監査checkoutとの一致であり、歴史的実行者の暗号学的証明ではない。F003/局所知覚/創発の構造は未接続。[検証・採用記録](../findings/F006-validation.md#2026-10-17-f006-限定的な正式採用--最新研究判断)。

## F007 提案データ構造・保存フロー（2026-10-17・未実装）

**以下は`f007.v0-proposal`の説明用構造。既存の採用済みスキーマではない。** 型・列順・不正入力拒否規則は実装前の独立レビューで確定し、新版`f007.v1`を凍結する。F003、F005、F002の既存契約はそのまま保持する。

~~~mermaid
flowchart TD
  CFG["config.json: 2セル＋接続＋Aモーター＋電池"] --> WORLD["世界真値: A/B位置速度、link force、残高"]
  WORLD --> STATE["states.csv: 片側指令/実適用、運動、力、支出、残高"]
  WORLD --> EVENTS["ledger/events.csv＋link_events.csv"]
  STATE --> CHECK["独立参照の全行照合"]
  EVENTS --> CHECK
  CHECK --> COMP["comparison.json＋図"]
  CFG --> META["manifest.json: git SHA/dirty・seed・source SHA・各artifact SHA256"]
  COMP --> META
  WORLD -. "未実装" .-> SENSOR["セルが見られる局所観測"]
~~~

~~~json
{
  "schema_version": "f007.v0-proposal",
  "experiment_id": "F007-B-theoretical",
  "seed": null,
  "dt_s": 0.25,
  "duration_s": 1.0,
  "drag_per_s": 0.0,
  "cells": [
    {"id": "A", "mass_kg": 1.0, "initial_x_m": 0.0, "initial_v_m_s": 0.0, "motor_force_n": 2.0, "external_force_n": 0.0, "capacity_uj": 3000000, "initial_balance_uj": 3000000},
    {"id": "B", "mass_kg": 1.0, "initial_x_m": 0.5, "initial_v_m_s": 0.0, "external_force_n": 0.0, "capacity_uj": 1, "initial_balance_uj": 0}
  ],
  "link": {"initially_attached": true, "length_m": 0.5, "detach_time_s": null}
}
~~~

| 種別 | 最小限区別すべき項目・単位 |
| --- | --- |
| 設定 | f007スキーマ・seed=null・dt/duration [s]・セル質量[kg]・リンク長[m]・A motor指令[N]・各外力[N]・セルごとの容量/残高[µJ] |
| 世界状態 | step, time[s], attached, x_A/x_B[m], v_A/v_B[m/s], link_force_A/B[N] |
| モーター | Aの`command_n`と`applied_n`、正仕事[J]、拒否理由、`spent_uj`（正味符号付き仕事とは別） |
| 台帳 | `balance_a_uj`、`balance_b_uj`、Aのspend event、合計残差[µJ]。Bのエネルギー転送イベントは生じない |
| 保存証拠 | config・states・ledger/events・link_events・manifest・再構成可能なSVG・比較JSON・Git/SHA256 |

**真値と局所知覚の境界**：出力される位置/結合状態/電池残高は研究者の世界真値であり、ロボット自身の能力としては認定しない。**時間刻み**：各ステップ整数µJ切上げと受否判定はdtに依存する。出所・台帳・ログを混同しない。

[仕様](../topics/F007-linked-motor-work/SPEC.md) / [実験計画](../experiments/F007/PLAN.md) / [記録](../findings/F007-validation.md)。


### F007 事前監査で追加する観測契約（2026-10-17、未確定）

[PLAN F-01〜F-06](../experiments/F007/PLAN.md) を保存CSVから検証できるよう、**実装前に**次の区別を凍結対象とする。これはまだ採用済みのフィールド名・列順ではない。

| 意味 | 記録すべき区別 | 誤った実装の検出 |
| --- | --- | --- |
| A motor | `command_n`、`candidate_motor_positive_work_j`、`applied_n`、`motor_positive_work_j`、`decision_reason` | 電池不足で棄却した候補を実支出へ混入させない |
| 仕事・電池 | `motor_signed_work_j` と `motor_positive_work_j`、`spent_a_uj`、A/Bそれぞれの残高 | 速度反転時の相殺・Bの誤請求を検出 |
| 外力・拘束 | `external_force_a_n`、`external_force_b_n`、`link_force_a_n`、`link_force_b_n`、`attached` | Aモーター拒否時でもB外力とリンクが残ることを確認 |
| 時刻イベント | `step_index`、`time_s`、`detach_before_after` | 切断瞬間の速度・位置ジャンプと二重イベントを検出 |
| 監査 | 保存runのconfig/source/Git identity、台帳events、raw CSV、`manifest.json` と独立参照 | CSV改変・不正出自・再実行不一致を検出 |

**実験ごとのレコード生成順**：入力検証 → 候補計算 → A支出ゲート → 採用または再計算 → 世界真値を確定 → 台帳・linkイベントを記録 → 原本を保存 → 別計算で全行監査 → 図・比較JSON・出自SHA → CI再実行照合。候補仕事や棄却理由は研究者用の監査データでありセルの知覚には入れない。数値はF005規約で計算するためF006のdt依存は残る。最終の型・列順・公開方式は独立設計レビュー後に確定する。

## F007 v1 実装候補の保存契約（2026-10-17）

実装で固定したスキーマは`f007.v1`。上の`f007.v0-proposal`例は**設計履歴**であって採用済みデータ契約ではない。入力は`schema_version, experiment_id, seed(null), dt_s, duration_s, drag_per_s, cells[A,B], motor_force_n, link`を厳密に含み、セルは`id, mass_kg, initial_x_m, initial_v_m_s, external_force_n, capacity_uj, initial_balance_uj`を含む。`link`は`initially_attached, length_m, detach_time_s`である。

| 実データ | 契約 |
| --- | --- |
| `states.csv` | `step_index,time_s,attached,x_a_m,x_b_m,v_a_m_s,v_b_m_s,motor_command_n,motor_applied_n,external_force_a_n,external_force_b_n,link_force_a_n,link_force_b_n,candidate_motor_work_j,candidate_motor_positive_work_j,motor_work_j,motor_positive_work_j,external_work_j,drag_work_j,link_work_j,kinetic_delta_j,mechanical_residual_j,spent_a_uj,balance_a_uj,balance_b_uj,ledger_event_index,decision_reason` |
| `ledger/events.csv` | F002受理されたAの`spend`イベントのみ。`step_index,time_s`とF002 Entryフィールドを格納。Bへのtransferイベントはない |
| `link_events.csv` | `time_s,kind,attached_before,attached_after`とA/Bのbefore/after x/v、`link_force_before_n`。切断の瞬間状態は不変 |
| `config.json` | 正規化した決定論入力（seed=null）。単位m,m/s,N,kg,s,µJ |
| `manifest.json` | モデル・実験ID・原本SHA256・依存ソースhash・Git HEAD/dirty・支出と残高・イベント件数・台帳残差 |
| スイート | 9runを含む`comparison.json`、ソースコピー2件、全成果物SHAを含むmanifest、同条件byte replay |

列順は`soma/f007.py`内の`STATE_COLUMNS`/`LEDGER_COLUMNS`/`LINK_COLUMNS`を唯一の確定列定義とする。`candidate_motor_*`はA残量0/指令0ではnull、非ゼロ指令かつ残量ありで棄却された候補は記録するが**実支出0**。開始行の候補はnull。切断時刻の行はpost-eventリンク力0、直前の内部力はlink_eventsに保存。区間の力・仕事は直前時間刻みに対応する。

保存CSV/イベントは`experiments/F007/verify.py`で毎行別式再計算する。hashは完全性の一部であり、単独で正しい数式・歴史的実行者・採用を証明しない。GitHub CIの実出自と別途照合する。環境の真値をセル側センサーに直結しない。


## F007 正式採用した保存契約の補足（2026-10-17）

`f007.v1`の上記列順・整数µJ・イベント意味論を**固定9条件の離散モデル整合性として限定採用**。各runとsuiteのCSV等は完成した私有ステージで監査してから、Linux `renameat2(RENAME_NOREPLACE)`で公開する。別の実行や他者の既存出力は上書きしない。入力不正、改変と再hash、異常終了時の部分公開を負例テストで確認。保存manifestの`origin.git_commit`はCIのmerge checkout、`origin.pr_head_sha`はPRソースHEAD。SHAは歴史的実行者の暗号署名ではない。通常例外時に自作業の出力をclean upするが、二宛先の停電原子性・fsync耐久性は保証しない。[限定採用判断](../findings/F007-validation.md#2026-10-17-f007-限定的正式採用--最新の研究判断)が優先。


## F008 提案：世界真値からセル別観測・推定・研究証拠へ【2026-10-17・未実装】

~~~mermaid
flowchart LR
  CFG["研究設定・理論参照"] --> W["F007 世界真値：研究者のみ"]
  W --> T["全状態ログ：既存F007を保持"]
  W --> P["局所射影：他セルを遮断"]
  P --> O["セルAの観測：自身のΔv / 指令 / 適用 / 電池"]
  O --> I["単体モデルとの差：局所の残差"]
  T --> V["研究評価器：接続の正解はここだけ"]
  I --> V
  V --> E["実験CSV・対照A〜F・manifest・SHA256"]
~~~

| 区分 | 提案上の情報 | 提供先・禁止情報 |
| --- | --- | --- |
| 世界真値 | A/B運動・リンク真値・リンク力・台帳 | 研究者専用。セルへの直接提供禁止 |
| セル側観測 | schema_version=f008.v0-proposal、cell_id、time_s、delta_v_m_s、dt_s、own_motor_command_n、own_motor_applied_n、own_battery_uj | 自分のみ。Bの状態、attached、ケース真値は**含めない** |
| 局所判定 | observed_accel、nominal_accel、residual、identifiable | 残差は未知負荷・未知外力の区別を保証しない。実行力0なら見かけ質量はnull |
| 研究証拠 | config、理論参照、観測と研究真値の別CSV、評価JSON、manifest、出自・hash・再現データ | 検証用。コントローラへ逆流させない |

提案列は**未確定**であり、実装前に列順・浮動小数点許容差・バージョンを凍結する。世界の真値とセルの観測が混同されていないことを、スキーマ監査と実際のログの両方で検証する。A〜Fの理論値はWolfram計算であり、**SOMA実験は未実施**。従来のF001〜F007データや採用済みAPIを変更しない。

[研究Issue #22](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/22) / [仮説・境界](../topics/F008-local-load-detection/SPEC.md) / [事前計画](../experiments/F008/PLAN.md) / [未実施の記録](../findings/F008-validation.md)。


## F008 v1 implementation candidate: local observation and evidence (2026-10-18, unadopted)

Source of researcher-only world truth: unchanged `f007.v1` saved
`config.json`, `states.csv`, `link_events.csv`, `ledger/events.csv`,
`manifest.json`. Before projecting any A-local data, the complete F007 saved
run is independently audited. The source is not overwritten.

`f008.local.v1` = a fixed allowlisted A-only observation, frozen `dataclass(slots=True)`
with exactly these eight input fields:

| Field | Unit | Semantic origin |
|---|---|---|
| `step_index` | int | self sample index, contiguous |
| `time_s` | s | local sample time |
| `dt_s` | s | local consecutive time difference |
| `v_prev_m_s` | m/s | prior A self velocity |
| `v_a_m_s` | m/s | current A self velocity |
| `motor_command_n` | N | A requested force, not automatically accepted |
| `motor_applied_n` | N | A actuator execution feedback, idealized local permission |
| `balance_a_uj` | µJ integer | A own battery balance |

Only these eight fields enter `soma/f008.detect`; it also receives nominal
single-cell mass (1 kg in frozen experiments), a given prior, **not** an
inferred linked-body mass. Neither `attached`, B state, link forces,
unknown external force, case identifier, researcher labels, nor trajectory
position may enter that function.

Per case `local.csv` has ordered columns:
`step_index,time_s,dt_s,v_prev_m_s,v_a_m_s,motor_command_n,motor_applied_n,balance_a_uj,observed_accel_m_s2,expected_accel_m_s2,residual_m_s2,status`.
Rows correspond to source steps 1..4; initial step 0 is the velocity baseline
and is not itself an acceleration interval. Status values:
`nominal` (|residual|<=1e-12 m/s²),
`anomaly` (larger residual), and
`not_excited` (applied force=0, prediction and residual serialized empty).
No body attachment classification or apparent mass is output.

Researcher-only `comparison.json`, case-local immutable F007 source runs and
`manifest.json` form the `f008.evidence.v1` suite; manifest maps every
artifact path to SHA256 and stores the trusted checkout identity. A separate
saved-data verifier re-reads F007 CSVs, checks all A fields and equations,
frozen A–E expectations, real linked/free truth and equal B/D A-local
histories. A full same-identity byte replay and tamper cases are required.
Case labels and world truth are used only on this **researcher evaluation**
path. This is a deliberately narrow synthetic-sensor contract, not proof of
hardware observability or exact performance on arbitrary dt/noisy samples.


### F008 source provenance and trust boundary — 2026-10-18 audit refinement

The outer `f008.evidence.v1` manifest's `origin` extends the unchanged
F007 `provenance()` snapshot with `f008_source_hashes` (mapping fixed relative
paths to SHA256). Required files are the F008 detector, suite runner, saved-data
verifier, F008 tests, CI workflow, SPEC, PLAN, F008 README/decision log/findings,
cross-feature architecture/data contracts, repository README and AGENTS.md.
`verify_suite(root, trusted_origin=...)` must compare both the saved origin to
an **external trusted checkout identity** and the recomputed checkout hash map
to the fixed source list; never use the saved manifest to supply its own trusted
identity. F007 independent saved-state audit and the artifact hashes are further
checks, not substitutes for independent human review or source provenance.

Agent local API is `detect(LocalObservation)` (8 allowed fields; no case or
topology). The researcher-side adapter `analyze(world_rows)` has access to
F007 truth for allowlisted projection; this is a software data contract, not
a protected operating-system or adversarial code-execution security boundary.
A researcher-only saved suite **contains** both the world source and local CSV;
do not distribute that entire researcher bundle to an agent as if it were a
private sensor payload. The numerical threshold `1e-12 m/s²` is frozen for
these deterministic controls, not a calibrated general sensor noise threshold.

### F008 independent audit hardening (2026-10-18)

The suite's `comparison.json` is **researcher-facing interpretive evidence**, not merely an opaque SHA-protected file. Independent verification must require the **complete frozen comparison contract** (schema, design reference, A/B/D/C predictions, confound warning, pending-review status) rather than trusting self-rehashed summary text. The outer `manifest.json` also fixes the exact A–E case list and evidence-source descriptor. `verify_suite` rejects deviations even if artifact SHA256 hashes are recalculated. These checks complement, but cannot replace, the row-by-row F007/F008 numerical oracle.

The two byte-replay output paths must be distinct **and non-nested** after canonical path resolution; overlapping paths are rejected before creating any output. This is failure/publication integrity, not an additional physical hypothesis or new cell capability.

### F008 limited-acceptance contract status (2026-10-18)

The researcher expressly approved the fixed `f008.local.v1` A-only offline observation and anomaly-residual contract for the preregistered deterministic F007 A–F controls. The immutable `comparison.json` field `science_status=model_result_pending_independent_review` describes the **original experimental output/provenance at creation**, not live researcher-adoption status: do not rewrite original artifacts to claim adoption. Formal adoption and later main merge are recorded separately in `findings/F008-validation.md` and PR #27. World truth remains researcher-only; local field allowlist and source SHA checks remain enforced. This does not certify a real-world observation sensor or identify links.


## F009 — 研究者専用運動量収支候補データ契約（2026-10-18・未実装）

New schema candidate: f009.momentum.v1, separate from frozen f007.v1. Input: schema_version, experiment_id, seed(null), dt_s, duration_s, masses A/B kg, x0 A/B m, v0 A/B m/s, attached, link length m, force_origin, drive_command_n, contact_enabled, traction_limit_n. Only preregistered A-F scope. Strict types and step grid.
Proposed ordered world CSV: step_index,time_s,x_a_m,x_b_m,v_a_m_s,v_b_m_s,external_force_a_n,external_force_b_n,internal_force_a_n,internal_force_b_n,ground_traction_n,ground_reaction_n,link_force_a_n,link_force_b_n,p_before_kg_m_s,p_after_kg_m_s,external_impulse_ns,momentum_residual_ns. Initial row has no interval force/impulse. p from mA*vA+mB*vB; external impulse h*(external_force_a_n+external_force_b_n), R=ΔP−J. Internal pair and link forces cancel. ground_reaction_n=−ground_traction_n, and zero when no contact. Ground reaction is researcher truth, not cell observation.
Proposed files: config.json, steps.csv, comparison.json, manifest.json with raw SHA and checkout source provenance. Exact source, column and error contract to freeze in implementation branch before results. Hash validity does not prove correct physics or performer identity. Independent verifier recalculates each row without importing production model. Cell A F008 API receives none of these world-truth fields. The 1D traction saturation model is not a full contact simulator.


### F009 implementation contract v1 candidate (2026-10-18, not adopted)

Implemented schema = f009.momentum.v1, source: soma/f009.py. Exactly the 18 ordered fields proposed above, with 5 rows/case (initial row and 4 intervals). Input is restricted to six full frozen configurations only; a different configuration is explicitly rejected rather than silently extrapolated. Ground traction is external force ON cells, while ground_reaction_n is the equal opposite on the environment; internal pair is never included in external_impulse_ns. For linked cells, constraint/link forces sum to zero. Simulation uses semi-implicit Euler, not continuously integrated displacement.

Per case config.json + steps.csv + manifest.json; root comparison.json and suite_manifest.json = 20 canonical files per generated root. Two roots are generated in private staging, independently audited, byte-compared and published without replacing pre-existing outputs. Publication of the two roots is **not crash-atomic**; ordinary exception on the second rename attempts to remove the first. Every manifest identifies source hashes for source/model/tests/CI/SPEC/PLAN/findings/diagrams/README/AGENTS. Source SHA must match the trusted checkout, and GitHub workflow/commit must be inspected separately for actual execution identity. Science status in raw comparison is immutable model_result_candidate_not_adopted, regardless of later researcher acceptance.

F009 output stays researcher-only and never alters f008.local.v1 or cell-local knowledge. The experiment tests a fixed idealized source-of-force distinction, not practical locomotion, friction dynamics, electrical expenditure or morphology advantage.

## F010 proposed contracts — local-response multi-probe (2026-10-19, **design only**)

Researcher configuration: fixed A-D group definitions and E battery-negative; each group contains three independently initialized **F007 v1** run inputs with motor command `2,1,0.5 N`; unknown external A force and true attachment are **researcher-only**. `seed=null`; `dt_s=.25`, duration `1s`. No adopted schema is modified.

Estimator input proposal: ordered `tuple[tuple[soma.f008.LocalObservation, ...], ...]`, each inner tuple contains strictly four time-ordered A-only steps, same applied motor force, time 0.25..1 s, velocity prior beginning at 0; different independent force trials. No labels, attached/B fields, unknown external force, full configuration, ground contact, nor observer-free world data permitted. Local input fields are `step_index,time_s,dt_s,v_prev_m_s,v_a_m_s,motor_command_n,motor_applied_n,balance_a_uj`. The trial grouping is the researcher's offline aggregation and does not itself imply A has a clocked experimentation policy.

Output proposal: `f010.signature.v1` with `alpha_per_kg, beta_m_s2, holdout_residual_m_s2, response_signature, status, topology_verified=false`. The response signature is not a causal attachment label. A group with zero applied force or too few distinct force levels is `inconclusive`. Small exact-rational case tolerance `1e-12` is not noise calibration. The evaluator only maps raw F007 saved `states.csv` through strict F008 projection and compares it to frozen Wolfram values. Repository artifacts to include local trial CSVs, `comparison.json`, `manifest.json`, immutable F007 source evidence, trusted-checkout source SHA, and byte-identical replay; exact column sequence to be finalized before implementation.

### F010 implementation-candidate data contract (2026-10-19; NOT ADOPTED)

`f010.signature.v1` estimation input: `tuple` of precisely three tuples, each containing exactly four typed `soma.f008.LocalObservation` objects (`step_index,time_s,dt_s,v_prev_m_s,v_a_m_s,motor_command_n,motor_applied_n,balance_a_uj`). Times 0.25/0.5/0.75/1s, h=.25, prior vA=0, contiguous velocities, applied force constant in each trial and across trials equal to distinct `2,1,.5 N`; no full world records. Estimator returns keys `schema_version,status,reason,alpha_per_kg,beta_m_s2,holdout_residual_m_s2,response_signature,topology_verified`. Response signatures `inertia_like,offset_like,nominal_like,unclassified` are model-response descriptions **not link states**. Motor rejection/no distinct force ⇒ `inconclusive` and null estimates; nonlinear holdout ⇒ `non_affine_holdout` with residual (no topology). Third force is reserved holdout, not used to fit.

Researcher-only output `f010.evidence.v1`: `A-linked,B-constant,C-adaptive,D-free,E-empty` each with `u2,u1,u05` independent F007 run folders (untouched adopted F007 schemas and manifests) and one F008 `local.csv` with adopted `COLUMNS` 12-field ordering. Root `comparison.json` maps five frozen groups to estimator results, with an explicit non-identifiability statement; `manifest.json` stores trusted `origin.f007` and `origin.f010_source_hashes`, strict artifacts digest map, frozen case order. Independent `experiments/F010/verify.py` parses raw saved files, checks SHA against actual checkout, invokes the adopted F007 saved oracle and separately recomputes every expected F010 trajectory/local field with `Fraction`, compares full A=C local byte equality and summary semantics. An attacker who controls arbitrary Python can bypass these checks; source SHA is NOT signer/authentication. Twin destinations are one-by-one published, not crash-atomic across both.

### F010 limited-adoption decision (2026-10-19)

The implementation-candidate `f010.signature.v1` / `f010.evidence.v1` contracts above are accepted **only for the frozen 1D offline A-local three-input tests**, after enforcing per-step equality of `motor_command_n` and `motor_applied_n` (otherwise `inconclusive`) and adding exception-safe first-directory rollback if the second evidence publication fails. Python 3.11/3.12 hardened [CI #39255300092](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39255300092) validated the new negative tests, full 107-file replay and other F001–F010 regressions. Preregistered values and the raw evidence's immutable at-production candidate label are unchanged; the dated findings records formal acceptance. No claim of crash/power-loss transaction atomicity, generic identification or noisy real-world validity.


## F011 proposed data contract — 2026-10-20, **DESIGN ONLY / NO RUN**

Scope/refs: [Issue #34](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/34), [SPEC](../topics/F011-grounded-internal-drive/SPEC.md), [PLAN](../experiments/F011/PLAN.md). Existing F001–F010 schemas remain immutable.

- `f011.config.v1`: `case_id` among frozen A–E, `dt_s` one of {.01,.005,.0025}, `duration_s=9.6`, `m_kg=1`, `g_m_s2=9.81`, `x_a0_m=-.25`, `x_b0_m=.25`, `v_a0_m_s=v_b0_m_s=0`, `rest_m=.5`, `k_n_m=20`, `amplitude_n=1` or E=0, `period_s=1.2`, `mu_plus`, `mu_minus`, `stroke_min_m=.2`, `stroke_max_m=.8`, `seed=null`. Reject not-in-frozen-config inputs rather than silently support unvalidated arbitrary physics.
- `f011.states.v1` / `states.csv`: ordered step/time, `x_a_m,x_b_m,v_a_m_s,v_b_m_s,r_m,x_cm_m,internal_n,ground_a_n,ground_b_n,ground_work_j,motor_work_j,kinetic_j,spring_j,impulse_residual_ns,energy_defect_j,expected_defect_j`. Initial row has null interval-only fields. Exact ordered fields are fixed in implementation **before** measurements; when modified, bump version and preregister before running.
- `f011.evidence.v1`: per-case `config.json`, `states.csv`, `manifest.json` (SHA256 each source/data and checkout-origin metadata); root `comparison.json`, `manifest.json`, and reproducibility/CI record. Save negative results, not only positives. All measurements in SI; `ground_force` is world truth (not cell observation), energy residual explicitly accounts for semi-implicit discretization.
- Integrity: independent saved CSV verification without calling production simulator; same frozen config and exact raw outputs compare deterministically; missing/tampered/rehashed-science claims rejected; source-SHA is not cryptographic proof of author identity; crash-atomic publication across independent directories not claimed.
- **No new cell-local API or autonomous controller**. Only researcher reads `states.csv` or friction parameters; any future local observations require a separate allowlist and research question.


### F011 implementation candidate raw schema (2026-10-20; not adopted)

`soma/f011.py` defines the fixed order of 18 `states.csv` columns:
`step,time_s,x_a_m,x_b_m,v_a_m_s,v_b_m_s,r_m,x_cm_m,internal_n,ground_a_n,ground_b_n,ground_work_j,motor_work_j,kinetic_j,spring_j,impulse_residual_ns,energy_defect_j,expected_defect_j`. Initial row retains blank interval-only fields. World truth only, no agent knowledge. All SI. Effective ground force is impulse/dt; this is a numerical passive Coulomb proximal law, not measured contact.

`f011.comparison.v1` stores complete vs stroke_inconclusive for each of 15 cases, fixed H1–H4 status and C↔D mirror metrics. `f011.evidence.v1` stores canonical artifact and source hashes. Check `experiments/F011/verify.py` independent arithmetic/semantic (including rehashed false science) and the reproducibility guide; no data loss or smoothing at stroke violation, raw valid prefix preserved. Separate artifact directories are normal-exception rolled back, but power-loss two-directory atomicity is not certified.

### F011 post-experiment evidence-contract scope decision (2026-10-20)

`f011.config.v1`, `f011.states.v1`, `f011.comparison.v1` and `f011.evidence.v1` schemas remain the **unchanged** frozen implementation contracts. Formal **limited** adoption covers fixed-model C/D/B/E trace integrity, reproducibility and control results only. Full-duration A:no_contact remains `stroke_inconclusive` at ~2.1s due to the original 0.8m gate; no 9.6s complete A trace or all-controls-pass status exists, despite separate analytic COM conservation and preserved valid-prefix support. Owner acceptance is an **explicit retrospective gate exception**, not a rewrite of `comparison.json`, a version bump, a reclassification of historical negative evidence, or proof of physical contact/autonomy. Raw states continue to be researcher-only world truth. See [SPEC scope decision](../topics/F011-grounded-internal-drive/SPEC.md) and [F011 evidence/findings](../findings/F011-validation.md).


## F012 proposal: finite positive-work ground-drive data contract (2026-10-20; UNIMPLEMENTED)

Version proposal `f012.energy.v1`, exclusively researcher-facing. Inputs: strict frozen `case_id` B/C/D/E, `budget_uj` in [0,1000000,3000000,10000000], `dt_s` in [.01,.005,.0025], `seed=null`. Implicit fixed F011 m=1kg, xA/B=-.25/+ .25m, T=9.6s, spring 20N/m rest .5m and stroke [.2,.8]m; active internal u±1N / E zero, directional ground law coefficients listed in SPEC. Unknown keys invalid.

Planned `states.csv` order to freeze before implementation: `step,time_s,x_a_m,x_b_m,v_a_m_s,v_b_m_s,r_m,x_cm_m,motor_command_n,motor_applied_n,motor_candidate_positive_j,motor_positive_j,motor_signed_j,spent_uj,balance_uj,decision,ground_a_n,ground_b_n,ground_work_j,kinetic_j,spring_j,impulse_residual_ns,energy_defect_j,expected_defect_j`. Initial row (step 0) has no interval values; integer budget retained. Mechanically signed work is F011 end-velocity discrete convention; positive work is linearly interpolated relative-velocity integral; ceil(positive work *1e6) per accepted step is bounded by positive integer microjoules. Never call this experimentally measured electricity. Unaccepted step recalculates passive model with zero motor.

Planned suite: `config.json`, `states.csv` per frozen case; root `comparison.json`, `manifest.json`, `source` hashes and replay, explicit stroke-failure prefixes. World truth may be used by researcher/oracle only. No new cell-local observation contract. Proposed verifier must recompute each row and all science-summary metrics, not trust a rehashed comparison JSON or trust the artifact's own claimed source SHA.

## F012 implemented candidate — `f012.energy.v1` (2026-10-20, not adopted)

Actual `soma/f012.py` controls: `Config(case_id,budget_uj,dt_s)` validates exactly `B-isotropic/C-directional/D-mirror/E-no-drive`, budgets 0,1000000,3000000,10000000 integer µJ, dt=.01/.005/.0025 float, fixed 9.6s. Strict config serialized with `schema_version`, `seed=null`, masses/spring/ground/friction/stroke/actuator constants and charge rule. The source file is separate from all accepted F001–F011 interfaces.

Output researcher-only ordered `states.csv`:
```text
step,time_s,x_a_m,x_b_m,v_a_m_s,v_b_m_s,r_m,x_cm_m,motor_command_n,motor_applied_n,motor_candidate_positive_j,motor_positive_j,motor_signed_j,spent_uj,balance_uj,decision,ground_a_n,ground_b_n,ground_work_j,kinetic_j,spring_j,impulse_residual_ns,energy_defect_j,expected_defect_j
```
The initial row lacks interval force/work/gate entries; later rows have valid finite values. `decision` in `zero_command/zero_balance/accepted_positive_work/accepted_nonpositive_work/insufficient_balance`. Full exact integer `budget_uj = sum(spent_uj)+final_balance_uj`. Signed motor work uses F011's endpoint velocity convention; positive ideal mechanical work uses F005's **linearly interpolated relative velocity**; rejected candidate incurs **no** charge, and passive mechanics are independently recomputed.

Saved `48 x (config.json,states.csv)`, plus `comparison.json`, `manifest.json`, two independent byte-identical output roots, Python3.11/3.12 CI artifact ZIPs. SHA256 manifest lists raw files and source-checkout hashes; independent verifier uses trusted checkout not the saved manifest's self-asserted origin, recomputes every row and every summary field and checks C/D cost mirror. It is not cryptographic author identity nor real electricity evidence. No F008/F010 knowledge leak. Archived artifact availability is time-limited by GitHub.

## 2026-10-20 F012 data-contract decision (post-audit)

The researcher-delegated limited adoption covers **only** `f012.energy.v1` frozen B/C/D/E × budgets × dts, ideal positive-work charge, experimental CSV and evidence verification. Every saved B COM and E static row and matched C/D reflected xA/xB, r, COM, motor command, applied motor, balance and per-step charge are audited at all three dt values and every budget; no relaxation of frozen thresholds. File artifact retention is provider-bounded; reproduce with `python -m experiments.F012.run_suite` using a trusted checkout of the recorded PR/main commit. It is not crash-atomic publication across two destination roots, and this limitation does not imply real electrical energy consumption. See F012 Issue #38/PR #40 for merged source SHA and post-merge checks.


## F013 smooth passive-friction experiment — 2026-10-20 IMPLEMENTATION CANDIDATE, NOT ADOPTED

Independent version `f013.config.v1`: case in B-isotropic/C-directional/D-mirror/E-no-drive; `eps_m_s` in {.02,.005,.001} m/s; `dt_s` in {.01,.005,.0025} s, fixed initial x=(-.25,+.25)m, v=(0,0)m/s, m=1kg per cell, L=.5m, k=20N/m, g=9.81m/s², u=±1N each 0.6s except E=0, 9.6s total, valid r [.2,.8]m; seed=null. Inputs restricted to 36 preregistered cases, no post-hoc parameter scan.

`f013.states.v1`: ordered CSV columns exactly:
```text
step,time_s,x_a_m,x_b_m,v_a_m_s,v_b_m_s,r_m,x_cm_m,motor_n,ground_a_n,ground_b_n,ground_work_j,motor_work_j,kinetic_j,spring_j,impulse_residual_ns,energy_defect_j,expected_defect_j
```
Initial row contains no interval force/work, but includes energy state. Every complete or invalid-prefix condition stores `config.json` + `states.csv`; output `f013.comparison.v1` includes primary period displacement (m), recurrence, per-epsilon dt results, declared H13 labels and F011 reference value. `f013.evidence.v1` manifest hashes raw files and trusted checkout source/spec/plan/runner/verifier; it is SHA provenance, not trusted-actor signing. Saved verifier independently checks the contact *implicit equation*, Newtonian momentum, semi-implicit energy defect, every-row mirror, frozen control, summaries and tamper/rehash. Independent same-byte replay is required. World-state CSV and coefficients are researcher-only; NO cell-local F013 API or real sensor.


### Post-registration F013 independent integration audit (implementation, not changed hypothesis)

`ode_audit.json`, schema `f013.postregistered_ode_audit.v1`, is an additional independent coupled 4D explicit RK4 ODE solution at h=.001 and .0005s for B/C/D/E × eps=.02/.005/.001m/s (24 diagnostic runs). Each `cases[case/eps-...]` object contains both methods' `center_final_m`, `last_period_m`, `penultimate_period_m`, `last_period_r_return_m`, `min_r_m`, `max_r_m`, plus `relative_to_implicit_euler_m` at the 0.0005s reference. The verifier recalculates all 24 diagnostic runs independently and rejects falsified summaries even if file hashes are updated. This does **not** modify frozen H13a/b thresholds, or establish physical contact correctness. The force is continuous C0 but not globally C1 (direction-specific one-sided slope at zero). `f013.evidence.v1` provenance source hashes now additionally bind `experiments/F013/ode_audit.py`.
