---
id: FIND-F021
title: F021 実験記録 — 初期の設計前検算
kind: append_only_findings
status: bounded_adopted_v1
updated: 2026-10-24
issue: 72
---

# F021 の検証ノート

**実験状態：未実施。F021コード・F021世界・乱数seedの主観測、CI、形式的採否は全て未実施。** [SPEC](../topics/F021-bilateral-actuation/SPEC.md) / [PLAN](../experiments/F021/PLAN.md) / [Issue #72](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/72)。

## 2026-10-24 — 設計段階の独立数学検算（観測ではない）

Wolfram Languageで質量1kgずつ、0.25s、初速0、外部有効モーター A=+2N、B=-2/0/+2N、理想1D剛体リンク、抗力なしの初回を有理数で評価（式は [preflight.wl](../experiments/F021/preflight.wl)）。位置はF001/F007型の半陰的更新、仕事はF005の速度時間積分を用いた。

| Bモーター | 予測a m/s² | 予測Δx m | 予測Aリンク力 N | Aの正仕事 J | Bの正仕事 J | 運動エネルギー増分 J |
|---|---:|---:|---:|---:|---:|---:|
| -2N | 0 | 0 | -2 | 0 | 0 | 0 |
| 0N | 1 | 1/16 | -1 | 1/16 | 0 | 1/16 |
| +2N | 2 | 1/8 | 0 | 1/8 | 1/8 | 1/4 |

**解釈**：力学・数値残差の理論校正値。運動機能の創発、資源への利益、双方の同意、自己組織化を示すものではない。等大逆向き駆動の「動かないがリンク力はある」状態は重要な負の校正。正の機械仕事ゼロは実電力ゼロの証明ではない。F005積分仕事と半陰的な位置変位の積 F×Δx は同じ離散量ではない。

**制約**：Wolfram計算と同じ式を使うだけでは独立した外部査読とは言えない。F021コード結果の第三者照合は未実施。実装後に保存データを別のコード経路で再構築して初めて限定的な技術的検証が始まる。

## F021実験の未記録スロット

- Frozen protocol commit: なし
- Primary world count / independent resource seeds: 未定
- F021 implementation SHA / Python CI / artifacts: なし
- Simulated per-cell payoff distributions / negative cases: 未観測
- Semantic tamper attacks / byte replay: 未実施
- Scientific verdict: **未実施**
- Software/API admission verdict: **未採用**

今後の結果はこの文書に追記し、先行する未実施状態や陰性結果を歴史から消さない。


## 2026-10-24 — frozen design merged, new source produced (engineering candidate; no observed F021 outcome yet)

The older UNEXECUTED text above is historical. F021 design [PR #73](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/73) was frozen before any F021 primary data, at design HEAD `8f82e3b0283b6523041647b38335c466034478f3`, merged to main via `ae37d2af5ce728c58bc8c2fd4e824f34fc1f2b71`. Frozen primary grid: 32 F019 environment seed blocks, 4,608 investigator-assigned YY/NN × A/B motor × fee × finite resource worlds and 2,304 paired YY-NN contrasts; no 4,608 independent lifeforms. At [implementation PR #74](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/74), `soma/f021.py` and standalone producer, non-importing independent verifier, six rehashed tamper controls, unit tests, CI were added. **Raw F021 outcomes and technical CI verification are still pending as of this source revision**; do not replace this sentence with an invented result. Append exact CI/source-specific quantitative findings and review separately after observed execution. Scientific hypothesis verdict UNEXECUTED; bounded adoption NOT YET AUTHORIZED.


## 2026-10-24 — F021 v1 source-bound observed results and limited scientific interpretation (append-only)

**Newer result; earlier UNEXECUTED text is preserved as historical state.** Prior to primary execution, the full factorial arithmetic erratum A1 [PR #75](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/75) was merged to main at `f2ce5d555aa4dcecd27c3e543f1275a017287a01`. Eight unchanged factors produce **9,216 worlds, 4,608 matched YY–NN contrasts, 32 reused environment seed blocks**, not the mistaken early 4,608/2,304 count. F021 preregistered positive or negative outcomes without selecting target improvements.

**Observed evidence from implementation PR #74 source head `717b006381e4a198a77977771db0371f1dd7e97f`:** [GitHub Actions run 40101888214](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/40101888214) successful on Python 3.11 and 3.12; each verified 9,216 saved worlds and 4,608 YY–NN matched comparisons with an independently implemented archived-data physics/energy/claim/summary verifier; 247 inherited+F021 unit tests, separate optimized 8 F021 tests, 6 rehashed semantic forgery attacks rejected, and two clean roots with byte-identical replay per Python version. All **22 head-SHA workflow runs succeeded** at that head. Archived evidence artifacts: `f021-worlds-py3.11` ID 12562259592 and `f021-worlds-py3.12` ID 12563182334 (GitHub artifacts have finite retention; do not present as permanent independent storage). [Long-lived source-bound aggregate and 32 block summaries](F021-ci-summary-2026-10-24.json).

| Fixed-command matched YY vs NN outcomes (both individually owned, ideal external-effective motors) | Paired contrasts |
|---|---:|
| Both private net energy changes >0 | 363 (7.88%) |
| Opposite-signed private change | 1,058 (22.96%) |
| Both changes <0 | 1,438 (31.21%) |
| At least one private change exactly 0 | 1,749 (37.96%) |

**Meaning:** `delta_i = net_YY_i - net_NN_i`. This is only a change *relative to the same predetermined nonjoining motor commands*. It is not an absolute profit or independently chosen consent. Simulated YY and NN can both be net-negative yet yield two positive deltas because YY loses less energy. In a separate predeclared stronger lower-bound outside comparison, `outside_delta_i = net_YY_i - max(0, net_NN_i)`, the 4,608 matched contrasts are: both-positive **0**, both-negative **2,355**, mixed **546**, one-or-both zero **1,707**. Thus **no observed pair strictly benefited on both sides relative to each individual's stronger fixed-action/idle lower-bound** in this frozen world suite; this does not prove none could benefit in other mechanics, resources, policies, or real robotics. The `max(0, NN)` baseline is investigator-calculated, not a fully simulated repertoire of all possible local controllers nor a jointly achievable negotiation.

**Mechanistic counterexample:** In the independently computed subgroup check, 350/363 fixed-command both-positive cases used **opposing A/B motor forces**, in which a YY rigid link can suppress translation and ideal positive motor work. The YY-on-vs-NN-fixed advantage is frequently **avoided waste** rather than productive cooperation or true joint energy gain. The extra 13 were B motor off, and aligned B-on yielded no both-positive fixed-command cases in this frozen sample. These subgroup counts come from the [separate auxiliary mathematical replication](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/72) rather than independent subgroup recomputation of the stored GitHub evidence and must remain labeled accordingly until source-bound subgroup audit.

**Ambiguous arbitration:** 1,024 world-steps logged `ambiguous_maximal` among 36,864 steps (2.78%). In the independent auxiliary inspection, ambiguity appeared only in YY, aligned-drive B=+A, each cell 80,000µJ at initial condition; the investigator rule chooses neither while A-only or B-only is feasible, and records the alternatives. These trajectories reflect *a declared arbitration assumption*, not autonomous choice or natural balance. All four subsets were independently recomputed for each archived step by the source-bound verifier. Dedicated no-ecology `calibrate.py` exposes A-only/B-only/off theoretical sensitivity; **a full alternative-arbitration ecological sensitivity suite was not executed**, so no claim of arbitration-robust bilateral advantage is authorized.

**Boundaries and falsification:** The simulator has external-effective ideal motors without modeled ground reaction, positive mechanical work is not electrical cost and ignores holding power, rigid 1D link is investigator assigned, initial world horizon only 1 s, finite sparse resources and per-cell 1,000,000µJ patch awards, no learned attachment, selection, autonomy, evolution or long-term biological survival. The 4,608 outcomes are factorial contrasts on only 32 reused field seeds: do not infer independent sample p-values. Negative cases remain and are not optimized away.

**Engineering judgment on validated implementation head:** independent verifier, model oracle, 22 CI workflows and source-bound evidence SUPPORT **a narrowly versioned F021.v1 experimental instrument**. Scientific judgment: H21a ideal dynamics SUPPORTED within frozen equations, H21b resource and private-payoff variation SUPPORTED as descriptive conditional effects, H21c rival arbitration/control explanations PARTIALLY RESOLVED with explicit residual ambiguity, H21d reproducibility/archived-data integrity SUPPORTED within recorded attack suite. **No evidence supports voluntary joining or bilateral improvement beyond idleness in this frozen environment.** This is *limited* software suitability, not emergence validation. Main-merge and post-merge CI should be tracked as distinct subsequent actions rather than retroactively asserting them from the PR test.


## 2026-10-24 — **FORMAL BOUNDED ADOPTION** of F021.v1 instrument (supersedes prior pending states)

The investigator's agreed engineering acceptance conditions were met. Implementation [PR #74](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/74) was **merged to main** at exact SHA `53efe7c78529ca81cbab4b11d4ddcf10245f44fa` on 2026-10-24. On its final pre-merge documentation-inclusive HEAD `59a8fa35ea59a83ec540e4ddf742bb7bdcdf4226`, **22/22 GitHub Actions workflows succeeded**; both Python 3.11/3.12 matrices ran 9,216 full worlds, each used an independent 4,608-pair oracle, six rehashed semantic forgery attacks, and byte-identical two-root replay. Separately downloaded real CI archives py3.11 ID 12562259592 and py3.12 ID 12563182334 were independently checked byte-for-byte identical across versions for `worlds.jsonl`, `summary.json`, and `manifest.json`, with SHA matching their own manifest. [Source-bound machine-readable per-seed summary](F021-ci-summary-2026-10-24.json) and [critical raw archive audit](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/74#issuecomment-6385435188) retained. Main post-merge CI at merge SHA is a distinct verification check and must be reported separately, not inferred as already passed.

**Software acceptance scope:** `f021.v1` is hereby adopted as a reproducible **investigator-controlled ideal 1D bilateral-drive resource/payoff measuring instrument**, with independent A/B force channels, individually owned integer µJ ledgers, F019 frozen finite fields, local resource credit, a declared and fully logged simultaneous gate, and a source-independent verifier. This admission is **not** an assertion of realistic embodied electric motors, 2D/3D, learned connection decisions or naturally evolved bodies. F001–F020 APIs and frozen scientific results are unchanged.

**Scientific findings:** In 4,608 fixed-action YY–NN contrasts, private deltas were bilateral positive 363, bilateral negative 1,438, mixed 1,058, at least one zero 1,749. The stricter idle-inclusive comparator had **zero bilateral strict positive outcomes**. Original archives show 350/363 bilateral positive fixed contrasts use opposing drive, 13 B off, zero B aligned; 1,416/1,438 both-negative contrasts had 25,000 µJ joining fee. Separate B-on vs B-off matched field contrasts changed claim maps and B private net; this is evidence of causal **model** capability, not spontaneous consent. Arbitrator ambiguity 1,024/36,864 steps persists by explicit policy; no ecology-wide arbitration sensitivity was performed. No independent ecological significance tests from repeated 32 seed blocks and no external human peer review claimed.

**Future hypotheses, not F021 success claims:** local joining/leaving policy; resource-rich contexts that may create absolute gain exceeding idle outside options; robust alternative arbitration; physical 2D contacts/support forces/real motor holding power. No retroactive seed/factor tuning to engineer more positive F021 cases.
