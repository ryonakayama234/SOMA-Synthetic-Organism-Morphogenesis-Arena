# SOMA — AI研究助手向け案内

**最新判断（2026-10-17）**：F007 `f007.v1` は**固定1D・2セル片側A駆動とA電池支出の離散モデル整合性に限って正式採用**。9条件のWolfram/保存データ独立照合、3.11/3.12各126全回帰＋14最適化、58ファイル再現、改ざん・失敗時保存試験を通過。[採用範囲・非採用事項](findings/F007-validation.md#2026-10-17-f007-限定的正式採用--最新の研究判断)を優先し、下の「設計のみ／未採用」などは当時の履歴として読む。PR #20（設計）→#21（実装）の統合状況はGitHubを正とする。**実機・創発・任意dt・二宛先crash-atomicは非採用。**

研究段階は最新のfindingsの採否節を優先。外部人間レビュアーの承認と同一支援AIによる独立数式監査は区別する。F008は自動着手しない。

## 読む順番（コンテキストを失わない）
1. [README.md](README.md) で現在の研究段階と資料索引を読む。
2. [docs/PROJECT.md](docs/PROJECT.md) で意図・禁止したい誘導を確認する。
3. 対象能力の \`topics/Fxxx-.../\` だけを優先して読む。
4. 必要なとき [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) と [docs/DATA_CONTRACTS.md](docs/DATA_CONTRACTS.md) を参照。
5. 関連IssueとPRの進捗を確認する。

## 不変の研究運営
- 原則一Issue＝主要機能一つ。変更範囲を局所化する。
- 仕様は仮説・代替仮説・測定量・反証条件・単位・入出力を含める。
- 観測結果がないなら「未実施」と明示する。仮説と測定結果を混同しない。
- 環境の真の身体構造をエージェントへ渡さない（観測境界を保持）。
- モジュールの役割を先に名づけたり、結合を恣意的に優遇しない。
- 研究上の重要な変更では、計画→実装→第三者的な監査→PRで証拠を整理する。
- READMEから新しい文書に到達できるようリンクを更新する。
- 文献引用は [library/INDEX.md](library/INDEX.md) に原著と限界を記録する。
- WSL2/Linux/bash を基準とする。コードが存在しない段階で実行結果を捏造しない。

## ステータス表現
proposed=仕様案、backlog=構想、active=運用中、implemented=コード実装済み、observed=実験観測済み。文書が書かれたことだけで implemented/observed にしない。

## F002以降のPR同時更新ルール
コードを追加するときは `docs/ARCHITECTURE.md`、`docs/DATA_CONTRACTS.md`、`findings/Fxxx-validation.md`、`README.md`、対象SPECを同じPRで検証・更新する。図とログの食い違い、記録の欠落、根拠のない「観測済み」昇格を監査する。デザインのみのPRは未実装・未実行として区別する。

## 現在の研究焦点（2026-10-15）
- F001/F002はmain統合済み。F003の1D二セル理想リンクは実装・検証済み。独立視点の監査修正、50テスト・A〜F・再現性・CI検証を経て採用判断済み。設計PR #7はmain統合済み、実装の統合はPR #8で追跡。
- [F003仕様](topics/F003-attachment/SPEC.md) → [A〜F計画](experiments/F003/PLAN.md) → [検証ノート](findings/F003-validation.md) → [Issue #3](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/3)の順に追う。
- 世界側の接続真値・リンク力は研究専用ログであり、後のセル行動器へ直接渡さない。F002台帳の数値移送と物理的結合を同一視しない。

## F003実装・監査時の読み順（2026-10-15）
- `topics/F003-attachment/SPEC.md`（事前仮説・反証・許容誤差）
- `experiments/F003/PLAN.md`（A〜F）
- `soma/f003.py` と `tests/test_f003.py`（理想1D力学）
- `docs/ARCHITECTURE.md`、`docs/DATA_CONTRACTS.md`（図・スキーマ）
- `findings/F003-validation.md`（予測、観測、CI証拠、未解決）
F003世界真値を将来のセル局所観測へ注入しないこと。F002の台帳と物理的に結線しないこと。未実施を実測と記載しないこと。監査前の44テストCIは履歴として扱い、現行HEADのCI証拠と混同しないこと。

## 現在の研究焦点（2026-10-16・F004採用）
- F004の1セル1D離散理想モーター／電池接続を実装・検証済みとして正式採用。設計PR #10はmain統合済み、実装・採用記録はPR #11で統合する。旧「未実装」「Draft」「未採用」は各時点の履歴。
- `topics/F004-actuation-energy/SPEC.md`末尾の採用範囲 → `findings/F004-validation.md`末尾の採用判断 → `experiments/F004/PLAN.md`の事前値 → 実装/契約の順に確認する。73テスト・10対照・17拒否・再実行一致、実装監査4件修正を確認済み。
- 保持/待機電力0、速度反転をまたぐ区間仕事の相殺、dt依存のµJ切上げはモデルの制約。自律制御の消費最適化・生存実験の前に別仕様で扱う。F003統合・実機・学習・身体創発は未検証。


## 次の研究提案（F005・2026-10-16、未実装）
- F001〜F004は正式採用済み。F004の速度反転・正味区間仕事相殺は**既知のモデル制約**であり、バグの修正が実装済みという意味ではない。
- F005は区間内の正のモーター仕事積算のみを対象とする提案。[Issue #12](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/12) → [SPEC](topics/F005-positive-work/SPEC.md) → [A〜F計画](experiments/F005/PLAN.md) → [F005未実施記録](findings/F005-validation.md)の順に読む。
- 図は`docs/ARCHITECTURE.md`、スキーマ案は`docs/DATA_CONTRACTS.md`のF005節を参照。F005はF004の既存API・証拠を改変しない別版とし、2セル・学習・生存は後続。仕様PRと実装PRを分け、最新の生ログ・独立参照・CI・監査と採否判断を混同しない。

## F005 implementation candidate instructions (2026-10-16)
- Candidate feature branch `feat/F005-positive-work-20261016` adds `soma/f005.py` and `f005.v1`. The main branch and F004 `f004.v1` are NOT changed; F005 is not yet adopted.
- Inspect `topics/F005-positive-work/SPEC.md` → `experiments/F005/PLAN.md` → `soma/f005.py` → `tests/test_f005.py` → `experiments/F005/run_suite.py` → `findings/F005-validation.md`. Verify CI **final HEAD** and saved raw CSV independent checks before claiming an observed result.
- Signed midpoint work explains kinetic energy; integrated positive work governs ideal battery spend. Do not conflate them and never expose simulation world truth as learned cell observation.
- Carry forward failed tests and reviewer findings. Do not merge design and implementation PRs or call F005 'adopted' before the explicit research acceptance gate.

## PR #14 review follow-up (2026-10-16)
- The corrected F005 verifier cross-checks an exact Fraction integral of binary64 endpoints and the separately frozen binary64 charging order; never derive integer spend from a different algebraic ordering.
- The suite now has 13 controls, including ordinary ceil-boundary reversal, endpoint-power underflow and decimal time splitting. Initial candidate-positive work must be null; tiny positive values must not pass a zero-value tamper under an absolute 1e-12 tolerance.
- Current local result: 93 total tests / 20 optimized F005 tests, 17 rejected inputs, 73-file suite replay. Check final-HEAD CI before claiming CI completion.


## F005 limited formal acceptance (2026-10-16)
User approved adoption and main integration **only** as the 1D single-cell discrete positive mechanical work accountant connected atomically to F002 integer-microjoule ledger. F004 history and APIs remain intact. Preserve [SPEC](topics/F005-positive-work/SPEC.md), [F005 findings](findings/F005-validation.md), A–F evidence and the review correction history. The older proposal/Draft sections describe earlier stages, not current acceptance.
**Do not infer** physically meaningful travel energy efficiency, timestep-independent motor-budget feasibility, real battery holding costs, or ungrounded propulsion from this acceptance. Position uses semi-implicit Euler, work a velocity interpolant; stepwise ceil and all-or-nothing gating are dt-sensitive; motor is an effective world force with no reaction partner. Do not use F005 as a validated autonomous/survival/morphology benchmark. Next research priority: dt-convergence of energy-gated motion as a *separate* hypothesis/feature. No multi-cell actuation is adopted by this decision.

## 次の研究提案（F006 / 2026-10-16、未実装）
F001〜F005の採用範囲を維持。次は`topics/F006-timestep-diagnostics/SPEC.md`の**時間刻み差分診断**という一能力のみ。Issue #16。設計ブランチの提案を採用済みと混同しない。既存F005は変更しない。`experiments/F006/PLAN.md`でWolframの理論値と未実施のSOMA実測を明確に分離する。実装時には同一PRでコード・テスト・システム図・データ契約・findings・READMEを同期し、独立監査とユーザー判断までmainに統合しない。


### F006 v2独立監査後の改訂方針（2026-10-17）
SPECのv2改訂節を旧入力/分類案より優先する。既存F005は不変。出自の期待値は信頼するcheckout/外部CIから得て、診断本体・再利用oracleもhash対象とする。公開前stage/replay監査、例外rollbackを実装し、2パスのcrash原子性は主張しない。固定対照の事前ラベルと観測signatureを分け、一般的な原因推論へ拡張しない。旧v1データを上書きしない。

### F006 実装担当への追加ルール（2026-10-16）
F006は後処理のdt横断診断器。既存の`soma/f005.py`と歴史的証拠を修正しない。既存の保存ログ独立検証器を利用しても、クロスdtの参照・原因分類は別に検査する。A〜Fの有理数参照とbinary64参照を混同しない。F006はモデルのdt不変性を証明しない。詳細はF006 SPEC末尾のG1〜G5採用ゲート、実験PLAN、図、データ契約。設計と実測を区別し、採否判断前にmain統合しない。

### F006実装候補の取り扱い（2026-10-16）
実装Draft [PR #18](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/18)は設計Draft PR #17に積む。現段階は未採用。F006 A〜Eは15run、Fはテスト側の改変・入力拒否・完全再生。ソフトウェアの`supported`を時間刻み非依存性、実機物理、生存、自律性や身体創発の証拠としない。最終HEAD CI・別視点監査・ユーザーによる採否決定まで`main`にマージしない。

### F006 v2修正候補の監査入口（2026-10-17）
現行実装PR #18はv2契約（SPECの改訂節を最優先）。通常/最適化の負例、3.11/3.12 CI、15run/81ファイル再生を検査する。audit_suiteのexpected_identityは外部CIや信頼するcheckoutから得る。未信頼manifestから自己検証用の期待値を作らない。独立レビュー後の修正を当人が検証したことと、別レビュアーによる再審査完了を混同しない。

## 現行の研究判断：F006限定的正式採用（2026-10-17）

F006はユーザーの明示的な採用・統合指示により、**F005 v1・固定A〜Eの15runのdt差分診断（`f006.v2`）のみ**正式採用。設計PR #17はmain統合済み、実装と本記録はPR #18で統合する。上記「候補」「未採用」は当時の履歴。[最終監査と採用対象](findings/F006-validation.md#2026-10-17-f006-限定的な正式採用--最新研究判断)を優先。A〜EのWolfram参照、Python3.11/3.12各112テスト、F006 19最適化、139ステップ/126イベントの別式照合、81原本と81再生のバイト一致とP2 2件の改修が根拠。正規化した入力と証拠出自・改変・失敗時公開の検証を再現すること。SPECを変更したので最終HEADのCIを確認してからmainへマージする。一般因果診断、刻み幅不変性、実物理/電気消費、F003への力学結合、生存、創発、crash-atomicな二宛先公開は認定しない。F001〜F005の物理コード・旧証拠は変更しない。

## F007設計提案の読み方（2026-10-17、未実装）
- [Issue #19](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/19) → `topics/F007-linked-motor-work/SPEC.md` → `experiments/F007/PLAN.md` → `findings/F007-validation.md`。
- 次の一能力は「結合2セルの片側A駆動とAの電池支出を合成する」だけ。F003/F005/F002の既存ソースや履歴データを変えない。実装・実験未実施、未採用、main未統合。
- Aの指令/適用力、F003リンク内力、F005正仕事、F002電池spend、外力を区別。リンク仕事とF002電気的移送を混同しない。F005の実際の推進反力の欠落、位置/仕事軌道差とF006 dt依存を引き継ぐ。
- 設計だけのDraft PRと、別の実装・証拠PRを分ける。コード・図・契約・findings・READMEは実装PRで同期し、最終HEAD CI・独立監査とユーザー判断まで統合しない。

## F007実装候補の変更管理・監査ルール（2026-10-17）

F007の設計PR #20と実装PRは分離する。後者は設計HEADにstackし、独立のレビューと研究者の明示採否まではDraft、mainへ統合しない。`soma/f007.py`、`experiments/F007/run_suite.py`/`verify.py`、`tests/test_f007.py`、CI、`docs/ARCHITECTURE.md`、`docs/DATA_CONTRACTS.md`、`findings/F007-validation.md`、READMEを同じPRで同期。

F007はAのみのmotor、Bはpassive。BのF002残高を機械リンクで支出してはならない。Aの不足でモーターだけを0としてF003のリンク/各外力は再計算。切断瞬間のx/v jumpは禁止。F005の区間正仕事・semanticsを変えない。CSVからの独立参照は数式別実装であり実行モデルを呼び戻さない。F005のbinary64課金を任意dtでFraction正確値と同一と一般化しない。

機械的な「リンクでBを動かす」と、「電気的にBへ移送する」、実機で地面反力を使う自己推進を区別する。CI未確認・外部レビュアー不在・まだ採用前を必ず明記する。


## F008 next one-capability task (2026-10-17, design only)

F007 is limited-adopted and merged; do **not** treat old historical Draft paragraphs as current status. F008 is currently **proposed / unimplemented / unexecuted / unadopted**:
- Task: [Issue #22](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/22)
- Hypotheses, allowed observation fields and scientific limits: [SPEC](topics/F008-local-load-detection/SPEC.md)
- A–F preregistered controls: [PLAN](experiments/F008/PLAN.md)
- Unexecuted findings and evidence gates: [findings](findings/F008-validation.md)
- Cross-feature diagrams and data contracts: [architecture](docs/ARCHITECTURE.md) / [data](docs/DATA_CONTRACTS.md)

Implement **only** A's local motion-response discrepancy using F007 as the unchanged world model. Never expose attachment/B/link ground truth to the cell-side API; use those exclusively in the evaluator. A disconnected cell with a hidden -1 N external force can mimic the linked motion response, so never label a residual as verified connectivity. Separate theoretical Wolfram references from actual experiment records. Future implementation requires a separate PR synchronizing code, tests, diagrams, data contracts, README/AGENTS and findings, plus CI, independent audit and the researcher's explicit adoption decision before any merge.


## F008 実装候補引き継ぎ（2026-10-18・PR #27、未採用）

設計Draft #23の上に積んだF008実装Draft #27を優先参照。F008の提案時の「未実装」は当時の履歴。今回の*ソフトウェア候補*は `soma/f008.py` のA-only allowlist/detect、`experiments/F008/run_suite.py` の固定A〜E、`experiments/F008/verify.py` の保存独立検査、`tests/test_f008.py` と CI、及び同一PRの図・データ契約・findings・索引。

- 同じA局所応答はB接続とD非接続の隠れ外力から生じる：**リンク同定を決して主張しない**。A観測にB/attached/未知外力を渡さない。
- F008はオフライン研究用の射影であり、実時間制御や悪意ある同一プロセスのPythonの隔離を示さない。適用モーター力はAの理想局所フィードバック。停止時は not_excited。
- 原本F007保存監査の上にF008別式ローカル検算、F008自身のソースSHA（trusted checkout）、改変拒否、A〜E理論値、同一バイト完全再現を確認。Git SHAをCI HEADとPR HEADで区別。**テスト完了・人間レビュー・採用は別物**。
- 実行証拠は [F008 findings](findings/F008-validation.md) の最新追記を確認。main変更・正式採否・証拠の削除にはユーザー承認が必要。旧F001–F007 API/証拠は改変しない。

## F008 最新判断：研究者による限定採用・統合承認（2026-10-18）

F008 `f008.local.v1` はAIの別視点数理・コード・証拠監査後、**研究者が限定的な正式採用とmain統合を明示承認**。旧「設計案／未実施／候補／未採用」は当時の履歴として保持し、[F008 findings の最新採用判断](findings/F008-validation.md)を優先。設計PR #23はmain統合済み。実装PR #27のmain統合とmain CIは最新GitHub状態で必ず再確認すること。

採用範囲はF007固定1D離散モデル上の、オフラインA自己速度差・自己モーター実適用力・自己電池残量からの単体予測**加速度残差の異常検出**のみ。B/接続真値や未知外力はセルへ渡さない。B接続とD非接続+未知外力の局所全系列は区別不能。`not_excited`を結合判定に使わない。1e-12は数値対照の閾値であり実機感度ではない。独立の人間監査、実機推進、接続同定、学習と創発は未検証。AI reviewerのコメントは人間のGitHub APPROVEと同義ではない。新しい研究課題に自動着手しない。


## F009 設計専用研究指示（2026-10-18）
[Issue #28](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/28)の一能力だけ：F007外部有効力、閉鎖二セル内部対作用、地面牽引反作用の運動量収支を比較する。SPEC/PLANのA〜F・理論値・許容差を観測前に凍結。別実装Draft PRでコード・テスト・原本・図・データ契約・findings・README/AGENTSを同期。独立オラクル、Python3.11/3.12、全回帰、失敗/改変/再現性、CI HEAD証拠を残す。F001-F008変更なし、V001 PR #25/#26には触れない。世界真値や地面反力はF008セル局所APIに送らない。理想1D接地モデルは実機接触/移動/創発の証拠ではない。独立レビューと研究者採否が未完ならDraft維持、mainマージ禁止。


### F009 implementation candidate handoff (2026-10-18)
Design Draft PR #29 / implementation Draft PR #30 / Issue #28. Frozen A-F references remain in PLAN, with actual software execution in findings. Initial implementation HEAD 74180c5 passed 3.11/3.12 144 full tests +7 optimized, 6×5 rows, 20 files×2 replay; all F001-F008 workflows green. Commit containing later docs/finding updates must pass its own CI. Do not upgrade model_result_candidate_not_adopted to adoption. Review source SHA, exact-rational oracle, rehashed-tamper negative cases, preservation of F007 physics and world-vs-F008 boundary. Separate human/external review remains unperformed. No main merge, formal adoption, or Issue closure without researcher explicit decision.


## F009 最新の正式採用範囲と監査引き継ぎ（2026-10-19）

研究者はF009 `f009.momentum.v1` を**固定1D・2セル・A〜F対照の離散運動量/力源会計**に限って正式採用し、現状の限界を記録したうえで設計PR #29 → 実装PR #30のmain統合を明示承認した。過去の「未採用」「Draft」は歴史的記録。最新の統合結果は[Issue #28](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/28)・各PR・[F009 findings](findings/F009-validation.md)で確認する。最終承認前の採用根拠は実装HEAD `e6873bcaa2f2619380793cf3157fb967020684f0` の[Actions #39135941901](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39135941901)、Wolfram/独立Fraction、全6×5生CSVの別式計算、原本ZIP、3.11/3.12全回帰。

**絶対に主張しないこと**：地面反作用は`-traction`のモデル定義であり、実機の接地反力の測定ではない。一般摩擦・接触・法線・滑り/車輪/脚、実際の自走・モーター電気消費、任意物理条件やdt収束、実際の推進効率、セルの接続構造推定、局所学習、身体形成・創発・進化の検証ではない。F009世界真値は研究者用でF008セルA局所APIには送らない。F001〜F008の採用済みソース/過去の結果、および別課題V001 PR #25/#26は変更しない。2つの出力フォルダ間で停電耐性のあるatomic commitは非保証。AIの別式・別チャット監査は独立の人間・外部レビュアー査読と異なる（未実施）。

mainへ反映する前に**採用記録の変更を含む最終HEADのCI**と、設計PRと実装PRの依存/差分を確認し、統合後もmain CIとIssue #28完了を確認すること。新課題へ自動移行しない。

## F010 handoff — active local identifiability (2026-10-19, design only / NOT ADOPTED)

Scope limited to [Issue #31](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/31). Frozen [SPEC](topics/F010-local-identifiability/SPEC.md), [A-F PLAN](experiments/F010/PLAN.md), [FINDINGS](findings/F010-validation.md), diagrams/data contracts in the DESIGN DRAFT PR. Use F007 unchanged independent 1s/h=.25 runs and strict F008.LocalObservation. Probe actual applied u=2,1,.5 N with two-point fit and third-force holdout; test constant unknown force vs link, and counterexample input-dependent force d(u)=-u/2 yielding identical A-local traces (including A battery). Never imply connection identification or autonomous probing. Implement code, tests, independent raw oracle, reproducible evidence, CI and synced docs in a separate stacked IMPLEMENTATION DRAFT PR. Do not touch other projects/V001 or merge main before researcher's separate adoption decision. Historical 'unexecuted' preregistration remains unchanged after later evidence; append dated findings instead.

### F010 implementation candidate review handoff (2026-10-19, unverified until HEAD CI)

Design Draft #32 first, implementation Draft stacked on it. New `soma.f010.estimate` accepts **only typed F008.LocalObservation tuples**. Source physical data are from unchanged F007, selected A/B hidden forces only in researcher-side runner/verify; signed effective-force and battery semantics are inherited, not new validated hardware physics. Existing F007 saved oracle plus F010 Fraction independent full-row oracle check all 15 runs/60 local intervals and A=C trace equality. F010 workflow runs full regression and optimized tests under 3.11/3.12, publish only after success. Never conflate branch CI success, independent human review, formal adoption and main merge; leave Draft open until researcher authorizes. 

### F010 successful candidate evidence and remaining gate (2026-10-19)

Implementation PR #33 `c370562`, Actions #39228478362: Python3.11/3.12 each 153 full tests +9 optimized, 15 model trials/60 A-local intervals, independent saved Fraction and rehashed tamper audit, 107-file replay succeeded; all ten F001–F010 workflow runs green on that code SHA. Previously failing additional forgery-fixture test at `4a2e24b` is preserved in findings, fixed in `c370562`. Recheck workflow success after ANY subsequent documentation change; append final HEAD evidence, never reuse the earlier HEAD success. Results prove only fixed 1D affine signature and non-identifiability for d(u)=-u/2, not coupling identity. Independent human review and formal acceptance/merge remain unperformed/unauthorized. Keep PR #32 and #33 Draft, Issue #31 open, main untouched until fresh researcher approval.

### F010 final reviewer decision (2026-10-19; earlier draft handoffs remain historical)

Reviewer **approves limited adoption and authorizes integration** for the fixed 1D offline A-local affine-response signature and input-dependent-hidden-force non-identifiability result, following corrected command/applied motor gate and normal-exception paired-publish rollback. Verified `e1c664e`: 155 complete regressions + 11 F010 optimized tests under Python 3.11/3.12, all ten workflows, independent saved-data Fraction audit, 107-file exact replay. Merge design PR #32 before retargeting/merging implementation PR #33 into main; record actual merge SHAs and main CI in Issue #31. Do **not** recast `inertia_like` as attachment or self-body-schema learning, describe researcher-orchestrated probes as online autonomy, or silently extend to hardware/contact/noise/variable dt. External human review and crash-power-loss atomicity remain unperformed. Preserve preregistration and immutable experimental-time evidence metadata.
