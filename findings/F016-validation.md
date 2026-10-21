---
id: FIND-F016
kind: validation
status: feasibility_only_no_f016_run
updated: 2026-10-21
issue: 52
---
# F016 検証台帳 — 成立性先行、未実験

## 2026-10-21: 事前の成立性検討
- 関連: [Issue #52](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/52)、[FEASIBILITY](../topics/F016-communication-value/FEASIBILITY.md)、[PLAN](../experiments/F016/PLAN.md)。
- **事実/出典**: F007は固定1D・2セル理想リンク＋A外部有効モーターを計算し、F002は整数µJのacquire/spend/transfer台帳を提供する。F015は実験条件内でB bit増分識別改善0を報告した。
- **仮説**: Bだけが直接知る資源方向を1bitでAへ伝えると、固定リソース到達行動で通信費用を上回る成果を得られる条件がある。
- **設計仮定**: 左右資源各1/2、同質量1kg×2、F007有効力±2N、距離0.5m、資源3J、bit費用0.05/2J、1s。モーター反力源・資源充電器・遮蔽は理想化。
- **理論計算のみ**: Wolfram Languageで有理数式を評価し {dx, motorWork, net(noBit), net(trueBitLow), net(shuffledLow), net(trueBitHigh), breakEvenCost} = {1/2 m,1 J,1/2 J,39/20 J,9/20 J,0 J,3/2 J} を得た。
- **この段階の解釈**: 正/負対照と正味評価指標を一貫して組めるという意味で **FEASIBILITY GO**。有利な値は設計で意図したもの。F016の実装・実験により観測した結果ではない。身体・信号規則の創発でもない。

## 未実施／未採用のゲート
| Gate | 状態 |
|---|---|
| 凍結SPEC・凍結PLANとソース起点SHA | 未完了 |
| F016 source / F007再利用を伴うsimulation | **UNEXECUTED** |
| 保存されたF016の位置・エネルギー生ログ | **NONE** |
| A-only/constant/shuffle/true/high-cost全試行 | **UNEXECUTED** |
| F002厳密台帳・偽造改ざん対照・独立oracle | **UNEXECUTED** |
| Python 3.11/3.12 CI＋two-root replay | **UNEXECUTED** |
| 研究者正式採用 / main merge | **NOT AUTHORIZED** |

今後は日付、source SHA、CI URL、全条件の**実測値と失敗**を追記する。理論予測を実験結果に上書きしない。

## 2026-10-21 — Wolfram PRE-EXECUTION discrete correction / F016 SPEC freeze
The previous continuous-time analytical target ±0.5m was **incorrect for the adopted F007 semi-implicit-Euler stepper** at dt=.25. In exact rational Wolfram step recurrence v'=v+u dt/(mA+mB), x'=x+v' dt, after 4 steps x=±5/8m (not ±1/2m), v=±1m/s; trapezoidal positive motor work by step [1/16,3/16,5/16,7/16]J sums to 1 J, not motor force × discrete displacement. The study *preregistered* target is corrected to ±0.625m in [SPEC](../topics/F016-communication-value/SPEC.md) and [PLAN](../experiments/F016/PLAN.md) **before** first F016 simulation. Earlier theoretical payoff numbers persist at true target ±.625m. This is theory-only and NOT observed F016 data.

**Frozen predicted 24 primary episodes:** A0/K/S/T/H/I 4 each, target [R,L,R,L], bit shuffle [R,R,L,L], predicted successful counts 2/2/2/4/4/0 and expected µJ per episode 500000/450000/450000/1950000/0/-1050000. Full source-bound saved-model audit and test status **UNEXECUTED** at preregistration. No F016 scientific acceptance.

## 2026-10-21 — Implementation candidate created; RUN OUTCOME STILL PENDING
After the **previously frozen** [F016 SPEC](../topics/F016-communication-value/SPEC.md) and [PLAN](../experiments/F016/PLAN.md), separate implementation source adds `soma/f016.py`, a 24-primary-trial producer, independent saved-CSV/JSON auditor, type/forgery/byte-replay tests and Python3.11/3.12 workflow. No F001–F015 source changes. **Creating code is not a simulator observation.** Do not replace the earlier theory-only notes; append actual source SHA, Actions URL, raw-artifact hashes, numeric table, any failed/red history and formal verdict only *after* verified execution.
