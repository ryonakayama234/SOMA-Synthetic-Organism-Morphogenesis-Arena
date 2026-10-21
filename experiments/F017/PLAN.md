---
id: F017-PLAN
kind: experiment_plan
status: frozen_before_first_world_run
updated: 2026-10-21
issue: 57
---
# F017 — 未知シンボル行動学習・秘密反転の反事実実験

**PROPOSED; NOT FROZEN; UNEXECUTED.** Canonical candidate physics, groups, counts, and gates: [SPEC](../../topics/F017-signal-action-learning/SPEC.md). Do not treat Wolfram arithmetic or the F016 inherited trace as new F017 results.

## Researcher schedule / leaks
- Independently precompute and save target direction permutations, 8 world-order seeds, 2 opaque B encodings, learner exploration sources, training/holdout boundaries; sign-balanced per phase; share identical ordered targets between paired treatments.
- Start all A policies with identical empty Q. An independent random exploration stream does not expose target sequence; do not pass scenario/trial/seed/phase/encoding/true target via A input. Verify allowed keys against a deny-list, not by developer intent only.
- Episode `B sensor -> intervention symbol/none -> verified framed packet -> A observe -> F007 4 steps -> F002 expense / A acquisition -> A-local feedback (if learning phase) -> separate truth auditor`. The A policy must not read F007 global states or F002 B ledger.
- For S use a balanced randomized bit sequence independent of target and prechecked for accidental correlation; no post-hoc reshuffle. Policy should be evaluated both with unseen targets and under B-symbol/feedback ablations.
- Phase ordering: pre-switch train64 → unseen holdout32 → blind-reverse freeze-probe16 → continued-adapt64 → reversed holdout32. No learner reset across phases (except separately labeled negative-reset control). Each phase is independently sign balanced.
- Apply proper sender charge exactly once in every delivered-message episode; when packet is absent/fails validation, do not silently reinterpret it as `0`; record and assess explicit fallback.

## Prospective observables
A-local `symbol, action_n, acquired_uj, motor_spent_uj`; hidden policy `Q before/after, random choice flag` (research audit only; don't grant access to environment truth); F007 position/velocity/attachment and per-step spend; F002 balances/events; B sender charge; investigator-only target, mapping id, reversed state, episode/seed, `reached`, `net_uj`.
Report per treatment and phase: reached/total, mean/median net J, A-only reward, sender fee, per-encoding rates, reversal probe-vs-final change, paired net differences and cluster-bootstrap 95% intervals. Give full sample counts and negative outcomes, not just success plots.

## Falsification / exact source tests
- Randomly replace a saved raw packet with a different valid bit, alter energy gain, time, source, learning-state update, target schedule, or world position and **recompute manifest file hashes**; independent truth oracle must reject every forged narrative.
- Verify mirrored final sign, exact 1J F007 motor spend and F002 residual=0 for every episode; ensure F016 known oracle reproduces preregistered theoretical benchmark only as a *separate control*.
- Prove against unit guard: no true `target_x_m`, `resource_right`, `encoding`, `reversed`, `trial_id`, `seed`, `reached`, `net_uj`, body/truth state or B-side spent field crosses the A controller call.
- Independent offline auditor consumes only saved raw traces and preregistered manifest; recreate local learning updates from A-visible feedback and action choices, recalculate all group/phase aggregates, hashes and false-science negatives.
- Two isolated output roots with identical input must yield byte-equal manifests, logs and experiment summaries. Run inherited tests, optimizations and F017 in Python3.11/3.12 on the same source commit. Any unstable or undocumented randomness blocks adoption.

## Verdict protocol
Each H17a–e receives separately SUPPORTED / CONTRADICTED / INCONCLUSIVE / UNEXECUTED. Interpret sender learning, group-formation, topology and new "meaning" only as **NOT TESTED**. Decide experiment revision vs limited adopted `f017.learning.v1` only after exact reviewed evidence, preserving failure logs. Reviewer must first freeze SPEC+PLAN in a *separate* design merge, before writing the executable F017 experiment.


## Additional causal intervention arm — offline policy forks, NOT extra physical episodes
At both unseen holdout checkpoints save A-policy snapshots (Q and exploration state) independently of any investigator truth. Clone each snapshot twice with matched independent RNG draws; replace only the validated message's *opaque symbol* 0↔1. Take 256 actions for each do-symbol condition WITHOUT executing F007 physics or learning. Record action distributions, signed causal response D, sampling method and source hashes. Also fork a no-feedback/frozen-Q policy. Neither probe branch can affect the primary training stream. Distinguish (a) a message actually influencing the A action policy from (b) task outcome advantage. This follows the positive-listening distinction in [Lowe et al. 2019](https://ifaamas.org/Proceedings/aamas2019/pdfs/p693.pdf). See proposed H17f threshold in SPEC. **No probe has been run.**


## 2026-10-22 preregistration freeze
**FROZEN PRE-EXECUTION, F017 SIMULATION UNEXECUTED AT THIS COMMIT.**
The dated final [SPEC](../../topics/F017-signal-action-learning/SPEC.md) appendix defines the exact deterministic SHA256-based world and scramble phase-balanced permutations, 8 seeds × 2 encodings, 6 primary arms plus the secondary R every-episode-reset/no-memory ablation: 23,296 F007 episodes in total. All groups run fresh physics in each episode; only the receiver's Q and RNG persist in arms I,N,K,S. H17a–f gates are frozen. This design is subject to independent post-run audit; negative outcomes will be kept, never used to change this frozen plan.
