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
