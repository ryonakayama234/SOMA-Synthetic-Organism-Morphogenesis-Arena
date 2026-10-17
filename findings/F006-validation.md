---
id: FIND-F006
title: F006 時間刻み依存の検証ノート
kind: experiment_finding
status: accepted_limited
updated: 2026-10-17
feature: F006
issue: 16
---

# F006検証記録 — 限定的正式採用（2026-10-17）


## 2026-10-17 F006 限定的な正式採用 — 最新研究判断

**研究上の判定：SUPPORTED / accepted_limited。** ユーザーの明示的な採用・統合指示により、F006 v2を「F005 v1の固定A〜E・15runについて、時間刻み差分の既知シグネチャと保存証拠を検証・再実行可能にするオフライン診断機能」として限定的に正式採用する。設計PR [#17](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/17)は先行してmain統合済み。実装・本採用記録の統合はPR [#18](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/18)に記録する。元の事前登録PLAN、期待値、旧v1実験・初回レビューの失敗記録は変更しない。下の「未採用・候補」は各時点の履歴であり、本節が現在の研究判断となる。

**証拠・独立検算**（変更前v2監査対象HEAD `47875a61bda0b959a33f85f888197324d5a41298`）：
- [GitHub Actions #38982865371](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38982865371)：PR #18用テストmerge commit `a45163674637f3439f4740286ec3fed13b742d1c`をcheckout。Python 3.11.17・3.12.15の各112通常回帰、最適化F005=20/F006=19、A〜E=15run成功。原本81ファイルと再実行81ファイルのバイト一致。F001〜F005の別workflowも成功。
- CI artifact [3.11: 12081991667](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38982865371/artifacts/12081991667) ZIP SHA256 `9086b3692d49151b61e82c5512ce31dacd61965c24fe992dc68b5fb97e428ae5`、[3.12: 12081782132](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38982865371/artifacts/12081782132) ZIP SHA256 `0e4aa3fec5a8a0e3adacff1cfeac7680e389d4b9358434050b6103cc7cde8dcb`。両archiveそれぞれの139ステップ、126支出イベント、状態・仕事・台帳をSOMA実行コードをimportしない別式で監査して一致。比較CSV/全artifact checksum/依存hash整合を検証。相互の生証拠内容も一致。
- Wolfram厳密有理数の離散参照：A `x(T)=(1,3/4,5/8)m`（連続参照は1/2m、誤差比2）、B `(x,v,spent_uj)=(0,0,0),(1/2,1/2,125000),(9/16,3/4,281250)`、C支出`1/10/100µJ`、D正仕事`1/2J`対符号付き`0J`、Eモーター支出`0µJ`。これは離散モデルの理論参照で、実機観測ではない。
- 初回独立設計・コードレビューでP2が2件（出自改変の見逃し、部分成果物公開）。v2では信頼するcheckout/外部CI identityに基づくsuite/run/参照/9依存hash照合、private staging→原本監査→バイト再実行→no-replace公開、通常例外での所有済み成果物rollback、異常・改変負例19 F006テストで修正を確認。修正後の別式・CI監査も[PR #18最終監査メモ](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/18#issuecomment-6228648338)に残す。GitHubの別レビュアーアカウントによるAPPROVEは得たと主張せず、研究上の採否判断と区別する。

**最終ゲート（採用範囲内）**：G1理論値PASS、G2生ログ/全ステップと会計PASS、G3固定した出自と改変検査PASS、G4通常例外/競合下の安全な公開と全バイト再生PASS、G5過去機能の回帰・別式監査PASS、G6システム図・入出力契約・findings・README同期PASS。

**採用外・残存制限**：任意条件での一般因果分類やmixed/undeterminedの自動判定、F005のdt不変性、連続系への一般収束保証、実機電力/効率、セルへの世界真値提供、F003との結合、資源獲得・自律性・生存・創発を認定しない。Bの結果はbudget gateだけでなくEuler位置誤差も併存。hash一致だけでは過去の実行者・実行事実の暗号学的証明にならない。二つの出力ディレクトリは停電・強制終了に対して一括crash-atomicではなく、監査済みprimaryだけが残る可能性がある。旧v1ログは改変せず保持する。

**コードの不変性**：この採用記録では `soma/f001.py`〜`soma/f005.py` とF006数値・負例コード、A〜E理論参照を変更しない。研究文書・SPECの版hashが変わるため、本記録を含むPR #18の新HEADでCIと証拠を再生成して最終確認した上でmainに統合する。

## 2026-10-17 独立監査と設計改訂（実装後監査、未採用）
独立レビューで参照数式と実装v1の主要結果は支持された一方、#18の証拠出自改変の見逃し、失敗時に出力が残るP2が2件報告された。分類も固定対照ラベルと一般因果推論の違いを明確化する必要がある。設計v2では信頼基準・依存ソース・分類列・公開/rollback契約を明記する。これは実装前レビュー完了の遡及主張ではない。実装修正と負例・最新版CIは別途記録する。

## 問い
dtの違いに伴うF005の運動・駆動受否・整数µJ支出の変化を別々に検証できるか。

## 事前仮説
[H006、対立仮説、受入条件](../topics/F006-timestep-diagnostics/SPEC.md)。
[実験A〜F計画](../experiments/F006/PLAN.md)。

## 現時点の証拠区分
| 対象 | 状態 |
| --- | --- |
| Wolfram厳密有理数によるdt=1,1/2,1/4の参照例 | **理論検算済み（SOMA実験ではない）** |
| F006コード、単体・回帰テスト | **実装候補／初回CI成功** |
| F006 A〜F実行・保存ログ・比較図 | **A〜E: 15run実行・保存成功。F: 負例・改変テストを実施** |
| F006 CI・artifact・完全再実行 | **初回CI success／生証拠162ファイル／再実行バイト一致** |
| 独立監査、採否 | 未実施・未判断 |

## 実験後に埋める欄
- 実行日時、最終HEAD、Git dirty、Python版、環境、seed、suite/コードSHA。
- A〜Fそれぞれの入力・全試行・理論参照・binary64参照・保存ログ、比較CSV、図、差分と不確実性。
- 行動受否による不連続、軌道の誤差、正仕事の積算誤差、µJ切上げ誤差の別々の推定。
- 正常な負の結果と失敗の理由、ソフトウェア欠陥とモデル意味論の境界。
- 別視点レビュー、修正履歴、CI artifact、採用判断、既存F005との互換性。

**禁止**：診断に成功したことを、F005の刻み幅収束・実機のエネルギー妥当性・身体機能の創発が成立した証拠として扱わない。後続の数値改善は別Issueで設計する。

[Issue #16](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/16)


## 2026-10-16 詳細設計時の追加Wolfram検算（F006実験は引き続き未実施）

1kg/1N/総試行時間1秒/外力・抵抗なし・初速0。厳密有理数で時間刻みを1,1/2,1/4とした独立反復では、**電池十分**：最終位置1,3/4,5/8m、速度は全1m/s、全正仕事費用500000µJ。連続運動の参照位置1/2mに対する差は1/2,1/4,1/8m。

**電池400000µJ**：最終(x,v,spent_uj)は(0,0,0)、(1/2,1/2,125000)、(9/16,3/4,281250)、駆動受理/拒否ステップは0/1,1/1,3/1。微小モーターと逆方向外力で正仕事合計1µJの対照Cは1/10/100分割に対して切上げ支出1/10/100µJ。反転Dは正仕事1/2J、符号付き仕事0J、有理数参照の支出500000µJ。

**証拠種別**：Wolframによる事前理論検算。実装したF006のソフトウェア観測・CI・実測の成功は一切示さない。F006の達成目標は差の測定・分類・追跡であり、時間刻み不変性の証明ではない。[事前登録の詳細](../experiments/F006/PLAN.md)。

## 2026-10-16 初回F006実装CI観測（実装Draft PR #18、正式採用前）

- **commit**: `d279472f7d1eb3c6a7a9121bb86d6518e25451b0`（実装ブランチの**初回**CI対象、最終HEADではない）。
- **workflow**: [F006 Action #38916091762](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38916091762)、結論`success`。Python 3.11.17、Linux runner。
- **検証**：F001〜F006全体で**100テスト成功**。`python -O`のF005 20テスト、F006 7テスト成功。A〜Eをそれぞれ3刻みで**合計15 run**、各原本を独立検査。`{"diagnosis":"supported","independent_saved_log_audit":true,"replay_bytes_identical":true,"runs":15,"schema_version":"f006.v1"}` とCIログで確認。
- **証拠**：[artifact 12052835687](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38916091762/artifacts/12052835687)。再実行分を含む**162ファイル**。config、state CSV、ledger events、run manifests、suite manifest、比較表、可視化、診断JSON、suite source snapshot。
- **A〜Eの観測**：初回CIで`tests/test_f006.py`による参照照合成功。Aの位置`1, .75, .625m`、Bの適用回数`0,1,3`、Cの支出`1,10,100µJ`、比較誤差比率`2,2`をテストが保存値から照合。その他の物理・仕事・イベントはF005の全ステップ保存証拠オラクルとF006の比較器で照合。Wolfram有理数参照とCIでのPython binary64観測を区別する。
- **発見・修正**：初回成功ログにCSVハンドル閉じ忘れによる`ResourceWarning`があったため、テストでコンテキストマネージャによる閉鎖に変更。これは物理モデルの変更ではない。
- **独立性・限界**：F005と異なる数式の保存証拠オラクルを通すが、別の人によるコード監査・他環境での再現・一般dt格子への収束保証は未了。`verdict=supported`は事前登録された限定対照に関する診断機能の成否のみ。

**必要な次ゲート**：最終HEADのCI success、原本・表・図・仕様の整合性監査、外部／独立レビュアーの確認、ユーザーによる正式採否。それまでは`main`未統合。



## 2026-10-16 実装候補の追加監査：HEAD CI と保存ZIPの別系統照合

- **実装候補commit** `437bdab1559b7ea7d1b8ab1f7071a24085a04736` に対応する[GitHub Actions #38916883630](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38916883630)は**success**。同CIで**102テスト成功**、最適化モードF005 **20**・F006 **9**テスト、F006の15run・完全バイト再実行も成功。先のCSVハンドルResourceWarningは再発せず。
- **最終実装候補の生証拠**：[artifact 12052881279](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38916883630/artifacts/12052881279)、162ファイル。内訳は15run×5ファイル＋suite6ファイル＝81ファイル、その**完全再実行分を合わせて162ファイル**。
- **CI外の別スクリプトによる保存ZIP監査**：ローカルで上記ZIPを解凍し、F001〜F006のモジュールを**importせず**、実験設定・全**139ステップ**の運動更新とモーター仕事、整数µJ会計、保存イベント、比較CSVの実測値、suite5ファイル＋runの4ファイル×15のSHA、81ファイルの再実行バイト一致を再計算して全件一致。ZIP SHA256 `262641712d57910f2ad2aca210fe37d95aa887864c3f88bc7a9f67813d73d84e`。
- 上記は**同じ実装担当側で作成した追加の独立計算法による証拠照合**であって、研究者・外部レビュアーなどの別人による監査完了を主張するものではない。
- **実データの主要観測**：Aの`x(T)`は`1,0.75,0.625m`（dt`1,0.5,0.25s`、連続参照`0.5m`）。Bは`0,0.5,0.5625m`、支出`0,125000,281250µJ`、受理ステップ`0,1,3`。Cは理想正仕事がほぼ`1e-6J`で同じでも整数支出`1,10,100µJ`。Dは正仕事`0.5J`、符号付き仕事`0J`。Eは外力で移動するがモーター支出`0µJ`。
- **採否境界**：この結果はF006が事前登録された離散モデルの人工的なdt依存を測り分けたことを示す。連続物理での収束、実機電気負担、多セル創発を示さない。設計PR #17はDraftで、実装PR #18はその設計ブランチに積まれたDraft、両方とも未採用・main未統合。外部／独立レビュアーによるレビューと最終ユーザー採否は未了。


## 2026-10-17 独立レビュー指摘への修正（v2候補、未採用）

- **元レビュー**：設計 #17 review `5550338166`、実装 #18 review `5550332235`。v1の数値参照・保存結果は支持されたが、G3/G4にP2が2件。suiteモデル/seed/Git/source hash、sweep参照ID改変の見逃し、既存replay指定でprimaryを生成してから失敗する反例を保持する。
- **修正1・出所**：schemaを`f006.v2`に改訂し、外部に固定する期待identityと、suite/run/モデル/参照ID/9依存ソースhashを照合。診断本体と再利用F005 oracleも含む。期待値を未信頼manifestからコピーする自己照合は禁止。hashは履歴実行の本人性・署名を証明しない。履歴CIのmerge SHAとPR HEADを区別する。
- **修正2・保存**：両出力先をresolveして事前確認し、private stagingで生成・原本監査・全バイト再生一致を済ませてからLinux no-replace rename。通常例外では当呼出しで公開したものだけをrollback。既存・競合先は保持。停電/強制終了時に2パスを一括rollbackする保証はなく、生成した空の親が残り得る。この限界をSPEC/READMEへ明記した。
- **意味論**：事前ラベル`expected_classification`と観測の`signature_matches_reference`を分離。一般因果帰属はnull＋理由。BにはEuler誤差も残る。未知条件でmixed/undeterminedを判別する能力としての採用はしない。
- **ローカル観測**：Python **3.12.14**、全**112テスト成功**、`python -O` F006 **19**／F005 **20**成功。A〜E **15run**、1suite **81ファイル**、replay含む162、全バイト一致。Aの位置1/.75/.625、Bの支出0/125000/281250、Cの支出1/10/100µJ、D正仕事.5J/符号付き0、E支出0は変更なし。初回ローカルF006検査は旧テストの偽source hash文字列`snapshot`で1件エラーとなり、実sourceのprovenanceを固定するfixtureに修正後、通常/最適化で成功。偽hashを受理するよう検証を緩和していない。
- **拡充負例**：suiteの出自6属性、sweep参照/ID、診断/再利用oracle hash、run出自/モデル/suite接続の改変（要約hash再更新付き）、外部期待identityの明示、既存replay・alias包含・壊れたsymlink、計算/監査/第2生成の例外、replay不一致、公開競合・rollback、空ディレクトリも置換しないことを確認。
- **理論と実測**：今回Wolframの厳密計算でもA位置、D正仕事.5J、C理論支出を再確認。理論再確認をソフトウェア測定や実装前の監査に読み替えない。F001〜F005コード・歴史的生ログは不変。
- **CIと次ゲート**：F006 workflowをPython3.11/3.12の独立job/独立artifactへ拡張。上記はローカル検証で、最終HEADのCI証拠はPR #18 Checksと修正完了コメントへ記録する。今回の修正者の再検査を、新たな別レビュアーによる独立再審査完了とは呼ばない。正式採用・main統合は未実施。
