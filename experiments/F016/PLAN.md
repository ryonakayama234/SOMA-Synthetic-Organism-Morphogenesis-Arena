---
id: F016-PLAN-CANDIDATE
kind: experiment_plan
status: unfrozen_unexecuted
updated: 2026-10-21
issue: 52
---
# F016 成立性対照計画（まだ実験前の草案）

**NO F016 SIMULATOR RUNS. NUMERIC CONDITIONS NOT YET FROZEN.**
[FEASIBILITY](../../topics/F016-communication-value/FEASIBILITY.md)／[Issue #52](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/52)

## 割付
A/Bの質量・リンク・F007モーター・電池・資源は同一とし、資源位置(左/右)を均等にする。1エピソードにつき開始状態と残量は完全リセットし、Aの初回指令は情報利用の後に一回決め、その後1秒固定する。Aは開始時に資源方向・真値・他者速度を観測できない。

| 群 | B bit | 通信費 | Aの行動 |
|---|---|---:|---|
| A | 通信なし | 0 J | 事前固定 +2 N（または同条件の独立乱択） |
| B | 常に右bit | 0.05 J | bitに従う |
| C | 資源方向から独立の均衡シャッフルbit | 0.05 J | bitに従う |
| D | B局所の本物方向bit | 0.05 J | bitに従う |
| E | B局所の本物方向bit | 2 J | bitに従う |
| F | bit欠損、time/source異常、sender残量不足 | ケースごと固定 | 不正を偽値に変換せず安全側の固定選択/棄却 |

正対照Dの改善に加え、B/Cで再現しないこと、Eの正味劣化を事前仮説とする。負の結果は同様に保存する。片側だけが常に良い数値バグを防ぐ左右鏡映照合、通信費・時間の改ざん陰性試験も含める。

## 指標（すべて研究者専用truthで独立検証）
- 結果: Aの最終x_A(m)、目標との差(m)、資源獲得の有無、資源の外部獲得量(µJ)。
- 費用: F007実消費 motor µJ、B側のbit送信/処理µJ、開始/終了時のA/B残量、台帳残差。
- 因果: D-A、D-B、D-C、E-A の**同じ資源位置と同じ初期条件**での paired delta。
- 対称性: 左右入替の到達距離とモーター消費、dt感度、full-reset。
- 保全: source commit SHA、仕様/物理/実験producer/verifier hash、raw traces、manifest、byte replay、独立数式/保存データ監査。

## 凍結前の研究監査
1. 位置判定で結果を定義し、通信ペイロードを報酬にしない。
2. 既存F007 motor spendと追加F002 sidecar acquire/spendの残高を二重計上しない。
3. source上の全ての負力・整数µJ丸め・正仕事・資源獲得・遮蔽を独立計算する。
4. 実験全seed/割付/閾値/予測/棄却条件を**初回F016 simulationより前**に固定して設計をマージ、別実装PRを作る。
5. テストを通したことを「新しい通信創発」や「実機で有益な通信」と言い換えない。
