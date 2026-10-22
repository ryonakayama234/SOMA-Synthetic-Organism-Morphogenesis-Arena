---
id: F018
title: 接続同意ゲートと個体別の結合利得
kind: preregistration
status: frozen_v1
updated: 2026-10-22
issue: 61
depends_on: [F002, F003, F005, F007]
related: [F017, PROJECT]
---

# F018 — 身体境界を選択できるか：結合に自分の利益がある条件

**DESIGN FROZEN v1 / NO F018 SIMULATION AT DESIGN FREEZE / NOT ADOPTED.**
[Issue #61](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/61) / [experiment PLAN](../../experiments/F018/PLAN.md) / [UNEXECUTED findings](../../findings/F018-validation.md) / [charter](../../docs/PROJECT.md).

## One question
For initially contact-ready, same-type 1D cells, does a *mutually consented* mechanical link yield positive or negative **own-account** resource/energy advantage depending on resource geometry and mechanical/connection costs? The researcher changes **only the attach requests** in exact paired counterfactual worlds. This asks for a map of attachment affordances, **not autonomous learned consent or spontaneously gathered bodies**.

## Hypotheses to audit and freeze BEFORE first F018 experiment
- **H18a physics/choice integrity**: `attach_A && attach_B` attaches iff F003 initial distance/equal-velocity constraints also hold. If either declines, the two cells remain independent; no force or electric energy transfer due to a nonexistent link. Invalid initial geometry fails explicitly, not by teleporting or synchronizing velocities.
- **H18b environment-dependent incentive**: there exist predeclared resource/drag/motor/cost settings with `Δ_i = net_i(join)-net_i(separate)` positive for both cells and others with a negative individual delta. Measure *per-cell* and *aggregate* outcomes. Reject if cherry-picked or only a single net sum is reported.
- **H18c no artificial attachment reward**: the link itself yields no score. Resource comes only from a declared geometric resource event; positive motor work is explicitly debited; optional join fee in F002 is declared an assumption and varied including zero.
- **H18d audit**: conserved fixed-µJ resource/accounting boundaries; inherited F003 mechanics, independent motor-work derivation, negative controls, two-root raw replay and verified exact-source CI with Python3.11/3.12.

All numerical gates, sample count, grid, allocation seeds and tolerances are **candidate only** and must be frozen by a distinct design review. If no mutually beneficial region exists, that is a valid falsification within tested conditions, not permission to force a join.

## Minimal experimental world / limitations
- Same cell type, `mA=mB=1kg`, initially `xA=0, xB=L=0.1m`, equal velocity zero. No arbitrary contact or docking at a distance. Fixed F003 ideal massless link, collision and physical latch/connector not modeled.
- Initial step-0 local `request_attach` for each cell. Both true plus F003 guard causes attachment; false by either causes free mode. In this stage the investigator stipulates candidate requests; no F017 signal packet, sender role, learned agent, online bargaining or evolutionary fitness.
- Fixed scenario has one active motor and one passive cell. Swap identity and mirror sign as controls, since this is *not* a permanent cell function/role. A later experiment can include dual drive and dynamic approach but must not silently change F007 external-effective-force semantics or conflate it with F011 internal actuation.
- Per-cell energy from F002: `net_i = acquired_uj - motor_spent_uj - join_spent_uj`, also keep balances, system residual and aggregate net. A motor-off/no-resource control measures baselines. A transfer is NEVER implied by F003 mechanical linkage (F002 transfer is separately a purely bookkept operation).
- Resource patches are exogenous spatial fields with specified first-hit/terminal sampling rules. Narrow single endpoint patches are illustrative only and inadequate to infer robust ecology. Compare preregistered grids, patch widths, mirror configurations and motor-owner swaps.
- Only investigator-side analysis sees world truth, targets and cross-world net/counterfactual delta. A local policy input eventually may see own signals and own balance only; do not leak world truth, condition ID, hidden expected best choice, counterfactual outcomes, or the paired fork.

## Wolfram FEASIBILITY arithmetic (2026-10-22; **not SOMA measurements**)
For ideal semi-implicit 4×0.25s at +2N, identical 1kg cells, one motor, no drag: linked displacement 5/8m and *midpoint positive motor work* 1J; separate driver displacement 5/4m and work 2J, passive cell stays. Link cost 0.1J per cell; acquiring one spatial 3J patch:
- B-only near linked B final position: `Δ_A=+0.9J`, `Δ_B=+2.9J`.
- A-only near free A final position: `Δ_A=-2.1J`, `Δ_B=-0.1J`.

These illustrate a mathematically possible **sign crossover**, not spontaneous agreement or a general result. If actual code produces different observations, report the discrepancy; never adjust frozen gates afterward. In a free-mode comparison, ensure work is computed from the very same update rule, not `F * semi-implicit displacement` misidentified as midpoint work.

## Minimal API proposal (not implemented)
- `AttachmentIntent(cell_id, step_index, request_attach)`: strictly validated bool, step0 initial only.
- `resolve_attachment(intent_a, intent_b, initial_world)`: decision/validation only; neither edits positions to satisfy F003 nor includes any reward or learning.
- `PairedAttachmentOutcome`: caller/researcher record of same initial world fork: joined/unjoined physical traces, per-cell accounted sums, `delta_a_uj`, `delta_b_uj`, and `pareto_gain`. Counterfactual differences are NOT local agent observations.

## Evidence / falsifiers
1. YES/YES, YES/NO, NO/YES, NO/NO under exactly the same initial seed/world; invalid misaligned/equal-speed inputs explicitly rejected. On failed request, no link force/no implicit motor or electric coupling.
2. Full per-step mechanical and energy ledger oracle, resource event identification, unit and integerµJ checks, nonnegative budgets, zero conservation residual, signed physical direction mirror and source-bound deterministic replay.
3. Resource geometry and cost sweeps must show where link profits **both**, only one, neither, or cause losses; report sign and magnitude, not merely summed benefit. Control for drive-off, no-resource and arbitrary role/motor sign.
4. Read-only diagrams and data contracts updated in the same PR; exact-source CI and scientific scope decision required before any production API or main adoption.

## Not claimed
No spontaneous approach, self-chosen policy, multiagent learning, genuine connector, environmental survival competition, communication evolution, actual watts or hardware energy, 2D/3D, actual body schema. F017 fixed 1D signal receiver remains an independent validated component, not a ready-to-plug autonomous attach learner.


## 2026-10-22 independent feasibility critique: forced-action advantage ≠ voluntary private incentive (design amendment, STILL UNFROZEN)

**Critical theoretical counterexample**: In the B-resource Wolfram construction above, `Δ_A(join vs *forced solo motor*)=+0.9J`, but A's actual joined `net_A=-1.1J`. If `motor_off` is a legal alternative giving 0J, A is **strictly better off doing nothing**. Thus the `(+0.9,+2.9)J` fixed-action difference **does not demonstrate that both independently rational cells would voluntarily agree to attach**. Avoid presenting it as a natural aggregation incentive; the two worked cases are feasibility checks for *conditional physical payoffs only*. This correction is pre-first-run and changes no observed data.

Revised candidate estimand hierarchy (all researcher-only):
1. `Δ_i_fixed = net_i(join, fixed motor protocol) - net_i(separate, same motor protocol)` — causal mechanical/resource effect with action held fixed.
2. `Δ_i_outside = net_i(join, joint protocol) - max(net_i(separate,idle),net_i(separate,available_individual_actions))` — minimum necessary individual participation advantage versus viable *outside options*. Include no-motion baseline; never assume constant motor action must be executed.
3. Actual simultaneous individual choice/Nash stability or spontaneous spatial approach **requires separate agent-policy study** and cannot be concluded from either quantity alone.

**Revised H18b candidate gate**: Report both fixed-policy and outside-option deltas; a positive `Δ_fixed` together with negative `Δ_outside` must be classified **insufficient for voluntary incentive**. It is scientifically acceptable if no settings produce robustly positive outside-option deltas; that negative finding indicates missing resource/physical conditions, not a license to inject a direct 'join reward'. Future consent learning requires this landscape first.

## Design freeze decision (2026-10-22, before implementation)

**F018 v1 numeric/sampling protocol is frozen in [PLAN](../../experiments/F018/PLAN.md).** The earlier feasibility notes and candidate controls remain historical. No experiment ran before this freeze. The scope is deliberately narrower than the earlier wish list: F007 A-only external effective drive, both signed motor directions, finite 90-scenario terminal-patch grid, 630 world forks, two separately measured per-cell deltas, plus disk-independent audit. This does NOT include motor owner swapping or physical docking and does not demonstrate informed learned consent. The terminal resource harvest is explicitly exogenous and model-chosen.

Wolfram exact arithmetic independent PRECHECK (not code measurements): A drive +2N, 4 steps × 1/4s: joined A=5/8m B=29/40m; solo A=5/4m; joined motor positive work=1J; solo=2J. With *two separate* 3J terminal patches at both joined endpoints and 0.1J joining cost each, theory predicts joined own accounts A=+1.9J, B=+2.9J; restricted solo/idle motor choices {-2,0,+2} give max zero individually for radius=0.01m, hence both positive outside deltas. With a B-only patch, A own joined net=-1.1J despite +0.9J fixed-action advantage. The dual patch environment is engineered for testing capability and cannot establish broad natural incentive.
