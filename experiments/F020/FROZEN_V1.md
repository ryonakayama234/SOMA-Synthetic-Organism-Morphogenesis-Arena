---
id: F020-FROZEN-V1
kind: preregistration
status: FROZEN_BEFORE_F020_EXECUTION
date: 2026-10-23
research_issue: 67
---
# F020 preregistration — frozen technical contract, before first F020 world

This file is the **pre-observation freeze revision** of the F020 PLAN/SPEC. It supersedes their DRAFT labels for the detailed settings explicitly fixed here; no F020 software or worlds had been run at the time this document was written. **The first Git commit adding this file** is the immutable protocol anchor. The design PR remains unmerged and F020 results remain UNEXECUTED at freeze.

## Primary universe, no output-dependent changes

- F019 SHA256 field generation exactly as existing `soma.f019.field_for`; seeds `range(32)`, motor signs `(-1,+1)`, patch counts `(2,5)`, radii `(.02,.06)` metres. Per patch 1,000,000 integer µJ, one first claimant, destructive first-entry and deterministic ties by `(step_index, entry_fraction_in_step, patch_id, cell_id)`.
- Every cell starts with **the same** battery balance in `(75_000,250_000,4_000_000)` µJ; capacity 20,000,000µJ; researcher-set step-0 per-cell joining fee `(0,25_000)` µJ only in YY. No credit before fee. Initial A x=0, B x=.1m, velocities zero, masses 1kg each, no drag or external force other than fixed A-only **effective** motor force `2*sign` N; link length .1m, fixed for episode, no B actuator.
- Time grid four steps each dt=.25s. Factor ordering: seed, sign, count, radius, balance, fee; exactly **1,536** canonical scenarios and **6,144** matched primary worlds `YY/NN × feedback/deferred_credit`. Scene ID must uniquely encode all factors. Same initial field cloned for each fork; forks cannot supply policy inputs. Block uncertainty by the **32 field-generation seeds**, not scenario/world count.
- No parameter, seed, cutoff, quantization or directional adjustment in response to outcomes. Calibration and adversarial checks are not part of the primary random-field estimand; null and adverse signs are valid.

## Temporal state machine and numerical semantics

1. Construct F007 config, use F018 step-zero bilateral consent gate; spend YY fees in F002 in cell order A, B before k1. Refuse any scenario where fees cannot be paid. Initialize zero pending credit per claimant.
2. At each k=1..4, record **pre-motor** available A/B integer balances and pending A/B. The A motor command is the fixed ±2N (negative calibration may set 0N). If A available balance is zero, reject with `zero_balance`; if command is zero, reject with `zero_command`; else obtain motor-on candidate next state from **F007 motion(cfg, x, v, joined, u)**; compute positive work using **F005 positive_motor_work(u,vA,trialVA,.25)** and required integer µJ as **math.ceil(1_000_000 * positive_work)**. Accept iff required <= pre-step A balance; accepted charge uses F002 spend from **A only**. A rejection causes F007 passive motion with applied force 0, **not** velocity reset.
3. Compute F007 motion once with accepted/applied effective force, calculate diagnostics and mechanical energy residual; update positions and velocities. For world-state display at k show post-motion and post-harvest balances **and** pre-motor balances, cost, applied flag, reason and F002 event-index.
4. For each patch not yet exhausted, perform F019 `first_entry` for A/B over their complete closed **linear-in-fraction** motion segments from k-1 to k. Sort candidate hits by `(fraction, patch_id, cell_id)` within the same step. Deplete patch once, assign amount to actual first claimant. `entry_time_s=(k-1+fraction)*.25`. Ties to lexically first patch ID, then A.
5. If `feedback`, post F002 `acquire` to the actual claimant after step motion/spend, making it motor-eligible only in k+1, never k. If `deferred_credit`, increment cell-specific **pending** amounts, deplete patch, and do NOT F002 acquire during steps 1..4. After k4 state snapshot is recorded, settle pending claim events in original global claim order as F002 acquire; record terminal settlement and zero pending. All ledger receipts use F002 integer µJ, capacity checked, no A↔B transfers. Zero positive-work actions still require nonzero A balance exactly as F007.
6. Kinematic and field calculations use Python IEEE-754 binary64 and established F001/F005/F007/F019 function semantics; no independent rounded-work formula replaces F005. Integer µJ, event counts, IDs, boolean flags, chronology, source and content hashes are **exact**. Independently recomputed floats are checked with `math.isclose(rel_tol=1e-11, abs_tol=1e-11)`; comparisons to pick claims/costs use original producer operations rather than tolerance heuristics. No NaN/infinity in JSON.

## Explicit saved world/evidence schema

Each world record has exact keys `scenario, world_id, arm, credit_mode, motor_force_n, attached, states, harvests, events, ledger, acquired_uj, spent_motor_uj, spent_fee_uj, net_uj`.
- `states` is 5 chronological records k=0..4, with `step_index, time_s, x_a_m, x_b_m, v_a_m_s, v_b_m_s, available_a_before_uj, available_b_before_uj, balance_a_uj, balance_b_uj, pending_a_uj, pending_b_uj, motor_command_n, motor_applied_n, candidate_positive_work_j, candidate_charge_uj, spent_a_uj, reason, ledger_event_index, mechanical_residual_j`. At k=0 no motor candidate, applied 0, decision `initial`; initial balances reflect fees and all pending zero.
- Harvest records retain F019-compatible exact keys: `patch_id,step_index,entry_fraction_in_step,entry_time_s,winner_cell_id,available_before_uj,acquired_uj,available_after_uj,ordinal`, in event order.
- Ledger `events` retain `step_index,phase,event_index,kind,source_id,target_id,amount_uj,eta_bps,received_uj,loss_uj,external_in_uj,external_out_uj,residual_uj,balance_a_uj,balance_b_uj`; phase `fee` (k0), `motor` (k1..4), `harvest` (k1..4 feedback only) or `settlement` (post k4 deferred only). Ledger summary includes F002 `initial_total_uj, acquired_uj,spent_uj,loss_uj,residual_uj,balance_a_uj,balance_b_uj,event_count`. `net_uj` is per-cell actual harvested minus motor and fee charges; ledger summary is after terminal settlement.
- Deterministic JSONL `worlds.jsonl`: sorted keys, compact separators, ASCII escaping, no NaN, newline. `manifest.json` records schema, count, source Git HEAD/clean state/source SHA256 map, world-file SHA256, numerical summary and protocol-anchor commit SHA. A separate standalone verifier must reconstruct from saved states and scene geometry with no imports from producer or `soma` and reject rehashed semantic forgeries.

## Positive technical calibration and falsifiers (not random evidence)

Synthetic **non-primary** one-patch calibration: patch ID P0, center=1/16m, radius=1/200m, amount=1,000,000µJ; A/B initially 75,000µJ, fee=0, +2N. Exact Wolfram rational oracle predicts xA at step4: YY+feedback = 5/8m; YY+deferred = 1/4m with retained inertial v=1/4m/s; both NN arms = 0. The first A claim is in YY step1, its energy is not available until step2. See audit note for full step vectors.
- Negative/edge controls: no patches; B-only hit never enables A; no motor; ± reflection; no retroactive spend; zero balance, nonpositive work, boundary of ceil, fee, simultaneous/overlapping/duplicate first claim, settlement order, capacity; high budget no-field YY/NN reproduces exact F007 trajectories; F001–F019 unchanged.
- A technical gate is **not** dependent on ecological positivity. Independently verify logs, sha256 hashes, source SHA binding, byte-identical two clean-root producer runs (except output paths), altered records with recomputed file and manifest hashes, both Python 3.11 and 3.12 regression workflow at exact HEAD. Same-model review is not human external peer review.

## Acceptance / release

Keep implementation in a **separate PR** stacked against this frozen design branch until design is appropriately reviewed/merged. Record actual findings append-only; promote to limited software instrument only after verifier, adversarial negative tests, CI, exact source, review. Do not claim autonomous morphogenesis, biological metabolism, ecological generalization or learned linkage from this capability.
