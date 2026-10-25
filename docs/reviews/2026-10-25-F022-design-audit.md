---
id: F022-REVIEW-2026-10-25
kind: internal_critical_review
status: PREOBSERVATION_DESIGN_ONLY
updated: 2026-10-25
related: [F022, ISSUE-77]
keywords: [collision, impact, review, tunneling, restitution, pre-observation]
---

# F022.v1 internal critical design review (NOT external peer review)

**Internal adversarial review + independent Wolfram theoretical calculations only. No F022 primary outcomes or software tests.** [Frozen protocol](../../experiments/F022/FROZEN_V1.md).

| Risk / severity | Why dangerous | Frozen solution and falsifier |
|---|---|---|
| Missed contact / HIGH | 0.25s frame endpoints can miss rapid collisions | Continuous analytical TOI; C13 impact .095s |
| Fake motor power / HIGH | F021 external-effective forces lack 2D reaction-source validity | No motors, ground force, resources or batteries in F022; momentum/energy audits |
| Contact misnamed bonding / HIGH | Touch or normal impulse is not a durable connection | No attachment graph/port; only passive impulse/graze/no-contact |
| False science from rehashed logs / HIGH | Hash checks alone trust a forged producer | From-disk verifier independently reconstructs roster, trajectory and events; rehash tamper attacks |
| Glancing collision angular error / MEDIUM | Normal-only rule accidentally changes tangential velocity or creates KE | Wolfram exact rational C03/C04, restitution and momentum checks |
| Near-tangent instability / MEDIUM | Solver snaps a missed contact or creates spurious impulse | C05/C06/C07, explicit discriminant ambiguity fail-closed, zero-impulse tangent |
| Hidden order/bias / MEDIUM | Labels or coordinates change apparent physics | C10 translation, C11 rotation, C12 A/B label swap |
| Statistical overinterpretation / MEDIUM | 117 sampled frames are correlated; 13 scenarios chosen | Fixed deterministic benchmark, no biological significance claims |
| Knowledge leak / MEDIUM | Researcher truth becomes cell knowledge | No F022 agent observation; future researcher-view path separate |
| Post-hoc threshold / HIGH | Adjust tolerance after seeing data | 1e-9 per scalar scaled SI; 1e-9m overlap fixed before primary run; changes need new version |

**Resolved model scope:** 2 force-free translating frictionless 2D disks, max one event, no multi-body persistent contacts, spin, barriers, static friction, ground reaction, actuated pursuit, learned behavior or body. More powerful 2D engine may be necessary later; F022's minimal solver is not declared universal.

**Internal outcome:** sufficiently specific for v1 **design freeze** and subsequent separate implementation PR; NOT evidence of correctness of unimplemented source. Additional technical issues discovered before the first F022 world require documented pre-observation amendment; issues discovered after observation cannot be silently tuned away. External human review is outstanding/not claimed.
