---
id: EXP-F003
title: F003機械結合の比較実験計画
kind: experiment_plan
status: proposed
updated: 2026-10-14
feature: F003
---

# F003 — 実験計画（未実施）

[仕様・図](../../topics/F003-attachment/SPEC.md) / [追跡 Issue #3](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/3)

## 一度に変えるのは結合条件だけ
初期条件 m_A=m_B=1 kg、gamma=0.2 1/s、x_A=0 m、x_B=0.5 m、v_A=v_B=0 m/s、dt=0.01 s、duration=10 s。外部駆動力は指定された場合だけ印加する。数値は**事前設定案**であり測定値ではない。

| 条件 | リンク | 外力 (A/B) | 観測・検証 |
| --- | --- | --- | --- |
| A 未結合対照 | OFF | +1 / 0 N | AはF001に一致し、Bは静止 |
| B 片側牽引 | ON | +1 / 0 N | 共通速度、距離L一定、リンク力±0.5 N（理想モデル） |
| C 双側駆動 | ON | +1 / +1 N | 共通速度、等質量なら内部リンク力0 N |
| D 中途切断 | ON→OFF (t=5 s) | +1 / 0 N | 切断瞬間の状態連続、以降は独立更新 |
| E 力の符号反転 | ON | +1 / 0 vs -1 / 0 N | 共通変位・速度の反転対称性（初期オフセットLを除く） |
| F 数値・不正条件 | ON / 拒否 | B条件のdt半減・不整合な初速／位置 | 理論誤差の収束傾向、無理な瞬間結合を拒否 |

## 保存する観測量
- t [s]、x_A・x_B [m]、v_A・v_B [m/s]、外力F_A・F_B [N]。
- 結合状態、リンク内部力T_A・T_B [N]、距離拘束誤差 [m]、速度拘束誤差 [m/s]。
- 重心位置・速度、解析解との差、切断前後のジャンプ量、数値刻み感度。
- 実験ID、設定、シード（乱数未使用なら明示）、Git commit SHA、ファイルSHA256。

## 実験成果物（予定・存在しないものを存在すると記載しない）
~~~text
experiments/F003/
  PLAN.md
  configs/           # 実装後
  run_suite.py        # 実装後
findings/F003-validation.md   # 実験後
GitHub Actions artifact: raw configs / states / events / comparisons / figures / manifest
~~~

## 実行→監査→採否
1. SPECの境界と許容誤差を実装前に監査し、F001既存テストの回帰を先に確認。
2. A〜Fを実装・実行し、生ログ・対照グラフ・失敗したテストも残す。
3. 別視点のレビューで、結果と事前仮説・理論予測を突き合わせる。
4. 支持／反証／不明を条件別に記録し、改善なら仕様へ戻す。成功かつレビュー済みの場合のみmainへ採用。

**現段階の実験結果：未実施。** F002のレビュー待ちとは独立して設計を進める。
