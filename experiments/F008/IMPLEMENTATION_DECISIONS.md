# F008 candidate implementation / audit decision log (2026-10-18)

This audit was opened **after** an F008 implementation candidate already existed on the branch, and before this audit's CI evidence was evaluated. The pre-observation scientific predictions are in design PR #23, Issue #22 and experiments/F008/PLAN.md (dated 2026-10-17). Do **not** misrepresent this document as a pre-implementation preregistration.

- The frozen candidate uses the fixed 1e-12 m/s² residual threshold for deterministic A–E rational controls, no sensor noise. This tolerance is a numerical conformance parameter, not an experimentally estimated detection threshold.
- Agent-only fields are A's timestamp, own pre/post velocity, own command, own applied motor feedback and own battery. A's calibrated known self-mass is 1 kg. A does not know the external force, attached state or B state.
- B and D are expected to have equal A-only *entire traces*, not merely their first acceleration. D is **a negative control disproving unique link inference**, not a false positive to suppress.
- A motor-applied value of zero produces status `not_excited`, null predicted acceleration and null residual, even if external forces cause motion.
- At t=0.5s in C the F007 event flag is already detached, but the interval ending at that instant used the **attached** dynamics. Observe acceleration transition on step 3.
- F007 model, F007 saved oracle and source evidence are reused unchanged.
- Distinguish frozen model predictions, actual code/CI observations, and adoption/independent third-party review.
- Existing source-hash provenance in the candidate covered F007, but **did not cover new F008 source, verifier, test and workflow**; audit correction explicitly adds externally checkable F008 dependency hashes before evidence claim.
- Observer projection consumes world rows inside a researcher adapter; detector `detect(LocalObservation)` has no topology input. This is a whitelist/software information boundary, **not a proof of isolation against arbitrary malicious Python code**.
- No changes to preregistered physical hypotheses, no main merge and no scientific acceptance in this audit.
