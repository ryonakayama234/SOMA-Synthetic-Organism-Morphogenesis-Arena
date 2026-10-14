---
id: DATA
title: データの構造と流れ
kind: contract
status: partially_implemented
updated: 2026-10-13
related: [ARCHITECTURE, F001, F002]
---

# データの構造と流れ

「どんな情報が、どこからどこへ移るか」を図で保持するための、最小限の約束。**ここに示した構造は提案であり、まだ実装済みのAPIではない。**

## 三つに分けて考える
~~~mermaid
flowchart LR
  I["① 設定\n実験条件"] --> E["② 実行中の状態\n刻々と変化"]
  E --> O["③ 記録\n再解析できる保存物"]
~~~

| 種別 | 意味 | F001の例 |
| --- | --- | --- |
| 設定（input） | 何を固定して試すか | 質量 kg、力 N、抵抗 1/s、刻み s、総時間 s |
| 状態（state） | いまどうなっているか | 時刻 s、位置 m、速度 m/s |
| 記録（output） | 実験後にも調べられる証拠 | 時系列CSV、設定JSON、要約と図 |

## 一個のセルの状態（F001）
~~~mermaid
flowchart TD
  ID["Cell-001"] --> X["位置 x [m]"]
  ID --> V["速度 v [m/s]"]
  ID --> M["質量 m [kg]\n変更しない設定値"]
  ID -. "未導入・将来" .-> E["電力量 [J]"]
  ID -. "未導入・将来" .-> B["接続情報"]
~~~

## 仮の入力形式例
~~~json
{
  "schema_version": "0.1-proposal",
  "experiment_id": "F001-run-001",
  "seed": 1,
  "model": "1d_linear_drag",
  "mass_kg": 1.0,
  "drag_per_s": 0.2,
  "force_n": 1.0,
  "dt_s": 0.01,
  "duration_s": 10.0
}
~~~
**数値は実験準備の例で、確定仕様ではない。**

## 仮の時系列記録
~~~csv
time_s,x_m,v_m_s,force_n
0.00,0.0,0.0,1.0
0.01,0.0001,0.01,1.0
~~~
これは説明用の2行。実験結果を示すものではない。F001の仕様が承認されたら正式な列を固定する。

## 研究の再現性に必要な紐づけ
- 実験識別子 → 設定 → 乱数シード → 実行コードのコミットID → 生ログ → 図 → 解釈
- 記録は追記または新規作成。別条件の結果を同じファイルに上書きしない。
- 物理エンジン用の真の状態ログと、セルが実際に知覚した観測ログを分ける。

[システム図鑑](ARCHITECTURE.md)

## F001で確立した入出力（2026-10-13）
- 設定は `schema_version=f001.v1` を使用。 `model=1d_linear_drag`。
- `initial_x_m`、`initial_v_m_s` も入力として追加。
- 時系列 `states.csv` の列順は `time_s,x_m,v_m_s,force_n` で確定。
- 各実験に `config.json`、`manifest.json`（コードコミットIDとチェックサム）、`motion.svg` を出力。
- 実行結果の上書きを禁止し、出力先には未使用のディレクトリを指定。
- 詳細： [F001の再現方法](../experiments/F001/README.md)。


## F003の提案データ構造（2026-10-14、未実装）
F001が確立した単一セルの位置・速度・外力を二セルに拡張する。**以下は仕様案であり、動作するAPIや保存済み実験データではない。**

~~~mermaid
flowchart LR
  INPUT["設定JSON\n2セルの初期状態\n各セルの外力・リンクON/OFF"] --> WORLD["世界の真の状態\nCell A / Cell B / Link"]
  WORLD --> TRACE["states.csv\n位置・速度・外力\n内部力・拘束誤差"]
  WORLD --> EVENT["events.csv\n結合・切断・拒否"]
  TRACE --> META["manifest.json\n設定・commit・各成果物ハッシュ"]
  EVENT --> META
  INPUT --> META
  TRACE --> REVIEW["対照比較・図・判断"]
~~~

~~~json
{
  "schema_version": "f003.v0-proposal",
  "experiment_id": "F003-B-planned",
  "seed": null,
  "dt_s": 0.01,
  "duration_s": 10.0,
  "drag_per_s": 0.2,
  "cells": [
    {"id": "A", "mass_kg": 1.0, "initial_x_m": 0.0, "initial_v_m_s": 0.0, "force_n": 1.0},
    {"id": "B", "mass_kg": 1.0, "initial_x_m": 0.5, "initial_v_m_s": 0.0, "force_n": 0.0}
  ],
  "link": {"initially_attached": true, "length_m": 0.5, "detach_time_s": null}
}
~~~

- 実行状態：時刻、各セルの位置・速度、外部指定力、結合ON/OFF、各セルに作用するリンク内部力。
- 記録：拘束誤差や重心の解析値との差分も追加して、間違った内部力や数値積分の劣化を発見可能にする。
- イベント：接続/切断/拒否を理由とともに記録。無理な初期接続を黙って修正しない。
- 境界：すべて**世界の真値を用いる研究用データ**であり、セルが知覚できる情報とは異なる。セル観測ログはセンサー能力を別途実装するまで作らない。
- 再現性：F001と同じく設定・コードSHA・生ログ・SHA256と図を関連づける。乱数を使用しなければ seed は null と記録する。

列名・厳密な許容誤差は実装前の仕様レビューで決定し、実験データに合わせて後付けしない。
[設計仕様](../topics/F003-attachment/SPEC.md) / [実験計画](../experiments/F003/PLAN.md)。
