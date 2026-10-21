---
id: F016
title: 1bit局所通信の正味行為価値 — 凍結実験仕様
kind: preregistration
status: frozen_design_unexecuted
updated: 2026-10-21
issue: 52
depends_on: [F002, F005, F007, F014, F015]
---

# F016 固定1D理想世界における1bit通信の正味行為価値

**PRE-EXPERIMENT FREEZE: NO F016 SIMULATOR TRIALS AT THIS DOCUMENT REVISION.**
[Issue #52](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/52) / [feasibility history](FEASIBILITY.md) / [PLAN](../../experiments/F016/PLAN.md) / [findings](../../findings/F016-validation.md).

## 科学的問い（ただ一つ）
Bが局所的に観測する資源方向の1bit（研究者が固定した符号化）をAが受け取ったとき、位置による資源獲得量から通信費と実モーター正仕事を差し引いた**正味行為結果**が、同じ環境のA-only/偽通信対照より改善できるか。

**正対照として利益が出るよう意図して構築した課題**であり、通信規則や身体が自然に創発するかを検証しない。

## 既存コード境界
- F007 `soma.f007.Config.from_dict`・`simulate` を無改変で使用。A/B各1kg、初期 A x=0, B x=0.1m、両v=0、link.initially_attached=true, length=0.1m, detach_time_s=null、drag=0、両外力0、Aモーター指令は±2N、dt=1/4 s、T=1s（計4ステップ）、`seed=null`。
- 電池A/B初期 10,000,000µJ、各capacity 20,000,000µJ。F007は外部**有効力**駆動であり、実機の地面反力・電力変換効率は扱わない。F011–F013物理を混ぜない。
- 各エピソードでF007世界・B側送信費/研究者資源台帳を完全リセットする。意図的な停止はT=1秒の**終端位置評価**であって、速度が0の停止を意味しない。

## 実験前の訂正：連続時間の予測とF007離散物理
以前のFEASIBILITY予測は連続時間位置0.5mを用い、`dt=0.25`のF007 semi-implicit Eulerの終端位置と食い違う。この仕様では**資源位置を±0.625mに固定**する。
- 等質量剛体系のa = 2/(1+1)=1m/s²、v_k=k/4m/s、x_k = k(k+1)/32 m。x_4=5/8m=0.625m、v_4=1m/s。
- F005/F007が積算する台形速度による区間正仕事は (1/16,3/16,5/16,7/16)J、合計1J。**2N×離散位置0.625m=1.25Jではない**。F007実台帳の各ステップ支出と照合する。
- Bは初期x=0.1mなので、+0.625資源をBから見た位置=+0.525m、-0.625資源をBから見た位置=-0.725m。B局所センサーは開始時の相対符号だけを返す。Aは資源を見られないという**外生的な観測可能性マスク**を使う。1D遮蔽光学を実装したとは主張しない。

## 凍結割付・行動
研究者専用ターゲット方向 `[right,left,right,left]` の4エピソード（順序固定; seed labels 0,1,2,3）。各群は同一4方向と同一初期状態、計4×6=24 primary runs。乱数を使わないので `seed` は実験エピソードIDでありF007 `seed=null`を変更しない。

| group code | bit payload（研究者側の介入） | B送信費（µJ） | A初期力指令 |
|---|---|---:|---|
| A0 | なし | 0 | +2N固定 |
| K | 定数true（right） | 50000 | bit方向 |
| S | シャッフル固定 `[right,right,left,left]` | 50000 | bit方向 |
| T | B-local資源側の真正bit | 50000 | bit方向 |
| H | B-local真正bit（高コスト） | 2000000 | bit方向 |
| I | B-local bitの反転・偽信号 | 50000 | bit方向 |

- `None`はFalse/leftにしてはならず、A-only右方向フォールバックとする。source=`B`、step_index=0、time_s=0 が必要。時間/送信元異常は拒否し、通信費なしの成功扱いを禁止。
- Bが送信費を払えなければ、送信イベントをコミットせずA-onlyへフォールバック。通信費はBが支払い、AのF007 motor支出はそのまま。未来の軌道/資源座標・`attached`真値をAへ渡さない。
- パケット内容は**resource-relative directionのbool**。F014 `moved` とは異なるメッセージ型（フレーミングを含めて「全通信路1bit」と主張しない）。
- 資源獲得はT=1秒のA位置が研究者truthのtarget xに一致（許容差`1e-12 m`）した場合のみ、Aが`acquire`で3,000,000µJ。モーター支出はF007の**記録された**整数µJを研究者がF002統合台帳に一度だけ再生。B sender feeもF002 `spend`で計上する。資源獲得もF002 `acquire`。残高収支残差=0。
- 評価指標`net_uj = acquired_uj - motor_spent_uj - communication_spent_uj`。資源の発生と帰属はゲーム環境の仮定であり、実物理エネルギー保存の検証ではない。

## 凍結された反証可能な予測 (Wolfram exact rational precheck)
| 群 | 4エピソード成功数予測 | 期待正味 µJ / 1エピソード |
|---|---:|---:|
| A0 | 2 | 500000 |
| K | 2 | 450000 |
| S | 2 | 450000 |
| T | 4 | 1950000 |
| H | 4 | 0 |
| I | 0 | -1050000 |

H16a: T−A0 = +1,450,000µJ平均、T−K/T−S = +1,500,000µJ。H16b: H−A0 = −500,000µJ。H16c: K/SにはT固有の利益がなく、Iは有害。H16d: 力符号反転で終端座標・運動仕事が鏡映、全試行でF007/F002 ledgerとtruth-only資源判定が一致。H16e: falsified source/time、packet absence、insufficient sender battery が安全側拒否／明示的無通信になり、既存F001–F015を変化させない。

## 採否
- 各物理トレースはF007保存状態と一字一句一致する必要はないが、数値値・エネルギー支出・鏡映を独立に検算し、両方のPython 3.11/3.12で全既存テストを通す。
- primary 24/24をすべて保存・監査し、平均値は上の予測と整数µJの完全一致、終端位置絶対誤差≤1e-12m、台帳residual=0、4×6の固定割付を変えない。
- producerと独立検証器を**別コード経路**で実装。manifestのコードhash/全証拠hash、改ざん再ハッシュの否定例、別出力ルートへ2回実行したbyte再生で検証。追記型のfindingsに否定結果を残す。
- 既存の採用済みF007/その他F001–F015 sourceとV001、F011 #37は無変更。**科学的限定採用とmain統合はCI成功と独立の研究判断**。
- 実機通信、未知のsensor mask、通信の自発的獲得、任意dt、身体構造同定、自己組織化への一般化は認めない。
