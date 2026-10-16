---
id: FIND-F005
title: F005 速度反転とモーター正仕事の実験記録
kind: experiment_finding
status: adopted
updated: 2026-10-16
feature: F005
issue: 12
---

# F005 検証ノート【現在：計算部品として正式採用／冒頭は事前登録の履歴】

## 問い
1セル1Dの正味区間仕事を課金するF004の既知制約を解消するため、**区間内正仕事の積分**によって再加速費用を計量できるか。

## 事前登録されたH005
[仕様](../topics/F005-positive-work/SPEC.md) と [実験計画A〜F](../experiments/F005/PLAN.md) を参照。反転の解析例は `m=1kg, u=-2N, v0=1m/s, dt=1s` で `W_signed=0J`, `W_plus=0.5J`。理論値はWolfram Languageの事前積分結果 `1/2` に基づく。**実験観測ではない。**

## 証拠の状態
| 記録 | 状態 |
| --- | --- |
| SOMA F005 コード・計算ログ | 未実装・未実施 |
| A〜F実測、CI、ソースSHA・artifact | 未実施 |
| 実測値と理論値の差 | 未算出 |
| 不正入力拒否、再実行、改変検知 | 未実施 |
| 独立実装監査と採否 | 未実施・未判断 |

## 実装後に追記する様式
- 日時、ブランチと実行commit、dirty状態、source/suite SHA、Python版、seed、環境条件。
- 事前参照（Wolfram有理数・binary64独立オラクル）とSOMA実測値。A〜Fごとの支持・反証・不明。
- 全ステップ真値CSV・F002 spend・残高不変条件・仕事分離・数値許容差。
- 速度反転の粗いdtと細かいdt比較。誤差と整数µJ切上げ差を分離。
- 無効ケース、ログ改変・再実行一致、CI artifactのURLとハッシュ。
- 統合前の独立監査の指摘、改訂履歴、保留課題、正式採用範囲。

**禁止**：仕様作成だけで成功・観測済みと記載すること。F005の単一セル正仕事計測を、2セル結合の有利性・創発・実機妥当性の証拠とみなすこと。

[Issue #12](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/12) / [計画](../experiments/F005/PLAN.md)。

## 2026-10-16 Wolfram事前理論検算（実装・実験は未実施のまま）

実装前に一定力・端点速度の線形補間に対する`Integrate[Max[0,u*(v0+(v1-v0)*t/h)],{t,0,h}]`を独立評価。反転A：`W_signed=0, W_plus=1/2 J`、通常加速C：`1/2, 1/2 J`、制動D：`-1/2, 0 J`、外力のみE：`0, 0 J`、0.5秒×2の反転F：`W_plus=0+1/2 J`、非対称反転：`W_signed=4, W_plus=9/2 J`。2分割正仕事と1分割正仕事が同じことも検算。

上記は**理論・事前予測**のみであり、F005 Python実装・CI・artifact・GitHub main統合・採用判断の証拠ではない。F004既存のモデルとF001の位置積分誤差を混同しない。定量ゲートは[仕様](../topics/F005-positive-work/SPEC.md)と[A〜F計画](../experiments/F005/PLAN.md)の2026-10-16追記に記録。

## 2026-10-16 Implementation candidate (not yet independently validated in CI)

An implementation branch contains the new single-cell module `soma/f005.py`, `tests/test_f005.py`, A–F suite `experiments/F005/run_suite.py`, instructions, `.github/workflows/f005.yml`, synchronized architecture and data-contract sections. This is **code availability only**, not an observed result or formal adoption.

### Implementation boundary
- F004 `f004.v1` and F001/F002/F003 are left unchanged.
- The new `f005.v1` contract adds candidate/accepted positive motor work, separately preserving signed midpoint work.
- The A–F saved-file independent oracle, tampering, microjoule rounding, and whole-suite byte replay are programmed for CI.
- Pending: GitHub Actions status for the exact implementation HEAD, immutable artifact hashes, independent review, any failed cases and corrective changes.

### Quality gate
Mark this feature `observed` only after obtaining successful CI **on the final proposed HEAD** and independently inspecting tests/results. Preserve error reports and failed iterations. Do not treat the earlier Wolfram rational reference as SOMA output.

## 2026-10-16 GitHub Actions 初回実装と監査修正後の観測

### 反例と改善
初回設計通りに端点`p=u*v`の値で正負を判定すると、`u=1e-200, v0=v1=1e-200, h=1e300`のような入力で両端のパワーが0へアンダーフローして、理論上正の仕事を無料にしてしまう。Wolframの有理数積分は`10^-100 J`で正。F005実装は力の方向と速度の符号を利用した判定に変更し、同一入力を**正仕事1e-100 J／1µJ支出**として回帰テストで検証。正仕事と電気消費の現実妥当性は依然非対象。

### GitHub Actionsの実行証拠（実装候補HEAD）
- **検証HEAD**: `6fa44afb057ce6dc2db66015575c0d7452d596a3`
- **F005 workflow**: [run #38876548177](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38876548177) — `success`、Python 3.11、**90 tests / OK**（既存F001〜F004 73＋F005 17）。
- 正常A〜Fは**10ケース**、不正入力は**17件を事前拒否**。保存CSV全時刻とF002支出イベントの独立照合、保存成果物SHA、tamper拒否、完全スイートのバイト再実行一致に関するCIジョブが成功。
- A反転：W_signed=0J、W_plus=0.5J、500000µJ支出、残高0。Bの残高1µJではモーターを拒否し、残高1。非反転、制動、外力、刻み分割、非対称反転についてA〜Fの事前ゲートと整合。
- GitHub Actions artifact: [F005-A-F-evidence（ID 12036090522）](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38876548177/artifacts/12036090522)。生成物一式のZIPとともに、個別のCSV・Ledger・SVG・manifest・suiteソースハッシュが保存されている。
- 他の4 workflowも初回実装HEAD `1fc95f9aa4d405050f03cc3ce5c274f4fdd982c3`ではsuccess。**修正済み最終HEAD**のF001〜F004 workflow結果は別途確認して確定する。

### 判定
上記は**ソフトウェアモデルに関する事前仮説を支持**するCI証拠であり、実機の電池消費や自律的な形態創発を確認したわけではない。バッテリー効率・保持消費は未モデル化。非有限な中間計算はrun保存前に拒否する。独立第三者による最終監査とユーザーの正式採用判断は未了。mainは変更していない。

### 最終のコード・記録同期HEADのCI確認（2026-10-16）
- 対象HEAD `c3f506f0d829296e20f5a02a99a5457c7663cee7` でF001/F002/F003/F004/F005の**5 workflowがすべてsuccess**。
- [F005 Actions #38876733416](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38876733416) では90テスト、10正常対照、17不正入力拒否、完全再実行一致（`full_replay=true`）。A残高0µJ、B残高1µJ。
- [raw evidence artifact #12035158501](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38876733416/artifacts/12035158501)（GitHub Actions artifact ZIP SHA256 `0ed49b5b9b3810a7b07dee0c38d7f295d148d4e35c12b488af2150fccba4906a`）。上記HEADはコード・図・データ契約・検証ノートの同期版。
- この節を追記した新HEADでも5 workflowを再実行して確認する。過去HEADの成功と新HEADの成功は同一視しない。

**採用判断**：基準モデルのソフトウェア実装仮説は支持。F005はまだDraft実装候補であり、独立監査と正式採用判断、設計PR #13→実装PR #14の順のmain統合は未了。

## 2026-10-16 PR #14 独立レビューと修正

対象：`1462d750e036f92a443e1e0d9a835f0775d967d4`。開始時の全90テストは成功し、そのHEADの全5 workflow successも確認した。次のP2相当2件はその検証をすり抜けていた。

1. **保存証拠オラクルの数値不一致**（`experiments/F005/run_suite.py`）。実装で修正済みの端点パワーunderflowがオラクルには残り、u=v0=1e-200,h=1e300,f_ext=-uの正しい1µJ支出ログを `wrong battery decision` で拒否。さらに通常の反転u=-10,v0=0.2,h=duration=0.05,battery=45000でも実装0.045J→45000µJに対し、旧オラクル0.04500000000000001J→45001µJで受否が逆転した。厳密Fraction積分と固定binary64課金参照を分離して修正。
2. **hash更新済み改変の見逃し**。初期行 `candidate_motor_positive_work_j=999` でも `independent_all_steps=true`。また絶対許容差1e-12は1e-100J→0の改変を許していた。初期候補2欄null、正仕事の正値性と相対/ULP比較を追加し、両改変を拒否する。

### 検証と観測
- ローカルPython 3.12.14：**93全テスト成功**（旧90＋新規3）、最適化PythonでもF005の20テスト成功。125通りの符号・端点組合せをFraction参照と照合。
- A〜F：元10対照＋反例/decimal刻み3件＝**13正常対照**、**17入力拒否**、保存CSV/台帳の独立照合、**73ファイル**の完全再実行バイト一致。
- A反転：0.5J、500000µJ支出、残高0。B：モーター拒否、残高1。追加ceil境界：45000µJ、残高0。追加underflow：1µJ、残高0。
- Aの0.5秒分割：正仕事総量0.5J・支出500000µJ。0.1秒分割：実支出500001µJ・残高499999、正区間5。実際のbinary64端点をFraction化した積分に対するbinary64仕事誤差は約−1.4572e-17J、厳密な各区間切上げ合計500002µJと実支出の差は−1µJ。厳密数量化差は約2µJで0以上5未満。これは端点誤差・仕事評価誤差・数量化を分けた観測で、連続物理の刻み不変性ではない。
- Wolfram厳密再検算：反転1/2J、非対称反転9/2J、微小積分10^-100J。Python実行とは別の数式検算。
- 変更はF005検証・テスト・補足記録。`soma/f001.py`〜`soma/f005.py`の運動・費用ロジックは維持。

現行HEADのCI・artifactは[PR #14 Checks](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/14/checks)とレビュー完了コメントでSHAを対応づける。上記ローカル結果をCI結果と取り違えない。F005はDraft候補を維持し、正式採用・設計PR #13と実装PR #14のmain統合は未実施。保持/待機消費0、実機電力・F003統合・自律制御は引き続き後続課題。

## 2026-10-16 意味論監査：正式採用範囲の判断材料

対象コードHEAD：`a7d55af699b0de89ff5b7693ac9c14af1fb1a9b1`。GitHubで設計PR #13・実装PR #14はともにDraft/open、#14のレビュー未解決スレッド0、同HEADのF001〜F005全5 workflow成功を再確認。ここで検討するのは「仕様どおり動くか」と別の、研究環境としての意味と誘導である。

### 再現した意味論上の懸念

全ケースm=1kg、drag=0、x0=0、外力は特記以外0。現行の`Config`/`simulate`をPython 3.12.14で実行し、運動・仕事・F002台帳から次を観測した。新しいA〜F事前登録結果には数えず、事後の診断として記録する。

| 診断 | 入力 | 実行結果と意味 |
|---|---|---|
| 位置と仕事の軌道 | u=1N,v0=0,h=T=1s,残高1J | x1=1m,v1=1m/s,正仕事0.5J。仕事計算用の速度補間の積分は0.5m。力×保存位置差は1Jで、記録された符号付き仕事0.5Jとは異なる。ΔK=0.5Jとの恒等式は成立するが、同じ位置軌道上の仕事を検証した意味ではない。 |
| 不足時の全区間棄却 | u=1N,v0=0,T=1s,残高0.4J | h=1s：x=v=0、支出0、残高400000µJ。h=0.5s：x=0.5m,v=0.5m/s、支出125000µJ、残高275000µJ。位置誤差だけでなく、駆動を採用する区間自体が変化する。 |
| 同じ運動の量子化 | u=1e-6N,f_ext=-u,v0=1m/s,T=1s,残高1000µJ | h=1/0.1/0.01sで速度1・最終位置約1m・総正仕事約1e-6Jを維持しながら、支出は1/10/100µJ。1µJ程度の微小な丸め差が常に無視可能とは言えない。 |
| 無償保持と残量0の不連続 | u=1N,f_ext=-1N,v0=0,h=1s,T=1000s,残高1µJ | 全1000区間でx=v=0、支出0、残高1µJ。残高0では最初の1秒からuが遮断され、x=-1m,v=-1m/s。無償保持は有限試行で確認し、任意の長さで不変という主張は同じ状態が反復する式からの推論。 |
| ブレーキの残量境界 | u=-1N,v0=1m/s,h=T=1s | 残高1µJ：v1=0、支出0、残高1。残高0：v1=1、支出0。電池がないとブレーキも無効という現在の有効アクチュエータ定義。 |

簡易再現（リポジトリルート）：
```python
from experiments.F005.run_suite import base
from soma.f005 import Config, simulate
cases = [
    dict(motor=1., dt=1.),
    dict(motor=1., dt=1., battery=400000),
    dict(motor=1., dt=.5, battery=400000),
    dict(motor=1., external=-1., dt=1., duration=1000., battery=1),
    dict(motor=1., external=-1., dt=1., battery=0),
    dict(motor=-1., velocity=1., dt=1., battery=1),
    dict(motor=-1., velocity=1., dt=1., battery=0),
] + [dict(motor=1e-6, external=-1e-6, velocity=1., dt=h, battery=1000)
     for h in (1., .1, .01)]
for inputs in cases:
    cfg = Config.from_dict(base('semantic-diagnostic', **inputs))
    rows, events, ledger = simulate(cfg)
    linear_dx = sum(cfg.dt_s*(a['v_m_s']+b['v_m_s'])/2
                    for a,b in zip(rows, rows[1:]))
    print(inputs, rows[-1]['x_m'], rows[-1]['v_m_s'],
          ledger.spent_uj, rows[-1]['balance_uj'], linear_dx)
```

### 独立数式検算と解釈
Wolframで位置差の一般式 `h*(v1-v0)/2` を積分から再導出。厳密有理数の候補→費用→受否→速度/位置更新を独立実行して、上の0.4Jの1区間/2区間比較を再現した。同じ総正仕事1µJの分割切上げも1/10/100µJと確認。これはPython観測とは独立の式検算。

さらにf_ext=drag=0の運動量変化はu*h。現行実装に接地や反作用相手の状態はなく、uは**有効な駆動力入力**である。反作用相手がモデルにないこと自体をF005の計算バグとは扱わないが、自由空間の純内部力による自己推進、あるいは接触条件から自律的に移動機能を獲得した証拠とは解釈できない。これは実装境界からの研究上の推論である。

### 採用についての推奨
正仕事積算・台帳接続という一能力の離散計算部品として、限定的な正式採用・マージを推奨できる。現時点で自律移動・生存・協調/形態の優劣を測る環境全体が成立したとは判定しない。優先する後続検討は、位置/速度/仕事の共通軌道と受否/端数処理の刻み依存、次に対象駆動機構の保持消費と反作用/接触の定義。全機能をF005へ追加するのではなく独立課題に分ける。

この監査は仕様/実行結果の意味を明確化するもので、F001〜F005のコードや過去の証拠は変更していない。**ユーザーによる採否確定・PR #13/#14のマージは未実施。**


## 2026-10-16 正式採用：F005の限定的な研究上の位置づけ

**採用決定**：ユーザーのレビューと採用判断に基づき、F005を**「単一セルの1D離散運動で、端点速度を線形補間して正のモーター仕事を区間積分し、その理想正仕事費用をF002整数µJ台帳へ接続する独立計算部品」**として正式採用する。F001〜F004の既存意味論を維持し、F004の既存実験ログ・APIを置換しない。設計PR #13と実装PR #14をmainへ統合する。採用はシミュレーターの広い妥当性を認めたものではない。

**採用理由**：F004の区間内速度反転で生じる正負仕事の相殺を排除し、候補/適用駆動を分けたF002原子的課金、不足時の外力維持、符号付き機械仕事と正仕事費用の分離を実装。独立レビューでP2相当のオラクル誤拒否・検証すり抜けを修正した後、実装最終レビューHEAD `b90d310270a505024ecf041ce7015e8fb1b76c8c` のF001〜F005全5ワークフローがsuccess。[CI #38892096531](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/38892096531)で93テスト、13正常対照・17不正入力拒否、独立保存CSV/イベント照合と再実行一致を確認。採用記録追記後のHEADでも同じCIゲートを再実行する。

**保留・禁止用途（意味論監査を採用の一部として明記）**：

1. **位置と仕事の軌道が異なる**：F001半陰的Eulerの位置変化は`h*v1`、F005仕事計算に使う線形速度の位置積分は`h*(v0+v1)/2`。その差`h*(v1-v0)/2`により、保存移動距離当たり効率の主張は禁止。
2. **刻み幅依存**：残高不足で時間区間をまるごと拒否するため、時間刻みにより行動採否・軌跡が異なる。正の仕事の毎ステップµJ切上げでも同一理想仕事が1/10/100µJに変化し得る。将来の運動報酬・電池消費の比較にそのまま使わない。
3. **無償保持**：正残量1µJで力を1000秒維持しても保持費用0の例がある。現モデルでの持久力・生存優位を実機や進化の結果として扱わない。
4. **反作用相手の不在**：`motor_force_n`は質点に作用する**有効駆動力**。接地・摩擦・環境・反作用相手は未定義。閉じた身体の純内部力による自律推進と解釈しない。

**次の優先研究**：F005をいじって4問題を同時解決しない。まず**電池制約付き運動と電池支出の時間刻み収束**を別課題で反証可能な形で実験設計する。共通軌道、部分時間駆動、端数累積を分離比較する。保持損失と反作用/接触モデルは後続の独立仕様とし、それらが妥当化されるまで、生存・形態・協調優劣の標準評価環境としての承認はしない。

**歴史の扱い**：本書前半の「未実装」「提案」「Draft」「採用前」は当時の実験計画と監査履歴であり消去しない。今回の正式採用範囲はこの節を優先する。
