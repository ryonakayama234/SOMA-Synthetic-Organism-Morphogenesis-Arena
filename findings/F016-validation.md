---
id: FIND-F016
kind: validation
status: observed_candidate_under_review
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

## 2026-10-21 — FIRST ACTUAL F016 SIMULATION, saved-evidence audit on exact implementation HEAD

**EVIDENCE, not prior Wolfram theory.** [GitHub Actions #39581144450](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39581144450) completed on source HEAD `3fc7b0a7e43af26441715b511476234fe94c7a66`. All **16/16** inherited+F016 workflows on that SHA passed. F016 jobs Python **3.11 and 3.12 both SUCCESS**; per-version **197 full unit regression tests, 6 `-O` negative/control tests**, **24/24 frozen primary episodes** (6×4) and **49 authenticated artifact files** in each of two byte-identical replay roots, saved JSON+CSV state audit, F002 sidecar balance residual 0, source+manifest SHA256 authentication. No red CI on this head. Archived evidence [Python 3.11 artifact #12337335052](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39581144450/artifacts/12337335052) and [Python 3.12 #12337040566](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39581144450/artifacts/12337040566).

**Observed** primary runs (per-episode means are µJ, not other physical forms of resource transfer):
| group | successes / 4 | mean net µJ | Wolfram prereg prediction µJ | verdict under frozen gate |
|---|---:|---:|---:|---|
| A0 no transmission | 2/4 | +500000 | +500000 | MATCH |
| K constant bit | 2/4 | +450000 | +450000 | MATCH |
| S predetermined shuffled bit | 2/4 | +450000 | +450000 | MATCH |
| T valid B bit (50kµJ charge) | 4/4 | +1950000 | +1950000 | MATCH |
| H valid B bit (2MµJ charge) | 4/4 | 0 | 0 | MATCH |
| I inverted bit | 0/4 | −1050000 | −1050000 | MATCH |

Independent Wolfram exact dyadic recurrence: `v_k = F*k/8`, `x_k=F*k*(k+1)/64`m for `F=±2N`, `dt=.25s`; `x_4=±5/8 m`, `W^+=[1/16,3/16,5/16,7/16]` J ⇒ total 1J, independently checked against 24 saved F007 world traces. Net gain `mean(T)-mean(A0)=+1,450,000 µJ` under this deliberately constructed resource task, and `mean(H)-mean(A0)=−500,000µJ`. Tampered saved `net_uj`, position, peer bit with **recomputed artifact SHA256** were rejected by separately authored truth verifier. Wrong source/time/invalid packet and insufficient sender battery had rejection or explicit A-only fallback in controlled unit tests. Two independently generated evidence roots had identical bytes.

### H16 scientific interpretation and serious scope restrictions
- **H16a SUPPORTED solely for the frozen ideal positive-control task:** true B direction bit causally selects correct signed effective motor and improves physically evaluated terminal resource arrival/constructed net score relative to A-only, constant and shuffled controls.
- **H16b SUPPORTED within the fixed groups:** sender fee of 2J removes net advantage although delivery conveys correct sign; cost threshold is a *designer-chosen* 1.5J for this task, not measured radio physics.
- **H16c SUPPORTED as a control contrast:** constant and shuffled bits yield only 2/4 hits each; inverted signal yields 0/4, so improvement cannot be attributed to mere fee/packet presence in these controls.
- **H16d and evidence contract SUPPORTED only numerically:** mirrored signed paths, ideal pre-programmed physical link, exact F007 positive motor work and F002 replay are consistent with preserved source. B-origin bit does NOT identify true topology, no arbitrary external disturbance or contact variation was tested.
- **Limits:** `read_b_local` is a researcher-defined observability mask, not empirically validated 1D optics; `ResourceBit` semantics are predefined, not learned; zero-latency ideal delivery, no bit noise, no decentralized formation, no physical energy harvester, no coupling mechanism design, no human independent review. Reference/witness code is distinct but generated by the same assistant. The intentionally tailored environment means **validating the implementation is not discovering a general natural advantage of communication**.

### Restricted candidate decision
**RECOMMEND LIMITED ADOPTION** of `f016.action.v1` and the 24-case independent comparison/evidence harness ONLY as an ideal 1D researcher-fixed B-bit → A-action → terminal-position/resource-scoring numerical module, if documentation-inclusive final source HEAD CI and actual GitHub integration/post-main CI succeed. Not recommended: general communication ability, natural semantic origin, real electromagnetic energy, physical body recognition, 2D/3D or morphology emergence. Prior to an actual merge, the above reviewed `3fc7b0a7` source evidence is factual, but current updated documentation **changes the source SHA**, so exact-final-HEAD verification is required again before formal integration. Preserve prior pre-run notes above, rather than rewriting them as results.
