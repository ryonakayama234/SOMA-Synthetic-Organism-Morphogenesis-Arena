> **F022.v1 technical status updated 2026-10-25**: limited passive 2D contact instrument **ADOPTED** after design PR #78, implementation PR #79, 22/22 merged-main workflows. This note supersedes historical selection-stage lines below *for status only*. No evidence of voluntary joining or biological embodiment. See [adoption decision](../../docs/decisions/2026-10-25-F022-limited-admission.md).

---
id: F022
title: Encounter Lab — 2Dで独立セルが出会うための接触世界
kind: feature_specification
status: TECHNICALLY_ADOPTED_LIMITED_V1
updated: 2026-10-25
issue: 77
related: [PROJECT, RESEARCH-AGENDA, F021, V001, ARCHITECTURE, DATA]
keywords: [2D, collision, contact, encounter, impulse, body_emergence, passive_dynamics, world_truth, experiment]
---

# F022 — Encounter Lab: 2D接触・衝突世界（設計候補）

**現状：F022.v1数値仕様・反証条件を事前凍結済み／実装・本実験未実施／採用前。** （当初の選定期の文脈は下記に保存）
[Issue #77](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/77) / [研究憲章](../../docs/PROJECT.md) / [研究アジェンダ](../../docs/RESEARCH_AGENDA.md) / [実験計画](../../experiments/F022/PLAN.md) / [findings](../../findings/F022-validation.md)。

## 研究上の欠落と今回の一能力
F021は両側独立理想モーターと個体別採算を1D・研究者指定の結合YY/非結合NNで比較した。9,216世界/4,608比較で、各個体のidle-inclusive outsideを超える同時厳密正利益は0。出会い・接触という幾何イベントはモデルに存在せず、結合は初期条件として設定されている。

今回の一能力は、**平面上を自由に運動する二つの受動的セルが、位置と半径に応じて衝突・離反し、その接触イベントを記録できる2D物理測定器**である。セルが意思決定・協力・合体する機能は追加しない。研究者の見る2D像とシミュレーターが実際に計算した2D運動を一致させる。

## H22 仮説（まだ結果ではない）
- H22a（力学）：十分離れた物体は衝突インパルスを受けない。接近する中央衝突では、凍結された反発係数の法線方向則・総運動量が成立する。
- H22b（幾何）：初期の横ずれと接線成分の有無によって、進行方向が近似的に向き合っていても非接触/斜め接触/正面衝突を区別できる。
- H22c（計測）：生データから独立検証器が接触時刻、法線、速度変化、衝突前後の運動量・運動エネルギーを再計算できる。
- R22a（数値アーティファクト）：刻み幅や衝突処理順で物体が貫通/反発/接触回数を偽って生む。
- R22b（エネルギー偽造）：外力ゼロなのに衝突により総並進運動量やエネルギーが不当に増える。
- Null：接触が一切起きないケースも有効。幾何上接近しても接触しないケースは保存する。

## 世界の契約（値は未凍結）
- 2体の受動的な円盤。質量、半径、2D位置・速度、有限のエピソード時間、摩擦なしの物体間衝突、非貫通。検証を容易にするため当初は回転・角運動量なし、遠隔吸引なし、壁なし/無境界の平面を候補とする。
- モーター、バッテリー、資源、通信、学習、結合ポート、ロボット役割、進化、複数セル群はF022に含めない。初速は研究者が条件設定するものであり、自律駆動ではない。
- インパルスは力学的な**接触イベント**であり、logical attachment edgeには変換しない。F021の外部有効理想モーターを物理的な2D推進手段に再解釈しない。
- 非貫通をどう実現するか（連続衝突時刻の解法か、限定刻み幅とイベント境界の検証か）、同時衝突、初期重なり、不正状態、丸め、反発係数、時間単位と許容誤差は**一次観測の前に事前登録で決める**。
- 将来の各セルに観測を与える場合は、world-truth / local-observation / researcher-viewを分離する。研究者の衝突記録・他方の真の位置・解析用反事実データは個体の政策入力ではない。
- 既存F001–F021の仕様、実験の世界、整数µJ台帳、アーカイブは変更しない。新しい版名 f022.v1 は候補。

## 候補方程式（解析的プレフライトであり実測でない）
2円盤の接触法線 n=(p_B-p_A)/||p_B-p_A||、相対法線速度 v_rel=(v_B-v_A)·n。接近時 v_rel<0 なら、滑らかな理想衝突の候補インパルスの大きさは
j= -(1+e)*v_rel/(1/m_A+1/m_B)  (e in [0,1])
で、v_A'=v_A-(j/m_A)n、v_B'=v_B+(j/m_B)n。接線方向速度は維持。これらをそのままコード化する決定は未凍結。イベントタイミングと重なり解消は別に解決する必要がある。e=1なら理想衝突前後の運動エネルギー同値、e<1なら非増加となる。

## 研究者に見せる物理世界のデータ経路（提案）
~~~mermaid
flowchart LR
  P["事前登録した2D初期条件"] --> W["独立セル2個の運動/衝突計算候補"]
  W --> T["世界真値: 位置・速度・接触"]
  T --> A["時刻付き生ログとmanifest"]
  A --> O["producerから独立した物理監査"]
  A --> V["研究者用2D観察/再生アダプタ（将来）"]
  T -. "将来別実験で射影のみ" .-> L["個体の局所観測（F022未実装）"]
  V -. "世界真値を個体へ返さない" .-> L
~~~
表示画面は計測器。実装がない画面を世界の実験実績としない。

## 先行研究との関係、採否
参照すべき既存V001 [#24](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/24) / [PR #25](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/25) / [PR #26](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/26)はF007の1D保存データを読むDraftで、まだ採用されていない。F022のデータアダプタは後続として構想し、勝手にV001を上書き・統合しない。

成功判定は**正しい接触計測器の限定的な技術採用**と**仮説の支持/反証/不明**を分離する。接触ができても集合・同意・自己組織化を示したことにはならない。実装前に[PLAN](../../experiments/F022/PLAN.md)を凍結し、その後別の実装PRと独立監査を要求する。


## 2026-10-25 F022.v1 design freeze (supersedes earlier selection-stage UNFROZEN status)
The original header and draft above are historical design selection notes. [FROZEN_V1](../../experiments/F022/FROZEN_V1.md) now controls numerical physics, continuous collision time, 13 valid scenes and 5 invalid probes, 117 expected sample frames, canonical logs and precise acceptance tolerance. [Critical review](../../docs/reviews/2026-10-25-F022-design-audit.md) and [independent theory](../../experiments/F022/PREFLIGHT.md) are **pre-observation only**. Source code, CI and F022 primary data are NOT produced. Freeze SHA is anchored in [Issue #77](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/77).


## 2026-10-25 — actual implementation candidate (Draft PR #79, NOT ADOPTED)
The earlier stage notes are retained historically. The separate stacked [implementation Draft PR #79](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/79) introduces `soma/f022.py` (continuous TOI, passive normal impulse, 13 frozen scenarios), `experiments/F022/run_suite.py` (immutable world files, exact source/protocol SHA), `experiments/F022/verify.py` (separately written analytic closest-approach oracle), `experiments/F022/attack_test.py`, `tests/test_f022.py`, and 3.11/3.12 GitHub CI. **Not a bonded agent, organism, motor, or externally peer-reviewed scientific result.** [Executable guide](../../experiments/F022/README.md). The frozen v1 protocol is unaltered.
