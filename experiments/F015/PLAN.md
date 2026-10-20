---
id: EXP-F015
title: Frozen active-probe identifiability experiment plan
kind: experiment_plan
status: preregistered_unexecuted
updated: 2026-10-21
issue: 48
---
# F015: 15-run active intervention suite — UNEXECUTED

**This is a PRE-EXPERIMENT registration.** [SPEC](../../topics/F015-active-body-probing/SPEC.md) / [FINDINGS](../../findings/F015-validation.md) / [Issue #48](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/48). Wolfram exact fractions in findings are not simulator output.

## Run matrix / immutable intervention schedule
- 5 distinct world-truth groups `L-linked, F-fixed, T-tracking, N-free, E-disabled`.
- 3 independent intervention inputs `u={2,1,0} N` in the displayed order. **Reset full F007 world + batteries + B velocity and clocks to t=0 before each trial**; 1s each, dt=.25s, four intervals per run = **15 F007 runs, 60 A local intervals, 60 B one-bit packets**.
- Masses 1kg/each, xA=0, xB=.5m, both initial v=0, drag=0, link length=.5m, no detach, A battery 3,000,000µJ except group E=0; B=0. No seed/learning/noise/real motors.
- dA/dB = (0,0) for L/N/E; (-1,+1) constant over ALL u for F; (-u/2,+u/2) for T. F/T/N/E are unlinked. F007 `motor_force_n=0` is valid; deliberate OFF differs from motor rejected for insufficient funds.
- Packet threshold 1e-10m/s; match step-index and .25s grid. The OFF trial's B bits are usable as raw observations in a **multi-episode experimental protocol**, but a single zero-motion OFF observation NEVER proves non-attachment.
- L/F/T at u2 expected all observable histories identical. At u1 and u0, L/F differ in A-local history; at u0, B bits L=0 and F=1. All u: L/T identical in A + B payloads. Important: u1 B-bit remains True for L/F/T, so no false assertion of B incremental information.

## Exact Wolfram rational precheck (not observed)
| u N | L (aA,aB) m/s² | F-fixed (aA,aB) m/s² | T (aA,aB) m/s² | B bit L/F/T |
|---:|---|---|---|---|
| 2 | 1,1 | 1,1 | 1,1 | 1/1/1 |
| 1 | 1/2,1/2 | 0,1 | 1/2,1/2 | 1/1/1 |
| 0 | 0,0 | -1,1 | 0,0 | 0/1/0 |

Exact step ΔvB = u/8 (L,T) versus 1/4 (F). Separate assertions must check A-only difference vs additional B bit. The motor-work/ledger remains full F007 truth but cannot be copied into B packet.

## Prospective run artifacts and audit gates
For each of the 15 independently reset cases save `F007/config.json`, `F007/states.csv`, ledger, manifests; projected `a_local.csv`, `b_packets.csv`. Across all runs: `probe_schedule.json`, `comparison.json`, `manifest.json`, an independent audit summary and two-root byte replay. Schema version draft `f015.probe.v1`, `f015.comparison.v1`, `f015.evidence.v1`; types frozen conceptually in DATA_CONTRACTS but not implemented.
- Require actual F007 applied force (especially E=0 vs commanded>0), strict A-only allowlist and B boolean payload, all 60 row checks, physical truth isolated to auditor.
- Additional negative transport controls: drop packet step2 for selected L u2,u1,u0 trials (3 deterministic injections); corrupt source, clock, reset continuity and forbid injected extra B velocity/world truth. No missing→false coercion.
- Independent auditor must reject changed physical truth or forged claim even if all saved hashes are recomputed; independent equations or arithmetic, not merely calling experiment producer/inference. Test exact source+artifact binding, two root byte equal under same source, and Python 3.11 + 3.12 inherited regressions. CI output/failed first attempts remain recorded.
- Findings append observed numbers, full exact SHA, actions run URL, failure caveats and scientific status. Run outcomes may be SUPPORTED, CONTRADICTED, INCONCLUSIVE. Do not retrofit plan or thresholds based on outcomes.

## Acceptance boundaries
A successful experiment confirms only **conditional identifiability under fixed nuisance assumptions** and **structural non-identifiability under tracking disturbance** in ideal two-cell 1D; never implement `connected` return. Never call this autonomous morphology discovery, independent human review, physical motor/sensor/network integration. No implementation, experimental F015 data, or main merge is authorized by this design document alone.
