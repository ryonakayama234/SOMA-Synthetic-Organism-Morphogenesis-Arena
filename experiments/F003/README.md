# F003 再実行ガイド（実装候補）

前提：Python 3.11+、追加パッケージ不要。リポジトリルートから実行。

~~~bash
python -m unittest discover -s tests -v
python -m experiments.F003.run_suite --output-dir runs/F003-local --replay-output-dir runs/F003-replay
~~~

各正常runのconfig.json、states.csv、events.csv、motion.svg、manifest.jsonに加え、比較結果comparison.json、rejections.json、suite_source.pyを保存する。過去データは上書きせず、新しい出力パスを使う。

GitHub Actions `F003 two-cell ideal mechanical coupling` によるartifact名は `F003-A-F-evidence`。最新HEADのCIと独立監査を確認する前に正式採用と書かない。

[事前登録SPEC](../../topics/F003-attachment/SPEC.md) / [アーキテクチャ](../../docs/ARCHITECTURE.md) / [findings](../../findings/F003-validation.md)

監査修正後は保存CSV/イベントそのものを独立離散式と照合する。10拒否例の入力全体と拒否証拠SHAを保存。`--replay-output-dir`は比較JSONを含む全成果物の再実行一致を検査し、`full_suite_replay.json`へ証拠を残す。初回と再実行は新しい別の出力先を指定する。
