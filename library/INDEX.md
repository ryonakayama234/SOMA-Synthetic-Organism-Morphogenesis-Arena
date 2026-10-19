---
id: LIBRARY
title: 研究文献図書館
kind: references
status: curated_initial
updated: 2026-10-13
---

# 研究文献図書館

AIが参照するときに **出典の主張** と **SOMAがそこから立てた仮説** を混同しないための書誌索引。掲載先を一次情報優先で示す。

## R001: Particle Robotics
- 論文：Li et al., “Particle robotics based on statistical mechanics of loosely coupled components,” *Nature* **567**, 361–365 (2019).
- DOI: https://doi.org/10.1038/s41586-019-1022-9
- [原著](https://www.nature.com/articles/s41586-019-1022-9)
- **原著が示したこと**：単独では並進移動できない要素が多数集まり、集団運動・光走性・物体輸送を実現した。
- **SOMAでの意味**：単体能力と集団能力を別に評価する着想。
- **注意**：SOMAの自律的な接続選択や生存競争が実証されたわけではない。

## R002: Robot Metabolism
- 論文：Wyder et al., “Robot metabolism: Toward machines that can grow by consuming other machines,” *Science Advances* **11** (2025).
- DOI: https://doi.org/10.1126/sciadv.adu6897
- [大学による研究紹介](https://www.engineering.columbia.edu/about/news/robots-grow-consuming-other-robots)
- [研究者の公開実装](https://github.com/RobotMetabolism/TrussLink)
- **報告されたこと**：Truss Linkの追加・結合で形状・機能を変更し、斜面の移動性能を改善した。
- **SOMAでの意味**：部品の取り込みが機能を変えることの実例。
- **注意**：取り込みが一般に常に有利とは結論づけられない。

## 未整理：Mori3
- 外観と形態再構成の重要な参照対象。
- 原著の書誌情報と設計上の制約の照合は今後実施。未検証の仕様をここに書かない。

## 文献追加時の型
- 固有ID / 著者・年・タイトル / DOI・一次URL
- 原著が実際に示したこと
- 研究上の限界・まだ示していないこと
- SOMAのどの仮説と関係するか
- 最終確認日

関連：[研究憲章](../docs/PROJECT.md) / [F001](../topics/F001-single-cell-motion/SPEC.md)

- **F010 (2026-10-19, preregistered design, NOT executed/adopted):** [SPEC](../topics/F010-local-identifiability/SPEC.md) | [A–F PLAN](../experiments/F010/PLAN.md) | [unexecuted findings](../findings/F010-validation.md) | [Issue #31](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/31). Two-level response slope and third-force holdout; compare constant confound with input-dependent non-identifiability. No world labels in local estimator.
