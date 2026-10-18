---
id: F008
title: 局所運動応答による未知の有効負荷の検知
kind: feature_spec
status: proposed_unimplemented
updated: 2026-10-17
issue: 22
depends_on: [F001, F002, F003, F005, F006, F007]
---

# F008 — 自分の身体が重くなったと気づけるか？

**状態：設計案。実装・実験・CI・採用はいずれも未実施。**

[Issue #22](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/22) / [事前登録実験](../../experiments/F008/PLAN.md) / [研究ノート](../../findings/F008-validation.md)

## 唯一の新しい能力
セルAが、自分の運動・自身のモーター指令と実行可否・自身の電池だけから、既知の単体運動モデルで説明できない**有効負荷の変化**を検知する。F007の世界真値から局所観測へ射影する境界と、A自身の運動応答残差だけを実装対象にする。

**対象外**：接続グラフの同定、相手個体の特定、学習、身体改造、制御最適化、実機・進化・創発。既存F001〜F007の物理・電池コードと証拠は変更しない。

## 仮説と反証
- H008a：mA=mB=1kg、Aの実効駆動u=2N、drag/外力0、dt=1/4sではAの初回速度増分は非接続1/2m/s、結合1/4m/s。局所運動のみで差を測れる。
- H008b：F007の時刻指定切断後、駆動が維持されるならAの加速度は結合中1から非結合2m/s²へ変わる。Aには切断真値を渡さない。
- H008c：セルが受け取る情報にはattached、Bの質量・位置・速度、リンク力、実験正解ラベル、全体グラフは含まれない。
- H008d：非結合で未観測外力fA=−1Nがあると加速度1m/s²を再現できる。よって**負荷変化の検出は、結合の一意な証明ではない**。
- 反証：参照差が現れない、外力の混同対照を結合と断定する、電池拒否/速度差0で偽の有効質量を出す、世界真値が局所APIに混入、証拠改変に気づかない。

## Wolframで検算した理論参照（SOMA観測ではない）
理想モデルで a=delta_v/dt。非結合はu/mA=2、結合はu/(mA+mB)=1 [m/s²]。一刻みdelta_v=1/2, 1/4 [m/s]、半陰的Euler delta_x=1/8, 1/16 [m]。条件付きの見かけ質量u/a=1,2 [kg]。非結合+未観測外力−1Nならa=1となり結合時と同じ局所観測を与える。

観測残差は r=a_observed−u_applied/mA。ゼロでない残差は**応答異常**を意味するが、原因が接続とは限らない。見かけ質量u/aを有効にする条件は、外力や抵抗が無く、uが実際に作用し、a≠0の時に限る。F007の有効モーター力には地面反力・実機推進を定義していない。

## 提案するシステム図
~~~mermaid
flowchart LR
 C["研究設定"] --> W["F007 世界真値：A/B、リンク、仕事、電池"]
 W --> P["F008: セル別の局所観測へ射影"]
 P --> A["A: 自分の速度差・自身のモーター状態・電池"]
 A --> R["単体予測との差を検知"]
 W --> T["研究者専用の全状態・正解"]
 R --> V["オフライン評価"]
 T --> V
 V --> L["実験記録、独立照合、manifest"]
~~~

**世界真値の漏洩を禁止**：セルの観測から直接リンクのON/OFFやBの状態を読ませない。研究者の評価器だけがAの残差を正解に照らす。

## 提案データ
1. 世界真値：既存F007の保存結果、研究者のみが使用。
2. セル向け観測：個体ID、時刻、自己速度変化、dt、自身のモーター指令・実行力・電池残量。列順・バージョンは実装前に確定する。
3. 局所推定：自己モデルの予測加速度、観測加速度、残差、推定成立可否。未知外力で結合状態を断定しない。
4. 評価・証拠：研究者だけがケース真値・局所推定を比較。条件・Git SHA・依存ソースSHA256・完全観測ログ・再実行一致を保存。

## 採用ゲート
事前A〜Fを固定→設計レビュー→**別実装PR**で最小実装→Python3.11/3.12全回帰・実験A〜F・独立オラクル・負例・改変拒否・バイト再現→別視点監査→findingsに結果/限界/失敗追記→研究者の明示的採否後に限りmain統合。図、データ契約、コード/CI、findings、READMEを同じ実装PRで同期する。


## 2026-10-18 implementation candidate (append-only; A–F predictions unchanged)

A separate implementation branch adds `soma/f008.py` for A-only allowlisted observations and the fixed nominal single-cell acceleration residual, `experiments/F008/run_suite.py` for A–E runs and full replay, `experiments/F008/verify.py` for saved-data oracle, and `tests/test_f008.py`. **This is not an adoption or a change to preobserved theoretical predictions.**

- Only A-local time, previous/current self velocity, A's commanded/applied effective motor force, and A battery balance may enter the detector. The nominal A mass is a predefined single-cell calibration (1 kg in frozen controls); neither B nor the link state is supplied.
- The applied-force field is treated as locally available actuator execution feedback, an explicit idealization that must not be silently generalized to real devices.
- If applied motor force is zero, the output is `not_excited`; no mass estimate or residual-based causal claim. Otherwise report `nominal` or `anomaly` from `observed_accel - applied/nominal_mass` (absolute tolerance 1e-12 m/s² on preregistered rational controls only).
- B (linked) and D (unlinked, hidden A force) must have identical A-local histories but different researcher-only world truths. No result is labeled `attached` by the cell.
- The detector is **offline processing of F007 saved states**, not a live sensor implementation or active probing. Position, mechanical work, battery and numerics of F007 stay unchanged.
- Run, CI and independent audit evidence are tracked in `findings/F008-validation.md`; main and user research acceptance are separate gates.
