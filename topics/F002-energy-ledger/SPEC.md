---
id: F002
title: 固定小数点エネルギー台帳
kind: feature_spec
status: observed
updated: 2026-10-13
issue: 2
depends_on: [F001]
next: [F003]
---

# F002 — エネルギー収支を一つの台帳で検証する【実装済み・数値検証済み】

## 研究上の位置づけ
SOMAは身体形態を先に定めず、相互作用から機能を発見する。F001は外力を受ける単体セルの1D運動を数値検証済み。F002では資源獲得・支出・数値上のセル間移送を検証できる最小の**会計的なエネルギー台帳**を導入する。

**今回の唯一の能力**：任意の有効なイベント列について、セル内に残るエネルギーと外部供給・支出・移送損失の収支を説明する。

機械結合・ポート・電力伝送回路、運動電力モデル、モーター効率、電池の電圧・温度、学習、報酬、生存、進化は **対象外**。F001の `force_n` は外部から与えた力であって電池の出力ではない。F001の `x,v` とF002の蓄積電力量を暗黙に結びつけない。物理エネルギーの保存則を実機について実証したわけではない。

## 問い・仮説・反証条件
- 問い：外部からの獲得、支出、セル間移送が任意の順で起きても、保存境界を明示した収支が破れないか。
- H002：すべての取引を固定小数点・原子的に扱えば、有効なイベント列の計算上の収支残差は **厳密に0 µJ** となる。
- 代替仮説：数値丸め、容量超過や部分更新によって残差が発生する。イベント分割の仕方により**到着電力量が変化する**可能性はある（単位丸めの設計依存）。
- 反証：有効イベントで残差非ゼロ、負残量／容量超過、無効イベントによる部分更新、同条件再実行時の結果不一致が一件でも生じる。
- 検証範囲：これは**実装の数学的・計算的整合性**の試験。自然界の電力伝送効率や移動性能は検証しない。

## 計算単位・状態
- 電力量は整数 `energy_uj` (µJ)。1 J = 1,000,000 µJ。内部では浮動小数点Jを使わない。
- セルは `cell_id`、`capacity_uj` (>0)、`balance_uj` (0以上容量以下) を持つ。すべて同じセル型を使用する（役割の事前割当なし）。
- 外部からの `acquire` はエネルギー境界への明示された入力であり、無限資源を物理的に仮定するものではない。供給上限・資源枯渇は後続研究。
- `spend` は系外支出として台帳へ記録。電気回路や実際の運動に必要な仕事を確定するものではない。
- `transfer` は**数学的な台帳間移送**で、機械的な結合が成立したことを意味しない。
- 整数効率 `eta_bps` は0〜10000の範囲（10000 = 100%）。`received_uj = floor(sent_uj × eta_bps / 10000)`、`loss_uj = sent_uj - received_uj`。損失には整数単位への切捨て差額も含まれ、その意味をログに明記する。
- 入出力のイベント順 `event_index` は離散的な取引順序であり、F001の時間刻み`dt_s`ではない。
- 無効な負値、ゼロ以下のイベント額、非整数、範囲外の効率、残量不足、受取先の容量超過、自己送金、存在しないセルは**全体を変更せず拒否**する。ゼロ移送は拒否。
- 実装時に任意精度整数の入出力・CSV/JSON表現を確認し、過大入力はあらかじめ制限する。表示用Jへの変換は可視化側だけ。

## 不変条件とモデル
開始残量合計 S0、外部からの取得累計 A、セルからの支出累計 C、転送で未着となった損失累計 L、現残量合計 S とすると

`residual_uj = S0 + A - (S + C + L) = 0`

任意のセル i について `0 <= balance_uj[i] <= capacity_uj[i]`。

これらは「セル内に貯めた量＋台帳で追った系外流出」を含む保存**会計**であり、全宇宙のエネルギーを表す式ではない。

## インターフェース案（必要になって初めて詳細化）
```python
state = LedgerState(cells={"A": (10_000_000, 20_000_000), "B": (2_000_000, 20_000_000)})
state2, entry = apply_event(state, Transfer(source="A", target="B", amount_uj=3_000_000, eta_bps=8000))
assert entry.received_uj == 2_400_000
assert entry.loss_uj == 600_000
assert state2.residual_uj == 0
```
上記は**仮のAPI**であり、実装済みのシグネチャではない。更新は原子的で、ログ出力や可視化と独立した純粋な計算部分を優先する。依存はPython標準ライブラリ中心。

## 実験と受入基準
| ID | 実験 | 事前予測 |
| --- | --- | --- |
| A | 10 Jのセル、取引なし | 10 Jを維持・残差0 |
| B | 外部から5 Jを獲得（容量内） | 残量が5 J増え、外部入力に5 Jを計上 |
| C | 3 Jを支出 | 残量が3 J減り、支出3 Jを計上 |
| D | A=10 J、B=2 J、Aから3 J・効率80%で移送 | A=7 J、B=4.4 J、損失0.6 J、残差0 |
| E | 残量不足・容量超過・不正数値・自己送金 | 例外として拒否し、残量も台帳も不変 |
| F | 同条件再実行・イベント分割と丸めの影響 | 決定論的に再現。分割時の到着量の変化は記録・解釈 |

- 結果の採否は実行前に固定。**すべての有効イベント後の残差0 µJ**、容量不変条件、拒否時の原子性、再実行の決定性を確認する。
- 無作為生成した有効イベント列についても残差0を検査する。乱数を使う試験ではシードを保存する。
- イベント分割が完全等価になることは要求しない：3 µJを効率50%で一括送ると1 µJ到着、1 µJずつ3回ならそれぞれ0 µJ到着（端数は損失として記帳）。この量子化誤差は失敗として隠さない。
- Wolfram Languageで理想的な整数移送例の代数的不変性を独立検算済み。**Python実装済み・GitHub Actions実行成功・物理的検証は未実施**。

## 出力物（実装と同じPRで必要）
- `soma/f002.py`：台帳更新・検証（今回の一能力）。
- `tests/test_f002.py`：A〜F、境界条件、無効イベントの原子性、生成イベント列。
- `experiments/F002/`：再実行用設定、実行スクリプト、README。
- `runs/F002.../` (GitHub Actions artifact等)：`config.json`、`events.csv`、`balances.csv`、`energy.svg`、`manifest.json`。既存runへの上書き禁止。コミットSHA、スキーマ、seed、ファイルchecksumを保存。
- `findings/F002-validation.md`：実際の観測結果・反証・留保。
- `docs/ARCHITECTURE.md`、`docs/DATA_CONTRACTS.md`、`README.md`：実装済み部分のみを反映して同期更新。
- GitHub ActionsでF001回帰テストとF002テスト・実験を実行。独立レビュー後にPR統合。

## 図・データ・証拠の同時更新
一機能を実装したPRで、**①動くコード ②システム図 ③データ契約 ④実験記録 ⑤README進捗** の整合性をレビューする。新しい実装だけを先行マージしない。詳細：[研究運営](../../docs/RESEARCH_PROCESS.md) / [データ構造](../../docs/DATA_CONTRACTS.md) / [F002実験計画](../../experiments/F002/PLAN.md) / [実験記録](../../findings/F002-validation.md)。

関連：[Issue #2](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/2)。F001数値安定性の[PR #5](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/5)は未統合・レビュー指摘未解決（2026-10-13確認）。

## 実装・初回数値実験の結果（2026-10-14 JST）

- 実装：`soma/f002.py`、`tests/test_f002.py`、`experiments/F002/run_suite.py`。セル・状態は不変、`apply_event` は新しい状態とEntryを返す。
- Python 3.11 / [初期修正CI #38430103190](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38430103190)では、F001・F002あわせて**21テスト合格（F001=9・F002=12）**。追加のXML境界テストを含む**22テスト**の成功は後段の [CI #38433251595](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38433251595) の観測であり、同一runの成果と混同しない。F002 A〜Fの全有効イベントで`residual_uj=0`。
- 乱数seed `20261014` の500イベント列について、残差0・状態範囲・完全な再実行一致。
- E：13種類の不正操作（小数・非有限値を含む）を拒否し、元の状態を保持。
- F：3 µJ・50%送金を一括で実行した場合はBが1 µJ受領、3回に分けた場合は0 µJ。どちらも残差0。量子化差は確認されたモデルの制約。
- D：Aが7,000,000 µJ、Bが4,400,000 µJ、損失600,000 µJ。Wolframの整数検算と一致。
- 出力証拠：[GitHub Actions #38430103190](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38430103190)、artifact #11830128744。レビュー指摘対応を含むコードSHA `f28b60ff30fb15d8f1160afbd15236cb721488f1`。
- **科学的判定**：会計上の整数不変量と再現性に関する仮説H002は、今回の実装および検証条件の範囲で支持。実世界の電池・アクチュエータ・接続の物理妥当性は未検証。

[詳しい結果・数値](../../findings/F002-validation.md)。

### 独立レビューからの研究プロトコル修正
PR #6のCodexレビューで、初回A〜Cの2セル設定が事前計画の単一セルと不一致であると発見された。条件を変更していたことを見落とした初回判定を訂正し、A〜Cを1セルで再実行した。Eの小数・非有限値の拒否証拠、実行コードのGit/dirty/SHA256 provenance、推移・内訳SVGを追加。**初回ログを隠さず履歴として残す**。詳細は[検証ノート](../../findings/F002-validation.md)。

### 2回目のレビューからの修正と追加テスト（2026-10-14）
Codexの2回目のレビューで、XML禁止文字を含む実験IDから不正なSVGが生成される可能性、SPECの修正版CI番号の表示不一致、ARCHITECTUREの拒否件数の記載誤りを指摘された。これらを修正し、**XML 1.0の文字制約を入力時に確認**する新たなテストを追加した。修正版の[CI run #38433251595](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38433251595)で**計22テスト（F001=9, F002=13）合格**し、実験A〜Fと13件の拒否実験が成功。WolframでXML文字境界の16例と移送会計の式を独立に検算。初回テストの失敗履歴は[検証ノート](../../findings/F002-validation.md)に残す。

## 初期構想との対応（2026-10-14追記）

[IDEA.md](IDEA.md) は当時の図・仮説を残した**履歴資料**（`id: F002-IDEA`）であり、実装状態の根拠は本SPEC（`id: F002`）と実験記録で一意に管理する。構想段階の「運動・待機の消費」や「結合を介した移送」はまだ実装されていない。

### 対照Fの同一イベント列の再実行証拠（独立レビューP1への対応）
追加レビューにより、旧A〜F保存証拠には一括・分割の**異なるイベント列**の比較しかなく、各イベント列の同一configの再実行結果が保存されていないと指摘された。F-bulkとF-splitをそれぞれ同じconfigで独立にもう一度実行し、`F-bulk-replay/`と`F-split-replay/`に全成果物を記録する。5つの生ファイルが初回実行とバイト単位・SHA256で一致した事実を`comparison.json.f_replay_checks`に記録し、不一致時は実験を失敗させる。事前に固定した計算条件・予測は変更していない。

### 保存可能な再現性の実測結果（2026-10-14）
commit `7b61e0c068ab3f2cb4cb1a408b5306141b63b43d` に対する [F002 CI #38507338366](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38507338366) は**success：計23テスト（F001 9・F002 14）**。`F-bulk`と`F-bulk-replay`、`F-split`と`F-split-replay`の各5成果物がバイト単位とSHA256ですべて一致したことを `comparison.json` に保存した。F001回帰の[CI #38507338216](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38507338216)も成功。artifact：`F002-A-F-evidence` ID `11868571427`。これはFの同一条件再実行を確認した時点の証拠（旧CIと当時の不備・訂正履歴は保持）。最適化モード下の受入検査は次節で追記する。

### 受入条件が最適化モードで無効化されないことの検証（2026-10-14）

CodexレビューP2を受け、A〜C・D・Fの最終残量と会計残差の検査を、最適化で除去される`assert`から、明示的な条件分岐による検査へ変更。正常実験と、6種類の異常結果を注入して`python -O`で拒否される負例試験を追加した。コードコミット`7a97d7a`の[F002 CI #38533052570](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38533052570)は24テスト合格、[F001回帰 #38533052578](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38533052578)も成功。実験予測値や数学モデルは不変。証拠と限界は[findings](../../findings/F002-validation.md)に記録。

### 対照Fの絶対期待値の固定と追加負例（2026-10-14）

Codexレビューの追加P2により、F-bulk／F-splitのB残量差1 µJの照合だけでは両結果が同時に誤る回帰を検出できないと判明。受入条件として、初期A=10,000,000 µJ・B=2,000,000 µJに対して、一括F-bulkの**A=9,999,997 / B=2,000,001 / loss=2 µJ**、3分割F-splitの**A=9,999,997 / B=2,000,000 / loss=3 µJ**をそれぞれ完全一致で要求する。残差0、到着量差1 µJ、同一config再実行の生ファイル一致も維持する。

最適化モード`python -O`で、既存6件の負例に、両FのB残量同時+1、両FのA残量同時+1、F-bulk損失+1、F-split損失+1を加えた**計10負例**を検証。READMEを**現行24件（F001=9、F002=15）**に同期した。[F002 CI #38534904906](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38534904906) と [F001回帰 #38534904676](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38534904676) はともに成功（24テスト全件合格）。テスト関数数を増やさず負例を拡張している。算術期待値はWolframで独立に確認。経緯と限界は[検証ノート](../../findings/F002-validation.md)に追記し、旧CI証拠も保持した。

### A〜Fの全計測値の厳密照合とCI参照先の継続性（2026-10-14）

追加Codex P2を受け、Fの絶対値だけでなく、**B取得量5,000,000 µJ、C支出量3,000,000 µJ、D損失量600,000 µJ**を含む、A・B・C・D・F-bulk・F-splitの各runの最終残量、取得・支出・移送損失累計、会計残差、イベント件数を事前予測と全項目一致で判定する。実験設定・モデル・予測は変更していない。比較概要`comparison.json.runs`にもこの6項目を残して証拠を追跡可能にした。出力形式の契約は[DATA_CONTRACTS](../../docs/DATA_CONTRACTS.md)。

`python -O`下で49回の負例実行（重複を除く42種類の数値改変）を拒否する負例試験を既存のテストメソッドに追加したため、テストは引き続き**計24件（F001=9、F002=15）**。[F002 CI #38546596268](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38546596268)と[F001回帰 #38546596161](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38546596161)が修正コードとテストに対して成功。以後のHEADのCIは [PR #6 Checks](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/6/checks) を入口として参照する。失敗履歴を含む経緯は[findings](../../findings/F002-validation.md)に保存。

### 負例件数の監査（2026-10-14）

旧表記「49種類」は重複7件を含んでいたため、49実行・42種類へ訂正。最適化サブプロセスでJSON正規化による実件数・重複除外件数の照合を行い、件数の誤記を防ぐ。ローカルPython 3.12.14で24テスト合格、最適化A〜F再実行も成功。重複の内訳と履歴は[検証記録](../../findings/F002-validation.md)の「負例件数の重複監査」を参照。最新コミットのCIは[PR #6 Checks](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/6/checks)から確認する。
