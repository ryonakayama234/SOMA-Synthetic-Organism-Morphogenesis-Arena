# F002 再現手順（数値台帳・非物理）

```bash
python -m unittest discover -s tests -v
python -m experiments.F002.run_suite --output-dir runs/F002-local
python -m soma.f002 --config experiments/F002/configs/D_transfer.json --output-dir runs/F002-D-standalone
```

各runフォルダに `config.json`、`events.csv`、`balances.csv`、`energy.svg`、`manifest.json` を保存する。 `comparison.json` と `E-invalid-events.json` も保存する。既存パスの上書きは禁止。別実験では新しいフォルダ名を使う。

- A: 入出力0、静止した残量10 J。
- B: Aが5 Jを外部から取得。
- C: Aが3 Jを系外へ支出。
- D: AからBへ3 J、80%で台帳上移送し、0.6 Jを損失として記帳。
- E: 不正入力9ケースを拒否（例外、台帳は変更されない）。
- F: 3 µJの50%移送で一括1 µJ到着、三分割0 µJ到着。量子化差を記録。

整数µJとbpsで計算し、`residual_uj=0` を厳密比較。エネルギー支出は電動機の消費電力や運動エネルギーを意味しない。セル同士はまだ物理接続されていない。制御学習・資源枯渇・実機物理は未実装。

個別の結果と留保：[findings](../../findings/F002-validation.md)。研究仕様：[SPEC](../../topics/F002-energy-ledger/SPEC.md)。