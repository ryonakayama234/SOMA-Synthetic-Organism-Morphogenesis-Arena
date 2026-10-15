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
