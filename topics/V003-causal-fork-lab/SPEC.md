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

## Third design audit — physical influence, not just contact (2026-10-28; PROPOSED, NOT FROZEN)

### Why this instrument matters for SOMA, and where it stops
The original V003 design primarily classified contact/no-contact. This is necessary but insufficient to operationalize SOMA's central distinction: *encounter opportunity* is not *mechanical influence*, and neither implies *sustained embodiment*. The research target of this **calibration instrument** is now the precise causal pathway
`externally chosen B Y -> approach geometry -> contact event -> transferred normal impulse -> change in A's later observable motion`.
The third step toward embodiment (persisting attachment, resource/behavioral advantage, individual choice) remains explicitly **UNMODELED**. Do not label these passive predetermined trajectories as self-assembly, emergent function, adaptive strategy or organism.

### Primary estimand: A receives a consequence even though only B's initial Y changes
Define the **model-world counterfactual contrast** against immutable original F022 C05 (B Y=1.01 m):
`D_A^v(y) = ||v_A(t=2 s; do(y_b=y)) - v_A(t=2 s; original C05)||_2` in m/s.
A's own initial position, velocity, mass and model must be exactly unchanged. Thus a nonzero `D_A^v` is attributable **within the fixed deterministic passive model** to the B-Y intervention mediated by an actual contact impulse; it is not an observed causal effect in hardware or learned agency. A's terminal position norm contrast `D_A^x(y)` in m is a secondary corroboration. Compare full signed component vectors in the verifier; norms are display summaries only.

Three separable observables, never conflated:
- **Geometric opportunity**: signed *unconstrained-free-flight* clearance `c_free(y)=y-1 m` at nominal closest approach (t=1 s), not the measured physical overlap/minimum separation of the collision-resolved trajectory. Negative means an imaginary unimpeded pass would overlap, **not** actual simulated penetration.
- **Physical event**: `contact_kind in {impulse,grazing_zero_impulse,no_contact}`, continuous exact TOI or null, and normal impulse `j` [N s]; `j=null` for no event versus `j=0` for tangency. Avoid replacing null with 0.
- **Mechanical effect**: `D_A^v(y)` and `D_A^x(y)`, both zero at tangency and non-contact; strict source-row and analytic-oracle audit. A recorded grazing event is therefore NOT evidence of changed action capability.

With the existing equal 1 kg discs, R=1 m, opposite x velocities and e=1, theory predicts for y<1:
`t_hit=1-0.5*sqrt(1-y*y) s`, `j=2*sqrt(1-y*y) N s`, `D_A^v=j/(1 kg)`, and `D_A^x=(2-t_hit)*D_A^v`.
At y=1: event at t=1, j=0, both A effects zero. For y>1: no event, `time_of_impact_s=null`, `normal_impulse_ns=null`, both A effects zero. Total momentum (0,0) kg m/s and total KE 1 J are conservation *diagnostics*, NOT signs of individual benefit. Approach is analytically prescribed, not cell-selected.

### Stronger falsification and controls without extra simulated worlds
H3b now has TWO independent subclaims: (i) proper impulse/tangent/miss event classification; (ii) the measured **A terminal velocity and position changes** agree with the independent analytical formula under the predeclared tolerance, not just that there is a contact marker. Support for one does not automatically support the other. Reject contact-without-physical-effect being called mechanically effective; reject simulated A motion changed with no applicable physical event or another modified input.

In addition to C05 y=1.01 identity control, the frozen *original* F022 roster already contains **C06 y=.99 impulse** and **C07 y=1.00 grazing** under exactly the same remaining physical parameters (except original `world_id`). The V003 .99 and 1.00 forks must match corresponding *independently verified archived original C06/C07 physical scenario/rows/events after excluding ONLY the frozen source world-ID field*. This is a prospective archived positive-control cross-check, not additional V003 forks, a replacement for the independent mathematics oracle, or an acceptance of modified f022.archive.v1.

### Epistemic boundaries and decision criteria
1. **Scientific-model statement**: the calibrated passive F022 model exhibits the predicted geometry-to-impulse-to-A-change chain under specified interventions; no life-science claim.
2. **Engineering statement**: one immutable source, one approved variable, an independently verified derived family, and truthful six-owner UI presentation. Schema validity, self-asserted hashes, screenshot reviews, or passing unit tests alone do not confer source authority.
3. **Research direction statement**: future attachment/selection experiments may reuse this calibrated intervention/evidence method only through separately approved physics, local-observation and UI contracts. They may find non-attachment or detrimental effects.
4. **GO/NO-GO**: if these metrics cannot be independently reconstructed from saved states/events, if an archived C06/C07 cross-check fails, if agent/world truth leaks, or if any panel consumes an unverified artifact, **NO IMPLEMENTATION/ADOPTION** until redesign. The next scientific functionality is not authorized by a successful viewer.

### No new runtime subsystems
The sole V003 feature owner remains `experiments/V003`; `soma/f022.py` and its source verifier stay unchanged. A new `mechanical_contrast` *data field in the existing proposed v003.lab.v1 display contract* summarizes derived-AND-verified evidence, not a new service, analytics engine, seventh panel, policy or free-form parameter interface. Evidence owns the summary; Cells owns each cell's source state; Arena owns physical geometry; Timeline owns clocks.

## Final researcher-approved design refinements — 2026-10-28, before freeze

Researcher authorized proceeding with the detailed V003 design and separate implementation, **not scientific admission**. The original trusted archive is a PREEXISTING successful GitHub Actions artifact: workflow run **40176213718**, Python 3.11 artifact **12592745454**, commit `824a8621944ea438388c54949a2b65719be2e419`, frozen F022 protocol `3984e9dcb2cb420abab5ca92b4d029b31b5173f8`. Require externally inspected matching workflow, checkout and **complete 13-world archive** before selecting C05. Do not create a new original F022 archive under a V003 run or treat source SHA echoed by a JSON request as external authority. The artifact expires in November 2026; its immutability must be independently secured before expiry, with trust receipts, not silently substituted.

The canonical, newline-terminated 11 request SHA-256 digests are fixed in PLAN and enforced by the V003 derived contract; request content uses the exact pinned original SHA and protocol above. `fork_id` and `candidate_y_b_decimal` are a strict one-to-one pair. Each raw derived record has separate on-disk three-file hashes and embedded scene/samples/contacts: independently assert full byte-level canonical file/embedded semantic equivalence; never trust a hash alone. Independent receipt remains out-of-band.

UI must represent two mutually exclusive states **PREPARE_REQUEST** (original-only evidence, no generated world, Setup exports an allowed request without a simulation bridge) and **VERIFIED_COMPARISON** (only audited `v003.lab.v1`). Setup shows all 16 physical scene keys from the two source scenes in comparison mode; `full_parameter_diff` is just the 0/1 changed-field INDEX and cannot replace the full mapping. During request preparation, a proposed candidate is NOT an observation. The six V002 panel owners and observer-only data boundary do not change.

Freeze must follow exact-head design review and must precede generation of any V003 derived-world primary observation. No biological, self-assembly or learning conclusion is authorized by this approval.
