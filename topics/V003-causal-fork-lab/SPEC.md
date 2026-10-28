---
id: V003
title: Causal Fork Lab
kind: design_specification
status: DESIGN_DRAFT_UNFROZEN_UNEXECUTED
updated: 2026-10-28
issue: 93
depends_on: [F022, V002]
---

# V003 — Causal Fork Lab / 実装前の精緻化仕様

**One capability:** independently verify a complete original F022 archive, take exact frozen original C05, vary only its B initial Y coordinate over a fixed eleven-value grid, generate *new* passive two-disc physics data with the unchanged F022 solver, independently validate that derived evidence, and offer a six-owner researcher comparison under an explicit new V003 view contract. No implementation or V003 physics run yet. Issue #93; parent research #51. This design is stacked on V002 candidate PR #89 and must not merge to main until V002 meets its separate admission/merge gates.

## Central unknown and measured quantities
Unknown: Can a controlled researcher intervention be traced unambiguously from an original trusted archive through separate new-world physics evidence to a truthful comparative display? This is a measurement-instrument question, **not** a novel contact law or evidence of voluntary assembly.

- **Manipulation:** y_b_m, B initial Y [m] only. Original F022 C05 initial B=(1,1.01)m; A=(-1,0)m; initial A speed (+1,0)m/s, B speed (-1,0)m/s; mA=mB=1kg, radii=.5m, restitution=1, duration=2s, sample_dt=.25s. Other original scenario fields copied exactly (including solver row world_id C05).
- **Input register:** exactly decimal strings 0.95,0.96,0.97,0.98,0.99,1.00,1.01,1.02,1.03,1.04,1.05. Fixed by design review and later pre-observation freeze. 1.01 is an **identity/zero-difference** control, ten other candidates are single-variable interventions. Eleven generated worlds × nine sampled post-frames = 99 proposed derived saved frames, distinct from the nine already recorded source C05 rows.
- **Primary physics outcome:** contact classification impulse / grazing_zero_impulse / no_contact. Secondary: exact event TOI in s (null for no event), geometric normal, impulse N·s, A/B pre/post velocities m/s, 2D total momentum kg·m/s, total kinetic energy J, post-grid sample position/velocity and geometric gap m. Never infer contact from a drawing.
- **Primary engineering outcome:** exact permitted diff, source/derived/view verification, semantic forgery refusal, original byte immutability, reproducible canonical output, browser comprehension and six-panel ownership. Each candidate is a deterministic calibration, **not** an independent biological/ecological replicate.

## Hypotheses / falsifiers (UNEXECUTED)
**H3a — single-input integrity:** y_b_m is the only allowed physical scenario difference against C05; at y=1.01 there must be none. Fork identity is stored separately as fork_id, not an additional physical-world input. Falsify on any second changed field, type coercion, source mutation or source identity confusion.

**H3b — 2D contact boundary:** r=(2,y), w=(-2,0), radii sum R=1. For y<1, earliest collision t=(2-sqrt(1-y²))/2 s and nonzero impulse; at y=1, exact tangency t=1s and zero impulse; for y>1, no recorded collision. With e=1, full-world momentum=(0,0) and KE=1J. Expected 5 impulses, 1 tangent, 5 misses. Falsify on omitted/phantom collisions, missed off-grid TOI, incorrect impulse or conservation residual beyond preregistered gates. These are **known idealized analytic predictions**, not new scientific discovery.

**H3c — derived evidence authority:** independent full-original F022 verification (with externally trusted checkout/freeze SHA), a *separate* V003 from-disk independent derived-physics oracle, and a separate source-to-view semantic check reject forged/rehashed modifications before any verified display. Falsify on a tampered input/event/sample or wrong source SHA being certified, or root/source mutation. Same source/software/Python environment produces byte-identical two-root output; across Python 3.11/3.12 demand physical equivalence, not universal identical bytes.

**H3d — bounded UI authority:** existing six slots communicate each result, original vs derived provenance, input diff and no-contact vs zero-impulse vs off-grid event without inventing observations or sending global truth to a local cell. Falsify on a new panel, changed owner without new contract, false sampled coordinates, missing verifier verdict, or viewer-to-policy feedback.

Distinct verdicts: software PASS/FAIL/INCONCLUSIVE; H3a-d SUPPORTED/REFUTED/INCONCLUSIVE/UNEXECUTED; separate researcher usability PASS/FAIL/INCONCLUSIVE and explicit admission.

## Physics / numeric and null semantics
Re-use existing source soma/f022.py with no edits: passive equal disks, 2D unbounded free flight, continuous analytic TOI and restitution. No ground friction, gravity, motors, batteries, ports, joints, local agents or learning. Input value identity/type must match EXACTLY (not fuzzy float tolerance). Request uses decimal-string enum, parsed to finite binary64 only after validation. For physical derived quantities use absolute criterion 1e-9*max(1,abs(expected)) in SI components, unless later reviewed preregistration expressly tightens a more specific threshold. Contact stream must have exactly 0 or 1 row; no-contact means empty contacts and time absent/null, **not** a fabricated time-zero event. Tangency must retain source event kind grazing_zero_impulse and j=0. Off-grid event is archived pre/post event and **not** an invented sampled XY frame. Invalid, nonfinite, out-of-enum, near-ambiguous or malformed geometry fails closed.

## Original / derived / view separation: mandatory architecture
~~~mermaid
flowchart TD
  S["Full original F022 C01-C13 frozen source archive"] --> G{"Independent original F022 verifier + externally trusted SHA"}
  G -->|pass| B["Immutable C05 baseline"]
  G -->|fail| R["Refuse / no verified view"]
  H["Researcher bounded y request"] --> Q["V003 request checker"]
  B --> Q
  Q -->|valid| P["Existing unmodified F022 physics solver"]
  Q -->|reject| R
  P --> D["NEW v003.derived.v1 immutable root"]
  D --> I{"Independent V003 on-disk physics oracle"}
  I -->|pass| X["NEW v003.lab.v1 verified two-authority view"]
  I -->|fail| R
  X --> U["Existing six panel owners"]
  U -.->|NO DATA / CONTROL FEEDBACK| A["Blocked: LocalObservation, Policy, Learning, source archive"]
~~~

**Critical boundary:** the existing F022 source oracle requires the **exact frozen 13-world roster** and must not be reused to claim a changed C05 is an accepted f022.archive.v1 source. A new V003 fork always has its **own** derived family and independent oracle. V002.view.v1 only permits same-source-family already archived pairs and cannot accept F022/derived V003 cross-authority pairs. V003.lab.v1 specifically authorizes that one new comparison only after both separate verification paths pass.

## Exactly six panel contracts; no ad-hoc growth
Proposed prospective V003 UI ownership map: contracts/v003.workspace.layout.v1.json, dependent on the already designed v002.workspace.layout.v1. Same 1500x950 reference, neutral grayscale, central two-world metrically scaled Arena, fixed bottom Timeline with bounded internal history scroll. Setup upper-left: choose **enumerated** y and export typed request JSON, inspect **full** physical-field diff. Arena: saved paired XY frames and separately recorded exact event pre/post. Cells lower-left: A/B state and F022 motor/battery **NOT MODELED** (never energy=0). Timeline: sample/event pointer and local cursor only. Evidence upper-right: original, derived, view verifier provenance and rejection reasons. System/Data lower-right: versions, actor authority and disabled agent/learning reservations.

**No browser-to-Python execution channel in V003.v1.** A local offline runner/operator consumes exported versioned request file and emits verified bundle, subsequently opened in the fixed UI. This keeps one new capability and avoids inventing browser/server authority. True one-click live local simulation, arbitrary physics editor, F023 forks, agent actuation/observation/training, mechanical joining, 3D or new panels require separately versioned researcher-approved contract.

## Adoption sequence
Design-only Issue/SPEC/PLAN, machine-readable source/derived/view/layout contracts and architecture/data/finding synchronized on a Draft PR -> critical review and design corrections -> separate **pre-observation freeze** SHA in experiments/V003/FROZEN_V1.md -> separate implementation and independent reviewer -> actual execution + negative/tamper tests + repeatability CI -> human browser comprehension -> separate scientific and engineering verdict + explicit researcher decision -> main integration. V002 #89 is a prerequisite to main integration; no frozen F022/V002 artifacts or original science changed.