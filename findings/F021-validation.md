---
id: FIND-F021
title: F021 実験記録 — 初期の設計前検算
kind: append_only_findings
status: unexecuted_design_only
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
