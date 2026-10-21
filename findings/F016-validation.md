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
