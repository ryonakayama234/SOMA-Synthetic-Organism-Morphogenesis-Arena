---
id: F019
title: 経路資源場における身体構造・資源アクセス・個体別収支
kind: research_preregistration_draft
status: FROZEN_PREREGISTRATION_UNEXECUTED
updated: 2026-10-22
issue: 64
depends_on: [F001, F002, F003, F005, F007, F018]
related: [PROJECT, F018, RESEARCH_PROCESS]
---

# F019: 身体構造が資源へのアクセスと個体別収支をどう変えるか

**SELECTED RESEARCH QUESTION / F019 v1 PLAN FROZEN BEFORE OBSERVATION / NO F019 CODE OR OBSERVATIONS YET / NOT ADOPTED.**
[Issue #64](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/64) / [PLAN](../../experiments/F019/PLAN.md) / [UNEXECUTED findings](../../findings/F019-validation.md) / [charter](../../docs/PROJECT.md).

## One question
In the existing F018 two contact-ready 1D cells, **how does the investigator-fixed connected versus unconnected body state causally change each cell's encounter time, resource claimant/ownership, finite-resource depletion, and individual net energy** under the *same trajectory-blind, exogenous resource field* harvested **along travel**?

The primary contribution is a causally auditable **environment/harvest instrument**, not a search for universally advantageous attachment. Linked/solo ownership switches, unequal benefits, mutual gains, mutual losses, and no difference are all legitimate observations. A jointly positive individual outside-option region is an **exploratory substantive subquestion**, not a technical acceptance gate. F019 does not implement learning, dynamic/repeated attachment, or a spontaneously assembled body.

## Why F019 now
F018 v1 (limited adopted) measured 630 worlds across 90 fixed factorial scenes. Both individuals had positive `delta_outside` in 18/90, and all 18 were constructed DUAL_LINK terminal endpoint patches. There is no test of unplanned spatial resources or sustained viability. Adding a learner now could memorize a designer-controlled label and be mislabeled emergence. First remove that terminal-reward confound and measure what connectivity actually changes about access, claimant identity, and individual accounting before asking an agent to choose connectivity.

## H19 hypotheses (frozen as defined by v1 PLAN; **no** observations yet)
- **H19a — environmental causality:** For each declared finite patch, an encounter is defined by the earliest within-step path-entry event, with one winner, irreversible depletion, no duplicate claims and auditable tie resolution. A resource event has a geometric cause, not a link-conditioned bonus.
- **H19b — morphology-conditioned access:** In preregistered trajectory-blind resource fields, paired connected/unconnected forks permit estimating each patch's first claimant (including unclaimed), entry timing where observed, changes in resource ownership, and the distribution of both cells' `delta_fixed` / restricted `delta_outside`. Positive, negative, asymmetric, and null effects must all be retained; mutual Pareto benefit is secondary and not a software gate.
- **H19c — negative controls:** no-resource, drive-off, nonconsensual intents, zero/large join fee, spatial reflections and manipulated resource timing yield interpretable signed outcomes, with F018 reference dynamics unchanged.
- **H19d — evidence integrity:** independent saved-file recalculation detects changes to entry time/order, winner, depletion, motor spend, position, counterfactual summary, or per-cell ledger even after all file hashes are recalculated. Replay is byte-identical across clean roots and source-identified Python versions.

## One-module scope
- Reuse F018 `AttachmentIntent` + `resolve_attachment`, F007/F001 1D ideal link dynamics, F005 positive-work debit and F002 integer-µJ ledgers. No modifications to adopted F001–F018 API. Strictly eligible initial separation/velocity; A alone has the existing F007 externally effective motor and B remains passive. No energy sharing follows from attachment.
- Add an **investigator-only** `ResourceField` and deterministic trajectory sweep. Patches are fixed before the arm is selected, independently of forecast endpoints. Every patch has spatial interval `[center-radius, center+radius]`, a nonnegative integer capacity in µJ, and a resource ID. One first-contact winner consumes its full amount, then its remaining supply is zero. No spontaneous regeneration in v1.
- Discrete F007 positions are the motion truth. Within each step, treat the path as a *linear interpolant of the two saved endpoints* solely for event ordering; this is NOT an exact physical 1D continuous-time trajectory or collision solver. Explicitly define initial occupancy, boundary contact, zero travel, coincident arrival and tie-break in the frozen PLAN. No hidden teleport, double capture, or missed pass-through when endpoints are outside the patch.
- Each same-field counterfactual world forks only the fixed researcher-supplied YY/YN/NY/NN attachment requests and declared motor menu, and begins with an undepleted identical patch field. This is a *causal fork*, not an interaction between parallel universes.
- Main resource worlds are generated from preregistered **trajectory-blind integer-lattice** draws and fixed hashes/seed lists; no generator is permitted to use joined/solo terminal positions, oracle reward, `scenario_id` winner labels, F018 DUAL_LINK targets, or prior observed outcomes. Fixed hand-designed patches are calibrations only, excluded from the primary ecological estimate. Report actual position histograms and separation from both policy endpoints to expose accidental targeting.
- Never give a future cell learner the field generator seed, other cell balance, complete resource field, paired outcomes, outside optimal action, oracle `delta`, or the physical/ledger ground truth. Future local sensors will require a separate design.

## Counterfactual meaning
`net_i = acquired_i_uj - motor_spent_i_uj - join_spent_i_uj`. For each common resource field and fixed motor command,
`delta_fixed_i = net_i(YY, u_fixed) - net_i(NN,u_fixed)`.
For an investigator-only benchmark with restricted unjoined A motor menu `U={-2,0,+2} N`,
`delta_outside_i = net_i(YY,u_fixed) - max_{u in U} net_i(NN,u)`.
The two individual maxima can refer to different hypothetical worlds and are NOT a jointly executable noncooperative equilibrium or locally learnable values.

Report: per-patch winner (`A`, `B`, `unclaimed`) and first entry, changes in winner/entry across the same-field connected versus unconnected forks, each cell's acquired resource and signed deltas, combined net, unique claimed patches, waste/remaining, resource concentration/inequity, mutually positive conditions (secondary), and seed-stratified counts. Entry-time comparisons are conditional on a well-defined encounter in both worlds; absent encounters are not assigned fictional times. Mechanically induced A-to-B mobility is not automatically B-owned motor agency or organismality.

## Falsifiers and boundaries
- A linked positive in hand-constructed calibration scenes **alone** does not support ecological generalization; a region discovered only after changing environment seeds does not support a preregistered result. Ownership switches or null effects must not be converted post hoc into proof of cooperation.
- Claims without path entry, claims after depletion, more than one claimant, hidden reward for consenting, shadow world differing in initial resources, cross-cell accounting leakage, or nonreproducible saved events fail H19a/d.
- A positive aggregate with negative individual A or B fails a bilateral incentive claim. A non-positive region with intact controls and oracle is **accepted negative scientific evidence**.
- F019 does **not** establish 2D bodies, physical docking/contact, actual ground/drive reaction, B motor, real electrical efficiency, resource perception, informed consent, population selection, learning, evolution, or spontaneous morphology.

## Searchable future direction (NOT F019 scope)
[Temporal morphology, repeated cooperation, resource transport and temporary tools — research note](../../docs/research-notes/2026-10-22-temporary-morphology-and-resource-access.md). This separate unfrozen ideation records possibilities without preassigning cell roles or changing F019's frozen-to-be mechanics. In particular F019 has **only a step-0 attachment decision and no mid-run detach/rejoin**.

## V1 preregistration boundary
The exact source-independent SHA256 sampling grid, 512 scenarios/3584 worlds, resource claim/simultaneity semantics, initial-balance motor isolation, and outcome estimands are frozen in [v1 PLAN](../../experiments/F019/PLAN.md). Candidate alternatives below the freeze section are historical design considerations only. Do not run v1 on changed seeds or patch grids under the same label. Independent external review remains necessary for scientific adoption.

## Next work — gated, not silently preimplemented
1. Independent design review and **freeze before simulation**: physical/event edge semantics, condition count/seeds, source and tolerances, exact gates and primary vs calibration partition.
2. Separate implementation PR with `soma/f019.py`, full tests, saved-world producer, *independent* verifier, rehashed adversarial negatives and CI; keep `soma/f018.py` untouched.
3. Append verified SHA-scoped results and any negative findings to `findings/F019-validation.md`; adopt only the bounded environmental measurement API if frozen technical gates pass. A later F020 may provide real per-cell dual motors; local mutually learned attachment is another distinct experiment.

## 2026-10-23 post-experiment status addendum (frozen hypothesis unchanged)

Earlier front-matter and "UNEXECUTED / NO CODE" passages above remain a **historical pre-observation design snapshot**. F019 was subsequently executed and audited at `6186077e`: 512 scenarios, 3584 forked worlds, 580/1792 resource-patch claimant/unclaimed-status changes (not independent observations), bilateral `pareto_fixed=0/512` and `pareto_outside=0/512`. An **AI-internal critical audit**, not external human/third-party peer review, conditionally authorizes **limited adoption only of the deterministic finite-patch/first-entry/depletion and per-cell ledger measurement API** if the documentation-and-extra-control-test inclusive exact source and post-main CI pass. The corresponding [append-only decision](../../findings/F019-validation.md) explicitly rejects broader claims of emergent joining, learned cooperation or real ecology. Neither this update nor any status label changes the preregistered PLAN or sample selection.
