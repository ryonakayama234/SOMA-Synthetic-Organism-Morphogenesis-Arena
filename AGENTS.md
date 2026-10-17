# SOMA — AI研究助手向け案内

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
