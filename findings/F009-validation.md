---
id: FIND-F009
kind: validation
status: implemented_candidate_audited_not_adopted
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

## 2026-10-18 独立artifact再監査（別セッションのAI監査、正式採用前）

対象実装コミット `8c99e1a7d5a0e40f615be08054c817277ebaa854`。対象[CI run #39121545352](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39121545352) は Python 3.11/3.12 双方 success（各144全回帰、各7件の最適化F009テスト）。同じSHAのF001〜F008ワークフロー8本も success。CIは `refs/remotes/pull/30/merge` の合成コミット `0396d0d2962d05273865ceac4ba409c29a5920b6` をcheckoutしていたが、これと当時のPR HEADのGit tree SHAはいずれも `0d0b814045a36427193ad8c8f73779d6930a86b4` で**同一ファイル木**。表示上のhead_shaのみを根拠にせず、実際のcheckoutとtreeを照合した。

以前「ZIP内部未監査」としていた留保を、このコミットのartifactについて追加調査で解消した。CIから直接取得した[3.11 artifact #12134626410](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39121545352/artifacts/12134626410)（ZIP SHA256 `17a1a139b0b65482af12d5fd1a369781f8fa863ea784e31bdb2540de492e1923`）と[3.12 artifact #12134740469](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39121545352/artifacts/12134740469)（ZIP SHA256 `caa8c2354800bd79d603211593d3f73b5621110a28f29c0b4bf90b3ad334e5fe`）を独立に解凍し、各40エントリを確認した。両方で20原本ファイルと20 replayファイル、suite/per-case SHA256 と manifest の整合性、同一環境内byte replay、**Python 3.11/3.12間も全40ファイルの内容が完全一致**することを検査した。

生 `steps.csv` 6条件×各5行の全30状態行について、F009本体および既存 `experiments/F009/verify.py` をimportせず、新規の監査用Python/Fraction漸化式で「各セルに作用する外力+内力+リンク反力→次速度→半陰的Euler位置」、各行の時刻・拘束・運動量・外力積・地面反作用・運動量残差を再計算し、すべて**厳密一致**。A=(5/8,9/8;1,1)、B=(0,1/2;0,0)、C=A、D=B、E=(5/4,1/2;2,0)、F=(5/16,13/16;1/2,1/2)。Wolfram Languageによる今回の新規独立記号計算でも、一般質量のリンク力の両セル方程式残差0、重心運動量残差0、A〜Fの予測一致、A/Cの連続解との差1/8 mを確認。これらは**保存された離散モデルについての照合**であり、実機で測定した真の接地反力ではない。

コード/データ契約レビュー：`soma/f009.py` は6つの完全固定configのみを受け付け、内部力対の和0、ground tractionは接触フラグと上限の理想規則、無接地では牽引0。研究者専用ログからF008のA局所知覚に世界真値を流すコードはない。テストの偽造CSV/判定、無効入力、既存F007基準、出力重複/入れ子拒否はCIで成功。ただし悪意あるPythonプロセス隔離、一般パラメータ域、2出力のクラッシュ原子性、実機の接触/摩擦機構、実電気支出/効率、学習、創発は**非検証・非採用**。本監査は別チャットのAIと独立算術による照合であり、人間・外部機関の独立レビューではない。

**独立監査の発見**：対象の固定1D離散運動量モデル、記録されたA〜Fの数値と出自について、今回追加で再現可能な反例・重大な矛盾は検出せず。設計上の地面反力はモデル内で `-traction` と**定義された値**であって独立に物理的に生じた観測ではない、という限定は採用条件に必須。受入基準、事前仮説、既存生ログは変更しない。結論：**固定F009運動量会計の計算能力としてのみ正式採用を推奨（研究者判断待ち）**。ただし、本節の新しい文書コミットを含む最終HEAD CIはこの追記時点では未実施であり、旧CIの結果を新HEADの成功と呼ばない。設計PR #29→実装PR #30の順に統合する前に最終HEAD CIを再確認し、採用/mergeには研究者の明示承認を別途得ること。V001は対象外。
