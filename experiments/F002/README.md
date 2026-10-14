# F002 再現手順（数値台帳・非物理）

```bash
python -m unittest discover -s tests -v
python -m experiments.F002.run_suite --output-dir runs/F002-local
python -m soma.f002 --config experiments/F002/configs/D_transfer.json --output-dir runs/F002-D-standalone
```

各runフォルダに `config.json`、`events.csv`、`balances.csv`、`energy.svg`、`manifest.json` を保存する。`comparison.json` と `E-invalid-events.json` も保存する。Fでは**同一設定を独立した出力先で再実行**し、`F-bulk-replay/`・`F-split-replay/` を作成する。比較した5ファイルのSHA256一致を `comparison.json:f_replay_checks` に記録する。元の実験設定（`experiment_id`・イベント列・seed）は変更しない。既存パスの上書きは禁止。別実験では新しいフォルダ名を使う。

- A: **単一セルA=10 J**、入出力0。
- B: **単一セルA=10 J**が5 Jを外部から取得。
- C: **単一セルA=10 J**が3 Jを系外へ支出。
- D: AからBへ3 J、80%で台帳上移送し、0.6 Jを損失として記帳。
- E: 不正入力13ケースを拒否（小数・非有限値を含む。例外、台帳は変更されない）。
- F: 3 µJの50%移送で一括1 µJ到着、三分割0 µJ到着。量子化差を記録。**一括と分割をそれぞれ同じイベント列で2回実行**し、`config.json`・`events.csv`・`balances.csv`・`energy.svg`・`manifest.json` のバイト同一性を保存証拠で監査する。

整数µJとbpsで計算し、`residual_uj=0` を厳密比較。エネルギー支出は電動機の消費電力や運動エネルギーを意味しない。セル同士はまだ物理接続されていない。制御学習・資源枯渇・実機物理は未実装。

個別の結果と留保：[findings](../../findings/F002-validation.md)。研究仕様：[SPEC](../../topics/F002-energy-ledger/SPEC.md)。