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
