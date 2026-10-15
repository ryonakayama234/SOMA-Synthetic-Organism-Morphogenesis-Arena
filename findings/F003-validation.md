---
id: FIND-F003
title: 二セル1D機械結合の検証記録
kind: experiment_finding
status: observed
updated: 2026-10-15
feature: F003
issue: 3
---

# F003 検証記録 — 実装候補の監査・修正

**現在（2026-10-15）：設計・実装を別視点で審査し、下記3件を修正。ローカル50テスト、A〜F、10拒否例、全証拠再実行一致を確認。main未統合。現行HEADのCI情報は末尾に追記する。**

| 指摘 | 再現と修正 | 判定 |
| --- | --- | --- |
| P2 数値範囲 | 質量各1e200・A外力1e200で内部力infを保存。合成質量あふれも受理していた。質量比先行・有限派生量検査・保存前拒否で修正 | 修正済み |
| P2 不完全な合否ゲート | 切断後のB位置+3 m、内部力和8.5 Nでも元スイートは合格。保存CSV/イベントの全時系列を独立式と照合するよう修正 | 修正済み |
| P2 時間格子の環境依存 | Decimal精度3で10/.03を333と丸めて受理。Fractionの十進有理数で厳密判定へ変更 | 修正済み |

Wolframによる一般質量の力学式残差はA/Bとも0。Bリンク力は一般に(m_B F_A-m_A F_B)/(m_A+m_B)、2kg/1kgなら1/3 N。連続値と事前離散値も再計算して一致。以下は修正後ソフトウェアのローカル測定で、実機の測定ではない。

| 条件 | 修正後の観測・検査 | 判定 |
| --- | --- | --- |
| A | x_A(10)=28.419859835044722 m、B静止、離散参照差0 | 支持 |
| B | x_A(10)=14.209929917522361 m、v=2.1623386938832914 m/s、最大距離誤差1.066e-14 m、内部力和0 N | 支持 |
| C | 内部力0 N、両セル離散参照差最大5.33e-15 m | 支持 |
| D | t=5切断前後・CSV同値、全切断後離散参照差最大1.78e-15 m | 支持 |
| E | 両セルの変位・速度鏡映を全時刻で照合 | 支持 |
| F | 位置誤差0.018238877064702 / 0.009118027943591 / 0.004558661430391 m、誤差比2.0003094 / 2.0001547、10拒否例 | 支持 |

追加監査：8種の保存CSV/イベント改変を検出。python -Oでも改変証拠を拒否。50テスト（F001=17、F002=16、F003=17）合格。Bの5ファイルだけでなく、comparison.json/rejections.json/suite_source.pyを含む全スイート成果物が同一条件でバイト一致。`full_suite_replay.json`に一致SHAを保存する。生ログは現行CI artifactに保持する。

### 限界と採否
監査した理想1Dモデル内では採用を妨げる既知の問題は修正済み。GitHubの正式な他者承認や人間の査読を得たことを意味しない。main統合・実機結合・自律的身体形成・F002連携は未実施。数値閾値の後付け緩和はしていない。

## 事前登録時点の記録（実装前の履歴）

**現状：実装なし・実験なし・実測値なし。** 以下の期待値は理想モデルの解析予測であり、SOMAコードによる観測ではない。

- [仕様／仮説／許容差](../topics/F003-attachment/SPEC.md)
- [対照実験A〜F](../experiments/F003/PLAN.md)
- [Issue #3](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/3) / [設計PR #7](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/7)

| 条件 | 事前仮説と評価点 | 実測 | 証拠URL | 判定 |
| --- | --- | --- | --- | --- |
| A 未結合 | F001系列一致・B静止 | 未実施 | 未生成 | 未実施 |
| B 片側駆動 | 共通速度・リンク力と拘束 | 未実施 | 未生成 | 未実施 |
| C 双側駆動 | 内部力0 | 未実施 | 未生成 | 未実施 |
| D 中途切断 | 位置・速度の連続 | 未実施 | 未生成 | 未実施 |
| E 符号反転 | 変位・速度対称 | 未実施 | 未生成 | 未実施 |
| F 刻みと不正 | 誤差収束・明示拒否 | 未実施 | 未生成 | 未実施 |

## 実行後の保存義務
設定JSON、世界の真値CSV、イベントCSV、比較結果、SVG、manifest、Git SHA・dirty・モジュールとsuiteのハッシュ、CI Actions artifact、同条件再実行の一致検査、否定的結果を一組にして記録する。

## 独立監査と採否
研究対象は**1D・二セル・理想リンクON/OFF**のみ。F002は連携しない。解析式・世界真値と局所観測の境界・回帰試験・図とログの一致を第三者視点で検査する。支持／反証／不明は実行後に判断し、レビュー承認まで正式採用としない。

## 2026-10-15 受入ゲート事前登録（実測ではない）

Wolframで検算した連続解：Bの10秒後に共通速度2.1616617919084682703 m/s、共有変位14.191691040457658649 m。
同じ名目条件の半陰的Euler法（dt=0.01）での離散基準：速度2.162338693883290987 m/s、共有変位14.209929917522377975 m。
dtを0.005／0.0025へ半減した位置誤差の事前期待：0.009118027943618595／0.004558661430422564 m。
切断t=5 sのstates.csvはイベント後1行、イベント前後の位置・速度はevents.csvで同値検証。不正設定はrejections.jsonへ別保存。数値・再実行・回帰・CI・独立監査の採用条件はSPECとPLANを正本とする。

**F003のコード・実験・実測値は依然として存在しない。支持・反証の判定は全て未実施。**

## 独立視点の設計監査（2026-10-15）
作用反作用、一般質量のリンク力、連続解・離散解をWolframで再検算し整合を確認。有限入力からの派生値あふれと、保存証拠に基づく全ゲート判定の契約が不足していたためSPEC/PLAN/図/データ契約を補足した。A〜Fの数値閾値は不変。このブランチでは実装せず、全観測は未実施のまま保持する。後続PR #8を監査・修正してから実装の採否を判断する。

## 実装候補の検証状態（2026-10-15）

- **コード**：専用実装ブランチにF003計算、A〜F実験スイート、9件の単体検査、およびCI workflowを追加。
- **設計側の予測**：連続系 v(10)=2.161661791908468... m/s、変位14.191691040457659... m；dt=.01の離散系 v(10)=2.162338693883291... m/s、変位14.209929917522378... m。Wolframで独立に再確認。Bの内部力 +0.5 N、不等質量2kg/1kgのB内部力 +1/3 N。
- **ローカル試作の検査**：モデル等価なF001小関数を用いたローカル試作では9件の検査とA〜F（7正常run／8拒否ケース）、B再実行のバイト一致が成功。ただしGitHubにある実装そのものとmainの既存F001/F002の回帰を確認したものではなく、**GitHub Actionsでの正式な検証証拠として扱わない**。
- **GitHub CI**：以下の2026-10-15の最新CI証拠を確認。
- **独立監査**：未完了。主張できるのは理想1D力学ソフトウェアの検証候補まで。実機接続や創発を示さない。

**ゲート**：CI結果・SHA照合・第三者視点のレビューを確認してから採否を記録する。失敗・修正履歴は削除しない。

[実験スイート](../experiments/F003/run_suite.py) / [CI workflow](../.github/workflows/f003.yml)。

## F003 GitHub CI 履歴（監査修正前・2026-10-15）

- 実装HEAD: 1512206596ca8939705e6e1ab603e9aa1bbd626d
- F003 Actions: https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38731190546 — success。Python 3.11で合計44テスト（F001 17、F002 16、F003 11）合格。
- A〜F正常7run、不正入力8件を拒否、B同条件再実行の生バイト一致。artifact: F003-A-F-evidence（ID 11970235937）。
- F001既存ワークフロー: https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38731190562 — success。
- F002既存ワークフロー: https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38731190549 — success。
- 以上は1D理想モデル・ソフトウェアの整合性を示す。実機による結合、エネルギー相互作用、身体創発を示さない。
- 独立第三者の監査は未了。PR #7の設計レビューと、PR #8の正式採用判断を区別する。

| 種別 | 現時点の判定 |
| --- | --- |
| Wolfram理論値 | 事前予測として固定 |
| ソフトウェア試験 | 44テスト・A〜F・再現性支持 |
| 独立監査 | 未実施 |
| 正式採用 | 保留 |

## 監査修正後のGitHub証拠（2026-10-15）

- 設計PR #7の修正HEAD：`c367a4207a0b53fbf011eea6767b91ae98277cee`。F001/F002回帰CI success（[F001](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38737005653)、[F002](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38737005652)）。設計ブランチにF003実装は含めない。
- 実装コードの監査修正HEAD：`e980f1772f24a4f4e77b99c1ab0ba41c3de7d47d`。[F003 CI](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38737032473)、[F001](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38737031197)、[F002](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38737031478)すべてsuccess。50テスト・正常7run・拒否10例・全スイート再実行一致をログで確認。
- ActionsはPR統合候補`d59f859e10cbe220d2797e8d8057e1c737e46163`を実行した。これは上記実装HEADと同じtree `fa7f8923a8b1c3b405264c3b1a62b74d42615d85`であることをGitオブジェクトで照合済み。artifact内Git SHAがブランチHEADと違うのはこのためで、dirty=false。
- [実験artifact](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38737032473/artifacts/11974127240)：87ファイル、ZIP SHA256 `95a8003047e73d1b2c796f4d157bc6cb746cc125715b69fb1128b2fdddd0ec2a`。ダウンロードしたZIPのハッシュ、43組の実験成果物バイト一致、拒否証拠SHA、suite_source.pyと実行ソースの一致を独立に再照合済み。
- F003モジュールSHA256：`c32b7946eb588eab576baa4b80d2c5eff66ade188a016e2c96bc747595d558ef`、F001依存モジュール：`f67be3b5fc06da4a98f42573c146ded62817dc26b28631759b2a5b2bb209210d`。ローカルの現行コードと一致。
- この追記は証拠を保存する文書更新。以後の現行HEADの成否は[PR #8 Checks](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/8/checks)で確認し、上記コード検証の固定証拠と区別する。

**審査結論：指摘3件は修正・再検証済み。理想1D機械結合のソフトウェア候補として、採用を妨げる既知の指摘は残っていない。両PRはdraft・main未統合のまま。** 設計→実装の統合順序を維持する。本記録はGitHubの別アカウントによるAPPROVEや人間の査読の代替を称するものではない。
