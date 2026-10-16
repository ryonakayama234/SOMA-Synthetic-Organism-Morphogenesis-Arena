---
id: FIND-F004
title: F004 内部駆動と残量の実験記録
kind: experiment_finding
status: observed
updated: 2026-10-16
feature: F004
issue: 9
---

# F004 検証記録【実装・検証済み／2026-10-16 採用決定】

最新の採用判断は末尾を参照。以下の「未実施」「正式採用前」は各時点の履歴として保持する。

- **対象**：1セル1D内部モーター力による正の仕事の消費と電池不足時の駆動抑止。
- **中心仮説**：H004（[SPEC](../topics/F004-actuation-energy/SPEC.md)）。
- **予測・対照**：[A〜F PLAN](../experiments/F004/PLAN.md)。
- **実行日／実行コードSHA**：なし（設計段階）。
- **CI artifact／生ログ／測定図**：なし（未実施）。

| 対照 | 事前の予測 | SOMA実行値 | 判定 |
|---|---|---|---|
| A | 外力による運動と電池不変 | 未実施 | 未実施 |
| B | モーターによる運動と正仕事の支出 | 未実施 | 未実施 |
| C | 0 µJで内部駆動なし | 未実施 | 未実施 |
| D | 残量不足の時刻から軌跡が変化 | 未実施 | 未実施 |
| E | 回生なしの理想ブレーキ | 未実施 | 未実施 |
| F | 刻み・丸め・拒否・リプレイ | 未実施 | 未実施 |

## 事前理論検算（実験観測ではない）
Wolfram Languageで離散運動と台形仕事の代数恒等式の残差0、およびB・C・Dの理想有理数反復を計算。Bは10ステップ後に (x,v,balance,駆動回数)=(0.55 m,1 m/s,500000 µJ,10)、Cは (0,0,0,0)、Dは (0.49 m,0.7 m/s,55000 µJ,7)。**これはSOMAのコードが正しいことの証拠ではない。**

## 実装後に追記する証拠
1. 先に凍結した入力・予測値・許容差の変更履歴（後付け修正は別版で明示）。
2. 全ステップの真値CSV、支出台帳、comparisonと実験グラフ。
3. 最初と再実行のGit SHA／dirty／ソースSHA／artifact SHA、全バイト比較。
4. 無効ケースとログ改変の拒否証拠。失敗・改善履歴。
5. 独立監査での疑義・対応・支持／反証／不明、既存F001〜F003の回帰とCI。
6. 採用可否と、その結論が成立する狭い理想モデルの境界。

重要：F004はF003の結合実験、実機の電池性能、創発・進化、生存戦略を**まだ検証しない**。

[Issue #9](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/9)。

## 2026-10-16 設計監査所見（F004コードは未実装）

1. P1（設計欠陥）旧案の「必要仕事=0なら残量0でも力適用」：u=+1 N／外力=-1 N／初速0／残高0の条件でWolfram計算により候補仕事0を確認。**電池残量が0の場合は仕事にかかわらず内部力0**とする受入基準をSPEC/PLANに追加。
2. P1（事前期待値と浮動小数点の差）：有理数モデルのB残高500000 µJ・D残高55000 µJは正しいが、各ステップをIEEE754 binary64で計算してceilすると、独立参照B=499995 µJ・D=54996 µJ。理論値と実装参照を区別してPLANへ追記。実装後の観測を使って閾値を決めたものではない。
3. モーター仕事のみを課金する理想モデルは、残量が正でも静止トルクで電力を消費しない。実機の電気的損失や保持電力は**未モデル化**。試験成功を実機の物理妥当性と同一視しない。

判定：**設計監査の指摘と対処案を記録。F004実装・CI実験・独立実装監査・正式採用は依然未実施。**

## 2026-10-16 初回実装・CI実測（PR #11：まだ正式採用前）

**初回実装コミット**：\`8026f19194b54d609505feacf230e593af58ac55\`（追加ドキュメント・監査修正前）。GitHub Actions \`38829244901\` の **F004 verify = success**、既存F001/F002/F003のworkflowも同HEADでsuccess。

- Python 3.11：\`python -m unittest discover -s tests -v\` **68 tests / OK**（既存50＋F004 18）。F004 A〜F \`python -m experiments.F004.run_suite --output-dir runs/F004-ci --replay-output-dir runs/F004-replay\` 完了。
- 保存CSV独立検算：正常10ケース、全ステップの力・状態・候補仕事・µJ量子化・支出イベント参照・F002保存残差0。無効入力16件はrun保存前に拒否。B同一設定と全スイートのバイト再実行照合パス。
- 観測：A x=0.55m, v=1m/s, balance=1000000µJ（外力のみ）；B x=0.55m, v=1m/s, balance=**499995µJ**；C x=0,v=0,balance=0；D x=0.49m,v=0.7m/s,balance=**54996µJ**；E x=0.45m,v≈0,balance=1000000µJ。事前binary64の参照と一致。理想有理数の B=500000/D=55000 との差は設計段階で記録済み。
- F：電池0かつu=1N,外力=-1Nで適用モーター力0、最初のステップv=-0.1m/s,x=-0.01m。残高1µJでゼロ仕事の理想モーター駆動は無料（実モーターを再現しない）。微小仕事は1µJへ切上げ。dt減少でF001数値誤差が減少。外力・抵抗を含む機械エネルギー恒等式残差は指定範囲内。
- **独立数式参照**：Wolfram Language 2026-10-16 実行結果：離散運動エネルギー恒等式の記号残差0、有理数A=(11/20m,1m/s,1000000µJ)、B=(11/20m,1m/s,500000µJ)、C=(0,0,0)、D=(49/100m,7/10m/s,55000µJ)、E=(9/20m,0,1000000µJ)。これは**理論参照**であり、F004の実行結果ではない。
- **監査上の改善**：Eではモーターを10回適用しても支出イベント0。初回比較実装にあった\`motor_steps\`（実際は支出回数）の曖昧な指標を、修正コミット\`3739a125b4b2bb1be08d86c03fc200fbd68e66e6\`で**\`applied_motor_steps\`と\`spend_event_count\`に分離**。改訂HEADのCIは再確認対象。
- [初回GitHub Actions](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38829244901) / [artifact 12015824529](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38829244901/artifacts/12015824529)。そのartifactには\`runs/F004-ci/\`と\`runs/F004-replay/\`に計117ファイル、生成条件とSHA付きの生ログ・図・比較値がある。
- **結果判定**：A〜Fのソフトウェアモデルに関する事前仮説を初回証拠は支持。一方、連続物理・モーター損失・実機・自己組織化・生存は**未検証**。最新HEADのCIと独立設計監査、ユーザーの採否判断までは**正式採用不可**。

## 2026-10-16 PR #11 独立視点の実装監査

対象HEAD：`60bb167747e8ec77863dd5ccb2aa9f07eb9df65f`。修正前の既存68テストは成功したが、以下4件のP2を追加の反例で再現した。

| ID | 問題と修正前の反例 | 修正・回帰検証 |
| --- | --- | --- |
| R1 | `dt_s=9007199254740992`, `duration_s=54043195528445952`は入力では厳密6ステップ。Config.from_dictの検証後にfloat化すると十進表記が変わり、stepsが5へ切り捨てられた | 生入力とfloat正規化後で厳密時間比が一致しなければValueError。正常な整数設定のroundtripも確認。スイートの拒否例を16→17へ追加 |
| R2 | `dataclasses.replace(valid_cfg, dt_s=.3)`が通り、duration=1秒なのに3ステップ・0.9秒で成功扱い。直接Config生成も質量・seed等の検証を迂回 | 全Config構築の検証を`__post_init__`へ集約。直接生成・replace・from_dictで時間、型、範囲、schema、IDを同じ条件で検証 |
| R3 | motor=0、dt=duration=1e308、初速0なら物理ログは有限でも、SVGの`680*time/time_end`がinf。状態のhigh-lowにもoverflow経路がある | 時間比と状態のスケールを先に正規化。初期位置-1e308、速度2、dt=4e307、duration=1.2e308の3ステップで有限な運動を保存・独立照合し、SVG全座標が有限で描画範囲内と確認 |
| R4 | manifest.artifactsを空にすると壊れたSVGが未照合のまま`artifact_hashes=True`。また初期行motor_work=123へ変更してhashを更新しても独立オラクルが合格 | 必須4成果物と一覧キーを厳密一致。初期行の5つの仕事・運動エネルギー差・残差をすべて0と照合。欠落/余分/空一覧、hash更新済みの初期行改変を拒否 |

**ローカルで実施した検証**（Python、Linux、修正済み作業ツリー）：
- `python -m unittest discover -s tests -v`：**73 tests / OK**（既存50＋F004 23、5テスト追加）。
- `python -m experiments.F004.run_suite --output-dir runs/F004-audit --replay-output-dir runs/F004-audit-replay`：10対照・17拒否、全時刻CSV/台帳照合成功。58ファイルを含む各スイートの生バイト一致。B=499995 µJ、D=54996 µJで事前binary64参照を維持。
- `python -O -m experiments.F004.run_suite --output-dir runs/F004-audit-optimized`：10対照・17拒否成功。オラクルは`assert`に依存しない。
- 今回のWolfram Context/Language/Alphaは接続エラーで**再検算未実施**。標準ライブラリFractionによる独立有理数反復ではA=(11/20,1,1000000)、B=(11/20,1,500000)、C=(0,0,0)、D=(49/100,7/10,55000)、E=(9/20,0,1000000)。全区間の機械恒等式残差は厳密0。過去のWolfram実行記録とは区別する。
- 修正後コードSHA256：F004=`f841a49b364750672f427c8a614b71ec0e45656e9bb50eafa0cc57ba7d63ef12`、suite=`77e52bac4c172b635c54725ececa01a04e9540ae68c1312006da057a1287d843`。GitHubでの最新コミットのCI結果・artifactは[PR #11 Checks](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/11/checks)で確認する。上記ローカル検証と過去HEADのCIを同一視しない。

**判定**：4件は修正と反例試験で解消。A〜Fの通常条件について物理・費用式と観測値は変えていない。保存hashは整合性確認であり、manifestごと書き換える攻撃に対する署名ではない。F001/F002/F003のAPIは変更なし。PR #10→#11の依存順とDraftを維持し、main統合・正式採用はユーザーの判断に残す。

## 2026-10-16 採用判断と統合

ユーザーが設計PR #10・実装PR #11の正式採用とマージを指示した。設計PR #10は先にmainへ統合済み（`d4b1c8bffe9c0e0cd4c5e47aab8b8db27cd0b012`）。実装と本採用記録は[PR #11](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/11)で統合する。

- 実装監査済み`142e810ba61a0e9c141d5971fa6e7b1c4b18e9a3`でF001/F002/F003/F004 CIすべてsuccess。[F004 CI](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38840628591)のログで73 tests、10対照、17拒否、全再実行一致を確認。[117ファイルの保存証拠](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38840628591/artifacts/12021411127)。本追記後の現行HEAD・mainのCIは[Checks](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/11/checks)で区別して確認する。
- **採用範囲**：1セル1Dの正の離散区間仕事と整数µJ台帳・残量依存駆動の接続。保存会計とソフトウェアの再現性を支持する。
- **今回追加で実行確認した制約**：m=1、u=-2、外力=抵抗=0、初速+1、dt=duration=1、初期残量1 µJで、終速-1、候補/適用仕事0、支出0、残量1、`accepted_nonpositive_work`。速度反転をまたぐ粗い刻みで正負の仕事が相殺される。現仕様に整合するが、連続無回生モーターの再加速費用を再現しない。
- **後続課題**：自律制御の省エネルギー最適化・生存実験に進む前に、反転時刻での分割または区間内の正仕事積分を別仕様で比較する。保持/待機電力・効率・損失、dt依存の積分誤差とµJ切上げ差、F003との統合も持ち越す。
- 実機・学習・身体創発の証拠には昇格させない。今回の採用処理に伴う変更は文書のみで、事前値とコードの演算順序は維持する。
