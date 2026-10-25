# F022.v1 — 事前登録・凍結仕様 (2026-10-25 JST)

**FROZEN DESIGN ONLY / NOT IMPLEMENTED / NO PRIMARY F022 WORLD EXECUTED / NOT ADOPTED.**
Parent [Issue #77](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/77), [Draft PR #78](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/78). [Internal critical design audit](../../docs/reviews/2026-10-25-F022-design-audit.md), [exact theoretical calibration](PREFLIGHT.md), [SPEC](../../topics/F022-2d-encounter/SPEC.md), [PLAN](PLAN.md). **This document overrides pre-freeze proposal values.** The containing commit SHA is anchored to Issue #77 *after* commit, since the commit cannot contain its own SHA. No primary world has been observed. Changes to scientific choices after first execution require a new F022.v2, never retroactive reinterpretation.

## Scientific question
Can two freely translating passive circular cells on a 2D plane undergo verifiable collision, glancing encounter, grazing or no-contact, without forcing a connection graph? H22a: momentum/restitution and ideal force-free ballistic dynamics hold. H22b: geometry/impact parameter, rather than a 1D fixed join switch, determines contact. H22c: source-independent saved-artifact verification detects both physical corruption and hash-repacked tampering. Rivals: numerical tunneling, fabricated energy, mislabeled contact, asymmetric order. A negative/null encounter is a valid outcome. Contact is **not** connection, consent, evolution or body formation.

## Physics: frozen assumptions and algorithm
- Exactly two passive, equal disks A/B, each **mass 1 kg, radius 0.5 m**. 2D unbounded plane, no walls, ground friction, gravity, propulsion, externally-effective ideal F021 motors, energy accounts, resources, learning, controllers, ports, joints, rotation/spin or torque. Prescribed **initial velocities** are researcher inputs, not cell actions. Time `0 <= t <= 2s`.
- Piecewise free flight `p_i(t+dt)=p_i(t)+dt*v_i` with constant v between events; **continuous analytic time-of-impact (TOI)** determines collisions, not discrete-sampling endpoint overlap. Output sampling only at `t=[0,0.25,0.5,0.75,1,1.25,1.5,1.75,2] s`, nine saved rows/world. Events coinciding with sample time yield **post-impulse** sample; contact record holds pre- and post-event velocities and positions.
- Contact between disks at `|p_B-p_A|=R=1m`; let `r=p_B-p_A`, `w=v_B-v_A`. Solve smallest valid future TOI of `a*τ²+b*τ+c=0` with `a=w·w, b=2*r·w, c=r·r-R²`, using a numerically stable quadratic roots method. No relative movement a=0 => no new contact in valid separated input. Negative discriminant => none; zero discriminant and valid in-horizon closest approach => record **grazing_zero_impulse** with zero force; positive discriminant => valid first approaching crossing only. No event for separating trajectory.
- For approaching contact define outward A→B unit normal `n=(p_B-p_A)/R`, `g=w·n<0`, e in **{1, 0.5}**, `j=-(1+e)*g/(1/m_A+1/m_B)` N·s. Update `v_A'=v_A-(j/m_A)n`, `v_B'=v_B+(j/m_B)n`. No tangent impulse. For geometric tangency g=0 and j=0. Momentum is conserved; e=1 kinetic energy unchanged; e=.5 dissipates exactly `(1-e²)*mu*g²/2` J, `mu=(1/m_A+1/m_B)^(-1)`. A/B interaction impulses are equal/opposite.
- Strictly **non-overlapping initial centers** `distance>1m`. Any touching/overlap initial state, nonfinite or malformed input (including NaN/Infinity), nonpositive mass/radius, forbidden coefficient, invalid timestamps are **rejected before producing a primary archive**; never silently teleport or correct positions. Frozen valid scenes require at most one event in this force-free 2-disk world; an unexpected second event is an error.
- Numerical ambiguity rule for discriminant D=b²-4ac and S=max(1,abs(b²),abs(4ac)): **if 0<abs(D)<=1e-12*S, return ambiguous_geometry and reject** rather than snap near-tangent geometry into a convenient outcome. Exactly D=0 admits zero-impulse tangency; none of frozen valid scenes is selected to need ambiguous reinterpretation. Contact near observation start/end with unresolved ordering <=1e-12s must fail closed, not be arbitrarily ordered.
- All physics uses finite IEEE-754 binary64, no rounding/truncation before archive. Run on CPython 3.11/3.12 Linux, canonical `json.dumps(sort_keys=True,separators=(',', ':'),allow_nan=False)` UTF-8 LF with deterministic scene/sample/event ordering; empty contacts file for no-contact is valid. No pseudo-random seed in v1 (a deterministic calibration grid, **not ecology/biological replicates**).

## Primary deterministic worlds: fixed set C01–C13, ALL 13 valid
Default A position=(-1,0)m, B=(1,y)m, A velocity=(1,0)m/s, B=(-1,0)m/s, mass 1kg each, radius .5m each, T=2s.

| ID | Change from default | e | Expected event result |
|---|---|---:|---|
| C01 | y=0 | 1 | one central elastic collision at t=.5s |
| C02 | y=0 | .5 | central dissipative collision at t=.5s |
| C03 | y=.6 | 1 | oblique elastic at t=.6s |
| C04 | y=.6 | .5 | oblique dissipative at t=.6s |
| C05 | y=1.01 | 1 | near miss, no contact |
| C06 | y=.99 | 1 | near graze but actual approaching impulse |
| C07 | y=1 | 1 | exact geometric tangent at t=1s, zero impulse |
| C08 | y=0, vA=(-1,0), vB=(1,0) | 1 | separating/no contact |
| C09 | y=.6, vB=(1,0) | 1 | parallel co-motion/no contact |
| C10 | y=0; translate both positions by (+10,-7) | 1 | C01 translated, same dynamics |
| C11 | rotate both C03 positions and velocities by 90° CCW: (x,y)->(-y,x) | 1 | C03 rotated |
| C12 | swap A and B entire C01 initial (position, velocity) states | 1 | C01 label exchange |
| C13 | A=(-10,0), B=(10,0), vA=(100,0), vB=(-100,0) | 1 | high-speed central at **t=19/200=.095s**, before .25s sampled frame |

**Negative input probes J01–J05**, *not* valid primary worlds: J01 centers=(-.2,0),(.2,0) overlapping; J02 coincident centers=(0,0),(0,0); J03 NaN/Infinity unquoted non-JSON numeric; J04 A mass=-1kg; J05 centers=(-.5,0),(.5,0) initially touching. Fail-before-publication. The 13-world suite has **13×9 = 117** grid frames; sample count is NOT a proxy for independent scientific samples.

## Analytic preflight references (not F022 observations)
Independently checked using Wolfram exact arithmetic: C03 has TOI=3/5, normal=(4/5,3/5), incoming normal relative speed=-8/5, j=8/5 N·s, A post v=(-7/25,-24/25), B post v=(7/25,24/25), total KE 1J, total momentum (0,0). C04 e=.5: j=6/5, A post v=(1/25,-18/25), B post v=(-1/25,18/25), total KE 13/25J, loss 12/25J. C01 equal-mass velocity exchange; C02 ±.5m/s, loss .75J. These are **math-only preregistered predictions**; see [PREFLIGHT.md](PREFLIGHT.md).

## Archive, oracle and fixed tolerances
- Intended scheme `f022.archive.v1`: `scenario.json` (all 13 initial conditions/physics); `states.jsonl` (exactly 117 post-phase sampled records with time, A/B XY, velocity, total kinetic energy); `contacts.jsonl` (0/1 events per world; event time, geometric normal, impulse, kind, pre/post positions/velocities, restitution); `audit.json` (per-world independent metric values and null/negative controls); `manifest.json` (frozen-protocol commit SHA, implementation SHA, full input/artifact SHA256, environment/Python version). Version, SI units, cardinality, nullable event policy and verification semantics in [DATA_CONTRACTS](../../docs/DATA_CONTRACTS.md). No cell-observation API or viewer is released by this specification.
- Frozen numerical criterion for scalar SI comparisons to analytic reference: `abs(observed-expected)<=1e-9*max(1,abs(expected))` (componentwise for vectors). Max penetration <=1e-9m. No allowed nonphysical momentum gain, non-elastic energy gain, event omission, fake sign, or silent fallback. e=.5 must match analytic dissipated KE, not merely KE nonincrease.
- Independent **from-disk** verifier must not import simulator's collision solver or producer. Recompute all 13 expected cases from their initial source-bound specification, TOI, event presence/absence (including C07 zero impulse), impulse, continuous/sample states, total momentum/energy and output hashes. Reject semantic forged-rehashed data: modified contact time/normal/impulse/velocity, deleted event or added fabricated event, permuted/missing row or world, rehashed altered scenario, NaN/Infinity and wrong protocol SHA. Standard hashes alone do **not** certify truth.
- Mandatory qualification: actual Python 3.11/3.12 source-bound CI and **all existing F001–F021 regressions**, 2 clean output-root byte-identical replays, strict final implementation SHA + protocol freeze SHA, synthetic tamper controls, physical analytic/symmetry/no-contact/high-speed comparisons, internal critical review and honest uncertainty if any. Same-AI review/independent-code-path is **not external peer review**.
- **Two different judgments**: (i) software limited admission as exact specified passive collision measurement instrument; (ii) H22a/b/c supported/refuted/inconclusive/unexecuted. Neither positive collision counts nor accurate diagrams prove attachment, cooperation, robot control, 2D ground physics, viability, individuality or evolution.

## Sequence
This freeze on the design branch precedes *all* F022 primary observations. Anchor SHA on #77. Implementation, new F022 CI, results and reviewer discussion belong to a separate implementation PR; F001–F021 source and historical measurements must remain unchanged. The design PR may remain Draft while acceptance gates are reviewed. This freeze is not consent to silently merge/claim adoption.
