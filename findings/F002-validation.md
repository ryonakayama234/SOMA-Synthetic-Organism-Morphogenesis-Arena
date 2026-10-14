---
id: F002-VALIDATION
title: F002 エネルギー台帳の数値検証と独立レビュー修正
kind: findings
status: observed
updated: 2026-10-14
feature: F002
---

# F002 — 台帳検証結果とレビューによる訂正（2026-10-14 JST）

## 仮説と実験の境界

H002：整数µJによる入力・支出・移送損失の記帳と原子的な状態更新によって、全有効イベントの収支残差を厳密0 µJにできる。

**対象はPython会計モデルの整合性のみ。** 実機の送電・電池・運動コスト・身体構造の創発は未検証。

## 独立レビューで判明した初回実験の問題

PR #6で初回の20テストとA〜Fの実験はCIで成功したが、Codexレビューにより次の**4点が判明**した。

1. **P1**：A〜Cの当初の実験スイートが事前計画上の「A単体」でなく「A+Bの2セル」だった。各残量は計算どおりでも、保存境界を10 Jから12 Jにずらしていたため、当初の「予測と一致」という判定は実験計画に対して正当化できない。**修正版でA単体に戻して再実行**。
2. **P1**：Eの保存証拠が整数・容量・自己送金など9件のみで、仕様が要求する小数の拒否が未記録だった。小数・非有限値の4件を追加し、13件を再実行。
3. **P2**：Git SHAが呼び出し元のカレントディレクトリを使う可能性があった。実行モジュール自身のリポジトリを特定し、Git dirty状態・モジュールSHA256をmanifestに追加。
4. **P2**：energy.svgは初期/最終だけで、計画した推移と内訳を示していなかった。イベントごとの推移プロット・会計内訳・先頭スナップショット表を追加。完全な時系列はCSVで保持。

**以前のCI実行とartifactは履歴として残す。訂正後の結果で上書きしない。**

## 訂正後にGitHub Actionsで実測した結果

- 修正コードSHA：`f28b60ff30fb15d8f1160afbd15236cb721488f1`。
- [F002 CI run #38430103190](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38430103190)：**success**、Python 3.11で **21テスト合格（F001 9・F002 12）**。A〜Fを実行し結果を保存した。
- [F001回帰 CI run #38430103226](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38430103226)：**success**。
- CI artifact：`F002-A-F-evidence`、ID `11830128744`。各runの`config.json`、`events.csv`、`balances.csv`、`energy.svg`、`manifest.json` と `E-invalid-events.json`、`comparison.json` が保存される。
- ランダム500取引の決定論的再実行・容量範囲・収支残差0 µJを単体テストで確認。乱数seed `20261014`。

| 条件 | 再実験での観測値 | 残差・拒否 | 判定 |
| --- | --- | --- | --- |
| A：無入出力（**A単体**） | A=10 J | 0 µJ | 計画と一致 |
| B：5 J取得（**A単体**） | A=15 J | 0 µJ | 計画と一致 |
| C：3 J支出（**A単体**） | A=7 J | 0 µJ | 計画と一致 |
| D：A→Bに3 J・効率80% | A=7 J、B=4.4 J、未着損失0.6 J | 0 µJ | 計画と一致 |
| E：不正入力 | 13ケースを拒否、元stateは不変 | 不正操作は拒否 | 計画と一致 |
| F：3 µJの50%移送を一括 | B=2,000,001 µJ、未着損失2 µJ | 0 µJ | 予測どおり |
| F：1 µJを3回送る | B=2,000,000 µJ、未着損失3 µJ | 0 µJ | 予測どおり |

### 修正前の履歴（削除せず保持）

- 旧コードSHA：`e0defe10a38e148b0ef6cb1fd8a24bb7b4f0c1d8`。旧[F002 CI run #38424989145](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38424989145)とartifact `11827224188`。
- 旧A〜CはB=2 Jのセルを含み、結果はそれぞれ`{A: 10 J, B: 2 J}`、`{A: 15 J, B: 2 J}`、`{A: 7 J, B: 2 J}`。当該設定における数値計算は正しかったが、**事前に固定した単体セル実験ではなかった**。
- 旧Eは9ケースのみ。こちらも計画の非整数入力拒否を保存実験で実証していなかった。

## Wolframによる独立した代数検算

整数µJと移送効率bpsの定義から、`received=floor(sent*eta/10000)`、`loss=sent-received` と置けば、`A+B=(A-sent)+(B+received)+loss` は記号的恒等式。10 J/2 J、送出3 J、効率80%の場合はA=7 J、B=4.4 J、損失0.6 J、残差0。3 µJ/50%は一括受取1 µJと3分割受取0 µJの差を確認。

イベント分割依存を残したまま損失を記帳するため、**計算上の保存式が正しいことと、物理的コストが正しいことは別**である。

## 限界と判定

- 残差0の検証は、整数台帳の内部整合性を確認したもの。実機の電池・送電・モーター損失を検証していない。
- 丸めによって取引の分割方式が到着量を変える。転送回数が人工的な「有利・不利」の原因になり得るため、将来の最適化・身体形成実験では量子化依存を制御・介入して確認する。
- 外部供給を有限資源としていない。セル間の数値送金は機械結合や物理電線ではない。
- F001の運動モデルとF002電力量はまだ別境界。F001解析解修正のPR #5に別件の未解決指摘がある。

**結論：レビューで修正した実験条件において、H002は会計ソフトウェアモデルの範囲で支持。物理・創発に関する主張は保留。**

[再現方法](../experiments/F002/README.md) / [SPEC](../topics/F002-energy-ledger/SPEC.md) / [事前計画](../experiments/F002/PLAN.md)。

## 再レビューでの追加指摘（2026-10-14 JST）

Codexによるcommit `0a87fae` への再レビューでは、新たに**P2が3件**見つかった。

1. `experiment_id` にXML禁止文字（例：U+0000）を含めると、`escape()`では防げず無効な`energy.svg`が保存される。→ XML 1.0文字集合に対する入力検証を追加し、正当な日本語・絵文字・記号は実際のXMLパーサーで読めること、禁止文字は保存前に拒否されることを新規テストで検証。
2. SPECで修正後のCIへのリンク表示が旧実行番号になっていた。→ リンク文字列も `38430103190` に統一。
3. ARCHITECTUREのEの監査件数が古い9件だった。→ 13件に修正。

以下の追加検証を実施した。以前のCI、特に失敗した中間CIは削除しない。

### 追加実験（SVGの入力条件とデータ保存）

- 修正対象コード `0ec53c911104cc17f5e0d0e2c882d4fa40174197`。
- [F002 CI #38433251595](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38433251595)：**success、全22テスト（F001 9、F002 13）合格**。A〜F実験および不正取引13件を再実行し、保存残差0 µJ。
- [F001回帰CI #38433251666](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38433251666)：**success**。
- F002の追加アーティファクト `F002-A-F-evidence` ID `11832217045`。
- 新規の `test_svg_experiment_id_xml10_character_contract`：日本語・絵文字・XMLエスケープ対象の記号・許容制御文字を含むIDは実際のXMLパーサで有効なSVGに復元でき、U+0000、U+0001、U+000B、サロゲート、U+FFFE/U+FFFFは**結果ディレクトリ作成前に拒否**される。
- **途中のCI失敗も保存**：中間コミット`85024454ec525fda3eec69422b788b56ecbf3675`の[F002 #38433163952](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38433163952)とF001 #38433163919は、新設テスト中の禁止文字を文字列リテラルのバックスラッシュとして誤表現していたため失敗。実際のUnicodeコードポイントを`chr(...)`で構成するように修正し、再検証で合格した。これは台帳会計の破綻ではなく、検証コード側の不備。
- Wolfram Languageは、XML 1.0文字境界の16サンプルの許容判定、3 J・80%移送の受取2.4 J／損失0.6 J／残差0 µJ、3 µJの50%一括と分割の差1 µJを独立に確認した。

**判定**：実装済みの整数µJ台帳の収支整合性と、現在の実験データ出力の入力制約は、指定した計算モデル・CI条件の範囲で支持。実機エネルギー保存・身体創発は未検証。

## 保存証拠に関する追加レビュー（P1：対照Fの再実行）
Codexが2026-10-14のPR #6レビューで、旧`comparison.json`にF-bulk／F-splitという異なる条件の差しか残されず、「同一条件・同一イベント列の再実行一致」をA〜Fの生証拠から監査できないことを指摘した。これを妥当な**証拠不足**と判定。単体テストの500イベント決定論的再生と、A〜Fの保存証拠に求められる独立再実行は別の検証である。

そのため旧実験の予測や結果を改変せず、F-bulkとF-splitをそれぞれ全く同じconfig（ID・seed・セル構成・イベント順）で2回ずつ実行して`F-bulk-replay/`と`F-split-replay/`を追加し、各runの5ファイル（設定／events／balances／energy SVG／manifest）をバイト・SHA256で比較する処理を導入した。監査結果は`comparison.json.f_replay_checks`に保存し、異なる場合はCIを失敗させる。

**実測確認（2026-10-14）**：commit `7b61e0c068ab3f2cb4cb1a408b5306141b63b43d` の [F002 Actions #38507338366](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38507338366) は **success・23テスト全件合格（F001 9、F002 14）**。ログ上の `comparison.json.f_replay_checks` で F-bulk と F-split の双方が `same_config=true`、`byte_identical=true`、5成果物の一致SHA256を記録。保存証拠 [artifact `F002-A-F-evidence` ID 11868571427](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38507338366) に初回・再実行の両フォルダを保存。[F001回帰 #38507338216](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38507338216) も成功。**数値の同条件再現性は今回の実行・保存条件で支持**される。従前の保存実験と中間失敗は履歴として保持し、同条件の数値再現性を実機のエネルギー・身体創発へ一般化しない。


## PR #6 の最適化モード検査（2026-10-14）

- 独立Codexレビューが、`experiments/F002/run_suite.py` のA〜C・D・Fの期待値と残差の検査に `assert` を使用しており、`python -O` / `PYTHONOPTIMIZE=1` では無効になると指摘した（P2）。
- 実験条件・期待値・台帳本体は変えず、`validate_expected_results()` 内の明示的な条件分岐と `AssertionError` に変更した。異常時は `comparison.json` の生成前に失敗する。
- `tests/test_f002.py` に最適化サブプロセスを起動する負例試験を追加。`__debug__ == False` を確認し、正常値は合格、A・B・C・D・Fの残量改変と会計残差の改変（計6パターン）は実行時例外で拒否されることを検証した。
- コードコミット `7a97d7a683fd0b38850ac92323efc07f1324f596` の [F002 CI #38533052570](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38533052570) は成功、Python 3.11で24テスト全件合格（F001=9、F002=15）、A〜F実験スイートも成功。[F001回帰 #38533052578](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38533052578) も成功。
- これは実験の合否判定に対する回帰防止であり、台帳の物理的妥当性や形態創発の検証ではない。既存の初回失敗・修正履歴・artifactは保持する。

## 対照Fの絶対予測と最新負例監査（2026-10-14）

- 最新Codex P2では、F-bulk／F-splitのB残量の**差が1 µJ**という旧検査だけでは、両B残量の同量のずれ、両A残量の破損、損失の破損を見逃すと判明。初期残量A=10,000,000 µJ・B=2,000,000 µJ、移送量3 µJ、効率50%をWolframで独立計算すると、**F-bulk: A=9,999,997 / B=2,000,001 / loss=2 µJ、F-split: A=9,999,997 / B=2,000,000 / loss=3 µJ**、いずれも会計残差0 µJ。分割・一括の受領量差は1 µJ。
- `validate_expected_results()` にFの**A・B残量と損失の完全な絶対予測**を追加し、差分検査と残差検査も維持。最適化実行`python -O`で、旧6負例に加えてFの両Bの同時+1、両Aの同時+1、F-bulkの損失+1、F-splitの損失+1の**追加4負例、計10負例**を拒否できることを検査。現物のA〜F出力も比較ファイルから直接照合する。
- READMEの進捗要約を **24テスト（F001=9 / F002=15）** に訂正。commit `67300f5d36a6d21c4dc16e7cf737ba80a205325d` の [F002検証 #38534904906](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38534904906) と [F001回帰 #38534904676](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38534904676) は成功、24テスト全件合格。追加負例は既存のテストメソッド内に置いたためテスト件数は増えていない。
- これは**ソフトウェア台帳と事前予測の照合**であり、物理的エネルギー伝送や身体構造の創発を実証するものではない。旧実験証拠・失敗履歴は保持する。

## PR #6 全測定量の事前予測照合（2026-10-14）

- commit `f21184a` に対する独立Codexレビューで、新規P2として **B-acquireの`acquired_uj`、C-spendの`spent_uj`、D-transferの`loss_uj` を最終残量と独立に検査していない**こと、および**READMEの固定CIリンクが古い**ことが指摘された。従来の検証は残量・残差・Fの損失まではカバーしていたが、実験manifestの他のフロー項目が正しく記録されたという証拠として不十分だった。
- 変更前に固定したA〜Fの事前予測を保持し、Wolframで次の整数計算を独立検算した。B: 取得`5,000,000 µJ`・最終A`15,000,000 µJ`、C: 支出`3,000,000 µJ`・最終A`7,000,000 µJ`、D: 損失`600,000 µJ`・最終A/B`7,000,000/4,400,000 µJ`、残差はいずれも0。F: 一括損失2 µJ、3分割損失3 µJ、受領差1 µJ。
- `validate_expected_results()` で **A-rest/B-acquire/C-spend/D-transfer/F-bulk/F-split** の各runの `final_balances_uj`、`acquired_uj`、`spent_uj`、`loss_uj`、`residual_uj`、`event_count` を個別の絶対期待値と比較する。最適化実行`python -O`でも省略されない明示的な失敗判定を使う。実験条件・数学モデル・イベントの挙動は変更していない。
- `tests/test_f002.py` の`python -O`負例試験を **49回の負例実行（重複を除く42種類の測定値破損）** に拡張。フロー量、ゼロであるべき項目、イベント数、両セルの残量、会計残差を個別に破損させ、すべて拒否する。Fの対照差のみを保って絶対値を変える従来の負例も維持した。テストメソッド数は増やしていないので計24件（F001=9、F002=15）。
- `comparison.json.runs` は従来の最終残量・損失・残差に加えて取得量・支出量・イベント数を記録し、`docs/DATA_CONTRACTS.md`へ同期した。READMEの「CI確認先」は過去の特定runではなく、現在のPR HEADに追随する [PR #6 Checks](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/6/checks) に変更（古いCIログは本記録に残す）。
- コード・テストコミット`72a40f8de3db1f3369859923091ad387789aef0e`に対する [F002 CI #38546596268](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38546596268) と [F001回帰 #38546596161](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38546596161) は成功。途中のコードのみコミット`300c0e6`は、テストの旧fixtureと新しい必須項目の不一致によってCI失敗となったが、同じPRでテスト更新を加えて解消した。この中間失敗も隠さず、Actionsの実行履歴に保持する。
- 上記が示すのは**事前登録したソフトウェア台帳モデルの出力値と保存記録の一致**まで。現実のエネルギー伝送・自律生存・身体形成は別課題であり、この数値結果からは実証されない。

## PR #6 負例件数の重複監査（2026-10-14）

- `94e2242` に対する独立レビューで、「49種類」の記載に重複が含まれると判明。正しくは **49回実行・42種類の異なる改変**。過去の全測定量検証の表記を訂正し、当時のCIリンクは保持した。
- 重複7件は、A-rest/B-acquire/C-spendのA残量、D-transferのB残量と残差、F-bulk/F-splitの損失の各+1改変。全フィールド走査は39種類、旧10負例のうち7件がそれと同一なので、`39 + 10 - 7 = 42`。F-bulkのB残量-1と、両FのAまたはB残量を同時に+1する3種類は走査と異なる。
- `python -O`サブプロセス内で全改変結果をキー順固定のJSONに正規化して重複を数え、49実行・42種類でなければ明示的な例外を出す。従来の負例49回は引き続きすべて拒否されることを確認する。台帳本体・実験条件・予測値は変わらない。
- Python 3.12.14のローカル実行で24テスト（F001=9 / F002=15）合格。A〜Fスイートを`python -O`でも再実行し、Eの13不正条件拒否、残差0、F-bulk/F-splitそれぞれの再実行5成果物のバイト・SHA256一致を確認した。最新コミットのCIは[PR #6 Checks](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/6/checks)で確認する。

- **GitHub CI実測**：修正テスト・記録 `d72ce101a7766ad71a74f71016dbe19bbbc8db39` に対する [F002 CI #38554395269](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38554395269) は成功。Python 3.11で24テスト合格、A〜F実行・artifact保存も成功。[F001回帰 #38554395287](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38554395287) も成功した。

## マージ前監査：生成物によるGit dirty誤認（2026-10-15）

- `a41f473`の独立レビューP2を再現。クリーンな統合作業コピーで`.review-suite-output-before`に出力すると、Aのみdirty=false、B/C/D/Fとreplayはtrueとなった。原因はrunごとのGit status取得が、先行runの未追跡生成物をコード変更と誤認すること。
- スイート開始時・出力作成前にGit SHA/dirtyを一度取得し、全runとreplayの`save_run`へ渡す。単独save_runは従来どおり自身で保存前に取得する。台帳式や事前実験条件は変更しない。
- 新規回帰試験で隔離したGitリポジトリを作り、クリーン・実行モジュールの未コミット変更ありの2条件を`python -O`で実行。Git未除外の出力ツリーで、全8 manifestに開始時のfalse/true、同一SHA、実行モジュールchecksumが残ることを確認。単なるdirty強制falseによる隠蔽を排除した。
- ローカルPython 3.12.14で**25テスト（F001=9、F002=16）合格**。旧CIの24件は当時の結果として保持。現行CIは[PR #6 Checks](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/6/checks)で追跡する。
- Wolfram LanguageでDの残量7,000,000/4,400,000 µJと損失600,000 µJ、F一括・分割の残量と損失2/3 µJ、3条件の残差0を独立に再計算し、事前予測と一致した。コード出自のバグは数値モデルの変更を要しない。
- **両PRのローカル統合検証**：main `275dcbf` にPR #5 `9879b25` とPR #6 `a41f473`を順に統合し、本節の修正コードを適用。コード競合なし、33テスト（F001=17/F002=16）全件合格。F001 A〜E、F002 A〜F（`python -O`）の再実行も成功。これはローカルの統合候補の検証であり、mainのマージ実行結果ではない。
