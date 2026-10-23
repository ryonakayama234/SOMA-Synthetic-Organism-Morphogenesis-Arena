---
id: FINDINGS-F019
title: F019 経路資源生態系・研究証拠台帳
kind: scientific_findings_append_only
status: UNEXECUTED
updated: 2026-10-22
issue: 64
---

# F019 validation — UNEXECUTED / UNFROZEN / NOT ADOPTED (2026-10-22)

[Issue #64](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/64) / [draft preregistration](../topics/F019-resource-ecology/SPEC.md) / [PLAN](../experiments/F019/PLAN.md).

## Current state
**No F019 simulator exists, no F019 world has been executed, and no result, effect size or scientific acceptance is asserted.** Documentation in the F019 draft PR is a proposed study design, not an implementation or experimental observation. F001–F018 main evidence is separate and unchanged.

## Reason to run
In [F018 limited-adoption evidence](F018-validation.md), only 18 of 90 conditions had both individuals' restricted outside-option deltas positive, and **all 18 belong to the hand-tailored DUAL_LINK terminal-patch layout**. Other 72 conditions had no bilateral outside-positive region. That is a bounded verified precedent, not evidence that untuned ecological resource encounters will induce linking.

## Wolfram precheck (theoretical only, independent of F019)
With mA=mB=1kg, force 2N on A, dt=1/4s, four ideal semi-implicit steps and zero drag: linked positions of A: 0, 1/16, 3/16, 3/8, 5/8m; linked B: A+1/10m; unlinked A: 0, 1/8, 3/8, 3/4, 5/4m. This matches the F018/F007 displacement assumptions. **No resource first-entry/depletion results have been computed in Wolfram or SOMA for F019.**

## Required append-only table (do not fill before actual run)
| Gate | Actual observation | Status |
|---|---|---|
| H19a first-entry and depletion uniqueness | NONE | UNEXECUTED |
| H19b untuned resources and individual outside deltas | NONE | UNEXECUTED |
| H19c no-resource/drive-off/refusal/mirror controls | NONE | UNEXECUTED |
| H19d saved-data oracle, forgery rejection and replay | NONE | UNEXECUTED |
| Frozen preregistration commit and exact-source CI | NONE | NOT STARTED |
| Independent scientific decision and final main CI | NONE | NOT AUTHORIZED |

## Decision rule
A negative Pareto region under valid untuned worlds is a **valid negative scientific result**. Adopt a bounded resource/harvest measurement API only when technical invariants hold, even if the scientific incentive hypothesis fails; keep the substantive "emergent morphology" claim unapproved. Later investigators append source SHA, exact sample universe, raw artifact identifiers, statistical aggregation rule, verdict, limitations and reviewer objections without replacing these pre-experiment entries.

## 2026-10-22 — pre-freeze research-question refinement (no observations)

The previous framing highlighted whether untuned patches reproduce F018's bilateral positive link benefit. Before any F019 freeze or world run, the study's **primary** question was broadened to *connectivity-dependent resource encounter, claimant identity/ownership, depletion sequence and individual net energy*. Both-cell positive outside-option deltas remain a **secondary, exploratory** observation. Neither winner switches nor bilateral gains are required for technical adoption. No physical mechanics, candidate generator, sampling count, or data-safety gates were changed; the earlier rationale and UNEXECUTED entries are preserved above as history. See [current SPEC](../topics/F019-resource-ecology/SPEC.md), [PLAN](../experiments/F019/PLAN.md) and [future-only research memo](../docs/research-notes/2026-10-22-temporary-morphology-and-resource-access.md).

## 2026-10-22 preregistration freeze — before first F019 world (append-only)

Committed design commits freeze the previously ambiguous generator and edge semantics in [PLAN](../experiments/F019/PLAN.md), with exactly 512 candidate main scenarios / 3584 counterfactual worlds. This entry records **no execution, evidence, positive effect, or acceptance**. A separate implementation PR will be required, and review beyond same-assistant computational auditing remains outstanding. Frozen technical criteria do **not** require any positive link or owner-switch result.

## 2026-10-22 implementation-candidate source addition — before CI verification

Separate implementation branch adds F019 patch-field sampling, within-step harvest, same-field paired outcomes, raw evidence producer, independent verifier, 10 deliberately rehashed corruption cases, unit tests, workflow and source/architecture/contracts documentation. **These are proposed source capabilities; no GitHub Actions result, numeric outcome, effect-size claim, independent external review or scientific adoption is asserted here.** The preregistered 512 worlds? No: 512 independent-parameter *scenarios*, seven arms each, 3584 worlds. This corrects any accidental conflation of conditions and counterfactual worlds. On successful exact-source CI, append observed counts and reviewer notes; do not overwrite this entry.

## 2026-10-22 initial PR #66 CI: failed, preserved (before first F019 world)

At implementation HEAD `ca24e4461393744fc298e308171dd1a525b26562`, [F019 run #39794847004](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39794847004) executed Python 3.11/3.12 full regression. Each failed **1 out of 227 tests**: a semantic-equivalent but byte-different float lattice coordinate `-0.9500000000000001` from `n * .025` versus `-0.95` from `n / 40` in the independently implemented sampler's direct-equality test. No frozen F019 world generation or adoption claim occurred (workflow skipped suite stage). The verifier is corrected to use the frozen preregistration's `* 0.025` serialization convention while retaining separate SHA256/hash-to-grid implementation. No seeds, protocol gates, geometry or outcomes were changed after observation, because no F019 suite observation had yet executed. Retest on next exact source SHA.

## 2026-10-22 frozen F019 v1 first actual software observation — source `1803f4b076a7f20f0b3018f8411af242e77adb3e`

[GitHub Actions run #39795739853](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39795739853) produced actual saved F019 resource ecology evidence on the **frozen** 32 seed/512 scenario/3584 world universe, and both Python 3.11 and 3.12 job logs show **227/227 full regression tests passing**, independent 3584-world semantic verification, **10/10 deliberately rehashed forgeries rejected**, and two-root byte-for-byte replay without differences; both jobs also uploaded artifact ZIPs. GitHub's asynchronous run-level status API may lag the completed job logs; official final conclusion should be checked independently before merging.

Observed after verification on this source SHA: `winner_switches=580` per patch comparison in the 512 paired scenarios; `pareto_fixed=0` and `pareto_outside=0` bilateral positive scenarios. From audited per-seed saved summaries: **31 of 32 independent seed blocks** contain at least one owner switch over their 16 repeated factor combinations; block totals range 0–28 owner switches. This is a **source-specific simulated numerical result**, not 580 independent samples, not 31 independent experimental replications of an autonomous organism, and not a learned/consenting dynamic body.

**Scientific interpretation:** the constrained 1D morphology changes who can reach/claim fixed exogenous finite patches. Neither individual bilateral outside benefit nor time-varying reconfiguration was found or tested. No resampling, parameter tuning, reward change or after-observation exclusion is permitted to make bilateral gains positive; preserve this null as substantive negative evidence. The F018/F007 motor remains investigator-driven on A only; B receives no transported A power. The current experiment's researcher-only source independent from-disk auditor is authored in the same research workflow and is **not external human/third-party review**. Technical adoption is a separate bounded decision pending exact final documentation-inclusive CI and independent assessment.

This is the initial **1803f4b** tested-source result; later descriptive-only analyzer additions and documentation produce a different SHA and require an additional clean rerun, not retroactive reassignment of 1803f4b evidence.


## 2026-10-23 — 内部反証レビューと条件付き限定採用判断（追記）

**審査の実体:** 同じAI研究ワークフローが批判役として自己点検し、producerと別に作成された保存ファイル検証器、GitHub Actions、Wolframの厳密有理数計算で照合した。これは**外部第三者や人間による独立査読ではない**。共有された仮定の誤りは見逃し得る。

**反対論点・限界:**
- 主たる「取得者変化580件」は**1792パッチ×条件の対応比較**（固定32seedを複数因子で再利用）から得た値で、580の独立標本ではない。31/32seedの変化は記述的結果。未知の環境母集団の効果量や信頼区間を主張しない。
- モーターはAのみの外部実効力、理想剛体リンク、最初から接触可能、1D、1秒。資源は消耗するがモーターにフィードバックしないほど初期電池が十分。**生態的適応、代謝、再結合、協調学習、実機の存在証明ではない**。
- YY対NNは研究者指定の結合状態。個体ごとに算出する最善の非結合outside optionは**研究者だけの反事実値**で、両個体に共同実現可能な意思決定ではない。
- SHA256による資源中心は有限格子121点、静的・軌道非依存の生成。連続一様な空間、自然な生成過程、長期枯渇／再生を代表しない。step内線形補間、先着・同時同着A優先、パッチ重複は仮想ルール。
- **両個体の参加利益:** `pareto_fixed=0/512`, `pareto_outside=0/512`。科学的に期待した正の領域は未支持。これを消さず、資源配置の再調整もしない。
- 検証済み実装SHA `6186077e2c4b5772f47c63d0f11f424b9a2b131f` の **20/20 workflows成功**、Python 3.11/3.12全テスト、3584世界の独立再計算、10/10再ハッシュ改竄拒否、二重再生の一致をGitHubで確認。追加のno-resource/drive-off/mirror/initial-overlap単体テストは後続SHAにあり、**そのSHAの最終CI確認前に採用完了としない**。
- Wolframでは幅のある例示資源の左端0.18mにおける到達を、結合時B=57/200秒、非結合時A=61/200秒と有理数で照合した。これは**概念例**であり、メイン512シナリオの独立実測を増やすものではない。

**項目別内部判定:** H19a/H19c/H19dは現行の限定1Dソフトウェア上で技術的支持（最終CI要確認）。H19bは外生資源の取得者が結合状態で変わる**モデル内の記述的・対応反事実差**として支持。双方が得するという副次仮説はこの凍結条件で**不支持**。自律的な身体形成・持続的協調・代謝・道具の取り込みは**未検証**。

**決定:** 外部査読なしの**内部・限定的な資源場／先着枯渇／個体台帳「測定器」の採用を条件付き承認**。条件は、新しい完全なソースSHAでのF019と既存CI成功、保存証拠検証、設計PR→実装PRの順序統合とpost-main確認。満たさなければ保留。現象の一般性や生物学的主張の正式採用ではない。事前凍結したPLANと過去の失敗・陰性結果は変更しない。
