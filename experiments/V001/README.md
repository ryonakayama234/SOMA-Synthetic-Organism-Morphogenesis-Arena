# V001 — F007保存実験をローカルブラウザで観察する

**2026-10-17 / PR #26の実装候補。V001は正式採用前。** 既存F007の世界真値を研究者向けに再生するのみ。F008のセル局所感覚・実機・2D/3D創発を実装しない。

## WSL2/Linux での実行

リポジトリのルートで次を実行する。

```bash
python -m unittest discover -s tests -v
python -m experiments.V001.run_suite --output-dir runs/V001-ci --replay-output-dir runs/V001-replay
python -m experiments.V001.build_view --source runs/V001-ci/f007/E-cut --output runs/V001/E-cut-single
```

`runs/V001-ci/v001/E-cut/viewer.html` をWindowsブラウザで開く。WSL2の場合、エクスプローラーから `\\wsl$\<ディストリビューション名>\...` を辿って表示できる（実際のディストリビューション名・作業ディレクトリに置換）。

使用できる操作：前へ／次へ／再生／停止／保存ステップ選択／表示速度0.5・1・2倍。保存時刻の間の物理状態は補間しない。速度倍率は閲覧速度だけを変更する。

## 構造と保存物
- F007原本：`runs/V001-ci/f007/<case>/`（config / states / ledger / link_events / motion / manifest）。
- V001の表示証拠：`runs/V001-ci/v001/<case>/frames.json`、`viewer.html`、`viewer_manifest.json`。
- 9条件＋byte replay：`runs/V001-ci/comparison.json`。同一9条件の二度目は `runs/V001-replay/`。
- 根拠となるコードは `soma/v001.py` と `experiments/V001/build_view.py`、原本オラクルは `experiments/F007/verify.py`、独立の出力監査は `experiments/V001/verify.py`。
- 正規化フレームは `v001.frame.v1`、V001の証拠は `v001.evidence.v1`。正確なキーは `docs/DATA_CONTRACTS.md` の実装候補節を参照。

実験原本は上書きしない。出力に既存ディレクトリを指定すると拒否。保存データはGit checkout側の`provenance()`とF007の数値・イベント・ハッシュを照合。異なるコミットで作られた原本を**未検証のmanifestを信用して**表示しない。必要なら正しいコミットのcheckoutに戻して生成するか、外部に検証された独立identityを明示的に使う。

## 採用しない主張
座標は一次元の理想モデルであり、表示上の四角形は実物の外形ではない。リンクの存在は研究者が参照する世界真値であり、細胞自身に公開された感覚ではない。F007の有効モーター力に実際の地面反力は定義されず、位置積分と機械仕事計算の軌道差・dt依存も残る。

[仮説・SPEC](../../topics/V001-readonly-replay/SPEC.md) / [A〜F PLAN](PLAN.md) / [研究 findings](../../findings/V001-validation.md) / [実装PR #26](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/26)
