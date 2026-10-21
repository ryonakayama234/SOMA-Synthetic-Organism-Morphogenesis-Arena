---
id: F017
title: 未知1bitの行為的意味を経験から学習する — 研究候補
kind: preregistration_candidate
status: proposed_unfrozen_unexecuted
updated: 2026-10-21
issue: 57
depends_on: [F002, F007, F016]
---

# F017 — 学習される「信号の使い方」

**DESIGN CANDIDATE / NOT FROZEN / NO F017 SIMULATOR RESULTS / NO F017 API / NOT ADOPTED.**
[Issue #57](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/57) / [PLAN](../../experiments/F017/PLAN.md) / [UNEXECUTED findings](../../findings/F017-validation.md) / [research program #51](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/51).

## 唯一の科学的問い
固定1D世界でBの無名1bitを受け取るAが、研究者によるbit→モーター動作対応表なしに、各エピソードの自身の行動と実際の局所エネルギー帰還から、信号条件付きの有益な行為選択を学べるか。

「意味」とはこの研究では**行動結果によって支持される条件付きの利用規則**を指す。対象指示記号の理解・言語・共有意図・Bとの共同符号創発を示さない。

## 凍結済み既存条件との関係
- F016限定採用のF007/F002境界を再利用する構想。A/Bそれぞれ1kg、初期x=0/0.1m、理想リンク0.1m、dt=.25s、4 steps、A motor±2N、resource位置±.625m、報酬3,000,000µJ、正常通信費50,000µJ/episode、F007 motor実支出1,000,000µJ/episode。世界、送信、学習政策は論理的に分離。物理原本F001–F016は変更しない。
- 実験世界のみが資源位置・符号変換（通常／反転）を知る。Bは開始時の局所資源方向だけを取得し、無名0/1シンボルを送信する。Aは信号、許された自身の直前行動、自己の獲得・支出観測だけを入力とする。Aは自身の受信bitから「右」を直接得てはならない。
- 物理状態/台帳はエピソードごと完全リセット。受信学習器の状態だけは実験条件に応じて保持。訓練・凍結テスト・突然反転の間でどこを初期化するかを保存する。
- `ResourceBit.resource_right` というF016意味付き内部ラベルをAへの学習入力として使わない。F016 `choose_force()` と `EXPECTED_MEAN_NET_UJ` の知識を学習器に移植しない。学習専用の不透明カテゴリへのアダプタを**別モジュールとして提案**する。

## 仮説・対立仮説（まだ実験前）
- H17a: 先天的なbit→force規則なしでも、履歴を保持する受信学習器は未知の二符号化の双方で、未見エピソードにおいてA-only、定数、独立シャッフルより高い正味行為成果を得る。
- H17b: 通信を切る・信号を独立シャッフルする・報酬フィードバックを遮断する・経験メモリを毎回消去する条件では、情報由来の増分学習は消失する。
- H17c [secondary]: 実験者が符号を通知なく途中反転した後、同じ学習器が古い規則で失敗し、追加経験から新しい行為対応に再適応する。
- Alternative: 固定右優先、episode時刻のリーク、訓練とテストの系列重複、通信コストの計上漏れ、F016固定decoderの混入、学習成績によるpolicy選択の後付け、単なるシンボル頻度推定が全結果を説明する。

## 受信器への情報隔離（厳守）
| 領域 | 受信Aに許す | 研究者・監査者だけ |
|---|---|---|
| 受信 | `symbol: 0/1/None`, 正常なsource/time framing | raw B observation、encoding/flip selector |
| 決定 | 原始選択肢 `motor_force_n ∈ {-2,+2}`, 自己Q状態、探索RNG | `target_x_m`, future reward, episode index, batch group |
| 帰還 | 自分が受け取った `acquired_uj`, 自分の実際の `motor_spent_uj`、選択した行動 | `reached`, `net_uj`, B communication cost, attached/world truth |
| 評価 | なし | saved F007 state, F002 ledger, exact run config, independent auditor |

学習用の結果はAの受け取るエネルギーから取得し、0/1正解ラベルを教師信号として渡さない。Aの原始動作が既知であることと受信bitの意味を知らないことは両立する。

## 最小の反証可能な学習機構
候補は2シンボル×2行動の小さな文脈付きbandit（例えばrecency-weighted Qと訓練時の固定探索率）。開始時のすべてのQは対称。これは**アルゴリズム候補**であり採用済みAPIではない。より複雑なNN/RL・B側policy learning・roleswapは行わない。

## 因果的な比較
1. Bの未知通常符号／未知反転符号（受信器には隠す）。
2. 無通信／定数シンボル／ターゲットと独立にシャッフルした同頻度シンボル。
3. 学習停止／毎回Qリセット／局所報酬帰還なし。
4. 学習後の保持された未知シーケンスへの一般化、通知なし反転後の行為・成果回復（secondary）。
5. 各条件の物理・報酬・通信負担・探索予算を一致させ、差異は操作した独立変数に限定する。

## Wolfram theoretical feasibility only, not experiment
資源到達確率pの平均正味 `J(p)=3p-1-0.05=3p-1.05 J`。F016 A0基準0.5 Jに勝つ最小pは `31/60=0.51666...`。この閾値は偶然でも超えられるため、**単なる正味上振れでは学習成立としない**。未見シーケンス、反事実対照、学習履歴・局所入力監査と事前凍結の効果量閾値を必須とする。理論上p=0.9なら1.65J、p=1なら1.95J。

## 進行・採否ゲート
1. [PLAN](../../experiments/F017/PLAN.md)でseed list, train/test episodes, symbols, costs, policy, predeclared statistic/CI, minimum effect, inversion windows, source SHAを**F017最初のsimulation前に凍結して別設計PRをmain統合**。この草案の値はまだ未凍結。
2. 別のimplementation Draft PRで最小`soma/f017.py`/独立ログproducer/oracle/型・偽通信・改ざんテスト・3.11/3.12回帰CIを追加。
3. saved-world audit（機械式F007/台帳F002）とA-viewのデータリーク禁止を検証し、二系統根の完全byte replayとsource-verified artifactsを記録。
4. H17a/b/cをそれぞれSUPPORTED / CONTRADICTED / INCONCLUSIVEで記録し、限定採用とmain統合は研究判断を別に行う。H17cが失敗してもH17a/bを後付けで書き換えない。

**明確な非対象:** 共同通信プロトコル・相互理解、実機/無線、身体再構成、A/B役割交換、F011–F013地面物理の統合、生物学的進化、個体性、V001、F011 #37。
