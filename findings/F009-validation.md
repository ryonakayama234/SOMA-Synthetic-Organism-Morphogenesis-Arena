---
id: FIND-F009
kind: validation
status: not_executed
updated: 2026-10-18
---
# F009 validation log

## Design-only preregistration (2026-10-18)
Hypothesis, A-F theoretical references, tolerances and negative controls frozen in [SPEC](../topics/F009-reaction-momentum/SPEC.md) and [PLAN](../experiments/F009/PLAN.md). Issue: [#28](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/28).
Wolfram theory: A/C (v=1m/s,xA=5/8m), B/D v=0, E A(v=2m/s,x=5/4m), F A/B(v=1/2m/s,xA=5/16m). C ground reaction impulse −2Ns. These are mathematical predictions, NOT F009 runs.
F009 code, experiments, GitHub CI, independent external reviews, formal adoption and main integration: **NOT EXECUTED** at this stage. Retain this history when appending actual results.


## 2026-10-18 実装Draft #30 初回CIの実測（正式採用前）

**観測対象コードHEAD**: 74180c5e1e2641ff1e4ec504b75ca0cfb90bf908（本findings追記より前）。[F009 Actions #39121301906](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39121301906) のPython 3.11/3.12両job **success**。各jobでF001〜F009を含む**144/144全回帰**、Python -OにおけるF009 **7/7** テスト、A〜F生成・保存後独立Fraction式オラクルと初期を含む各5行×6条件＝30行の照合・同条件byte replay、成功時のみartifact upload。既存F001〜F008の8 workflowも同一PR HEADに対してすべてsuccess。
- [Python3.11 ZIP artifact #12134586087](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39121301906/artifacts/12134586087) / [3.12 ZIP #12134296554](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39121301906/artifacts/12134296554)。各ジョブ20ファイル×2再実行＝40アップロードファイル。各archiveサイズは25,412 bytes。ZIPの全エントリをこのチャットから独立に取り出して手計算再照合する試験は未実施。CIログで別式オラクルと完全byte replayが正常終了したことを確認。
- A legacy: xA=0.625m,xB=1.125m,vA=vB=1m/s（採用済F007 B-linkedの最終値とも一致）。
- B 内部対作用: xA=0m,xB=0.5m,vA=vB=0m/s。内力対とリンク拘束を含め、外力積0。
- C 接地牽引ON: Aと同じ位置・速度、地面への反作用力積−2Ns。
- D 接地OFF: Bと同じ静止。モーター指令はあっても、牽引力は0。
- E 非結合・接地ON: xA=1.25m,xB=0.5m,vA=2m/s,vB=0m/s。
- F 接地牽引上限1N: xA=0.3125m,xB=0.8125m,vA=vB=0.5m/s、地面へ−1Ns。
- F009の結果は固定1D・h=1/4sの離散運動量・理想反力計算の範囲で事前H009a-dと整合。**判定 SUPPORTED (model/software consistency only) / not adopted**。全stepで反力・外部力積・内力相殺・運動量残差を別式で照合。Wolfram有理数再検算：A〜F終状態・総運動量残差0、A/Cの離散変位と連続理論の差1/8m。
- 対照Fの無効設定、NaN、bool、質量・時刻・接地状態改変の拒否、SHAを再計算したCSV数値偽造とcomparison科学判定偽造の拒否をテスト。same-checkout replayバイト一致、既存出力・入れ子出力拒否を検証。
- **証拠の限界**：現時点ではこの追加findingsとdocsを含む最新コミットのCIは未実施。最初の合格を最終HEADの合格と取り違えない。ソースのsource_hashesは検証対象checkoutのファイルSHAで、単独では実行者本人性・ソフトウェア正当性を証明しない。独立した人間/外部研究機関による査読は未実施。同じ支援AIが設計・実装・別式レビューを行ったため独立第三者とは呼ばない。
- **実験上の重要な限界**：ground_contactは現実の接地生成・滑り・支持機構をシミュレートせず、水平牽引の上限を与えるだけ。F002/F005の電気支出を接地モードで評価しておらず、物理的仕事や実機運動効率の証明ではない。相違が無いのは既知のニュートンモデルを実装した帰結で、新物理や身体創発の発見ではない。

## 残る採用ゲート
現文書更新後の最終HEADに対するCI/生証拠の確認、独立の外部レビュー（不能なら未実施と明記）、研究者自身の**正式な採否判断**、main統合の個別承認。V001 #24/#25/#26 は別課題として保留。採用を自称してIssue #28を閉じたりPR #29/#30をmergeしない。
