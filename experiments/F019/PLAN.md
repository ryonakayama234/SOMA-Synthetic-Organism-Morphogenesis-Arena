---
id: EXP-F019
title: 身体構造による資源アクセス差・実験事前登録ドラフト
kind: experimental_plan
status: FROZEN_PREOBS_UNEXECUTED
updated: 2026-10-22
issue: 64
---

# F019 experiment plan — FROZEN v1 / UNEXECUTED

[Question and falsifiers](../../topics/F019-resource-ecology/SPEC.md) / [Issue #64](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/64) / [findings](../../findings/F019-validation.md).

## Scientific aim and limitation
Measure **how connectivity changes who encounters and owns finite external resources, when encounters happen, and how each cell's net energy changes** across matched counterfactual worlds. Remove F018's terminal-location tuning as a confound; do not center the experimental validity test on finding mutual benefit. F018's externally effective A-only motor and researcher-chosen step-0 consent remain; this study measures morphology-conditioned ecological access, **not learned action, repeated reconfiguration, or spontaneous body formation**.

## F019 v1 PRE-OBSERVATION FREEZE — 2026-10-22 (no F019 world has run)

**Design authority:** this section replaces the earlier *candidate* ambiguities only. Changes after the first run require a separate new preregistration/version and must not relabel v1 outcomes. Independent *external* design review is still a separate gate for scientific adoption; deterministic implementation validation is not external peer review.

### Fixed main-sample universe and geometry
- Enumerate exact independent `base_seed` integers `0..31`, motor signs `(-1,+1)`, joint fees `(0,100000) µJ per cell`, patch counts `(2,5)`, half-widths/radii `(0.02,0.06) m`; lexicographic nesting `seed,sign,fee,count,radius`. Exactly `32×2×2×2×2=512` scenarios; `4` fixed-arm worlds `YY,YN,NY,NN` plus three `NN` outside worlds motor `(-2,0,+2) N`: exactly `3584` worlds and `17920` saved F007 states. Do not filter seeds by observed outcomes.
- `field_id=sXX-nN-rRRR` uses no motor sign or fee; all scenarios with same seed/count/radius clone the same pristine field. Patch IDs `P0..P{N-1}`, amount exactly `1000000 µJ` each; no regeneration. Spatial centers are integer multiples of `0.025 m` on the inclusive lattice `[-1.50,+1.50]m` (121 points).
- Per `seed`, patch index `i` and draw counter `j=0,1,...`, compute SHA256 of UTF-8 ASCII `F019-field-v1|seed=<seed>|patch=<i>|draw=<j>`; take the first eight digest bytes as unsigned 64-bit **big-endian** integer and choose `center = (value % 121 - 60) * 0.025`. Reject/resample candidate centers only if `abs(center-0.0) <= radius` or `abs(center-0.1) <= radius` (initial A/B overlap); retained patch samples may overlap each other or have identical centers (different patch IDs remain distinct). Cap attempts at 10,000, fail otherwise. No access to trajectories, candidate link endpoints, other worlds' scores or F018 DUAL_LINK targets. Width radius is a prescribed sweep, not learned from geometry.
- Constant physical initial state: A `x=0,v=0,m=1kg`, B `x=.1,v=0,m=1kg`; ideal `length=.1m`, `dt=.25s`, `duration=1s`, zero drag/external forces, fixed A motor `u=2*sign N`. A-only motor may be applied when affordable, F005 positive-work rounded up to whole µJ, pre-fee initial balance each `10000000µJ`, capacity each `20000000µJ`. This fixed supply always covers the motor in all 4 steps even without harvest; **acquired patches have no feedback on same-run motor decisions** in the frozen test and are posted at step end.

### Exact event ordering and counterfactuals
- F007 state points are motion truth. Each segment `x0→x1` uses affine interpolation `x(f)=x0+f*(x1-x0), f∈[0,1]` **only to timestamp resource first entry**. A closed patch interval `[center-radius,center+radius]` is hit when segment intersects it; if a cell starts inside it, entry fraction `0`; if segment crosses from left, `f=(left-x0)/(x1-x0)`; from right, `f=(right-x0)/(x1-x0)`. Strict real arithmetic is the reference, float implementation tolerance `abs<=1e-12` for event fraction/timestamp comparisons. Primary sampler excludes t=0 occupants; boundary/t0/stationary are synthetic **calibration-only** unit tests excluded from 512 scenes.
- Gather all cell×patch candidate first entries for a step, order by `(step_index, entry_fraction, patch_id, cell_id)` with literal `A < B` at exact ties. Only the first claimant of each patch wins and consumes its *full* supply, `remaining_uj=0`; later encounters have no acquisition and no repeated claim. Each field is cloned pristine independently for each of the seven causal forks. Concurrent different patch claims are independent and ordered by patch ID for reproducible ledger sequence.
- Event chronology: at step0 fees, for every later step first the F007 accepted A motor debit, **then** the harvested resource acquisitions in global path-entry order with actual `entry_time_s=(step-1+f)*.25` preserved in `harvests.jsonl`; financial posting occurs at the completed discrete step. Resource is an external µJ abstraction, not electrical energy generated by link contact; a patch never transfers A energy to B.
- Primary paired `YY` vs `NN` summaries per patch list `winner ∈ {A,B,null}` and `entry_time_s|null` for each side, `winner_switch` flag; time difference is `null` unless both hit. Individual `net_i=acquired_i-motor_spent_i-join_spent_i`, `delta_fixed_i=net_i(YY,u)-net_i(NN,u)`, `delta_outside_i=net_i(YY,u)-max_{v∈{-2,0,+2}}net_i(NN,v)`. Different outside maximizing actions are allowed by individual and are **off-world analysis**, not jointly realizable equilibria. The jointly-positive fraction is secondary, never an adoption gate.
- Technical acceptance: every expected sample/world/step exists exactly once; deterministic hash-to-grid world gen; reconstructed physical states and motor/fee accounting; closed-interval hit/tie/depletion and unique ownership; rederived same-field fork summaries; complete source+artifact SHA integrity; independent saved-data verifier without imports of `soma.f019`, `soma.f007` or producer; two clean-root byte replay; rehashed adversarial edits rejected; inherited regression tests and Python3.11/3.12. Positive effect size, claimant switch count, or bilateral payoff sign is **not** a technical gate.

### Reference boundary cases, not additional main samples
- Segment `0→.3` and patch `[.19,.21]` crosses before endpoint; reverse `.3→0`; stationary point inside/outside, exact edge contact, same-time A/B collision (A wins), revisit, patch overlap, zero motor/none, refused consent and fee-only control. Changes in these controls require separately documented amendments before scientific use.

## Historical candidate world (superseded where v1 freeze specifies exact values)
- Existing F018 mechanics: two 1kg cells at 0 and 0.1m, rigid 0.1m link only when initial eligible and both intentions YES; dt=0.25s for four steps; no physical docking/collision, zero drag, no unrelated forces, A-only signed ±2N externally effective motor, valid F002 upfront fee and F005 work accounting.
- Candidate path patches: interval center ± radius; no resource generated by attachment; patch at most one claimant and permanently depleted on first entry. Initial overlap handled explicitly at t=0 with collision-order priority; either exclude initial overlaps in primary generator or retain as a separate predeclared control. Prevent silent inconsistent treatment across linked/unlinked forks.
- During each F007 step reconstruct linear x(t) between the logged step endpoints, compute first interval intersection time for each cell and unclaimed patch, sort globally by (step, fraction_of_step, patch_id, cell_id), award once and record initial/final supply. This interpolation is a measurement convention, not actual force/velocity integration.
- Each arm starts from the identical field: YY, YN, NY, NN with fixed signed motor plus NN at each of -2/0/+2N: seven saved worlds per environment.
- Use deterministic SHA256-based integer-grid draws for center and width from public predeclared seed list and patch index, not a trajectory-aware/tuned distribution. A design reviewer must freeze allowed grid/domain, patch count/spacing, cell initial-overlap rule, amount, policy independence and hash-to-uniform method. Partition primary samples from fixed F018 reference and deliberately crafted boundary controls before running. Prevent cherry-picked scenes from entering main estimates.
- **Historical candidate size (now frozen above):** 32 independent environment seeds × 2 force signs × 2 fee conditions × 2 patch densities × 2 width bands = 512 paired scenarios, each 7 worlds = 3,584 worlds. Counts and numeric grids may change **only at design-review freeze, before first observed run**. Seeds, coordinate grid, reference case partition, tolerances and hypothesis gates must be committed in the frozen PLAN; no after-observation tuning.

## Hypotheses / controls / evaluation
| ID | Proposed falsification gate | Evidence before claim |
|---|---|---|
| H19a | Resource obtained iff geometric first-entry and positive undepleted supply; ties deterministic; no repeated claim | Saved positions, entry fraction/time and depletion ledger recomputed *without importing producer* |
| H19b | Under trajectory-blind fields, same-field forks reveal per-patch winner (A/B/unclaimed), earliest encounter and owner changes, along with separate A/B payoff distributions; asymmetry/null effects retained | Generator source/hash, seed list, paired per-patch winner tables, independently reconstructed event order, per-seed deltas and F018 tuned-vs-untuned separation |
| H19c | Failed consent yields no link/no fee; no-resource and drive-off controls behave as reference F018/F007; mirrored force symmetry | Consent gate tests; no-resource and mirror trajectories; physical work/source equality |
| H19d | Source-bound raw data withstand full counterfactual audit and reject adversarial rehashed edits | 3.11/3.12 inherited+F019 CI, independent from-disk verifier, two-root byte replay, mutated-then-rehashed negatives |

**Main estimands (no expectation of positive sign):** patch-level `winner ∈ {A,B,unclaimed}` in each world, same-patch **YY-vs-NN winner switches** (counting transitions to/from unclaimed), first-entry time where observed and paired encounter-status changes, each cell's acquired energy/net [µJ], `delta_fixed_{A,B}` and `delta_outside_{A,B}` [µJ], claimed/remaining resource, motor/join costs, resource-induced inequity and technical residuals. **Secondary exploratory estimand:** mutually positive outside-option fraction, never a code-adoption threshold. A time difference is reported only when both encounters exist; no-encounter is recorded explicitly rather than imputed. Conditions swept within the same base seed are not independent samples; report seed-block variability and exact counts, with uncertainty intervals only if their sampling interpretation is justified.

**Interpretation boundary:** a connectivity-dependent change in claimant identity is a causal effect of fixed morphology **under these paired-world assumptions**, not proof of cooperation. A Pareto-positive region, if any, is only a conditional physical/economic opportunity in an artificial 1D world, **not** voluntary agreement. Asymmetric, neutral, negative, and zero mutual-benefit outcomes all remain valid scientific data; none triggers post-hoc generator redesign.

## Specific boundary and attack tests
1. Both step endpoints outside a narrow patch but linear segment crosses it: the patch is claimed exactly once. Reverse travel and stationary initial occupancy tests.
2. Two cells enter the same patch at different fractions of a step, and exactly simultaneously: earliest wins, tie rule deterministic, resource exhausted.
3. Double visitation, zero motor, no patches, rejected single-sided intent, fee too costly or integer overflow, inconsistent link eligibility.
4. Adversarial worlds replace first entry, patch ID/winner, claim event order, resource amount, per-cell ledger, signed outside best, nullable physical diagnostics, manifest rehash; independent reader **must reject**, not merely verify hashes.
5. Same source/seed produces byte-identical evidence in two clean roots; source SHA/dirty marker binds results. F018 tests/CI remain unchanged.

## Pipeline and outputs (proposed; not presently implemented)
```text
frozen generator/seeds --> ResourceField(v1) + paired intents/motor
                         --> F018 gate --> F007 1D states
                         --> path-first-entry resolver --> F002 acquire/spend
                         --> raw worlds/states/harvests/ledgers/summary
                         --> independent from-disk oracle + falsification
                         --> source/CI/artifact verification + append-only findings
```

Proposed output schemas and visibility in [DATA_CONTRACTS](../../docs/DATA_CONTRACTS.md). All charts must read the recorded evidence and label simulated values; the independent oracle cannot import `soma.f019` or the physical producer. Future cells never receive off-world pair comparisons.

## Wolfram exact precheck — NOT F019 world evidence
For force +2N, 1kg A/B, 4×0.25s from rest, ideal link common A positions are [0,1/16,3/16,3/8,5/8] m and B positions add 1/10m; unlinked A positions are [0,1/8,3/8,3/4,5/4] m. Midpoint mechanical motor work is 1J linked vs 2J unlinked; for F019, crossing sequence is **not** inferred from terminal location alone. This checks inherited F007 analytical geometry, not resource ecology outcomes.

## Research operations
Pre-run design PR freeze (separate review), then implementation PR with code/tests + architecture diagram + data contract + README + *append-only* findings and raw CI links. Claim limited API adoption only after independent review of exact-source evidence, negative controls, 3.11/3.12 tests and post-main CI. See [process](../../docs/RESEARCH_PROCESS.md).
