---
id: F009
kind: research_spec
status: proposed_not_executed
updated: 2026-10-18
issue: 28
---
# F009 — 外界反力・内部力・外部有効力を区別する運動量収支

**設計事前登録。未実装、未観測、未採用。** [Issue #28](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/28) / [PLAN](../../experiments/F009/PLAN.md) / [findings](../../findings/F009-validation.md)。

## 一つの問い
F007は外部有効力で二セル結合体が動くことを離散検証したが、地面への反作用を定義していない。内部の作用反作用と、接地反力・外部有効力を別々に記録すると、どの条件で重心が加速できるか。これは新しい運動機能や学習・自律推進の開発ではない。

## 固定仮説（計算前）
H009a：外界力積0の剛体結合二セルにA +2N/B −2Nの内部対作用を与えても重心加速度0、終速度0。
H009b：二セル結合への正味外部有効力+2Nは既存F007と一致し、終速度1m/s、半陰的Euler変位5/8m。
H009c：地面から+2N牽引を受け、地面に−2Nの反作用を返すとH009bと同じセル軌道。接地OFFでは牽引力0。
H009d：非結合でAだけ外部から+2Nを受けるとA終速度2m/s・変位5/4m、Bは静止。
反証：閉じた内部力対で重心が加速する、無接地で牽引する、上限を破る、二セル内力の和が非ゼロ、F007基準や別式の運動量収支に一致しない。
これらはNewton力学の既知の帰結を用いた実装意味論検証であり新物理発見を主張しない。

## 操作・統制・定義
条件はforce_origin=legacy_effective/internal_pair/ground_contact、attached=True/False、contact_enabled=True/False、traction_limit_n。固定mA=mB=1kg、xA0=0,xB0=0.5m、v0=0、command=2N、dt=0.25s、T=1s、抵抗0、seed=null。
地面モデルは1D水平牽引の飽和のみ：接地ONでtraction=sign(command)*min(abs(command),limit)、接地OFFではtraction=0、地面へ−tractionの反作用。実際の接触形状、法線解法、滑り、車輪、モーター機構は含めない。内部力はA+u/B-uとして二セル全体では相殺。F007のA電池/正仕事は歴史的基準で、今回のモード別の電気支出は扱わない。

## 測定と反証ゲート
研究者用のみ：A/B位置(m)、速度(m/s)、外部/内部/リンク力(N)、地面反作用(N)、セル総運動量(kg m/s)、外部力積(N s)、残差 R=ΔP−J_external (N s)。各stepで独立式再計算し、A/C軌道、B/D静止、E単独移動、F牽引上限を照合。A〜Fの固定有理数参照に対する絶対許容差1e-12を事前固定する。
保存CSV・manifestのハッシュに加え、記録中の力の意味・数値を独立オラクルで照合し、SHA再計算済みの偽内容も拒否。実施済み/未実施/支持/反証/判定不能を区別する。同じcheckout/入力の再実行byte一致を確認する。

## 情報境界・実行ゲート
真値は研究者向け。F008セルA局所APIへ接続真値・B状態・接地真値・反作用を渡さない。旧F001〜F008 API/証拠を変更しない。V001 PR #25/#26は独立のまま。
Issue→設計Draft PR（SPEC/PLAN/図/契約/未実施findings/索引）→別実装Draft PR（最小実装・A〜F・負例・旧回帰・3.11/3.12 CI・raw SHA・再現）→独立視点監査→研究者明示採否。mainへの統合と正式採用は別途承認が必要。実機・生存・形態順位・創発・学習・自律結合・汎用接触ソルバーは対象外。
