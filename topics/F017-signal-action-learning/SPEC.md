---
id: F017
title: Unknown binary signal to embodied action — candidate preregistration
kind: preregistration
status: candidate_unfrozen_unexecuted
updated: 2026-10-21
issue: 57
depends_on: [F002, F007, F016]
---
# F017 — 経験による未知bit→身体行動の価値学習（設計候補）

**DESIGN DRAFT ONLY / UNFROZEN / ZERO F017 EXPERIMENTS / NOT ADOPTED.** Base main: `63b36ebc04b6e0d765bff923f6707f6c92b85a96`. [Issue #57](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/57) / [PLAN](../../experiments/F017/PLAN.md) / [findings](../../findings/F017-validation.md) / [research programme #51](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/51).

## Single scientific question
Can A **learn a previously unknown association** between B-origin binary symbols {0,1} and A's own physical actions {-2,+2} N **only from A's received symbol, chosen action, and subsequent A-owned acquired-energy and motor-cost feedback**, then recover after an **unannounced reversal**? Test performance on data unseen during learning.

**Scope:** Receiver-side, action-conditional value acquisition. NOT co-invention of a protocol, sender learning, spontaneous bit production, emergence of joint bodies, sensory optics, real communication, actual electrical generation, topology identification, or general understanding of symbols. A/B roles remain explicitly researcher-assigned.

## Hard physical/model constraints (inherit F016)
- Unmodified F007 ideal 1D mechanically linked A/B, each 1 kg; A x=0, B x=0.1m, both v=0, link length 0.1m, dt=0.25s, 4 intervals/episode, no drag. A receives one initial B-origin payload and commands either -2 or +2 N external effective motor force. F007 actual positive work = 1,000,000 µJ, xA endpoint ±0.625m.
- Resource at ±0.625m, 3,000,000 µJ acquired by A only upon terminal hit at |xA-target| ≤ 1e-12m. B has local direction sensing via ideal **researcher-assigned mask**. B transmission charge = 50,000 µJ, imposed on B by the independent F002 sidecar. No action on bit receipt alone earns reward.
- Fresh physical state + A/B battery balances each episode. **Only A's learned policy state persists**, and only within the explicitly controlled stream. A is never shown the resource location, encoding/reversal flag, trial/seed, body topology, future outcome, B's energy ledger or researcher net score.
- Mapping intervention on the **researcher/B side**: symbol=0/1 represents local left/right under one of two uniformly included unknown bijections (identity and inverted). It is not a decoded `resource_right` boolean at the A policy boundary. No `soma.f016.choose_force` inside learning.
- Receiver input `RawPeerSymbol | None` includes validated source=B, step=0, time=0 and an **opaque category** `symbol in {0,1}`; message framing/time are not claimed to cost a single physical bit. `None` is absence, never symbol 0.
- Receiver action API `observe(packet_or_none) -> {-2.0,+2.0}`; `learn(action, A_local_acquired_uj, A_local_motor_spent_uj)` separately accepts only own **verified completed** feedback, and never researcher `reached` or full `net_uj`. World runner alone computes `net_uj = acquired_uj - motor_spent_uj - B_sender_spent_uj`.
- Proposed minimal learner: two-context/two-action exponentially recency-weighted bandit (one context for `None` control), Q(s,a)=0 at start, independent A-policy pseudo-random stream, ε-greedy ε=1/8 with randomized ties, update observed Q(s,a) <- Q(s,a)+1/4·(rA-Q(s,a)), `rA=(A_acquired_uj-A_motor_spent_uj)/1e6`. No hidden world labels, episode indices or encoding identifiers in policy input. Test-time learning disabled externally by withholding feedback calls; policy does not receive a test-mode flag. Reversal adaptation starts from the SAME learned Q without reset.
- Randomness must be reproducible from investigator-side manifest with mutually independent world-order and learner-exploration streams. The A policy must not receive the resource-order generator or world seed/condition metadata. Specify deterministic platform-independent seed derivation and schedule hashing BEFORE first F017 simulation.

## Proposed preregistered allocation — **review / freeze required before implementation**
Eight paired independent world-order seeds × both symbol encodings. Within each pairing, target signs balanced independently in each phase, order pseudorandomized in a researcher-only manifest:
1. 64 discovery/training episodes (32 per direction), feedback/update allowed.
2. 32 unseen holdout episodes (16 per direction), feedback withheld, Q held fixed.
3. **Unannounced mapping reversal**; 16 immediate frozen pre-adaptation probes (8 per direction) for a genuine change-point baseline.
4. 64 continued-learning episodes (32 per direction), Q NOT reset.
5. 32 final reversal holdout episodes (16 per direction), feedback withheld.
Total `8 × 2 × (64+32+16+64+32) = 3328` episodes per treatment, with fresh physics each episode. "Unseen" refers to episode allocations; the 1D task and physics remain explicitly known and fixed to the investigator.

Treatments (paired target sequences): (I) informative raw B symbol + learning, (N) no bit + identical learner on None context, (K) constant B symbol + learning, (S) balanced scrambled B symbol independent of target + learning, (L) informative raw bit + **frozen Q/no learning**, (F) informative bit + feedback withheld during training. Research-only perfect-informed F016 decoder is an upper bound **outside the learning policy**, not evidence of learning. All sent-symbol arms charge the same B 50,000µJ; no-bit has zero message fee.

## Explicit hypotheses, disconfirmers, primary gates (candidate numerical choices to audit)
- **H17a learnable use:** On initial unseen holdout, I pooled hit rate ≥0.70 and at least 0.20 above each of N/K/S/L/F; paired cluster-bootstrap (16 seed×encoding blocks) 95% interval for net I-minus-each-control strictly above 0 J. Do NOT accept merely beating F016's +0.50J no-bit mean.
- **H17b label symmetry:** Both initial encodings separately achieve hit rate ≥0.65; swapping 0/1 reverses learned action preference. A fixed left/right hardcode or episode-clock cue must fail.
- **H17c experience causality:** Removing feedback, resetting Q before each episode, freezing policy, shuffling sender symbol, or replacing with constant cannot recreate I's holdout improvement. Preserve negative counterexamples.
- **H17d adaptation not reset:** Immediately after secret reversal, fixed-policy probe measures the mismatch, then final reversal holdout hit rate ≥0.70 and improves by ≥0.20 relative to the immediate probe. If no recovery, mark H17d unsupported independently of H17a.
- **H17e integrity:** Every saved F007 row/positive motor expense, F002 A/B ledger, packet validity, true held-out schedule, forbidden-input boundary and researcher-only outcome independently audited; source+artifact hashes; malicious data recomputed-hash tamper rejection; byte-identical two-root replay; Python3.11+3.12 regression/CI. Any violation blocks adoption, regardless of apparent hit rate.
- Do not change seed counts, thresholds, method or phase sizes after first run; if reviewer changes them **before** freeze, record in design review history. Independent checker must recompute from saved F007 and F002 traces, not trust producer's "reached" or "net".

## Wolfram-only feasibility arithmetic, NOT experiment results
With correct-action probability p, ideal fixed-action cost 1 J and B fee .05 J, mean net communication outcome is J(p) = 3p - 1.05 J. No-bit, balanced two-sided target baseline = 0.50 J. Thus J(p)>0.50 iff p>31/60 ≈0.5167 — **not a sufficient test of learning**. Correct oracle upper bound 1.95 J. This arithmetic has no sampled F017 training, success rate, reversal recovery or CI attached.

## Governance / immutable evidence
One design-only Draft PR must contain SPEC, PLAN, UNEXECUTED findings, architecture figure, data contracts, README/AGENTS index, with zero changes to F001–F016. Audit and **freeze/merge design first**. Separately implement `soma/f017.py`, producer, saved-data independent auditor and tests on a later implementation Draft PR; no scientific adoption or main merge without recorded actual source-HEAD CI, artifact checks and researcher judgment. Negative data and dated historical proposals append-only.
