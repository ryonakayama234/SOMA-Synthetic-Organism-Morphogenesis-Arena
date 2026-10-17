---
id: FIND-F007
title: F007 実験記録・レビュー・採否
kind: finding
status: adopted_limited
updated: 2026-10-17
related: [F007, EXP-F007]
---

# F007 — 結合二セルの片側駆動・電池支出：検証ノート

## 研究状態（2026-10-17）
**未実装／実験未実施／独立監査未実施／正式採否未決定。** この設計PRでは科学的な観測結果も、GitHub Actions合格も主張しない。mainの既存F001〜F006とログは変更しない。

- 研究課題：[Issue #19](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/19)
- 仮説・受入基準：[SPEC](../topics/F007-linked-motor-work/SPEC.md)
- A〜F前登録：[PLAN](../experiments/F007/PLAN.md)
- 図・提案データ：[ARCHITECTURE](../docs/ARCHITECTURE.md) / [DATA_CONTRACTS](../docs/DATA_CONTRACTS.md)

## 事前参照（**Wolfram理論値。SOMAの実測値ではない**）
等質量、Aモーター2N、dt=0.25s、1s、drag0なら非結合A支出2,000,000µJ／結合A支出1,000,000µJ、結合Bの変位0.625m、T_B=+1N。位置は半陰的Eulerの**離散値**。現実の効率、結合する利益、知能や創発の測定結果ではない。

## 後続実装後に記録する欄
| 事前対照 | 実験実行状態 | 観測・理論との差 | 判定（支持／反証／不明） | 生証拠 |
| --- | --- | --- | --- | --- |
| A 非結合 | 未実施 | 未測定 | 未実施 | なし |
| B 結合 | 未実施 | 未測定 | 未実施 | なし |
| C A残量0 | 未実施 | 未測定 | 未実施 | なし |
| D B外力のみ | 未実施 | 未測定 | 未実施 | なし |
| E 中途切断 | 未実施 | 未測定 | 未実施 | なし |
| F 再現/拒否/改変 | 未実施 | 未測定 | 未実施 | なし |

## 採用ゲート
- [x] 研究問い・対立仮説・境界を提案
- [x] Wolfram独立離散参照を実験前に記録
- [x] システム図・提案データ契約・事前実験計画を設計ブランチに同期
- [ ] 仕様の独立事前レビュー
- [ ] 別PRで最小実装・保存・検証
- [ ] 全回帰、A〜F全証拠、再現性、改変検査、CI最終HEAD確認
- [ ] 別視点の数理・実装・生ログ監査
- [ ] 結果に対するユーザーの明示的な研究上の採否決定
- [ ] 採用する場合のみmain統合（不採用・不明の場合も記録を残す）

**既知の注意**：F005の有効モーター力には地面/壁等の明示的な反力元がなく、実機の駆動・推進ではない。F006が示したdt依存の支出・拒否があるため、研究結果を複数形態の省エネルギー性や生存競争へ外挿しない。失敗や想定外の結果も生ログとともに残す。


## 2026-10-17 実装前のモデル整合性再計算（研究ログではない）

設計PR #20の既存A/B/E予測値を、Wolfram Languageの厳密有理数による独立式で再計算した。A: 終速度2m/s、変位5/4m、正仕事2J。B: 終速度1m/s、共有変位5/8m、正仕事1J。E: A終速度3/2m/s、終位置13/16m、A正仕事5/4J、B終位置15/16m。**事前参照と一致したが、SOMAの試験合格や実測を意味しない。**

Fの対照も実装前に具体化した（[PLAN](../experiments/F007/PLAN.md) のF-01〜F-06）。F-01の逐次電池拒否では、初回のみ62,500µJ消費して結合のまま惰走する参照を得た。F-04の速度反転では、正仕事9/16Jと符号付き仕事1/2Jを区別した。

**設計上の監査注意（未解消ゲート）**：
1. F005の力は地面や壁の反力を明示しない有効外力。実機の自力推進・結合の適応利益に外挿しない。
2. F003位置の半陰的EulerとF005仕事の速度補間を混同しない。時間刻みごとのµJ切上げ・all-or-nothing拒否の感度は残る。
3. F002 2セル台帳とF003剛体リンクは異なる状態空間。Aのcandidate/applied、Bの外力、リンク力、各セル残高を監査可能にする。
4. 補強したF-01〜F-06は**事前追加**であり既存A〜Eの事後修正ではない。実装PRで独立オラクル、生ログとCIを確認するまでは仮説は未検証。

これは同一支援AIによる事前のクロスチェックであり、**外部第三者による独立承認ではない**。実装・実験・正式採用はいずれも未実施／未決定のまま。

## 実装ブランチ上の候補（2026-10-17・CI監査前、正式採用前）

本節は上の**設計PR時点の「未実装」記録より後の状態**。F001〜F006採用済みAPIは変更せず、F007の計算・保存・独立オラクル・A〜Fスイート・Python 3.11/3.12 CIを実装ブランチ上に提案した。実行証拠とCIは**未確認**であり、ここで「仮説支持」や正式採用を主張しない。

- `soma/f007.py`: `f007.v1`入力検証、F001のsemi-implicit Euler、F005の正仕事、F002の2セル台帳、Aの電池拒否、リンク切断とイベントを接続。
- `experiments/F007/verify.py`: 生CSVとspend/linkイベントを独立の分数積分・離散式で全行チェック（同一支援AIによる別実装であり、外部第三者承認とは別）。
- `experiments/F007/run_suite.py`: A〜EとF-01〜04の9run、F-05不正入力12件、F-06保存CSV改変とbyte再生を検証する予定。
- `tests/test_f007.py`, `.github/workflows/f007.yml`: 全回帰/最適化・Python3.11/3.12のCI候補。
- `docs/ARCHITECTURE.md`, `docs/DATA_CONTRACTS.md`, README/AGENTS: 同じPR上で同期。

今後のゲート：実際のCIを確認してログから結果を記入→数式/境界/出自の独立レビューと修正→研究者の明示採否。履歴は上書きせず追記する。

## 2026-10-17 初回F007 CIの実測と追試待ち（PR #21）

**初回HEAD `20ebfe664f45c825d9f19e64473525cf668f8d15` で観測した結果**（[GitHub Actions #39012438734](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39012438734)）。

| 対照・検査 | 初回CI観測 | 判定の範囲 |
| --- | --- | --- |
| F007 A〜E | 保存9runに含まれ、全時刻の独立離散オラクルで照合 | 事前登録の離散数理と一致 |
| F-01〜F-04 | 電池途中枯渇・無償保持・外力のみ・速度反転を含めて一致 | 理想モデル内の支持 |
| F-05 | 不正入力12件を拒否 | 限定された負例で一致 |
| F-06 | 既存CSV改変検出、58ファイルの再実行byte一致 | 再現性・改変検出が成立 |
| 既存全回帰 | Python 3.11/3.12で各120テスト合格、F007の最適化8テストも成功 | 初回HEADのみ |
| 完全生証拠 | [3.11 artifact #12092624115](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39012438734/artifacts/12092624115) / [3.12 artifact #12093860051](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39012438734/artifacts/12093860051) | ZIP公開は確認、外部第三者の全バイト監査は未完了 |

**Wolfram追加の独立参照**：F-01は初回62,500µJを使い、後続3ステップはAモーターを停止して惰走し、A終点1/4m、B終点3/4m。F-04は正仕事9/16J、符号付き仕事1/2J、最終共通速度−3/4m/s。F-03はAの電池0でもB外力だけで共通加速度1m/s²、B側リンク力−1N。Wolfram参照とCI結果を区別する。

**初回CI後の監査改善**：保存manifestに書かれた任意の出自をそのまま信頼しないよう、`audit_run(..., trusted_origin=...)` を追加。GitHub checkoutから得た期待Git identityと依存ソースのSHA256を照合し、suite runner・別オラクルもhash対象に含めた。出自を書き換える負例テストを追加したため、**上記120テストの成功を修正後HEADへ流用しない**。最終HEADのCI、改変検査、成果物と独立監査を再確認する。

既知の持越し：通常の`save_run`とスイートは新しい出力パスに直接書き込むため、途中の異常終了時に部分生成されたディレクトリが残り得る。既存成果物を上書きしないが、F006の二宛先ステージング公開と同水準の障害原子性は未実装。この点を正式採用前に改善するか、明示的に採用範囲から除外して判断すること。外部の独立レビュアー承認も未実施。

**現時点の科学判断：固定離散モデルに関するH007a〜cは初回の保存証拠ではSUPPORTED候補。正式採用は未決定。** 結合による生存利益、実自走、創発は主張しない。

### 追試で発生した失敗と対処（履歴を保持）

[CI #39012666137](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39012666137) では、出自の外部期待値を検証する新テスト `test_origin_tampering_cannot_be_hidden_by_manifest` が3.11/3.12とも失敗。121テストのうち120は成功し、**原因は新しい負例テストが `source_hashes={}` という未完成の偽期待identityを「信頼済み」として渡したこと**。強化した監査器が9依存ソースの完全性を拒否した挙動は設計どおり。実験スイート自体は当該HEADでは実行されていない。

修正として、テスト用の信頼するidentityをmanifestから組み立てず、`soma.f007.provenance()` がcheckout内の実ファイルから採取するように変更。以後、このidentityに対してmanifestのgit_commitだけを偽装し、監査が拒否するか確認する。失敗CIを成功と記載しない。最終HEADのCIを改めて確認する。

### 修正後HEADでの追試成功（採否は別）

**実装＋修正HEAD `fc3ad9b0776b020a92f9b9e6e3d632aa2e49dfcb`、[CI #39012734598](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39012734598)：Python 3.11/3.12双方で121全回帰、F007最適化9テスト成功。** 9物理run、12入力負例、保存CSV改変検出、各58ファイルのbyte完全再実行一致。修正後の成果物は[3.11 #12093711422](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39012734598/artifacts/12093711422)、[3.12 #12093456671](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39012734598/artifacts/12093456671)。

監査改善点は `trusted_origin` をmanifestではなく信頼するcheckout側から渡し、F001/F002/F003/F005/F007、SPEC/PLAN、スイート/独立検証器の計9ファイルhashとの一致を確認すること。失敗CI #39012666137を履歴保持して修正した。研究判断は「固定の1D離散計算に限りSUPPORTED候補」であって、実機の力学や省電力の優位性は支持しない。

**本研究ノートを追記したコミット自身については、文書変更後の最終CIを別途確認する。** 独立第三者によるコード/数理/生証拠の再監査、通常エラー時の段階的公開を厳密にする検討、研究者の明示的な正式採否判断は未完了。採用前Draftを保持する。


## 2026-10-17 F007 限定的正式採用 — 最新の研究判断

**採用（範囲限定）**：`f007.v1`の固定1D・2セル・理想剛体リンク、A片側有効モーター力、F005正仕事、F002整数µJ支出ゲートのソフトウェア／離散数理的一貫性を採用。仮説H007a〜cは事前登録9条件の範囲で**SUPPORTED (discrete software/model consistency only)**。Aが支払いBの電池は消費・移送しない。負例12件、切断イベント、全時刻の独立数式照合、保存証拠完全性を受入条件とした。

**証拠**：[修正実装HEAD `90a97b8eb1ec30cf030187b7a08e399faa9127ea`](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/commit/90a97b8eb1ec30cf030187b7a08e399faa9127ea)、[最終機能修正後CI #39022049632](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39022049632)：Python 3.11/3.12各**126/126全回帰、14/14最適化F007**、9 run、12拒否負例、58ファイルのbyte replay一致、関連7 workflow成功。成果物は[3.11 #12097441434](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39022049632/artifacts/12097441434) と [3.12 #12096699318](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39022049632/artifacts/12096699318)。独立した標準ライブラリのFraction/CSV/ZIP監査（SOMAランタイムをimportしない）で保存runの全行・イベント、SHA256、Python間116ファイル同一性を検証。Wolframの9条件有理数計算と一致し、微小改変＋マニフェスト再hashの攻撃を意味検査で拒否。保存は個別ディレクトリごとにstaging→監査→renameat2 no-replace、通常の例外時の自前出力cleanup、CI成功時のみartifact公開を実装・検証した。

**明示的な研究判断**：ユーザーは上記結果と制限を確認のうえ、この限定的なF007正式採用および設計PR #20→実装PR #21の順の安全なmain統合を委任した。**コードと証拠の監査は別式・別実装であって、外部の人間による第三者承認ではない。** 採用/統合は実機や科学的一般性の承認を意味しない。

**非採用・限界**：地面／反力がモデル化されない有効モーター力の現実自走、実機電気消費、結合の適応・生存・省エネ優位、自律結合、感覚、学習、進化、形態創発、任意のbinary64境界と任意dtでの厳密参照、電力保持損失、二宛先をまたぐ突然の強制終了・停電時の原子的な一括確定、fsyncなしの電源断耐久性は認定しない。公開途中のプロセス即死では、二宛先のうち一つだけ**完成済み**のディレクトリが残り得る。これらは採用範囲外として記録し、欠陥が消滅したと主張しない。

**履歴の読み方**：この節がF007についての**最新の採否判断**。上にある設計時の「未実装」「未実施」、初回失敗CI、過去の「Draft/未採用」記述は当時の状態を示す履歴であり、改変・消去しない。PR #20/#21の統合成否と統合時点はGitHubのマージ履歴を正とし、本文内で先取りして断言しない。F008は別途設計・採否を必要とし、この採用に含まれない。
