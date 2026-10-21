---
id: F017-PLAN
kind: experiment_plan_candidate
status: proposed_unfrozen_unexecuted
updated: 2026-10-21
issue: 57
---
# F017 実験比較計画 — 設計案（未凍結・未実施）

**NOT FROZEN. NO F017 SIMULATIONS, RAW DATA, TESTS, CI, OR ACCEPTANCE.** [SPEC](../../topics/F017-learned-signal/SPEC.md), [Issue #57](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/57).

## 一つの目的
ビットの物理的受信と、経験から獲得したAの行為条件付けとを分けて測る。F016固定符号の正の結果は対照・再利用できるがF017の実測に転用しない。

## 暫定の実験単位と割付（実装前レビュー後に凍結）
- 世界: F016と同じF007/F002理想モデル、物理＋セル電池は1エピソードごと完全reset。AのQ/RNG経験は同一セッション内だけ保持。
- ターゲット: 左右均衡した、非周期・事前公開可能なseedで作成する擬似乱数列。訓練とholdoutは別sequenceで、受信Aにseed、時刻内のepisode番号、world truthを渡さない。2つのencoding条件は同一ターゲット系列をpairする。
- Policy candidate: bit×±2Nの各4セルQを0で初期化、訓練時のみ明示探索、自己`acquired_uj - motor_spent_uj`で更新。符号→行動表は未提供。Q更新・乱数使用はイベントとして研究者に保存、学習器へのtruth入力禁止。
- 初回設計案: 8 seed × (64 train + 32 frozen holdout) × encoding {normal,inverted}。これらは**暫定**であり初回simulation前の固定対象。variance/thresholdも事前決定。
- 真のsource-sign/packetは世界側で研究者だけに保存し、Aは`OpaqueBit(0/1/None)`と指定source/time framingのみ取得。失敗報酬0、成功ならA自身に3J獲得が記録される。Bの送信費0.05JはAの学習帰還には含めず研究者のnetに入れる。
- 受信不能時、A-only行動政策を明示定義する。学習あり／なし比較で学習予算を揃え、評価時の探索off、学習offとする。

## 暫定比較群
| group | B→Aの入力 | A履歴と帰還 | 研究目的 |
|---|---|---|---|
| U | 意味未知・通常符号 | 学習あり | 正対照1 |
| R | 意味未知・反転符号 | 学習あり | 正対照2 |
| N | なし | 学習あり | A-only |
| C | 常時同一bit | 学習あり＋同じ費用 | 単なる到着の効果を排除 |
| S | 真値と独立の均衡bit | 学習あり＋同じ費用 | 相関漏れを排除 |
| Q0 | 意味未知・通常/反転 | Qを毎エピソードreset | 累積経験を切断 |
| FB0 | 意味未知・通常/反転 | 自己報酬を隠す | feedbackの因果寄与 |
| F016 | 真偽固定decoder比較のみ | 学習なし | 既知の固定規則と逆符号の失敗参照 |

二次実験: 訓練済みAを追加セッションで学習モードに戻し、`U↔R`を通知なしで反転。前後の移動成績・Q変化・元の規則の失敗・回復を比較。固定decoder/no-update・全リセット対照とpairする。反転はpayloadを変える外生的介入であってBの自律コード進化ではない。

## 評価
- 独立評価: 一次`success_rate` (資源終端位置一致) + `net_uj`（研究者 truthからのacquire - F007 motor - B fee）。各group/seedでpaired difference, uncertainty intervals、セッションのtrace。
- 学習の直接検査: policy Q初期対称性、各ステップのbit/action/self-feedback、update履歴、holdout前後のpolicy凍結を保存。Aの利用規則にbidirectional sensitivityがあるかbit swap/ablationで検証。
- 一次判定値案: 各U/Rの未見正解率≥80%とpaired平均netがN/C/Sより優れ、95%CI下限が通信無効の成功率0.5を上回ること。これは**研究候補閾値で未凍結**。詳細なCI方法、multiplicity、seed acceptance、no-overfitをレビューで確定する。
- 二次反転判定案: 反転後の前半 vs 後半にnet/success回復を観測し、未通知でpolicyが変化したことを確認。閾値は実験実施前に凍結。
- Wolfram対照: 受信情報を使った到達確率pのnetは`3p - 1.05 J`、A-only=0.5J、同程度では不可。F016の24個は再解析用過去データでありF017学習結果に混ぜない。

## 実験で停止・留保すべき条件
- 配列やsource/time/targetがAへ直接露出、world truthがfeedbackに混入。
- ターゲット列が公開行動により簡単に予測できる（交互固定／周期性）、holdoutの同じシーケンス再使用。
- rewardがbitの正解を直接返す、packet受信そのものに正の報酬を付ける。
- F007 dt/force/target位置、F002台帳/費用を確認なく変更。
- 保存ログでは効いたが独立auditorでは再現しない、after-the-factでpolicy/thresholdを調整。

## 研究資産を毎作業同時更新
`docs/ARCHITECTURE.md`: learner / bit mask / private truth / feedback arrow、`docs/DATA_CONTRACTS.md`: schema, units, separation, validation、`findings/F017-validation.md`: source SHA/CI/raw fail history、README/AGENTS: 状態と索引。実装PRはソース・テスト・図・契約・保存実験を一つのレビュー単位で同期させる。
