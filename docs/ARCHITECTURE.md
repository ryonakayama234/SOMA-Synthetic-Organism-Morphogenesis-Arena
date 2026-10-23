---
id: ARCHITECTURE
title: システム図鑑
kind: diagram
status: conceptual
updated: 2026-10-16
related: [DATA, F001, F002, F003]
---

# システム図鑑（実装済み・提案の境界を明記）

全体図は**概念上の境界**。各機能の節で実装済み・未実装を区別し、実験結果を示す図と混同しない。

## 研究の主従と身体的情報（2026-10-21、概念仮説・未実装）

**最上位の問いは、独立した個体に集合・結合・離脱の実利が生じ、身体が形成・維持される条件である。** 通信の発達は身体創発を支える可能性のある任意の下位現象であり、研究目標そのものを通信へ置き換えない。[研究憲章](PROJECT.md) / [長期Issue #51](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/51)。

~~~mermaid
flowchart TD
  E["物理環境・資源制約・局所の運動コスト"] --> U["独立個体の局所センサーと行動"]
  U --> D{"結合・近接・分離の実利"}
  D -->|"環境により有利"| B["集合・結合と持続性・能力の変化"]
  D -->|"有利でない"| I["単独／非結合／離脱"]
  B --> P["接触・張力・振動・変形・行動／生存の痕跡"]
  P --> C["受動的な連動／他個体による手掛かりの利用"]
  C -.->|"相互適応が起きる場合だけ"| S["能動的な信号／解読の成立（任意）"]
  S -.-> B
  C --> O["研究者のみが介入比較・評価"]
  I --> O
  B --> O
~~~

この図は**研究で問う因果候補の分類**であり、現行ソフトウェアに学習器・送信ポート・集団選択が存在することを意味しない。個体の身体的振る舞いが他者へ物理的影響を及ぼすこと、他者がそれを情報として利用すること、発信行動がその効果に合わせて適応することを別々に検証する。明示的packetも1bitも必須ではない。結合・送信自体へ報酬を与えず、単体継続や非通信も有効な対照結果とする。研究者側の世界真値は各セルへ直接見せない。

F014–F016は事前定義されたbit・固定制御に関する**限定的対照研究**であり、上図の集合誘因・身体創発・通信創発を実装・実証したものではない。F007の外部有効力とF011–F013の内部駆動物理を無検証で混ぜない。

## 全体図
~~~mermaid
flowchart TB
  R["研究者・実験設定\n問い／仮説／条件"] --> W["環境と物理モデル\n真の状態を持つ"]
  W --> S["局所センサー\nセルに見える情報だけ"]
  S --> C["各セルの行動選択\n初期は固定／簡単なルール"]
  C --> A["アクチュエータへの命令"]
  A --> W
  W --> L["記録器\n真の状態と実験ログ"]
  L --> V["グラフ／再生"]
  V --> J["研究者が解釈し次の仮説を立てる"]
  J -.-> R
~~~

## 最も重要な情報境界
~~~mermaid
flowchart LR
  subgraph TRUTH["環境側：真の状態（正解）"]
    X["セル全体の位置・速度\n接続グラフ／内部力\n残量／資源分布"]
  end
  subgraph OBS["各セル側：自分が観測できる範囲"]
    Y["自分の局所状態\n感覚値／通信された値"]
    Z["行動決定器"]
    Y --> Z
  end
  X -->|センサーによる射影のみ| Y
  Z -->|行動命令のみ| X
  X -->|研究用には全状態を見せる| K["評価・可視化"]
~~~

**禁止事項：** 将来の未知の身体学習を壊さないため、細胞の制御器に環境側の完全な接続グラフを渡さない。実装上のデバッグ情報と細胞の観測情報は別の入口にする。

## F001だけを実装するときの図
~~~mermaid
flowchart LR
  U["入力：力 F\n設定：質量 m・抵抗係数 gamma・刻み dt"] --> P["一段階の運動計算"]
  P --> X["出力：位置 x・速度 v"]
  X --> LOG["CSVの記録"]
  LOG --> G["距離・速度グラフ"]
~~~

次の実験で追加される要素（接続、電源、学習）は今は描いても**実装しない**。

## 設計しないと危険な点
- 物理エンジンの真の状態と、セルの学習用観測を混ぜると「自己発見」の実験が成立しなくなる。
- 時間刻み・長さ・質量・力の単位を曖昧にすると、結果が再現できない。
- 運動に伴うエネルギーの消費は F002 で別に検証する。F001で黙って消費を導入しない。

[データの約束](DATA_CONTRACTS.md) / [研究の進め方](RESEARCH_PROCESS.md)

## 実装状況（2026-10-13）
- F001の `設定 → 運動計算 → 位置と速度のCSV → グラフ／比較` は `soma/f001.py` と `experiments/F001/run_suite.py` に実装済み。
- 局所センサー・セルの行動選択・機械結合は未実装。エネルギー台帳はF002として実装済みだが、運動とは未連携。
- [F001の実験ノート](../findings/F001-validation.md)

## F002 実装後のシステム図【Python実装・数値検証済み】

~~~mermaid
flowchart LR
  SET["config.json\n初期電力量・イベント列"] --> L["F002 台帳\n整数 µJ を原子的に更新"]
  L --> ST["セル別残量\ncapacity / balance"]
  L --> TX["供給・支出・移送損失\n収支残差"]
  ST --> LOG["events.csv / balances.csv"]
  TX --> LOG
  LOG --> EVAL["グラフ energy.svg\n検証 manifest.json"]
  F1["F001: 1D運動（既存）"] -. "電池との因果関係未定義・接続しない" .-> L
  F3["F003: 機械結合（将来）"] -. "物理結合は別課題" .-> L
~~~

F002での `transfer` は**数値台帳上の取引**であり、力学的な結合・電線・電力供給ポートを意味しない。研究者・物理環境の真の状態と、将来のセルが局所センサーで取得できる状態は分ける。F002の台帳・トランザクション・CSV・manifest・可視化部分は `soma/f002.py` と `experiments/F002/run_suite.py` で実装済み。F001の外部力からF002の蓄電量への結合と、F003の機械結合は未実装。図は実装境界を明示する。

[仕様案](../topics/F002-energy-ledger/SPEC.md) / [入力出力とデータ構造](DATA_CONTRACTS.md)。

### コードの責務分割（F002）

- `Cell`：個体ID、最大容量、現在残量（immutable）。
- `LedgerState`：セル群、初期残量合計、外部供給・支出・移送損失の累積、取引番号。構築時に残差0を検証。
- `Event`/`apply_event`：取得・支出・数値移送。入力を検査し、成功したときだけ新しいstateを返す。失敗時に元stateを変更しない。
- `save_run`：設定・イベント・セル別残量・SVG・manifestを新しい出力先へ保存。
- `experiments.F002.run_suite`：A〜Fの対照実験とEの13件の拒否監査。出力をCI artifactへ保管。

[実験記録](../findings/F002-validation.md) / [コード](../soma/f002.py)。

### レビュー #6 後の保存証拠の検査
取引 → 中間残量の全履歴（balances.csv）→ CSVに対応するイベント推移・台帳内訳（energy.svg）→ manifest（Git SHA、dirty判定、モジュールSHA256、artifact SHA256）の順に検証できる。なお、グラフの間引きは表示だけであり、CSVは間引かない。

### F002の再現性証拠データフロー
`experiments.F002.run_suite` → F-bulkとF-splitの**各同一設定を2回実行** → 元run・replay runそれぞれにconfig／events／balances／SVG／manifest → 5ファイルずつのバイト一致とSHA256 → `comparison.json.f_replay_checks`に保存。新規出力ディレクトリのみを使用し、F001運動モデルには接続しない。

### 出自取得と保存の順序（2026-10-15）

スイート開始 → 出力前のGit SHA/dirtyを一度取得 → 各runとreplayの`save_run(..., provenance=...)` → 同一開始状態を8 manifestへ保存。単独runは自身で保存前に取得する。未追跡の実験出力によるdirty判定の変化を防ぐため、開始時の出自取得をスイートの責務とする。台帳の演算やF001との境界は変わらない。

### 条件生成・判定コードの保存（2026-10-15）

スイート開始 → Git出自とsuiteソースを取得 → `suite_source.py`を証拠へ保存 → A〜Fと再実行 → `comparison.json`へsuite SHA256と保存先を記録。台帳モジュールのhashだけでなく、条件生成・事前予測の照合を担当するスクリプトも識別する。

## F003の設計追加（2026-10-14、PRで審査中・未実装）
「二つのセルが理想的な機械リンクで拘束される」能力のみを新設する案。F002のエネルギー台帳とは独立させる。

~~~mermaid
flowchart LR
  EXT["研究用の外力入力 F_A / F_B"] --> W["世界：2セルの真の運動状態"]
  W --> G{"リンクON?"}
  G -->|OFF| U["セルごとにF001運動式を適用"]
  G -->|ON| C["合成質量・共通速度で更新\n内部力は作用反作用"]
  U --> W
  C --> W
  W --> O["研究専用ロガー\n位置・速度・リンク真値・内部力"]
  O --> V["単独 / 結合 / 切断の対照比較"]
~~~

これは**中央制御器の構築ではない**。実験者が力とリンク状態を指定する最小モデルで、セル自身には完全な接続グラフを提供しない。ロガーは世界の真値を見てよいが、将来の局所センサーからは明確に隔離する。

- 力学：非結合の各セル＝F001式。結合中は2セル合成質量の一次元運動（等速度・一定距離）。
- 拘束：接続時に初期距離・速度が整合している場合だけ許可。位置や速度を飛ばす瞬間修正はしない。
- 切断：それまでの位置・速度をそのまま引き継いで独立運動へ戻す。
- 非目標：2D/3D、接触・衝突、実機コネクタ、通信、電力移送、AI、創発。

[詳しいF003仕様とシステム図](../topics/F003-attachment/SPEC.md) / [F003の対照実験計画](../experiments/F003/PLAN.md)。
F002はmainに統合済み。F003は機械結合のみ提案し、F002台帳との接続は未実装のまま維持。

## F003 イベント時刻の状態遷移（2026-10-15、事前設計・未実装）

~~~mermaid
flowchart TD
  C["設定JSON"] --> V{"開始前検査"}
  V -->|拒否| R["suite: rejections.json"]
  V -->|受理| A["結合状態に従い区間の運動を更新"]
  A --> B["時刻tの位置・速度を確定"]
  B --> D{"tに切断イベント？"}
  D -->|yes| E["位置・速度を変えずON→OFF"]
  D -->|no| S["状態を保持"]
  E --> L["post-event states.csv／before-after events.csv"]
  S --> L
  L --> N["次の時間区間へ"]
~~~

切断時刻のstates.csvはイベント反映後1行。切断前後の位置・速度はevents.csvで直接照合する。拒否入力は正常runのイベントではない。すべて将来F003の設計で、現在の実装はF001/F002まで。

### F003 設計監査の補足（2026-10-15）
入力検査→有限な世界状態・派生量→新規出力の保存→CSV/イベント読み戻し→独立離散参照による全ゲート照合、という責務を分離する。数値表現不能は保存前の拒否経路へ流し、内部力や重心のinfを正常な世界真値と扱わない。仕様・許容差は維持し、実装・観測は後続PR #8で検証する。

## F003 実装候補（2026-10-15）

下図は実装ブランチ `feat/F003-1d-coupling-validation-20261015` の責務とデータフロー。**mainへの統合前**であり、F002との物理結線・局所知覚・AI制御は存在しない。

~~~mermaid
flowchart TD
  SET["config.json: 2セルと結合/切断設定"] --> VALID{"入力検証: dt格子/距離/初速"}
  VALID -->|不正| REJ["suiteのrejections.json"]
  VALID -->|正常| W["世界真値 (A,B,リンク状態)"]
  W --> G{"attached?"}
  G -->|yes| COUPLED["合成質量+合計外力 -> F001 step"]
  G -->|no| FREE["A/BそれぞれF001 step"]
  COUPLED --> EVENT{"時刻kで切断?"}
  FREE --> EVENT
  EVENT -->|yes| POST["位置/速度は不変、リンクだけOFF"]
  EVENT -->|no| POST
  POST --> LOG["states.csv (post-event) / events.csv (before/after)"]
  LOG --> EVAL["comparison.json + motion.svg"]
  EVAL --> PROV["manifest.json: Git SHA / ソースhash / artifacts SHA"]
  F2["F002：エネルギー台帳"] -. "物理的に未接続" .-> W
~~~

`Config.from_dict` が不正入力を実行前に拒否。`simulate` は世界の真値の時系列とイベントを返す。`save_run` は新しいフォルダにのみ保存する。`experiments.F003.run_suite` は開始時のGit出自と実験スクリプトhashを全runで共有し、生ログと再実行のバイト一致を判定する。**これらの真値をセル自身へ渡す制御器は実装しない。**

[事前登録SPEC](../topics/F003-attachment/SPEC.md) / [実装テスト](../tests/test_f003.py) / [検証台帳](../findings/F003-validation.md)。

## F003 GitHub CI 履歴（監査修正前・2026-10-15）

- 実装HEAD: 1512206596ca8939705e6e1ab603e9aa1bbd626d
- F003 Actions: https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38731190546 — success。Python 3.11で合計44テスト（F001 17、F002 16、F003 11）合格。
- A〜F正常7run、不正入力8件を拒否、B同条件再実行の生バイト一致。artifact: F003-A-F-evidence（ID 11970235937）。
- F001既存ワークフロー: https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38731190562 — success。
- F002既存ワークフロー: https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38731190549 — success。
- 以上は1D理想モデル・ソフトウェアの整合性を示す。実機による結合、エネルギー相互作用、身体創発を示さない。
- 独立第三者の監査は未了。PR #7の設計レビューと、PR #8の正式採用判断を区別する。

## F003 監査修正後の証拠検証（2026-10-15、実装候補）
~~~mermaid
flowchart TD
  C["設定・数値表現可能性・厳密時間格子"] --> W["F001 stepを再利用する世界更新"]
  W --> V["全状態・内部力・重心の有限性検査"]
  V --> S["CSV・イベント・SVGを新規保存"]
  S --> R["保存済みCSV・イベントを読み戻す"]
  R --> O["stepを呼ばない独立離散オラクル"]
  O --> G["全A〜Fゲート・最大誤差・拒否証拠SHA"]
  G --> P["比較JSONを含む全スイート再実行一致"]
~~~
不正状態は保存前に拒否する。スイートは別のsimulate結果を合否根拠にしない。F001依存モジュールSHAも開始時出自に保存する。F002との物理結線とセル制御器は対象外。監査前の未実装・未監査表記は設計時点の履歴。

### F003の採用判断（2026-10-15）
監査修正・50テスト・A〜F・再現性・CI検証を経て、記載した1D二セル理想リンクの実装を採用する。設計#7はmain統合済み、実装の統合はPR #8で追跡。既存の図・スキーマ・観測境界は不変で、候補・未統合表記は過去時点の履歴。

## F004：内部駆動と電池の因果接続【2026-10-15 設計提案・未実装】

F001の運動とF002の整数µJ台帳の間に、**一セルの内部モーター仕事**だけを扱う薄い接続層を追加する案。F003の二セル理想リンクはmainに存在するが、F004とは**未接続**。

~~~mermaid
flowchart TD
  CONF["設定：モーター指令 u、外力 f_ext、初期残高"] --> CAND["F004：F001による候補1Dステップ"]
  CAND --> W["台形速度による内部機械仕事 W_motor"]
  W --> G{"F002の残高は足りるか"}
  G -->|足りる| YES["内部＋外力で運動／spendをF002へ記帳"]
  G -->|足りない| NO["内部力0／外力のみでF001を再計算"]
  YES --> WORLD["世界の真値：位置・速度・残高"]
  NO --> WORLD
  WORLD --> LOG["研究ロガー：states／spendイベント／manifest"]
  LOG --> GATE["独立予測／不変条件／対照A〜F／図"]
  F003["F003：2セル機械結合（既存）"] -. "F004の範囲外" .-> CAND
  WORLD -. "セルの局所観測へ直結しない" .-> SENSOR["将来のセンサーAPI（未実装）"]
~~~

役割：F001は運動更新、F002は残高・会計不変条件、F004はモーター仕事と実行可否の調停のみを担当。**外力は電池消費対象ではない**。研究側ロガーは世界の真値を知るが、セルの意思決定器には真値を渡さない。モーターの実機効率、待機電力、熱、回生、二セル協調は未実装。

[仕様・仮説](../topics/F004-actuation-energy/SPEC.md) / [A〜F計画](../experiments/F004/PLAN.md) / [未実施の記録](../findings/F004-validation.md) / [Issue #9](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/9)。

### F004 2026-10-16 設計ゲート修正（未実装）
~~~mermaid
flowchart TD
 S["世界状態とF002電池残量"] --> B{"残量が0？"}
 B -->|Yes| Z["モーター力0／外力だけをF001.stepへ"]
 B -->|No| C["モーター+外力でF001候補運動を仮計算"]
 C --> W["binary64正仕事をceilしてµJ費用確定"]
 W --> E{"費用が残量以下か"}
 E -->|Yes| Y["候補運動とF002 spendを一体採用（費用0ならイベントなし）"]
 E -->|No| Z
 Y --> V["有限値・原子的確定の検査"]
 Z --> V
 V --> L["世界真値ログ・台帳イベント・Git出自"]
 L --> O["独立の全時系列オラクルと対照比較"]
~~~
反例：残量0でu=+1 N、外力=-1 N、初速0の候補仕事は0だが、**内部モーター力は0にする**。電池残量0の判定は費用計算より先に置く。これは設計修正であり、現時点の動作する実装ではない。

## F004 実装候補（2026-10-16／PR #11、正式採用前）

~~~mermaid
flowchart TD
 C["設定: f004.v1、全コンストラクタで共通検証"] --> V{"有限値・範囲・float変換前後の格子一致"}
 V -->|reject| X["何も保存しない・ValueError"]
 V -->|valid| W["世界真値: Motion(x,v) + F002 LedgerState(A)"]
 W --> B{"残量=0？"}
 B -->|Yes| Z["内部力0でF001.stepに外力のみ"]
 B -->|No| T["F001.stepで候補運動を仮計算"]
 T --> E["台形速度による理想正仕事をceil(µJ)"]
 E --> G{"候補費用 <= 残量？"}
 G -->|Yes| Y["候補運動 + F002 spend（費用0はeventなし）"]
 G -->|No| Z
 Y --> A["有限派生量検査、物理+台帳の不可分commit"]
 Z --> A
 A --> S["states.csv: 各ステップの世界真値"]
 A --> L["ledger/events.csv: F002で受理した支出のみ"]
 S --> O["初期行を含む独立CSV参照・必須4成果物のhash照合"]
 L --> O
 O --> M["comparison.json、SHA付きmanifest、motion_energy.svg"]
 M -.-> N["後続研究: F003結合や局所センサーは未接続"]
~~~

実装責務：\`soma/f001.py\`＝運動更新、\`soma/f002.py\`＝エネルギー台帳、\`soma/f004.py\`＝エネルギーに依存する内部駆動の採否と不可分step。\`experiments/F004/run_suite.py\`＝**CSVを読み戻す**独立計算・比較。内部エージェントへの世界全体情報の付与、F003との統合、実電池・実モーターのモデル化はしない。初回CI 68テスト合格／10対照／16拒否は実装候補の範囲のみ。

### PR #11 独立視点の実装監査修正（2026-10-16）
Configの検証は`__post_init__`に集約し、JSON/dict、直接生成、`dataclasses.replace`で同じ条件を課す。生入力とfloat正規化後の十進有理数による時間比が同じ整数でなければ保存前に拒否する。SVGは時間と状態を先に正規化してから座標へ変換し、有限状態からの表示計算のoverflowを回避する。保存検証では4成果物の完全なhash一覧と、初期行の全仕事・運動エネルギー差・残差0を必須にする。物理更新・費用式・F001〜F003のAPIは変更しない。

### F004 採用決定（2026-10-16）
ユーザーの指示で上記F004の離散理想モデルを正式採用。設計PR #10はmain統合済み、実装と採用記録はPR #11で統合する。既存の実装図・世界真値と観測の境界は維持。物理コードと費用式は変更なし。保持/待機電力、区間内の速度反転時の正負仕事相殺、dt依存の切上げ差を制限として記録し、自律制御・実機への適用前に別途設計する。[採用記録](../findings/F004-validation.md#2026-10-16-採用判断と統合)。


## F005：速度反転時の正仕事積算【2026-10-16 研究提案・未実装】

**責務境界**：F001（離散運動）・F002（整数µJ台帳）・F004（既存の符号付き区間仕事と残高制約）は採用済み。F005はF004の既知の「反転区間の無料再加速」を防ぐ**代替費用計算の候補**。F003の二セルリンクは接続しない。**以下の図のF005部分は未実装**。

~~~mermaid
flowchart TD
  C["設定 config.json：1セル/力/速度/残高"] --> V{"F005入力事前検査"}
  V -->|妥当| A["F001候補運動：v0→v1（世界真値）"]
  V -->|不正| RJ["rejections.json（正常runは作らない）"]
  A --> SG["符号付き仕事 W_signed：機械収支用"]
  A --> PG["F005提案・未実装：線形速度を区間内で補間し正仕事 W_plusを積分"]
  PG --> B{"F002電池：残高 > 0 かつ費用を賄えるか"}
  B -->|yes| APPLY["内部力+外力を採用／F002 spend（正額時のみ）"]
  B -->|no| EXT["モーター力0でF001を再計算／外力は残す"]
  APPLY --> T["states.csv：世界真値（signed/positive/spent/残高）"]
  EXT --> T
  SG --> T
  APPLY --> L["ledger/events.csv：受理支出だけ"]
  T --> J["comparison.json／motion_energy.svg：独立照合・表示"]
  L --> J
  C --> M["manifest.json：入力・Git/ソース・成果物SHA256"]
  J --> M
~~~

- **新しい計量** `W_plus = integral(max(0, u*v(t)), t=0..dt)`。現ステップの前後速度を線形補間する理想離散近似。F001の位置・速度更新自体は変更しない。
- `W_signed = u*dt*(v0+v1)/2` は引き続き**運動エネルギー恒等式**のために保存する。`W_plus`を代用して機械エネルギー保存を主張しない。
- 残高不足は**候補運動を棄却**して内部力0で再計算。F002の台帳と状態は原子的に確定。世界真値を将来のセルの観測値として露出しない。
- F004を上書きせず、提案F005の版を明示した別実験とする。機械力学も費用も「実機の電気消費」ではない。

[仕様](../topics/F005-positive-work/SPEC.md) / [実験計画](../experiments/F005/PLAN.md) / [検証記録・未実施](../findings/F005-validation.md) / [Issue #12](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/12)。

### F005 implementation candidate (2026-10-16; implementation PR, not adopted)

The implementation branch adds `soma/f005.py` without modifying F001–F004. F005 reuses the F001 semi-implicit Euler `step()` and F002 immutable ledger `apply_event(spend)`; it computes positive mechanical work by exact integration of the **chosen linear-in-time velocity interpolant**, but does not simulate electrical motor loss.

~~~mermaid
flowchart TD
    IN["Config f005.v1 / Motion / F002 LedgerState"] --> V{"Validate immutable input and time grid"}
    V -->|valid and balance>0, motor nonzero| P["F001 candidate with motor+external force"]
    V -->|empty battery or zero motor| X["F001 external-force-only"]
    P --> PW["F005 positive work of linear velocity interpolant"]
    P --> SW["F004-compatible signed midpoint work for mechanical identity"]
    PW --> COST["ceil positive joules to integer microjoules"]
    COST --> BAL{"candidate cost <= balance"}
    BAL -->|yes| PAY["Accept candidate + F002 spend if positive"]
    BAL -->|no| X
    PAY --> COMMIT["Atomic motion and immutable ledger result"]
    X --> COMMIT
    SW --> LOG["Signed work stays separate from positive work"]
    COMMIT --> LOG
    LOG --> CSV["states.csv and ledger/events.csv"]
    CSV --> VERIFY["Independent saved-CSV Euler/positive-work oracle"]
    VERIFY --> EVIDENCE["comparison.json, SHA manifests, SVG, replay comparison"]
~~~

- `f005.v1` adds candidate and accepted **positive** motor work fields; existing signed work is unchanged in meaning.
- The F005 `experiments/F005/run_suite.py` verifier reads saved CSV and event files and checks every timestep without using F005's step or positive-work function. SHA checks alone are insufficient; numeric semantic checks are mandatory.
- `tests/test_f005.py` and `.github/workflows/f005.yml` exercise all F001–F004 regressions, F005 A–F, reject cases, and replay; complete raw evidence is stored as GitHub Actions artifacts.
- A successful automated suite is not adoption, a real motor-battery model, or evidence of emergent morphology. F003 link is still not attached to F005.

### F005 PR #14 独立監査後の検証経路（2026-10-16）
上図の `VERIFY` は保存CSVから再計算する二段階の照合を含む。①入力binary64端点を厳密有理数に変換した区分積分で正仕事を確認、②仕様に固定したbinary64演算順で整数µJ課金と受否を確認する。端点パワーの浮動小数点積で符号を失わない。初期行の候補2欄はnull、正仕事が微小でもゼロへの改変を拒否する。`comparison.json`に積分誤差・厳密切上げ差・binary64支出差を分離して保存する。運動器と台帳の経路は変更しない。


### F005 正式採用後の責務境界（2026-10-16）
上記のF005「implementation candidate」はレビュー時点の記録。現在の採用済み範囲は**正仕事をF002整数µJ台帳へ接続する離散計算部品のみ**。F001の位置は半陰的Euler、F005仕事は線形補間速度を積分するため、保存軌道との距離効率は保証しない。dt依存のモーター棄却・数量化、無償保持、反作用相手未定義が残る。セルの局所センサー、F003へのモーター統合、生存・身体優劣の評価環境は未承認。[採用判断と反例](../topics/F005-positive-work/SPEC.md#2026-10-16-正式採用f005の限定的な研究上の位置づけ)。

## F006：時間刻み収束性の診断（2026-10-16／設計提案・未実装）

**F006の新しい能力は、F005の計算を変更せず、同じ条件を複数のdtで走らせて違いと原因候補を記録すること。** F001〜F005は採用済み。図中のF006計測・照合は未実装。

~~~mermaid
flowchart LR
  H["研究者の問い / 仮説H006"] --> CFG["F006 sweep.json\nA〜F固定条件＋dt一覧"]
  CFG --> LOOP["F006 比較実行器\n提案・未実装"]
  LOOP --> MODEL["F005 1セル1D運動＋正仕事＋電池\n採用済み・変更なし"]
  MODEL --> RAW["F005各dtの原本\nstates / events / manifest"]
  CFG --> REF["独立の理論参照\n有理数・binary64を区別"]
  RAW --> CHECK["F006 原本検証／誤差分類\n提案・未実装"]
  REF --> CHECK
  CHECK --> OUT["比較CSV / diagnostics.json\n比較SVG / provenance"]
  OUT --> NOTE["findings/F006-validation.md\n支持・反証・不明"]
~~~

**世界の真値とセルの観測の境界**：F006はオフラインの研究者用検証器。原本ログ（位置、速度、残高、受否）は解析側にだけ提供し、セルの局所観測APIや制御入力に直結させない。

- **A（運動離散化）**：電池十分の場合でも、F001半陰的Eulerの位置がdtに依存する。
- **B（受否の離散化）**：F005は残高不足時、当該ステップのモーターを丸ごと拒否する。
- **C（会計の離散化）**：正仕事が同じでも、各ステップのµJ切上げ回数が変わる。
- F006の合格は**診断の正確さ**。dt不変・実機妥当・自律移動の成立とは異なる。部分時間駆動、端数繰越、共通軌道などの修正は後続研究。

[仕様](../topics/F006-timestep-diagnostics/SPEC.md) / [事前A〜F](../experiments/F006/PLAN.md) / [研究記録（未実施）](../findings/F006-validation.md) / [Issue #16](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/16)


### F006 v2 証拠と公開の設計改訂（2026-10-17、未採用）
```mermaid
flowchart TD
  P["出力2パスを正規化・事前検査"] --> T["非公開の一時領域で15run生成"]
  T --> A["原本・参照・出所を監査"]
  S["信頼するcheckout / 外部CI記録"] --> A
  A --> R["replayを監査・全バイト比較"]
  R --> O["no-replace renameで公開"]
  A -->|例外| C["一時成果物を破棄"]
  R -->|例外| C
  O -->|通常例外| B["自分の公開分だけrollback"]
```
診断本体とF005保存検証器もソース照合範囲に含める。出力ラベルは事前登録のexpected_classification、観測はsignatureの参照一致と数値として分離する。セルへの経路を追加しない。2パスの公開間に強制終了すると監査済み一次出力だけが残り得るため、crash時の一括原子性は保証しない。

### F006実装候補の責務境界（設計詳細・未実装）

~~~mermaid
flowchart TD
  SET["F006 run_suite.py\n固定条件をdtごとに展開"] --> EXIST["採用済み soma/f005.py\nConfig.from_dict → save_run"]
  EXIST --> RAW["変更しないF005原本\nconfig / states / events / manifest"]
  RAW --> V["既存 verify_saved_run\n全行・イベント独立照合"]
  RAW --> NEW["新規 diagnostics.py\ndt横断の比較と原因候補"]
  V --> NEW
  THEORY["独立の有理数・binary64参照\n事前に固定"] --> NEW
  NEW --> OUT["comparison.csv / diagnostics.json\ncomparison.svg / manifest"]
  OUT --> F["findings/F006-validation.md\n再現性・反証・採否"]
~~~

F006は研究者の**後処理**専用。セル制御器や物理エンジン内部に横断比較値を戻さない。表示の補間は可視化に限定し、観測値と区別する。測定不能な寄与は`mixed`・`undetermined`で記録する。実装後のコードと図を必ず同一実装PRで更新する。

## F006 実装候補の実際の流れ（PR #18、2026-10-16・未採用）

~~~mermaid
flowchart TD
  P["事前登録A〜E：同一条件、dtのみ変更"] --> RUN["experiments/F006/run_suite.py"]
  RUN --> F005["既存soma/f005.py\nConfig → save_run"]
  F005 --> RAW["15組の既存F005生ログとmanifest"]
  RAW --> ORACLE["既存F005保存証拠オラクル\n全行とイベントの独立数式検査"]
  RAW --> ANALYZE["F006 diagnostics.py\n5系列の横断比較"]
  ORACLE --> ANALYZE
  REF["Wolframの厳密有理数事前参照"] --> ANALYZE
  ANALYZE --> OUT["comparison.csv + diagnostics.json\ncomparison.svg + SHA256 manifest"]
  OUT --> REPLAY["同条件15run再実行\n全バイト一致を検査"]
  REPLAY --> CI["F006 GitHub Actions\n全回帰・-O・証拠artifact"]
~~~

**境界**：比較器はログを読み、物理系・セルの観測／方策に返さない。比較図は表示用であり記録済み数値の証拠はCSVとイベント。F対照の不正入力とハッシュ付替えによる改変はテストで実施し、A〜Eと混同しない。設計上のG1〜G5全体の独立監査・正式採用は未了。


### F006 v2実装対応（2026-10-17）
run_pairが両パスの正規化・事前確認→非公開の生成/監査→全バイト比較→Linux no-replace公開を担う。通常の公開例外は自分の公開分のみrollbackする。diagnosticsの監査は信頼するcheckoutの9ソース/参照hashと外部に固定した実行identityを使い、原本manifestの出自も照合する。上のv2図が現行実装責務で、旧図の最終出力への直接生成は履歴。F005の運動/仕事・会計・観測境界は変更しない。

## F006 限定的正式採用後のシステム境界（2026-10-17）

上のF006提案・候補図は履歴。現行採用済みは既存F005の**オフライン検証機能だけ**。ユーザーの採用判断に従い、実装[PR #18](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/18)で次の責務を統合する。

~~~mermaid
flowchart TD
    P["凍結A〜E設定と各dt"] --> R["F006 run_suite / private staging"]
    R --> M["既存F005 v1 の運動・台帳（変更なし）"]
    M --> LOG["15runのF005生CSV・events・config・manifest"]
    LOG --> O["F005 saved-file独立オラクル＋F006 cross-dt参照照合"]
    W["Wolfram厳密有理数：離散モデル参照"] --> O
    O --> A["v2 suite/run出自・9依存hashを照合"]
    A --> Q["81ファイル完全再実行／比較"]
    Q --> OUT["Linux no-replace公開：comparison / diagnostics / SVG / manifest"]
    OUT --> CI["3.11・3.12のCI artifactと研究監査"]
    OUT -. "世界真値をセルに戻さない" .-> N["将来の局所観測／制御器（未接続）"]
~~~

固定条件のみ`expected_classification`を事前ラベルとして出し、観測からの一致は`signature_matches_reference`、汎用`causal_attribution=null`。二保存先間のcrash原子性と実機・F003統合は非採用。実証値・制限・採用判断は[findings](../findings/F006-validation.md#2026-10-17-f006-限定的な正式採用--最新研究判断)。

## F007 提案：片側の電池で結合した2セルが動く（2026-10-17・設計のみ）

> **まだ動かない構想図。** F003のリンク、F005の正仕事、F002の整数µJ台帳を接続する予定の境界。既存F001〜F006は現行mainのまま。

~~~mermaid
flowchart LR
  CFG["設定: A/B質量・リンク・外力・Aモーター・電池"] --> CAND["F003型候補運動<br/>ON: 合成質量 / OFF: 独立"]
  CAND --> WORK["F005: Aの正仕事（区間速度補間）"]
  WORK --> GATE{"F002: A電池が足りる?"}
  GATE -->|Yes| ACCEPT["採用 + Aのみspend"]
  GATE -->|No| RETRY["Aモーター=0で力学再計算"]
  ACCEPT --> TRUE["研究用世界真値: A/B運動・リンク力・残高"]
  RETRY --> TRUE
  TRUE --> RAW["時系列CSV・イベント・manifest・SHA"]
  RAW --> ORACLE["独立参照 + A〜F対照 + CI"]
  TRUE -. "感覚データに直結させない" .-> OBS["将来の局所観測（未実装）"]
~~~

このリンクは**機械仕事の授受**を扱い、F002のセル間**電力量移送**とは別。結合による加速度変化を観測するだけで「有利」と結論しない。F005の外部有効力に物理的な推進反力は未実装。F006のdt依存を引き継ぎ、形態間の効率比較は現段階の非目標。

[研究仕様](../topics/F007-linked-motor-work/SPEC.md) / [事前A〜F](../experiments/F007/PLAN.md) / [検証ノート（未実施）](../findings/F007-validation.md) / [Issue #19](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/19)。


### F007 実装前レビュー：モーター拒否時も結合・外力は残す（2026-10-17、未実装）

追加のF-01〜F-06対照は、モーター仕事と機械的な拘束の責務を切り分けるためのもの。以下は**設計検証用のフロー図**であり、実装済みフローではない。

~~~mermaid
flowchart TD
  Q["Aの指令uA、A/B外力、リンク状態、A/B残高"] --> K{"A残高 > 0 かつ指令あり?"}
  K -->|yes| C["F003型の候補力学：uA + 外力 + リンク"]
  C --> W["F005型のA正仕事からµJ候補費用"]
  W --> G{"A残高で支払える?"}
  G -->|yes| Y["候補運動を確定／Aのみ支出"]
  G -->|no| Z["Aモーター0：外力とリンクは保持"]
  K -->|no| Z
  Z --> R["F003型の力学・リンク力を再計算"]
  Y --> S["世界真値：位置速度・A/B電池・力・受否"]
  R --> S
  S --> L["元CSVとリンク/台帳イベント"]
  L --> D["独立参照／F-01〜F-06／manifest／CI"]
  S -. "ロボット自身には公開しない" .-> O["将来の局所観測（未実装）"]
~~~

F-01は時間途中の残高枯渇、F-02は0仕事の非ゼロ指令、F-03は電池空でもBの外力が拘束でAへ伝わるケース、F-04は速度反転で正仕事と符号付き仕事が異なるケース。世界真値は実験器にだけ与える。研究対象は一能力（F007）だけで、局所知覚・自己学習・結合意思決定は追加しない。

## F007 実装候補の実際の責務とデータフロー（2026-10-17）

~~~mermaid
flowchart TD
  Q["f007.v1 Config: 2セル、A motor、外力、電池とリンク"] --> V["厳密な時間格子・有限値・リンク拘束・容量の入力検査"]
  V --> C{"A残量とmotor指令"}
  C -->|正の残量かつ非ゼロ指令| P["F001/F003型で候補運動を計算"]
  P --> W["F005 positive_motor_work -> ceil µJ"]
  W --> G{"候補費用をAだけが支払える?"}
  G -->|yes| Y["候補運動を採用し、F002のA spend"]
  G -->|no| R["A motor=0: 外力と理想リンクで運動・力を再計算"]
  C -->|zero balance or zero command| R
  Y --> L["世界真値：両セル状態と台帳"]
  R --> L
  L --> T["指定時刻でリンクだけ切断（x/v無ジャンプ）"]
  T --> LOG["config、states、ledger/events、link_events、SVG、SHA manifest"]
  LOG --> ORC["別実装のverify.pyが全行・イベントを再計算"]
  ORC --> SUITE["A〜E/F-01〜04対照 + F-05/06拒否・改変・byte replay"]
  SUITE --> CI["3.11 / 3.12 CI Evidence（検証待ち）"]
  L -. "世界真値はセルの観測に渡さない" .-> FUT["局所知覚（未実装）"]
~~~

研究者だけが完全な状態、拒否候補、リンク内部力と出自を閲覧する。これは物理的に結合するユニットが自律的に力を分配する実証ではなく、**有効外力と理想リンクの離散計算**の整合検証である。[F007実験手順](../experiments/F007/README.md)。


## F007 限定的正式採用後のフロー（2026-10-17）

旧「提案」「検証待ち」図は当時の履歴。実装済みの流れは、入力検証 → Aモーター候補力学・正仕事積分 → A電池ゲート → A/B運動・F002台帳 → *私有ステージ*内CSV/イベント/manifest生成 → 保存バイトの独立監査 → 1宛先ずつ既存結果を置換しない原子的公開 → 9条件・58ファイル再生とCI検査。CI成功時のみ証拠ZIPを公開。二宛先全体の停電原子性はなし。詳細は[最新研究判断](../findings/F007-validation.md#2026-10-17-f007-限定的正式採用--最新の研究判断)を優先。


## F008 提案：局所運動から未知の負荷変化に気づく【2026-10-17・設計のみ／未実装】

F007の物理真値を**研究者専用**と**セル自身に許される局所観測**に分離する。単体予測からの速度応答のズレだけを観測し、接続グラフの真値やBの状態は教えない。新しい制御・学習・身体改造は今回実装しない。

~~~mermaid
flowchart TB
  SET["研究者：A〜Fの設定・反証条件"] --> W["F007 世界：A/B・力・接続・電池（真値）"]
  W --> SENSOR["F008 局所センサー射影：セル別に分離"]
  SENSOR --> A["A自身：Δv・自分の指令/実行力・自分の電池"]
  A --> R["単体モデルの予測と比べて負荷異常を検知"]
  W --> TRUTH["研究者専用：A/B真値、接続イベント"]
  R --> VERIFY["保存ログを別式照合・反証条件で評価"]
  TRUTH --> VERIFY
  VERIFY --> LOG["観測CSV・評価・出自SHA・findings"]
~~~

**情報境界**：観測データにリンク状態・Bの位置速度・結合全質量・世界側ケース名を含めてはならない。研究者用の全状態ログは別ファイルに残す。非接続でも外力によって同じ減速が生じ得るので、応答異常を「接続を同定した」と呼ばない。モデルはF007の外部有効力（地面反力未定義）を継承し、実機推進の証拠にはしない。

[研究Issue #22](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/22) / [F008仕様](../topics/F008-local-load-detection/SPEC.md) / [事前実験](../experiments/F008/PLAN.md) / [実験記録（未実施）](../findings/F008-validation.md) / [データの境界](DATA_CONTRACTS.md)。


## F008 implementation candidate: actual A-local pipeline (2026-10-18; unadopted)

The earlier F008 design flow remains historical preregistration. This implements an **offline observer** over F007 saved traces, not an on-line cell controller.

```mermaid
flowchart TD
  CFG["Fixed F008 A–E (researcher only)"] --> W["Unchanged F007 v1 physics + battery"]
  W --> S["Saved F007 source: config / states / ledger / link_events / manifest"]
  S --> ORACLE["Independent F007 saved-evidence audit"]
  S --> PROJ["NEW soma/f008.project_local: strict A-only allowlist"]
  PROJ --> OBS["A only: self velocity, clock, motor command/applied, own battery"]
  OBS --> DET["NEW soma/f008.detect: nominal A response residual"]
  DET --> LOCAL["F008 local.csv: observed/predicted acceleration, residual, status"]
  S --> EVAL["Researcher-only evaluation; world topology and unknown force"]
  LOCAL --> EVAL
  ORACLE --> EVAL
  EVAL --> VERIFY["Independent F008 CSV oracle; frozen A-E and B/D equivalence"]
  VERIFY --> ART["Private stage → hash manifest → no-replace public evidence → replay"]
  S -. "B state, attached, world force not passed to A" .-> NO["Forbidden agent information"]
  style PROJ fill:#dbeafe,stroke:#2878bd,color:#172554
  style OBS fill:#dbeafe,stroke:#2878bd,color:#172554
  style DET fill:#dbeafe,stroke:#2878bd,color:#172554
  style LOCAL fill:#dbeafe,stroke:#2878bd,color:#172554
```

`soma/f008.detect` accepts a frozen `LocalObservation` only; it cannot read
F007 world truth. `run_suite.py` is researcher-controlled and may read full
F007 saved source only to construct the strict projection. `verify.py` is
researcher-only and **does not import the F008 detector**. F007's
`attached` at the 0.5 s cut is post-event, while the acceleration at the
same row is from the preceding linked interval. No online learning, link
identification, ground-reaction propulsion or morphology is claimed.


### F008 provenance and review gate — 2026-10-18 audit addendum

```mermaid
flowchart LR
  SRC["Trusted GitHub checkout: F007 + F008 source SHA"] --> ROOT["F008 origin snapshot"]
  W["F007 saved world data"] --> AUDIT["F007 independent full-state replay"]
  W --> PROJ["A-only allowlist projection"]
  PROJ --> DET["A local residual detector"]
  DET --> CSV["local.csv"]
  CSV --> ORC["F008 independent local CSV oracle"]
  AUDIT --> ORC
  ROOT --> ORC
  ORC --> GATE{"A–E / confound / tamper / same-byte replay"}
  GATE --> EVID["Evidence artifact + CI source/merge HEAD"]
  EVID --> REVIEW["External audit + researcher adoption gate, pending"]
```

Only the researcher-side evaluator reads `W`; the detector is typed to
`LocalObservation` and never sees connected/B/hidden external-force fields.
The saved evidence suite is researcher-only. A completed CI check is not an
adoption or a proof of isolation against malicious Python code.

### F008 decision-state amendment (2026-10-18, researcher approval)

The diagram above depicts the **historical preapproval gate**. The researcher subsequently expressly approved limited F008 adoption and main integration after P2 evidence-integrity corrections and independent AI/Fraction cross-checks. The validated implementation remains unchanged: full F007 world truth is held by the researcher-side adapter/oracle, never by `soma.f008.detect(LocalObservation)`. This acceptance is *not* a hardware/agent-isolation or morphology claim. For merged implementation, CI and final state, consult PR #27, `findings/F008-validation.md` and live main; an AI audit is not human third-party certification.


## F009 — 力の起源を区別する二セル運動量比較（2026-10-18、設計提案のみ）

~~~mermaid
flowchart TD
  PLAN["研究者: F009 A-F設定"] --> NEW["提案: 内部力/外部有効力/接地牽引を分離"]
  OLD["採用済F007: 外部有効力の既存離散基準"] --> ORACLE["研究者のみ: 独立数理比較"]
  NEW --> CELLS["研究者真値: A/B位置,速度,力積,結合力"]
  NEW --> GROUND["提案: 地面へ反作用力積"]
  CELLS --> ORACLE
  GROUND --> ORACLE
  ORACLE --> SAVE["提案: steps.csv, 比較, SHA,再実行"]
  CELLS -. "真値をセルAへ渡さない" .-> F008["採用済F008: 局所観測は変更しない"]
~~~

実線のF009要素は**提案で未実装**。研究者は系全体の運動量と地面との交換を見る。内部作用/反作用は相殺、外部有効力/地面牽引はセル系の外力。F002/F005電池計量・F008セル側推定・V001ビューアは変更しない。[SPEC](../topics/F009-reaction-momentum/SPEC.md)。


### F009 実装Draft #30：研究者専用の実際のデータフロー（2026-10-18、未採用）

~~~mermaid
flowchart TD
  CASE["事前A-F: 独立の力源・結合・接地設定"] --> SIM["soma.f009.simulate 固定1Dステップ"]
  SIM --> WORLD["研究者用A/Bの全世界真値と地面反作用"]
  WORLD --> CSV["steps.csv / config.json"]
  CSV --> FRACTION["verify.py: Fractionによる別式の全行再計算"]
  SRC["Git checkout source SHA256"] --> FRACTION
  FRACTION --> CASES["6ケース比較 / manifest / 負例"]
  CASES --> REPLAY["run_suite: 20ファイル×2 byte replay"]
  REPLAY --> CI["GitHub Actions: 3.11/3.12 / 旧全回帰"]
  WORLD -. "world truth を提供しない" .-> LOCAL["既存F008 A-local APIは変更しない"]
  OLD["既存F007外部有効力の基準"] --> FRACTION
~~~

F009はground_contactを牽引上限の理想パラメータで実現するので、現実の摩擦/車輪/支持反作用の接触解法ではない。source_shaは保存ファイル同一性の監査材料であり実行者認証ではない。設計時の図は歴史として保持する。

## F010 preregistration — multiple A-only probes and structural non-identifiability (2026-10-19, **design only, unimplemented**)

```mermaid
flowchart TD
  P["Researcher: independent F007 1D A-D/E trials, u=2,1,.5 N"] --> WORLD["EXISTING F007 ideal two-cell world + battery"]
  WORLD --> TRUE["Researcher-only truth: B, attached, hidden external force"]
  WORLD --> OBS["EXISTING F008 projector: A velocity and local applied force/balance"]
  OBS -. "strict A-only local information" .-> EST["PROPOSED F010: alpha/beta from two force levels + held-out .5 N"]
  EST --> SIG["PROPOSED response signature; never a topology label"]
  SIG --> AUDIT["PROPOSED independent Fraction/SOMA evidence audit"]
  TRUE --> AUDIT
  AUDIT --> LOG["PROPOSED raw evidence/negative cases/manifest/replay"]
  TRUE -. "FORBIDDEN: no world truth to estimator" .-> X["No connection/B/external force in cell API"]
  style EST fill:#fff0d6,stroke:#b68220
  style SIG fill:#fff0d6,stroke:#b68220
  style AUDIT fill:#fff0d6,stroke:#b68220
```

**Knowledge boundary:** each fresh run may be labeled by the *researcher* but F010 inference receives only groups of typed F008 `LocalObservation` fields, no case names or F007 world config. The design intentionally compares separate trials rather than implementing online agent control. A and C are indistinguishable from A-local data including battery. No contact/ground reaction or real locomotion has been established; F009 remains separate.

### F010 implementation candidate — actual proposed modules (2026-10-19, **unadopted**)

```mermaid
flowchart LR
  RC["Researcher A–E x 2/1/0.5 N configs"] --> F007["ADOPTED F007 unchanged: motion + motor/µJ gate"]
  F007 --> RAW["Researcher-only immutable F007 CSV + ledger + link events"]
  RAW --> F008["ADOPTED F008 project_local strict A-only projection"]
  F008 --> NEW["F010 candidate estimate: 2-point alpha/beta + .5 N holdout"]
  NEW --> SIG["Response signature; topology_verified = false"]
  RAW --> ORACLE["Researcher-only F007 independent replay + F010 Fraction oracle"]
  SIG --> ORACLE
  ORACLE --> ART["F010 15x evidence, manifests, same-byte replay, CI"]
  RAW -. "FORBIDDEN: B/attachment/unknown world force" .-> NEW
  style NEW fill:#fff0d6,stroke:#b68220
  style SIG fill:#fff0d6,stroke:#b68220
  style ORACLE fill:#fff0d6,stroke:#b68220
```

Input variation is orchestrated by a **researcher-side offline experiment**, NOT by autonomous cell control. Each run resets state/battery. A/C local equivalence includes A battery and actuator feedback. `F010` cannot infer structural attachments even when `alpha=1/2`. No F009 real contact physics is imported.

**F010 limited adoption decision (2026-10-19):** The offline local-signature path in the immediately preceding candidate diagram is now approved under the narrow frozen F007/F008 1D model after command/applied-force gating and normal-exception replay-publication rollback passed final implementation tests. It does not add information flow from researcher-only truth to the estimator and does not infer mechanical topology. See [dated acceptance](../findings/F010-validation.md) and Issue #31 for actual main merge verification; the earlier candidate label records the state when the diagram was proposed.


## F011 design preregistration: passive grounded internal drive (2026-10-20, UNIMPLEMENTED)

**Unimplemented proposal; F001–F010 limited-adopted flows are unchanged.** Issue #34 / [SPEC](../topics/F011-grounded-internal-drive/SPEC.md) / [PLAN](../experiments/F011/PLAN.md). The new model is **not** F007 external effective propulsion or F009 prescribed ground traction.

```mermaid
flowchart TB
  R["Researcher: preregister A-F, friction, open-loop period"] --> U["PROPOSED: internal force u and passive spring"]
  U -->|"+Fint"| A["Cell A, m=1kg"]
  U -->|"-Fint"| B["Cell B, m=1kg"]
  A <-->|"mechanical relative distance r"| B
  G["PROPOSED passive directional ground, same law per cell"] -->|"ground impulse A"| A
  G -->|"ground impulse B"| B
  A -->|"world state/contact velocity"| G
  B -->|"world state/contact velocity"| G
  A --> T["RESEARCHER truth: xA/vA, xB/vB, impulses, energy"]
  B --> T
  G --> T
  T --> O["PROPOSED independent CSV oracle, dt check, replay"]
  T -. "FORBIDDEN world-truth link to cell" .-> C["Cell-side controller: NOT IMPLEMENTED"]
  O --> F["findings: SUPPORT / CONTRADICT / INCONCLUSIVE"]
```

Direct cells-to-ground contact forces transfer momentum; internal +F/-F cannot alter total momentum. Researcher's world truth is distinct from possible future cell local sensors. Proposed 1D direction-dependent stick/slide idealization has no physically modeled normal contact, battery efficiency, learning, active anchor switching or general 2D morphology. Frozen schema in [DATA_CONTRACTS](DATA_CONTRACTS.md).


### F011 implementation candidate (2026-10-20; stacked Draft, NOT ADOPTED)

Implementation modules `soma/f011.py` (frozen 1D numerical world), `experiments/F011/run_suite.py` (A–E×3 conditions and negative-stroke prefix), `experiments/F011/verify.py` (researcher-only independent raw-state oracle) and `tests/test_f011.py` keep physics, evidence and interpretation separate. Unlike F007, F011 *internal* ±F and a passive ground law do not inject a hand-coded effective propulsion force. The observer reads full world truth; no F011 cell-side sensor/controller exists.

```mermaid
flowchart LR
  C["Frozen A–F research configuration"] --> M["NEW F011 internal ±F / spring"]
  M --> A["Cell A"]
  M --> B["Cell B"]
  A --> G["NEW passive grounded Coulomb impulse"]
  B --> G
  G --> A
  G --> B
  A --> W["WORLD truth CSV"]
  B --> W
  G --> W
  W --> V["Independent verifier: force/momentum/energy"]
  V --> R["Comparison/manifest/byte replay/CI"]
  W -. "NO WORLD truth to cell" .-> X["Local self-model/control: unimplemented"]
```

A without ground reaches preregistered stroke limit early: save prefix as INCONCLUSIVE rather than clipping. B symmetric, C anisotropic drift, D mirrored drift, E no motor. External human review / formal research adoption still pending.

### F011 post-experiment scope decision (2026-10-20; separate from the original diagram/design record)

The research owner authorized **limited adoption of the frozen 1D discrete passive-directional-ground rectification capability** (internally driven identical cells, prescribed asymmetry, C/D mirrored COM drift and controls B/E). The original A:no_contact 9.6s bounded-stroke case is **INCONCLUSIVE** because the prescribed r<=0.8m gate fails around 2.1s; the original full A–E completion requirement is **not passed**, but a separately documented owner exception accepts the narrower model result. All model arrows, world-truth-only evidence, frozen forces and observability boundaries above are unchanged. No agent-level selection, locomotor controller, end-stop contact, battery/power integration, hardware grounding or spontaneous morphology is implied. See [SPEC adoption addendum](../topics/F011-grounded-internal-drive/SPEC.md) and [F011 findings](../findings/F011-validation.md).


## F012 — PREREGISTERED proposal (2026-10-20; NOT IMPLEMENTED / NOT ADOPTED)

```mermaid
flowchart TB
  R["Researcher: frozen B/C/D/E, budget and dt"] --> W["Existing F011 numerical world semantics"]
  W --> G["PROPOSED F012: candidate motor step and positive relative work"]
  G --> B["PROPOSED: bounded integer-µJ budget gate"]
  B -->|"accept/reject ±u; preserve spring"| PAIR["2 identical cells + passive ground"]
  PAIR -->|"world truth: state, force, ground work"| RAW["PROPOSED researcher-only CSV"]
  B -->|"accepted cost, balance, gate event"| RAW
  RAW --> AUDIT["PROPOSED independent ledger/physics replay"]
  RAW -. "NO world-truth API" .-> LOCAL["cell sensing / self-model NOT IMPLEMENTED"]
```

F011 accepts prescribed open-loop internal force without finite budget; proposed F012 is **a new experimental version**, not a change to the accepted F011 model. Mechanical force links and ground reaction are physical-model interactions; integer energy allowance is an administrative ideal actuator constraint; CSV is researcher-only. Existing F008/F010 A-local data interface is NOT integrated and remains unchanged. No real current/voltage, real contact or emergent policy.

## F012 implemented-candidate dataflow — 2026-10-20 (PR #40, **not adopted**)

This is a SEPARATE frozen numerical experiment `soma/f012.py`, **not** a replacement for conditional limited-adopted `soma/f011.py`.

```mermaid
flowchart TB
  R["Researcher-only: frozen budget / ground / dt / open-loop command"]
  W["F011 passive ground + spring numerical semantics (unchanged source)"]
  C["F012: propose internal +/-u force and candidate motion"]
  P["F005 positive work of RELATIVE endpoint velocities"]
  B["F012 integer µJ budget gate; reject or accept whole motor step"]
  A["Cell A: +u, spring, passive ground"]
  D["Cell B: -u, spring, passive ground"]
  L["Researcher-only full world states.csv / config.json"]
  V["Independent alternative-step physics + budget + source/summary audit"]
  S["GitHub CI Python 3.11/3.12, byte replay and artifacts"]
  R --> C
  W --> C
  C --> P --> B
  B -->|"accepted/rejected motor"| A
  B -->|"opposite internal force"| D
  A <-->|"mechanical spring, internal reaction"| D
  A -->|"ground reaction, world state"| L
  D -->|"ground reaction, world state"| L
  B -->|"accepted work, µJ spending, remaining budget"| L
  L --> V --> S
  L -. "FORBIDDEN: world truth cannot reach cell-local inference" .-> X["F008/F010 local estimator unchanged"]
```

F012 imports F011's **passive_contact** and F005's **positive_motor_work**; these prior functions/files are not changed. Its new pair dynamics and budget gate are implemented, whereas any real physical friction/contact, motor electricity, cell sensing, self-model and autonomous actuation are **NOT IMPLEMENTED**. All world data are researcher-facing. A rejected motor does **not** disable the spring or passive ground.

## 2026-10-20 F012 research-director post-audit acceptance (limited; historical proposed diagram above retained)

The separate F012 ideal budget gate, world-only trace, independent F012 stored-data oracle and C/D and B/E pointwise counterfactuals are **implemented**. The research director is authorized to merge design #39 followed by implementation #40 once final commit checks are green. F012 is **LIMITED ADOPTED for prescribed 1D numerical finite-positive-motor-work study**, not hardware, electrical or emergent morphology. The figure above continues to show the actual implemented F012 candidate components. F011 original source and F008/F010 local observation boundaries are unchanged. Merge SHA and exact checks are recorded in the GitHub PR/Issue timeline.


## F013 separate contact-rectification study — LIMITED ADOPTED within ideal 1D scope after formal 2026-10-20 review

The adopted F011/F012 models remain byte-unchanged. F013 evaluates a *different* smooth dissipative passive friction law; its world-state output is only available to the researcher's offline verifier. There is no F013 local sensor, agent controller, battery or body design. The new code does not depend on importing F011/F012 physics.

```mermaid
flowchart TB
    R["Researcher: 36 frozen conditions B/C/D/E × eps × dt"]
    F["EXISTING F011: accepted fixed velocity-proximal Coulomb model"]
    N["PROPOSED F013: smooth tanh passive friction + independent implicit solver"]
    A["Cell A: +internal drive, spring"]
    B["Cell B: -internal drive, spring"]
    G["Model ground: independent passive reactions"]
    T["Researcher-only full truth: per-step x,v,r,forces,work"]
    V["PROPOSED independent stored-CSV physics, symmetry and provenance audit"]
    J["SUPPORTED / CONTRADICTED / INCONCLUSIVE; researcher decision"]
    L["Cell-local inference / self-model: NOT IMPLEMENTED here"]
    R --> N
    R -. "frozen original reference" .-> F
    N --> A
    N --> B
    A <-->|mechanical spring and ±u| B
    A <-->|ground reaction| G
    B <-->|ground reaction| G
    A -.-> T
    B -.-> T
    G -.-> T
    T --> V --> J
    F -. "independent comparison of saved results" .-> J
    T -. "world-truth leak forbidden" .-> L
```

The motor force is internal and cancels in the two-cell momentum sum. Ground reactions transfer momentum with the environment. The numerical friction and regularization width are **researcher-set assumptions**, not discovered locomotive roles. A failed/invalid stroke does not justify extending the interval after data are observed.


### F013 post-preregistration review: truly alternative ODE time integrator

```mermaid
flowchart LR
  H["Same registered physical hypothesis: 2 cells + fixed passive C0 friction"] --> P["F013: semi-implicit x with implicit friction velocity root"]
  H --> Q["Independent ODE auditor: coupled 4D explicit RK4"]
  P --> E["36 frozen cases + saved world-truth CSV"]
  Q --> F["24 ODE reference runs (12 cases x 2 fine grids)"]
  E --> V["Independent CSV/energy/momentum verifier"]
  F --> V
  V --> R["Scientific results + numerical differences (researcher only)"]
```

The independent RK4 code imports no `soma.f013` functions and integrates the continuous-time force rather than reproducing F013's split discrete contact projection. This is post-registration numerical validation and does not revise frozen thresholds. No cell-local access to world truth.


**Formal research status:** F013 model-level numerical contact robustness is LIMITED ADOPTED as decided in Issue #42; the timeline of real PR merges and exact main SHA is authoritative in that Issue, not inferred from this research diagram. **No** runtime F013 local perception, decision-making, physical hardware contact or emergent roles are implemented.


## F014 design preregistration — one-bit peer observability (2026-10-20, PROPOSED / UNIMPLEMENTED)

[Issue #45](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/45) / [SPEC](../topics/F014-peer-body-observability/SPEC.md) / [PLAN](../experiments/F014/PLAN.md) / [FINDINGS](../findings/F014-validation.md).

```mermaid
flowchart TD
    H["Researcher presets L/G/C/N/E control and hidden forces"] --> W["ADOPTED F007: 1D world simulator (world truth)"]
    W --> A["ADOPTED F008 A-local allowlisted observation"]
    W -. "PROPOSED: project B-local delta-velocity only" .-> S["B motion sensor: binary moved bit"]
    S -. "PROPOSED: framed packet, one measurement bit" .-> J["PROPOSED F014 co-response evaluator"]
    A -. "PROPOSED input" .-> J
    J -. "PROPOSED inference, not attachment truth" .-> O["Peer motion seen / peer still / inconclusive"]
    W --> R["Researcher-only raw world truth"]
    O --> V["Researcher-only independent verifier (PROPOSED)"]
    R --> V
    V --> F["F014 evidence and adoption decision (UNEXECUTED)"]
```

**Existing boundary:** F007 mechanics and A-only F008/F010 observational streams are adopted within fixed ideal worlds. The B packet projection, F014 estimator and F014 results shown dotted/PROPOSED do not exist at preregistration. World `attached`, `external_force_*`, `link_force_*`, B's numeric velocities, researcher case labels and ground truth must never reach F014 inference. A packet containing a movement bit is not a physical joint; co-motion under separate external forces can mimic a rigid link. F011–F013 passive-grounded internal-drive models are NOT wired to this F014 design.


## F014 implementation candidate — real code path (2026-10-20; NOT adopted)

The older F014 diagram above is the **historical preregistration state**. On the stacked implementation branch, these components now exist; CI evidence and scientific acceptance must be checked separately.

```mermaid
flowchart LR
  C["Researcher-only frozen L/G/C/N/E x 3 configs"] --> W["UNCHANGED F007 world + F002 ledger"]
  W --> P["Researcher adapter: F008 A allowlist"]
  W --> Q["Researcher adapter: B delta-velocity > 1e-10 m/s"]
  Q --> T["B-origin framed packet: exactly one boolean payload"]
  P --> E["NEW F014 estimate_trial: typed A only"]
  T --> E
  E --> D["Peer motion seen / peer still / inconclusive"]
  W --> R["Researcher-only saved raw truth + F007 auditor"]
  P --> V["Independent saved-data F014 verifier"]
  T --> V
  R --> V
  D --> V
  V --> X["Researcher-only evidential review + replay + CI"]
  W -. "FORBIDDEN: attachment, external forces, B speed" .-> E
```

Implementation: [`soma/f014.py`](../soma/f014.py), [15-run producer](../experiments/F014/run_suite.py), [non-producer oracle](../experiments/F014/verify.py), [tests](../tests/test_f014.py), [Actions](../.github/workflows/f014.yml) and [WSL2 guide](../experiments/F014/README.md). The new project addition is *distributed evidence about B's motion*, not a discovered topology. Truth-side adapter and verifier do access researcher-only raw F007; estimator cannot. F011–F013 physical/contact models remain separate and untouched.

### F014: 2026-10-21限定採用と実装済み知識境界

上のF014図は設計時と実装候補当時の履歴。新しいF014推論コードはF008の型付きA局所観測とBの測定真偽値+フレームだけを消費する。F007の機械接続・隠れ外力・B速度の数値は研究者側のプロジェクション・保存データ独立監査に閉じる。L/Gの部分的区別とL/Cの識別不能性を同時に実証した範囲で限定正式採用。身体全体の同定、因果的力伝達、発信源真正性、実機・ノイズ・自律探査は非採用。人間独立査読は未実施。採用/統合の正確な状態はIssue #45とGitHub PR #46/#47を参照。

## F015：能動介入と身体関係の条件付き識別（2026-10-21・設計のみ／未実装）

**Issue [#48](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/48) / [SPEC](../topics/F015-active-body-probing/SPEC.md) / [PLAN](../experiments/F015/PLAN.md) / [UNEXECUTED findings](../findings/F015-validation.md)。** 以下は**将来のデータフロー**であり、`main`の実装済みF014や既存物理を変更しない。

~~~mermaid
flowchart TB
  CTRL["研究者が事前固定: u=2,1,0 N / full reset"] --> WORLD["F007 1D truth: A/B/attached/dA,dB
(15-run future; NOT IMPLEMENTED F015)"]
  WORLD --> A["F008 A local allowlist
IMPLEMENTED F008"]
  WORLD --> B["B-local delta velocity -> moved boolean
IMPLEMENTED F014 projector reusable"]
  A --> PAIR["F015 trial-pair signature comparator
PROPOSED ONLY"]
  B --> PAIR
  WORLD --> AUDIT["Researcher-only truth / independent oracle
PROPOSED F015"]
  PAIR --> AUDIT
  AUDIT --> EVIDENCE["F015 immutable CSV/JSON + hypothesis verdict
NOT RUN"]
  WORLD -. "FORBIDDEN: topology, external forces, B numeric speed" .-> PAIR
~~~

観測者Aはuを自分のコマンド履歴として知る。F-fixed（外力固定）のように識別できる場合と、T-tracking（外力がuに追随）のように**すべての介入でも識別できない場合**を区別し、`connected`を出さない。u=0単独は結合不在の証拠ではない。F011–F013地面物理／V001 viewerと混ぜない。

## F015 実装候補の責務境界（2026-10-21／最終HEAD-CI確認前）

[研究Issue #48](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/48) / [実験再生](../experiments/F015/README.md) / [記録](../findings/F015-validation.md)。下のフローは **F015専用ブランチに追加済みの候補コード**（実測値はCI・独立監査待ち）。これより前の「F015提案のみ」図は設計履歴として保持する。

~~~mermaid
flowchart TD
  U["研究者が事前登録した3指令: 2/1/0 N\n各試行フルリセット"] --> W["既存F007運動＋電池真値\n5条件×3＝15 runs"]
  W --> P["研究者限定プロジェクタ"]
  P --> A["既存F008: A LocalObservationだけ"]
  P --> B["既存F014: B moved boolean + source/time"]
  A --> I["soma/f015.py\n3独立試行の理想応答比較"]
  B --> I
  I --> C["A-only vs A+bit 判別寄与/不確定\nNO connected field"]
  W --> AUD["experiments/F015/verify.py\n保存世界真値と独立数式の監査"]
  C --> AUD
  AUD --> LOG["source/file SHA256 + 全原本CSV\n改ざん負例・byte replay・CI"]
  W -. "禁止: リンク真値/外力/B数値速度の流出" .-> I
~~~

**科学的境界:** `soma/f015.py` はF007の実装も`soma/f014.py`も変更しない。参照 `a_A=u/2` は既知と仮定された理想2質点モデルであり、自己生成の身体構造認識ではない。A-onlyでもF-fixedとLを区別できるならB bit独自の価値を誇張しない。T-trackingの一致は「結合真偽を識別できない」という重要な反証例。

### F015 2026-10-21 observed/limited-adoption decision

The F015 implementation candidate was **executed and verified** on source HEAD `9725c556741b373184a53e6a407644644ff75952`, [Actions #39538071630](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39538071630): 15 frozen software trials, 60 A-local + 60 B boolean observations, independent saved-world ledger and reference audit, false-science negatives, 138 saved files byte-identical across independent runs. F-fixed differs from linked reference in **A-only** after u decreases; the B-bit has **zero extra discrimination** here, and T-tracking still mimics L fully. The proposed-only diagram directly above retains its date; this paragraph is a newer verified implementation milestone. **Scientific acceptance limited to ideal F007 observation response signature, conditional on docs-inclusive final CI and actual main merge; no topology verification or autonomous morphology.**


## F016 成立性レビュー：1bit通信は「知識」ではなく「行為」を変えるか（2026-10-21 / PROPOSED / UNEXECUTED）

[F016 feasibility](../topics/F016-communication-value/FEASIBILITY.md) / [候補実験](../experiments/F016/PLAN.md) / [未実験の記録](../findings/F016-validation.md) / [Issue #52](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/52)。

次図は**設計検討の概念図**。F016のモジュール・センサー・通信路・資源獲得はまだ実装されていない。F007既存剛体リンクの世界を今後の実装案として利用するだけで、F011–F013の接地/内部反力世界とは統合しない。

~~~mermaid
flowchart TD
  CFG["研究者：左右資源位置、支出条件、物理初期状態\ntruth only"] --> PHYS["F007理想1D剛体二セル\n既存 physics + motor account"]
  CFG --> TARGET["資源位置 ±0.5m\n理想3J acquire（提案）"]
  PHYS --> LOCALB["B局所センサー（提案）\n開始時の資源方向だけ"]
  LOCALB --> TX["B sender: 1bit payload\nF002 spend：0.05J / 2J（提案）"]
  TX --> RX["A allowed sensor + bit\n不正/欠損を区別"]
  PHYS --> LOCALA["A自身の位置・速度・motor履歴のみ"]
  LOCALA --> RX
  RX --> ACTION["A固定指令 ±2Nを一回選択\n学習/創発なし"]
  ACTION --> PHYS
  PHYS --> EVAL["研究者専用: A終点 vs 資源位置\nF002 acquireと収支監査"]
  TARGET --> EVAL
  EVAL --> LOG["比較群別 raw traces / event ledger / provenance\nF016 FROZEN AFTER REVIEW; NOT YET RUN"]
  CFG -. "禁止：target位置、世界真値、接続真値、未来の成果" .-> RX
~~~

区別すべき2系統：**Aの意思決定入力**はAローカルとB由来1bitだけ、**研究者オラクル**は真値から到達結果と台帳整合性を評価する。bit内容はF014のB移動bitと別物であり、F015の身体関係識別不能性を解決したことにはならない。

### F016 preregistration correction (2026-10-21, pre-experiment)
The F016 diagram above is **conceptual, not implemented**. [Frozen SPEC](../topics/F016-communication-value/SPEC.md) sets F007 discrete 1-second terminal resource coordinates ±0.625m (prior ±0.5m continuous-time target withdrawn) and a researcher-side observability mask: B can observe initial resource-relative direction, A cannot. That mask is an assumed ideal sensor interface, **not demonstrated occlusion optics in 1D**. F016 will separately replay F007 motor expenditures into F002 and charge B communication / grant A 3J resource reward; existing F007 source stays untouched. Compare A0/K/S/T/H/I fixed 24 primary runs; science ledger records any negative result. Actual implementation status still UNEXECUTED at this document version.

### F016 candidate implementation boundary (2026-10-21, pending exact-HEAD CI)
```mermaid
flowchart TD
  R["Researcher-only world resource at ±0.625m"] --> S["B local resource-side bit projector"]
  S --> P["Typed ResourceBit B/time 0 / true-or-control"]
  P --> A["A.choose_force: packet or None -> ±2N only"]
  A --> F["UNMODIFIED F007 ideal linked 2-cell 1D"]
  F --> U["Unaltered F007 state + A motor spend"]
  U --> T["F002 independent sidecar: replay motor once, charge B packet, award A 3J only if xA matches"]
  R --> V["Researcher-only independent oracle"]
  T --> V
  V --> E["24 truth-trace CSV+JSON, source hashes, manifest, falsification and replay"]
  R -. "never provide resource position or topology" .-> A
```
Candidate `soma/f016.py` is **not** an accepted API; used source/model only in its implementation branch. The packet meaning is fixed, transmission time is ideal zero latency and only B energy cost is modeled. This is NOT evidence of naturally invented communication/physical radio or confirmed linkedness. Earlier conceptual F016 diagram is design history. [Frozen SPEC](../topics/F016-communication-value/SPEC.md) / [experiment README](../experiments/F016/README.md).

### F016 actual execution boundary (2026-10-21, initial source SHA 3fc7b0a7)
[Observed 24-run findings](../findings/F016-validation.md) report that the implementation-candidate truth→B sensor sign→A fixed command→F007 motion→F002 sidecar→independent audit path executed on ideal frozen 1D assumptions. Source-behavior and the separate 24 saved-world audit passed Python3.11/3.12. The diagram above has now been executed **only for** the explicit idealized B-local direction observation mask with instant costly packet and researcher-scored terminal resource. Do not label this an autonomous communication protocol, actual body topology discovery, radio, contact physics or morphological self-organization. Human external peer review absent; formal adoption and post-main CI depend on final SHA. [Run #39581144450](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39581144450).

### F016 final main integration and limitation (2026-10-21)
The F016 truth→B-local initial resource-side bit→A fixed ±2N policy→unmodified F007 two-body 1D→F002 combined sidecar→researcher-side frozen terminal task oracle **now executes as an ADOPTED LIMITED ideal numerical module** on main merge `146e51db0e2356ed671599266b6c4acd7b7ec954`; [post-main F016 run](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39582766235) and all 16 inherited/new workflows succeeded. Diagram segments describing this F016 design as *future/proposed* are archived context. Persistent physical-model boundary: F007 motor is external effective force, B sensor access is a manually assigned observation mask, bit meaning is fixed, and payload delivery ideal zero-latency; no learned body's dynamic reconfiguration, real radio or sensor simulation.

### F017 candidate architecture — receiver learns symbolic action value (2026-10-21; NOT IMPLEMENTED)

**STATUS: DESIGN DRAFT / NO F017 DATA.** [F017 SPEC](../topics/F017-signal-action-learning/SPEC.md) / [PLAN](../experiments/F017/PLAN.md) / [findings](../findings/F017-validation.md) / [Issue #57](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/57).

~~~mermaid
flowchart TD
 W["Investigator world: hidden target sign, trial order and secret symbol mapping"] --> B["B-only local resource-side sensor (ideal F016 mask)"]
 B --> M["Researcher-controlled mapping: opaque symbol 0 or 1"]
 M --> P["Verified B packet / absent-packet control"]
 P --> A["A receiver: observe(raw symbol / None); choose ±2 N"]
 Q["A private Q(symbol, action), experience-based"] --> A
 A --> F["UNCHANGED F007 ideal fixed 1D two-cell physics"]
 F --> E["F002 independent sidecar: A work, B fee, A resource acquisition"]
 E --> L["Allowlisted A own feedback: acquired_uj + motor_spent_uj"]
 L --> Q
 W --> T["Researcher-only truth & experiment allocation"]
 E --> V["Independent saved-world auditor / physical, ledger, leakage and hash verification"]
 T --> V
 Q -. "Policy snapshot for research audit only" .-> V
 V --> R["Append-only findings; heldout and reversal comparisons; no F017 observations yet"]
 W -. "FORBIDDEN: true target, mapping, reversal, episode id, topology" .-> A
 E -. "FORBIDDEN: B fee and net score to learner" .-> A
~~~

**Data/control distinctions:** A observes only opaque symbol (not fixed F016 resource-direction bool), own chosen action and settled own ledger feedback. Trainer is an independent experimental-layer feedback switch: frozen holdouts have no learn call, not a phase flag passed to A. B does NOT learn. Mapping reversal is made only by investigator after a frozen no-learning holdout; the same A policy state persists. Researcher-only world, true attachment, F007 global state and cross-cell net score NEVER enter A policy. Diagram represents a future, not implemented, module; F016's limited-adopted fixed decoder remains unchanged.


### F017 design-only causal listening audit (pre-execution)
In addition to the F017 main diagram above, the researcher-only audit may clone a frozen A policy at an unseen holdout checkpoint and vary just `do(symbol=0/1)` with matched RNG and fixed input. Compare resulting ±2N action distributions WITHOUT running F007, changing original learning state, paying a B transmission fee or disclosing the intervention to A. This separates causal response of A's policy from independent physical resource advantage. The B sender rule remains externally specified; both sending and listening emerging spontaneously are **NOT TESTED**. [H17f candidate](../topics/F017-signal-action-learning/SPEC.md).


### F017 executable candidate pipeline (2026-10-22, NOT ADOPTED)
~~~mermaid
flowchart TD
  T["Researcher-only per-phase hidden target / mapping / seed"] --> B["B ideal local resource-sign projector"]
  B --> X["Researcher maps to opaque bit 0/1; B pays .05J"]
  X --> V["Validated RawPeerSymbol or None"]
  V --> A["Receiver.observe -> -2N/+2N (Q policy, no ground truth)"]
  A --> W["UNMODIFIED F007 fixed linked 1D; 4 steps"]
  W --> L["Separate F002 sidecar: replay actual motor spends, B fee, 3J terminal acquisition"]
  L --> F["Only A acquired and A motor spent to Receiver.learn"]
  F --> A
  T --> R["Researcher-only paired world ground truth and phase"]
  W --> R
  L --> R
  R --> O["Independent SAVED-file oracle + SHA verification + forged rehash negative"]
  O --> S["Holdout/flip analyses; 8-seed paired bootstrap; append-only findings"]
  A -. "No source packet, mapping flag, target or B fee leak" .-> R
~~~
**Status: implementation candidate only.** `experiments/F017/run_suite.py` creates 23,296 1D worlds using F007 and F002, `experiments/F017/verify.py` independently recalculates raw world/learned Q/reward and `analyze.py` applies the frozen gates. Paired counterfactual listener forks operate OFF-WORLD. A's policy has no researcher target or trial flags. This is NOT sender-rule co-emergence, real radio/ground, role formation or morphology. [Frozen SPEC](../topics/F017-signal-action-learning/SPEC.md) / [PLAN](../experiments/F017/PLAN.md).

### F017 causal-listening auditor wiring correction (2026-10-22)
~~~mermaid
flowchart LR
 A["A learner after training Q + PRNG state"] --> F0["Frozen full fork: do(B bit=0)"]
 A --> F1["Frozen full fork: do(B bit=1)"]
 F0 --> C["Matched ±2N action distribution; 256 draws"]
 F1 --> C
 C --> V["Separate saved-evidence oracle reconstructs RNG state and recomputes D"]
 C -. "No F007 world advance, no B fee, no learning" .-> A
~~~
The full learned PRNG state, not a freshly seeded unrelated probe generator, is the paired intervention checkpoint. This is an OFF-WORLD policy causal test, **not** evidence that the sender B developed communication incentives.


### F017 2026-10-22 limited-adopted topology of the software module (no body emergence)
The frozen single-function `RawPeerSymbol → Receiver.observe → fixed ideal F007/F002 task → only A-local feedback to Receiver.learn` path is **LIMITED ADOPTION APPROVED** under H17a–f, [recorded 23,296-run findings](../findings/F017-validation.md). Researcher-only `target/encoding/phase` do not enter receiver. Off-world full learned Q+RNG cloned `do(symbol)` probe is an audit path only. B has no learned send policy; signal route is ideal, predetermined, charged to B. This diagram is **not** a spontaneously attached or morphologically evolving body and cannot be used to claim physical communication or group-level agent evolution. Final merge and post-main CI are separately verified milestones.


## F018 proposed boundary — bilateral attachment intent and per-cell causal energy value (2026-10-22; DESIGN ONLY)

**UNIMPLEMENTED / NO F018 EXPERIMENT / NOT ADOPTED.** [Issue #61](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/61) / [SPEC](../topics/F018-attachment-value/SPEC.md) / [PLAN](../experiments/F018/PLAN.md) / [findings](../findings/F018-validation.md). F017 fixed receiver is *not* wired into F018. Initial contacts are researcher-prepared; no spontaneous approach, mutual learned consent or physical connector.

~~~mermaid
flowchart TB
  S["Researcher predeclares paired initial worlds and spatial resource geometry"] --> M["Same start state and motor action: four request pairs"]
  LA["Cell A local request: YES/NO (fixed test action)"] --> G{"Both YES and F003-eligible?"}
  LB["Cell B local request: YES/NO (fixed test action)"] --> G
  M --> G
  G -->|"yes"| J["F003 ideal attached mechanics"]
  G -->|"no"| U["F003 unlinked mechanics"]
  J --> E["Mechanical trajectory + positive motor work + cell-specific resource hits"]
  U --> E
  E --> L["F002 bookkeeper: A/B balances, acquisition, spend, optional explicit join fee"]
  L --> W["Researcher-only paired forks and signed individual deltas"]
  W --> V["Saved-data independent auditor / frozen gates / findings"]
  W -.->|"NEVER accessible to cell choice"| LA
  W -.->|"NEVER accessible to cell choice"| LB
~~~

**Responsibilities**: The proposal changes *choice availability* and independent researcher-side evaluation, not underlying F003 link physics. Zero-jump eligible initial state, no ad hoc impulses or teleport; F007 external-effective-force and F011 grounded internal force must not be conflated. Mechanical link does not imply automatic F002 electrical transfer. Forbid **any bonus for attachment**. Only resource geometry/motion/declared costs may affect net balance. The future self-learning component that chooses YES/NO from local history is a **distinct later experiment**, not an F018 outcome.


## F018 concrete candidate implementation wiring — not yet validated (2026-10-22)

The older F018 proposal diagram above is historical. The new `soma/f018.py` implements researcher-fed strict step-0 `AttachmentIntent`, two-YES and F003 geometry/velocity eligibility (without snapping), and per-arm F007 ideal attached vs free motion. F018 explicitly invokes existing F007 motor-work/F002 spending, inserts upfront F002 join fees, and adds **terminal-only** resource events, **not continuous path crossing**. The separate verifier is independent of F007/F018 application logic.

~~~mermaid
flowchart TD
  I["Off-world frozen 90 scenes: layout/sign/radius/fee"] --> C["4 consent pairs + 3 NN motor options each"]
  A["A step-0 request: bool"] --> G{"soma.f018.resolve_attachment AND valid F003 link geometry"}
  B["B step-0 request: bool"] --> G
  C --> G
  G -->|YY+eligible| J["Existing F007: fixed ideal 1D attached; upfront fees"]
  G -->|otherwise| U["Existing F007: independent 1D dynamics; no join fee"]
  J --> T["t=1s terminal harvest, per-patch nearest claimant"]
  U --> T
  T --> E["F002 per-cell integer-µJ ledger: join/motor/acquire"]
  E --> D["90 paired Δfixed and Δoutside tables, A and B separately"]
  D --> R["Raw states.csv / worlds.jsonl / events.jsonl / ledger.jsonl / summary.jsonl"]
  R --> V["Independent verifier without importing producer/F007, semantic attack tests"]
  V --> Z["source-bound SHA manifest + two-root replay + CI + research review"]
  D -. "NO paired/oracle payoff enters a local controller" .-> A
  D -. "NO paired/oracle payoff enters a local controller" .-> B
~~~

**Still absent**: an actually responding learned YES/NO local policy; B-owned motor actuation; contact/collision/docking; ecological/generalizable resource distributions; private-local observation input to a learner; a stable connected morphology; real grounded/electric powertrain. F007 motor is A-only external-effective-force. Paired `delta_outside` uses an omniscient investigator-side max over the **restricted** A-motor options -2/0/+2N, not a claim about what a local decision maker can discover. [Code](../soma/f018.py) / [reproduction](../experiments/F018/README.md) / [F018 frozen PLAN](../experiments/F018/PLAN.md).



## F019 selected next — path-dependent finite resources (2026-10-22; PROPOSED, NOT IMPLEMENTED)

[Research Issue #64](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/64) / [F019 SPEC](../topics/F019-resource-ecology/SPEC.md) / [PLAN](../experiments/F019/PLAN.md) / [UNEXECUTED findings](../findings/F019-validation.md).

The solid historical modules below are F018/F007/F002 components **already present in main**. Dashed F019 components are **design-only**. No learned consent, B-owned motor, real collision docking or actual resource world has been added.

~~~mermaid
flowchart TD
  G["外生的資源場のseedと配置規則<br/>(軌道・報酬から独立)"] -. "F019 design" .-> FIELD["有限 ResourceField<br/>patch ID / 区間 / 在庫"]
  IA["研究者指定: Aの結合要求"] --> CH{"既存F018<br/>両者YES＋F003適合?"}
  IB["研究者指定: Bの結合要求"] --> CH
  CH -->|YES| LINK["既存F007: 理想リンク1D"]
  CH -->|NO| FREE["既存F007: 非結合1D"]
  LINK --> TRAJ["既存F007 positions / motor work"]
  FREE --> TRAJ
  TRAJ -. "F019 design" .-> SWEEP["step内の線形経路<br/>初回進入時刻を計算"]
  FIELD -.-> SWEEP
  SWEEP -. "F019 design" .-> DEP["先着セルへ一度だけ獲得<br/>残資源→0"]
  DEP -. "F019 design" .-> LED["既存F002台帳へcell別acquire"]
  TRAJ --> LED
  LED -. "F019 design" .-> RAW["研究側: states / harvests / ledgers / paired worlds"]
  RAW -. "F019 design" .-> AUD["独立保存データ監査 / 改竄攻撃 / CI"]
  AUD -. "F019 design" .-> FIND["append-only findings<br/>結果はまだない"]
  RAW -. "禁止: off-world true state / oracle" .-> AGENT["将来の局所学習器<br/>現時点では未実装"]
~~~

Each paired arm receives the **same fresh original** resource field, not a field depleted by a different counterfactual arm. Within-step interpolation is an event ordering *approximation*, not F007's continuous physics. Historical diagrams remain time-scoped and are not rewritten to imply present F019 capabilities.

**F019 design-question update (pre-freeze, 2026-10-22):** this proposed causal pipeline primarily measures how a fixed connected/unconnected configuration changes *resource encounter time, claimant, depletion and per-cell ledger* under identical exogenous field forks. A jointly positive attachment incentive is only a secondary question, not a required outcome. The diagram and module boundary are unchanged. [Long-horizon dynamic-body note](research-notes/2026-10-22-temporary-morphology-and-resource-access.md) is separate ideation, **not** a dashed F019 component or implemented capability.


## F019 implementation-candidate wiring (2026-10-22, not yet adopted)

This section reflects code in **the separate F019 implementation PR**, not capabilities on main until reviewed/merged. The earlier dashed preregistration diagram is retained as historical intent. Researcher-only world data never reaches a future cell controller.

~~~mermaid
flowchart LR
  GEN["soma.f019.field_for | SHA256 fixed external patches"] --> SCN["512 prescribed scenarios"]
  SCN --> FORK["7 independent worlds per scenario"]
  FORK --> GATE["F018 AttachmentIntent / resolve_attachment step0"]
  GATE --> MOTOR["F007 1D positions, positive motor work"]
  MOTOR --> ENTRY["F019 closed-interval first entry and single winner"]
  GEN --> ENTRY
  ENTRY --> LEDGER["F002 per-cell acquire/spend and depletion"]
  MOTOR --> RAW["states.csv and link events"]
  LEDGER --> RAW
  RAW --> VERIFY["independent F019 raw-file geometry/physics/ledger oracle"]
  VERIFY --> ATTACK["rehash adversarial negatives and byte replay"]
  RAW --> SCORE["YY vs NN patch owner/time and outside payoff summary"]
  SCORE --> FIND["append-only findings: implementation candidate"]
~~~

The F019 module cannot change F007 trajectories via acquired energy in this frozen ample-initial-battery world; acquisition is posted after the step and the motor never needs the harvested supply. There is no biological metabolism, electrical contact or dynamic topology. Source SHA and full fields are auditor-only.


## F020 — Metabolic Closure: proposed step-causal boundary (2026-10-23; DRAFT, UNIMPLEMENTED)

[Issue #67](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/67) / [SPEC](../topics/F020-metabolic-feedback/SPEC.md) / [PLAN](../experiments/F020/PLAN.md) / [data proposal](DATA_CONTRACTS.md). **Dotted edges and F020 orchestrator are NOT implemented yet. F001–F019 are unchanged.**

```mermaid
flowchart LR
  CFG["Researcher-only config\nF019 trajectory-blind field, fixed motor, fixed YY/NN"] --> G["Proposed F020 step orchestrator"]
  L["F002 A/B integer-µJ balances at start of step"] --> G
  G -->|"A's current balance only"| M["F005 candidate positive-work / F007 one-step A motor gate"]
  M --> P["F007 ideal 1D next physical state"]
  P --> R["F019 first-path-entry / first-claim depletion"]
  CFG --> R
  R -->|"credit to actual A or B claimant at end of k"| L2["F002 next-step balances"]
  L2 -.->|"available only at k+1"| G
  P --> E["Source-bound research logs: physics, decisions, ledger, claims"]
  R --> E
  L2 --> E
  E --> V["Independent saved-data verifier / falsification"]
  V --> J["Append-only findings and researcher interpretation"]
```

**Counterfactual:** `feedback` makes valid k-end harvest available to the *same cell* for k+1 motor eligibility. `deferred_credit` quarantines the same acquisitions until the episode ends; compare YY/NN × modes under exactly matched exogenous field. World truth and absent-controller inputs are never exposed to a cell policy. This is still A-only externally effective force, no real B motor/energy sharing, learning or dynamic joining. The theory/calibration example is **not observed F020 simulation**.

**F020 pre-observation review correction (2026-10-23; design only):** Proposed upper battery 4,000,000 µJ is a harvest-independent trajectory-parity control (NN 2 J and YY 1 J motor work in four ideal steps). In the flow above, the `L2` edge is *only* spendable from k+1 for feedback; deferred claims instead go to per-cell pending/quarantined credits and post as F002 acquire events after k=4. Never infer B-to-A energy transfer. [Review and falsifiers](reviews/2026-10-23-F020-preobservation-audit.md). Diagram remains **UNIMPLEMENTED**.


## F020 implementation branch #69 — genuine chronological loop (2026-10-23; NOT main)

This realized implementation supplements the preceding **historical proposed-only F020 diagram**, without rewriting that pre-observation history. [Frozen protocol](../experiments/F020/FROZEN_V1.md) at `f3e3a4de4ff47677db575efaafe342655dede6c2`; [source](../soma/f020.py); [stacked PR #69](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/69). No formal adoption.

~~~mermaid
flowchart TD
  C["Canonical 32-seed F019 field + battery, sign and fee"] --> G["F018: frozen step-zero bilateral consent"]
  G --> L["F002: individual A/B available µJ after join fee"]
  L --> M["F005 charge: ceil of positive motor work from F007 trial"]
  M --> D{"A can afford motor from PRE-step balance?"}
  D -->|"yes"| X["F007 one-step motion with fixed A force; A F002 spend"]
  D -->|"no"| Y["F007 passive motion preserving inertia"]
  X --> H["F019 whole-segment path first-entry; one claimant per patch"]
  Y --> H
  H -->|"feedback"| A["F002 acquire to actual claimant AFTER step k"]
  H -->|"deferred_credit"| P["Claimant-specific quarantined pending until post k4"]
  A -->|"only next step k+1"| L
  P -->|"after k4 only"| Z["F002 acquire in original claim order"]
  A --> E["worlds.jsonl + SHA manifest"]
  P --> E
  Z --> E
  E --> V["No-soma-import independent saved-world reconstruction"]
  V --> S["Per-seed-block analysis + rehashed forgery tests"]
~~~

The agent never sees the experimenter's field map or fork outcomes; the only A actuation in this model remains the ideal external effective force. **No physical self-assembly or independent B actuator** is implemented.
