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


## 一機能ごとの必須同時更新（2026-10-14追加）
- 実装・調査・実験の各PRでは、仕様（topics）、システム図（docs/ARCHITECTURE.md）、データ構造/流れ（docs/DATA_CONTRACTS.md）、実験計画と結果（experiments / findings）、入口（README）を同時に確認・更新する。
- Mermaid図は文章と整合させ、提案だけの設計を実装済みと表示しない。観測値と理論予測を分ける。
- 実験の生ログ、対照群、コードSHA、失敗結果をPRに紐づける。第三者レビュー前にmainへ統合しない。
- F002はレビュー待ちの別PR。F003はF001だけに依存する設計で、F002ブランチを混ぜない。
- 詳細：[研究運営の同期規則](docs/RESEARCH_PROCESS.md)。
