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
