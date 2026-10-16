---
id: FIND-F005
title: F005 速度反転とモーター正仕事の実験記録
kind: experiment_finding
status: proposed
updated: 2026-10-16
feature: F005
issue: 12
---

# F005 検証ノート【2026-10-16：事前登録・未実施】

## 問い
1セル1Dの正味区間仕事を課金するF004の既知制約を解消するため、**区間内正仕事の積分**によって再加速費用を計量できるか。

## 事前登録されたH005
[仕様](../topics/F005-positive-work/SPEC.md) と [実験計画A〜F](../experiments/F005/PLAN.md) を参照。反転の解析例は `m=1kg, u=-2N, v0=1m/s, dt=1s` で `W_signed=0J`, `W_plus=0.5J`。理論値はWolfram Languageの事前積分結果 `1/2` に基づく。**実験観測ではない。**

## 証拠の状態
| 記録 | 状態 |
| --- | --- |
| SOMA F005 コード・計算ログ | 未実装・未実施 |
| A〜F実測、CI、ソースSHA・artifact | 未実施 |
| 実測値と理論値の差 | 未算出 |
| 不正入力拒否、再実行、改変検知 | 未実施 |
| 独立実装監査と採否 | 未実施・未判断 |

## 実装後に追記する様式
- 日時、ブランチと実行commit、dirty状態、source/suite SHA、Python版、seed、環境条件。
- 事前参照（Wolfram有理数・binary64独立オラクル）とSOMA実測値。A〜Fごとの支持・反証・不明。
- 全ステップ真値CSV・F002 spend・残高不変条件・仕事分離・数値許容差。
- 速度反転の粗いdtと細かいdt比較。誤差と整数µJ切上げ差を分離。
- 無効ケース、ログ改変・再実行一致、CI artifactのURLとハッシュ。
- 統合前の独立監査の指摘、改訂履歴、保留課題、正式採用範囲。

**禁止**：仕様作成だけで成功・観測済みと記載すること。F005の単一セル正仕事計測を、2セル結合の有利性・創発・実機妥当性の証拠とみなすこと。

[Issue #12](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/12) / [計画](../experiments/F005/PLAN.md)。

## 2026-10-16 Wolfram事前理論検算（実装・実験は未実施のまま）

実装前に一定力・端点速度の線形補間に対する`Integrate[Max[0,u*(v0+(v1-v0)*t/h)],{t,0,h}]`を独立評価。反転A：`W_signed=0, W_plus=1/2 J`、通常加速C：`1/2, 1/2 J`、制動D：`-1/2, 0 J`、外力のみE：`0, 0 J`、0.5秒×2の反転F：`W_plus=0+1/2 J`、非対称反転：`W_signed=4, W_plus=9/2 J`。2分割正仕事と1分割正仕事が同じことも検算。

上記は**理論・事前予測**のみであり、F005 Python実装・CI・artifact・GitHub main統合・採用判断の証拠ではない。F004既存のモデルとF001の位置積分誤差を混同しない。定量ゲートは[仕様](../topics/F005-positive-work/SPEC.md)と[A〜F計画](../experiments/F005/PLAN.md)の2026-10-16追記に記録。

## 2026-10-16 Implementation candidate (not yet independently validated in CI)

An implementation branch contains the new single-cell module `soma/f005.py`, `tests/test_f005.py`, A–F suite `experiments/F005/run_suite.py`, instructions, `.github/workflows/f005.yml`, synchronized architecture and data-contract sections. This is **code availability only**, not an observed result or formal adoption.

### Implementation boundary
- F004 `f004.v1` and F001/F002/F003 are left unchanged.
- The new `f005.v1` contract adds candidate/accepted positive motor work, separately preserving signed midpoint work.
- The A–F saved-file independent oracle, tampering, microjoule rounding, and whole-suite byte replay are programmed for CI.
- Pending: GitHub Actions status for the exact implementation HEAD, immutable artifact hashes, independent review, any failed cases and corrective changes.

### Quality gate
Mark this feature `observed` only after obtaining successful CI **on the final proposed HEAD** and independently inspecting tests/results. Preserve error reports and failed iterations. Do not treat the earlier Wolfram rational reference as SOMA output.

## 2026-10-16 GitHub Actions 初回実装と監査修正後の観測

### 反例と改善
初回設計通りに端点`p=u*v`の値で正負を判定すると、`u=1e-200, v0=v1=1e-200, h=1e300`のような入力で両端のパワーが0へアンダーフローして、理論上正の仕事を無料にしてしまう。Wolframの有理数積分は`10^-100 J`で正。F005実装は力の方向と速度の符号を利用した判定に変更し、同一入力を**正仕事1e-100 J／1µJ支出**として回帰テストで検証。正仕事と電気消費の現実妥当性は依然非対象。

### GitHub Actionsの実行証拠（実装候補HEAD）
- **検証HEAD**: `6fa44afb057ce6dc2db66015575c0d7452d596a3`
- **F005 workflow**: [run #38876548177](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38876548177) — `success`、Python 3.11、**90 tests / OK**（既存F001〜F004 73＋F005 17）。
- 正常A〜Fは**10ケース**、不正入力は**17件を事前拒否**。保存CSV全時刻とF002支出イベントの独立照合、保存成果物SHA、tamper拒否、完全スイートのバイト再実行一致に関するCIジョブが成功。
- A反転：W_signed=0J、W_plus=0.5J、500000µJ支出、残高0。Bの残高1µJではモーターを拒否し、残高1。非反転、制動、外力、刻み分割、非対称反転についてA〜Fの事前ゲートと整合。
- GitHub Actions artifact: [F005-A-F-evidence（ID 12036090522）](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38876548177/artifacts/12036090522)。生成物一式のZIPとともに、個別のCSV・Ledger・SVG・manifest・suiteソースハッシュが保存されている。
- 他の4 workflowも初回実装HEAD `1fc95f9aa4d405050f03cc3ce5c274f4fdd982c3`ではsuccess。**修正済み最終HEAD**のF001〜F004 workflow結果は別途確認して確定する。

### 判定
上記は**ソフトウェアモデルに関する事前仮説を支持**するCI証拠であり、実機の電池消費や自律的な形態創発を確認したわけではない。バッテリー効率・保持消費は未モデル化。非有限な中間計算はrun保存前に拒否する。独立第三者による最終監査とユーザーの正式採用判断は未了。mainは変更していない。
