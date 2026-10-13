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
