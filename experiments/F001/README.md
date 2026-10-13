# F001 実験の実行方法

このフォルダの実験は、単一セルの一次元運動モデルを検証するためのものです。**このモデルには結合・制御学習・エネルギー消費はありません。**

WSL2/Linux、Python 3.11 以降を想定。外部パッケージ不要です。repo直下から実行します。

```bash
python -m unittest discover -s tests -v
python -m experiments.F001.run_suite --output-dir runs/F001-first
```

`runs/F001-first/` に A〜Dと Eの時間刻み変更による計6ケースが保存されます。各ケースに `config.json`、`states.csv`、`motion.svg`、`manifest.json` が入り、全体の `comparison.json` に理論解との差と時間刻み収束を記録します。

```bash
python -m soma.f001 --config experiments/F001/configs/B_positive.json --output-dir runs/F001-single
```

既存の出力ディレクトリを上書きしません。同じ名前で再実行する場合は新しい名前を指定してください。

## モデルの限界

- `m dv/dt = F - m gamma v`。抵抗は**線形粘性抵抗**であり、クーロン摩擦や接触力をモデル化していません。
- `v`を先に更新し、その値で`x`を更新する半陰的Euler法です。
- `dt*gamma <= 1`、かつ`duration/dt`が整数となる設定のみ受け付けます。
- `seed`は互換性のため記録しますが、F001に乱数はありません。
- `manifest.json`のコード版は`git rev-parse HEAD`で取得し、Git外で実行した場合はnullです。Gitの未コミット変更を追跡しないため、比較結果の正式な記録はクリーンなコミット上で行ってください。

[仕様](../../topics/F001-single-cell-motion/SPEC.md)
