---
id: EXP-F014
title: F014 frozen experiment plan
kind: experiment_plan
status: preregistered_not_executed
updated: 2026-10-20
issue: 45
---
# F014 prospective experiment — UNEXECUTED

Design preregistration on branch `design/F014-one-bit-peer-body-20261020` **before F014 simulation code or F014 experimental outputs**. The 2026-10-20 Wolfram fractions in [SPEC](../../topics/F014-peer-body-observability/SPEC.md) are **not empirical F014 runs**. [Issue #45](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/45).

## Fixed experimental matrix
- Force levels `u=2, 1, 0.5 N`, each starts from rest, mass 1kg per cell, xA=0m, xB=0.5m, dt=.25s, T=1s (4 intervals). No random seed, no learning, 0 drag; same 3,000,000µJ initial A ledger reserve as accepted F010.
- Cases L-linked, G-ghost, C-coforced, N-free, E-unexcited (definitions in SPEC). `5 cases × 3 forces × 4 steps = 60 observed intervals`. E forces are commanded but rejected due zero battery. Each run has initial row, four step rows. All `external_force` labels hidden from A and peer observer.
- Additional transport-only negative M-dropout: use L raw run, remove B packet on predeclared step 2 for each input level (3 deterministic diagnostic injections, no new world simulation); decision must be inconclusive. Additional malformed timestamp, forbidden field, and tamper negatives must raise errors. No post-output parameter sweep.
- B local packet `moved = |ΔvB| > 10^-10 m/s` with a packet sequence index and time label for alignment only; **payload 1 bit, not protocol 1 bit**. Missing packet is not False; reject stale, duplicated, reordered or wrong-source packets. No use of `attached`, B numeric velocity, link force, or world force by any inference code.
- Observability classifier may report `peer_motion_seen`, `peer_still`, or `inconclusive` (invalid/missing/unexcited). No `attached`, `connected`, `topology_verified` success label.

## Prospective numerical expectations (from frozen algebra, NOT observed)
| u [N] | linked B Δv per step [m/s] | G-ghost B Δv [m/s] | C-coforced B Δv [m/s] | A accel shared L=G=C [m/s²] |
|---:|---:|---:|---:|---:|
| 2 | 1/4 | 0 | 1/4 | 1 |
| 1 | 1/8 | 0 | 1/8 | 1/2 |
| 1/2 | 1/16 | 0 | 1/16 | 1/4 |

H14a: full A allowlisted local stream L/G/C byte-equal within same applied u under canonical serialization; L/C packet arrays also byte-equal. H14b: L/G one-bit differences at each excited timestep; L/C observationally indistinguishable even when A knows u. H14c: N peer bit 0 but A acceleration nominal (not link proof); E and M always inconclusive. H14d/e: safety and reproducibility.

## Mandatory experiment / audit artifacts
- `config.json`, raw F007 `states.csv` for every run, `a_local.csv`, `b_packets.csv` with `source=B, step_index, time_s, moved`, `comparison.json`, `manifest.json`; version keys `f014.config.v1`, `f014.packet.v1`, `f014.comparison.v1`, `f014.evidence.v1`.
- One researcher-only provenance adapter reads F007 truth and emits A's F008 strict allowlist plus B's binary observation; F014 estimator accepts only those typed objects. A packet does not carry actual B numeric speed, attached or world labels.
- An independent saved-data verifier (**no importing the F014 producer/inference**), strict version/key checks, source checksum binding, row-wise known F007 controls, peer-bit recomputation, A-local full identity and L/C counterexample, summary-independent oracle and hash-consistent forgery negatives; two-root byte-identical replay. Verify F001–F013 inherited tests, Python3.11/3.12 exact HEAD Actions.
- Report every failed premise, omitted row, missing packet and negative result; no silent threshold changes. Any new testing after initial outcomes must be labeled post-registration, preserving this original PLAN.
- Adoption requires scientific review of observed F014 evidence and CI; **pre-experiment design PR stays Draft**. No claim of observed F014 data, real electrical energy, noisy sensor, secure radio, new organism, actual 2D contact, or human independent review.

## Research interpretation rule
If L/G are separable but L/C remain identical, record **local causal evidentiary improvement and global structural non-identifiability** together. Avoid the fallacy that synchronized movement implies physical linkage. Future research could vary independent B excitation, sensor modalities or assumptions, but those are separate versions and not allowed to revise these preregistered controls after seeing data.
