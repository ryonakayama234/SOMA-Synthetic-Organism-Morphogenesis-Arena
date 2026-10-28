---
id: V003-PLAN
kind: preregistration_candidate
status: UNFROZEN_UNEXECUTED
updated: 2026-10-28
issue: 93
---

# V003 deterministic single-coordinate fork — design-only test plan

**No V003 run yet. These are hypotheses and predicted counts, not observed data.** Freeze after independent design review and before any primary new-world generation. Attach freeze commit SHA and original trusted F022 source+protocol SHA to Issue #93. Original F022 protocol SHA is 3984e9dcb2cb420abab5ca92b4d029b31b5173f8.

## Input fixture / primary register
Source: entire independently verified original F022 C01–C13 saved archive, selecting original C05 only *after* whole-archive verification from inspected checkout trusted SHA. Fixed original C05 A=(-1,0), B=(1,1.01) m, VA=(1,0), VB=(-1,0) m/s, m=1kg both, radius=.5m both, e=1, T=2s, dt=.25s. Reuse unchanged F022 simulator and reject modification of original inputs or simulator. Fork ID belongs to envelope; inside solver scenario keep world_id=C05.

Exactly 11 decimal candidate y_b_m values **["0.95","0.96","0.97","0.98","0.99","1.00","1.01","1.02","1.03","1.04","1.05"]**. One fork output root per y, no overwriting. Each predicted nine sampled post-phase frames at t=[0,.25,.50,.75,1.00,1.25,1.50,1.75,2.00]s. Eleven newly produced forks = 99 predicted stored sampled frames. Reference original C05's 9 existing rows reused unchanged. Zero to one contact event per fork. No random seeds; not a statistical replication set.

## Analytic prediction / contrast
For y < 1: t_impact=(2-sqrt(1-y^2))/2, normal from exact contact positions, positive restitution impulse; for y=1, t=1 and j=0 geometric tangent; y>1, no contact. Expected full grid: .95–.99 five impulse, 1.00 one grazing_zero_impulse, 1.01–1.05 five null/no-contact. Original 1.01 against derived 1.01 is zero-diff control; other ten pairs have exactly one changed physical input. Total P=(0,0) kg m/s, initial KE=1J, e=1 conserves KE even after impact. The event may occur between saved grid frames; never interpolate missing observed XY samples. Same time sample coinciding with event has phase=post.

## Measurements (not aggregate contact-rate estimates)
- Changed field IDs/count, exact scenario value/type equality and fork/base provenance; zero fields for identity, one y_b_m for others.
- Event count, kind, true event timestamp or null, normal, normal impulse, A/B before-and-after positions/velocities.
- All nine stored t, phase, x/y [m], vx/vy [m/s], KE [J], total P x/y [kg m/s], geometric overlap [m] and conservation/reference residuals.
- New evidence trust: original full-file and externally trusted SHA, freeze SHA, v003 request and derived file digests, exact code SHA, independent per-row oracle, source-to-view semantic guard, two-root same-environment byte equality and original-source byte preservation.
- Researcher UI: six-owner mapping, complete input diff, real event vs sample, zero impulse vs null, mandatory refusal of unverified derived bundle. F022 energy is NOT MODELED, not a zero.

## Controls and adversarial cases (preregistered candidates)
**P**: y=1.01 identity yields same physical rows as C05 after removing separate envelope provenance, no contact. **Q**: y=1.02 remains null although input differs. **R**: y=1.00 zero impulse recorded, not a non-contact. **S**: y=.99 true nonzero impulse and off-grid timestamp with discrete post-grid samples. **T**: all 11 candidates including failures, not only appealing contact examples.

Invalid negative tests: non-enumerated decimal, 1.00000000000001, wrong type, NaN/Infinity, second changed physical field, untrusted original source SHA, malformed/deleted original roster, duplicate fork ID, existing output path, ambiguous geometry, wrong original freeze hash. Edited+rehashed derived archive attacks: change y, fake or remove event, edit event time/normal/impulse or A/B event velocities, alter saved frame KE/position or row order, change original source SHA, rehash malicious manifest. All must be rejected by **independent V003 source/derived physics audit** and separately view audit, not by hashes alone. Reject V003 derived as V002.view.v1 input, block viewer direct simulator/policy writes and source overwrites.

## Evidence gates
1. Independently validate **whole original frozen F022 archive** with externally trusted expected checkout/source SHA and unmodified protocol. No self-authenticating manifest.
2. New V003 saved-file verifier must **not import soma.f022, producer or shared TOI helper**; independently reconstruct contact/free flight and compare every original and derived row, plus exact unchanged input map except y. Reject numerical/semantic source inconsistency even if files are rehashed.
3. Physical comparison <=1e-9*max(1,abs(reference)) for SI scalar components; exact candidate/request/physical input type-and-value and geometry event class (no tolerance rounding of y or j=0). Check momentum, KE, no overlap >1e-9m and exactly 0/1 events.
4. Fully source-bound original/derived provenance, independent view projection checker, strict versioned JSON schema and zero changed original-source file bytes. Same interpreter/environment + same trusted source and code SHA -> exact two-root canonical byte comparison. Python 3.11/3.12 separate semantic gates and existing regression workflows; exact final SHA CI/review. No general cross-interpreter bit-for-bit claim.
5. Browser/manual six-panel gate: scale, scrolling, UI request **export only**, source vs derived labels, exact event time vs saved sample, null, tangent and verifier failure. Human approval explicitly recorded; screenshots are secondary illustration.
6. Record per-case pass/fail and negative attempts in append-only findings. Technical PASS/FAIL/INCONCLUSIVE and H3a–d SUPPORTED/REFUTED/INCONCLUSIVE/UNEXECUTED separate; no biology/autonomy conclusion.

**Hard stop:** no V003 primary run before design review and explicit frozen V003 protocol SHA; no main merge before V002 PR #89 accepted + its exact-head review and post-merge gates.

## Third pre-implementation refinement — primary estimand and archived positive controls (UNEXECUTED)

**Design-only amendment; NOT a post-hoc result.** Keep exactly 11 y values, zero new input degrees of freedom, original C05 baseline and the current nine samples/fork (99 derived rows planned). Explicitly distinguish three unrelated kinds of claims: saved physical observations, deterministic independent model predictions, and display-only summaries. All numerical predictions below are algebra, NOT a V003 run.

### Predeclare one primary mechanical outcome
`D_A^v(y)=hypot(vx_A_fork(2)-vx_A_original_C05(2), vy_A_fork(2)-vy_A_original_C05(2))` m/s.
Report BOTH signed component residuals as verifier inputs and the norm as a researcher summary; record `D_A^x(y)` analogously from A's (x,y) at t=2 s. A is an especially clean intervention receiver: A's entire initial state is frozen while **only B's Y** is manipulated. Do not claim that any resultant change is learned behavior, adaptive benefit, survival advantage, or sustained body integration.

Analytical expectations for each fixed candidate:
- `c_free=y-1` m is the **counterfactual straight-line closest-approach clearance**, never logged as actual collision overlap.
- If `y<1`: `t_hit=(2-sqrt(1-y*y))/2` s, `j=2*sqrt(1-y*y)` N s, `D_A^v=j/1kg` m/s and `D_A^x=(2-t_hit)*D_A^v` m.
- If `y=1`: ONE archived grazing event at t=1, j=0, `D_A^v=D_A^x=0`.
- If `y>1`: ZERO events, TOI=null, impulse=null, `D_A^v=D_A^x=0`.
Always verify terminal A and B **component** velocities/positions against independent equations; compare total P and KE for conservation (P=(0,0), KE=1J, within frozen numeric tolerance). Do not infer individual fitness from conserved total energy.
The impulse curve is nonlinear and tends to zero at tangent boundary; `d j/dy=-2*y/sqrt(1-y*y)` (y<1) becomes steep as y approaches 1. These 11 discretized deterministic cases identify only this chosen grid, not a continuous robustness envelope or an empirical contact probability.

### Embedded source-roster controls: no additional experiments
- C05 y=1.01: derived identity .01-against-1.01 matches entire original C05 physical record *byte-for-byte canonical physical values where original record formatting permits*; provenance envelopes are not compared for equality.
- C06 y=.99: derived fork .99 matches original independently accepted F022 C06 physical scenario, nine saved states and contact event **after stripping only the original `world_id` label**.
- C07 y=1.00: derived fork 1.00 matches original F022 C07 physical scenario, nine saved states and zero-impulse grazing event by the same restricted label normalization.
These controls are valid only after independent full original 13-world archive verification; never bypass the original full-roster oracle. Exact binary identity is required for the identity control under same source implementation/environment, with numerical/oracle comparison for cross-world canonical data when record representations differ.

### Specific adversarial and null controls for the new estimand
Fail on `no_contact` with zero-valued fabricated impulse instead of null; a tangency described as `no_contact`; `impulse` event with zero impulse; analytic nonzero A effect but display says zero; tampered/rehashed A final velocity, A final position or displayed norm; swapped C06/C07 purported positive-control labels; injected nonzero `c_free` claimed as actual physical penetration; a false archived sample interpolated at off-grid TOI; a hardcoded `pass` in producer output. Derived verifier and independently coded view verifier recompute all summaries from source rows, source-independent mechanics and externally inspected anchor; a JSON Schema parser alone is insufficient.

### Decision gates separated by domain
- **Measurement**: all 11 results have complete signed vectors, correct event/null semantics, analytic signed normal/TOI/impulse, independent primary/secondary A contrasts, and explicit full original C05/C06/C07 controls.
- **Software/provenance**: no altered original bytes, no additional scenario field differences, immutable new derived roots, rehashed tamper refusals, source-independent oracle and receipt, two-root reproducibility, exact-HEAD CI/review.
- **UI/authority**: six owners only, central metric Arena, Setup only exports bounded request, Evidence distinguishes raw source/verified mechanical contrast/theory and the three audit verdicts, Timeline refuses fabricated frames, no agent feedback; manual browser comprehension.
- **Science**: classify model-physics prediction separately from pipeline adequacy, mark missing/negative results, no biological/emergence claims. Researcher must separately approve a freeze before any implementation.

### Minimal future scientific payoff and stopping rule
The calibrated V003 output can later become a control for **contact without mechanical effect vs contact with effect** in a different, explicitly approved attachment experiment. It does NOT itself test whether joining is beneficial. If the only feasible output is an attractive 11-trajectory animation without independently auditable A influence, stop V003 at design and revisit priority against attachment mechanics. No new panels or modules should be invented to conceal an unconvincing research endpoint.
