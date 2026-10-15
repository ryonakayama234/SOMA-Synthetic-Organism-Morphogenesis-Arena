---
id: EXP-F003
title: F003機械結合の比較実験計画
kind: experiment_plan
status: proposed
updated: 2026-10-14
feature: F003
---

# F003 — 実験計画と実装候補の検証

**以下の事前登録節は実装前の履歴。現行の実測・合否はfindingsと本末尾の監査記録を参照。**

[仕様・図](../../topics/F003-attachment/SPEC.md) / [追跡 Issue #3](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/3)

## 一度に変えるのは結合条件だけ
初期条件 m_A=m_B=1 kg、gamma=0.2 1/s、x_A=0 m、x_B=0.5 m、v_A=v_B=0 m/s、dt=0.01 s、duration=10 s。外部駆動力は指定された場合だけ印加する。数値は**事前設定案**であり測定値ではない。

| 条件 | リンク | 外力 (A/B) | 観測・検証 |
| --- | --- | --- | --- |
| A 未結合対照 | OFF | +1 / 0 N | AはF001に一致し、Bは静止 |
| B 片側牽引 | ON | +1 / 0 N | 共通速度、距離L一定、リンク力±0.5 N（理想モデル） |
| C 双側駆動 | ON | +1 / +1 N | 共通速度、等質量なら内部リンク力0 N |
| D 中途切断 | ON→OFF (t=5 s) | +1 / 0 N | 切断瞬間の状態連続、以降は独立更新 |
| E 力の符号反転 | ON | +1 / 0 vs -1 / 0 N | 共通変位・速度の反転対称性（初期オフセットLを除く） |
| F 数値・不正条件 | ON / 拒否 | B条件のdt半減・不整合な初速／位置 | 理論誤差の収束傾向、無理な瞬間結合を拒否 |

## 保存する観測量
- t [s]、x_A・x_B [m]、v_A・v_B [m/s]、外力F_A・F_B [N]。
- 結合状態、リンク内部力T_A・T_B [N]、距離拘束誤差 [m]、速度拘束誤差 [m/s]。
- 重心位置・速度、解析解との差、切断前後のジャンプ量、数値刻み感度。
- 実験ID、設定、シード（乱数未使用なら明示）、Git commit SHA、ファイルSHA256。

## 実験成果物（予定・存在しないものを存在すると記載しない）
~~~text
experiments/F003/
  PLAN.md
  configs/           # 実装後
  run_suite.py        # 実装後
findings/F003-validation.md   # 実験後
GitHub Actions artifact: raw configs / states / events / comparisons / figures / manifest
~~~

## 実行→監査→採否
1. SPECの境界と許容誤差を実装前に監査し、F001既存テストの回帰を先に確認。
2. A〜Fを実装・実行し、生ログ・対照グラフ・失敗したテストも残す。
3. 別視点のレビューで、結果と事前仮説・理論予測を突き合わせる。
4. 支持／反証／不明を条件別に記録し、改善なら仕様へ戻す。成功かつレビュー済みの場合のみmainへ採用。

**現段階の実験結果：未実施。** F001/F002はmain統合済み。F003は別PRで設計・実装を管理する。

## 観測前に事前登録した期待（2026-10-15）
- Aは個別のF001計算に一致し、B静止、内部リンク力0。
- Bは10秒時の共通速度`2.161661791908468 m/s`、共通変位`14.19169104045766 m`、Bへのリンク力`+0.5 N`（Aは`-0.5 N`）を連続系の基準値とする。**解析予測であり観測ではない。**
- Cは左右の等力駆動のため内部力0。Dは5.0秒の境界で状態を飛ばさず切断し、以後独立更新。
- Eは初期位置の差を差し引いた変位と速度の鏡映対称性。Fは`dt=0.01/0.005/0.0025 s`の解析誤差収束と、無効接続・非有限入力・刻みに合わない切断時刻の拒否。
- 事前許容値とイベント順序は[SPEC](../../topics/F003-attachment/SPEC.md)の規約を参照。試験結果を見て閾値や予測値を後付け変更しない。

## 実装・実験の具体的手順と合格ゲート（2026-10-15事前登録）

1. 設計PR #7の仕様・図・データ契約・判定値の独立レビューを完了し、切断時刻のpost-event記録と拒否ケースの別保存を固定する。実験後の閾値変更は禁止。
2. mainを起点に専用の実装ブランチと別PRを設け、F003だけの最小運動モジュール、単体テスト、A〜Fスイート、GitHub Actions workflowを作る。F001/F002の運動・会計意味論を変更しない。
3. A未結合、B片側結合、C両側、D切断、E鏡映、F誤差収束と不正入力の順に試す。参照はWolframの連続解と、F001型半陰的Eulerの独立離散解を**区別**する。
4. Bの離散基準10秒後はdt=0.01で速度2.162338693883290987 m/s、共有変位14.209929917522377975 m。連続解は速度2.1616617919084682703 m/s、共有変位14.191691040457658649 m。混同した比較を合格させない。
5. Dのt=5.0 sのstates.csv行は切断処理後とする。切断前後のx_A/x_B/v_A/v_Bの一致はevents.csvで別途検査する。Fの不正設定はrejections.jsonにまとめ、正常runイベントに混ぜない。
6. 各config.json、states.csv、events.csv、comparison.json、描画SVG、manifest.json、rejections.json、suiteソースと出自SHAを保存し、同じ条件での再実行一致を確認する。F001/F002の全既存テストを回帰させる。
7. 別視点の監査で実測・予測・失敗・ログ・図・SHAを照合。条件ごとに支持／反証／不明をfindingsへ記録。全ゲート通過時だけmain統合とIssue #3完了を提案する。不合格は修正して再測定し、旧結果を消さない。

**採用の全数値閾値はSPECの「A〜Fの数値合格ゲート」節を正本とする。現状は未実装・未実験。**

## 独立監査による検証方法の補足（2026-10-15）
A〜Fの事前条件・数値閾値は維持する。保存CSVとイベントを一次証拠として全時系列オラクル・両セル鏡映・切断前後の参照状態を照合し、各ゲートの最大誤差と合否をcomparison.jsonへ保存する。非有限の派生量とDecimal精度変更による誤受理を補助回帰で検査する。拒否入力全体、拒否証拠SHA256、F001依存ソースの出自を保持し、比較結果を含むスイート全体の再実行一致を検証する。これは判定の具体化であり、実験閾値の変更ではない。

## 実装候補の実行順と証拠（2026-10-15）

事前登録の条件・閾値を維持。新たな不等質量の単体テストは補助検査であり、A〜Fの操作変数を変更しない。

1. `python -m unittest discover -s tests -v` でF001/F002/F003回帰。
2. `python -m experiments.F003.run_suite --output-dir runs/F003-ci` でA・B・C・D・E・F（Fの刻みは3条件）を実行する。
3. 比較結果に理論値と各条件の終値/拘束誤差/内部力/刻み感度を保存する。異常設定8ケースの拒否理由を別ファイルに保存する。
4. B条件を同設定で再実行し、config/raw CSV/SVG/manifestのバイト・SHA256一致を保存する。
5. GitHub Actions artifactと実行HEADを台帳に記入。実測値と予測値は別の欄で保持し、独立監査後に採否を判定する。

[実行方法](README.md) / [設計正本](../../topics/F003-attachment/SPEC.md)。

## F003 GitHub CI 履歴（監査修正前・2026-10-15）

- 実装HEAD: 1512206596ca8939705e6e1ab603e9aa1bbd626d
- F003 Actions: https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38731190546 — success。Python 3.11で合計44テスト（F001 17、F002 16、F003 11）合格。
- A〜F正常7run、不正入力8件を拒否、B同条件再実行の生バイト一致。artifact: F003-A-F-evidence（ID 11970235937）。
- F001既存ワークフロー: https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38731190562 — success。
- F002既存ワークフロー: https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38731190549 — success。
- 以上は1D理想モデル・ソフトウェアの整合性を示す。実機による結合、エネルギー相互作用、身体創発を示さない。
- 独立第三者の監査は未了。PR #7の設計レビューと、PR #8の正式採用判断を区別する。

## 監査修正後の検証（2026-10-15）
50テスト（F001=17、F002=16、F003=17）、A〜Fの正常7run、異常入力10例、B再実行、全スイート再実行のバイト一致をローカルで確認。8種のCSV/イベント改変をすべて拒否し、python -Oでも合否検査が消えない。旧8拒否例は維持し、数値範囲の2例を補助追加した。スイートは保存CSV・イベントを一度だけの運動実行から読み戻して検査する。comparison.jsonの各case.gatesに最大誤差と全数値ゲートを保存し、full_suite_replay.jsonに比較JSONを含む全成果物の一致SHAを保存する。
