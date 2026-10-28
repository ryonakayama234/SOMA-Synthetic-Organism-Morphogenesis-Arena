# V003.v1 — frozen pre-observation contract (2026-10-28 JST)

**DESIGN FROZEN / NO V003 DERIVED PRIMARY WORLDS HAVE BEEN PRODUCED / NO V003 IMPLEMENTATION OR UI ADOPTED.** Parent Issue [#93](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/93), reviewed design PR [#94](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/94), [SPEC](../../topics/V003-causal-fork-lab/SPEC.md), [PLAN](PLAN.md), [four versioned machine contracts](../../contracts). Researcher expressly delegated proceeding on 2026-10-28, without claiming final scientific adoption. Last exact-head prefreeze Codex critical review **b013a66e8cf03c930d31844ce4210cabf17f1f20**: no major findings after fixing canonical LF (P1) and 11-way one-to-one request binding (P2). Same-AI and Codex checking are NOT external peer review.

The **containing Git commit SHA is anchored separately in Issue #93 after this file is committed**. This file defines an immutable protocol **before any V003 generated world is observed**. Any later modification of primary y grid, source identity, estimand, analysis, tolerance, authority, or panel control is a new approved V003.v2, never silent retroactive retuning.

## Source trust: one pre-existing independently validated original

- Trusted original source is the *previously generated* F022 full frozen C01–C13 archive, successful F022 GitHub Actions run **40176213718**, Python 3.11 artifact **12592745454**, with **original implementation commit `824a8621944ea438388c54949a2b65719be2e419`** and F022 frozen protocol `3984e9dcb2cb420abab5ca92b4d029b31b5173f8`. Its GitHub Actions source and expected SHA are fixed independently of the request and untrusted archive manifest. It must never be replaced by a new F022 source archive during V003 primary execution.
- Original ZIP sha256: `6e3e3d8f06bfe325276eff0e7d0675b85a620afd53d13f06b17f6214d2ce3a44`. Required five original files: `scenario.json` sha256 `498a16056ad7220aaee19080c1fd8064ba6d9c9c161808864cda94c3da565605`; `states.jsonl` `ea2ead1117fe55d53d79791dbf190dc0740d02676d5bc79df7ff0d71d29c102c`; `contacts.jsonl` `cee1c52bab4d9d0ca6dda92185a93fae8a7bb09be7660d14c87e4621da15b530`; `audit.json` `dad1dd5891d0815c61980e4fc48f667458fbb87a51ac719ccd06b5c65b858d52`; `manifest.json` `f0d5d9fd4e1d126b0f0e0f77fb5e796b7b3a0860118891c10c70d919e05fadc0`. Source bytes are read-only.
- **Pre-freeze source-only preflight completed**: downloaded prior CI ZIP; separately reconstructed 13 original frozen scenario inputs, all 117 original saved sample rows, all 10 contact events and all 13 per-world audit metrics, manifest/file digests and frozen identity against source-independent analytic mechanics, 1e-9 scaled-SI criterion; PASS. Its evidence receipt is on Issue #93. This is a reread of *existing* F022 data, NOT a V003 primary result.
- During actual implementation/execution the same pinned root file digests plus independent **complete** F022 source verifier must pass again before selecting C05. Expiration/missing files, trust ambiguity, changed source hash or rehashed forgery => HARD STOP; no substitution.

## Exactly one bounded intervention, one primary estimand

- Immutable original F022 C05 B initial y=1.01m, A=(-1,0)m with vA=(1,0)m/s, B=(1,y)m with vB=(-1,0)m/s; 1kg and radius .5m for each disk, e=1, duration=2s, nine post-grid samples at 0, .25, ..., 2s. No motor, resource, bond, ground physics, controller, local observation or learning.
- Fork `y_b_m` alone to the exact decimal strings `0.95,0.96,0.97,0.98,0.99,1.00,1.01,1.02,1.03,1.04,1.05`. Exactly **11 independent new derived output roots / 99 saved rows**, zero random seeds. Each physical scenario retains `world_id=C05`; experiment-only `fork_id=V003-Ynnn` belongs outside physics. For y=1.01 identity, zero physical field changes; otherwise exactly 1 field (`y_b_m`) changes. No 12th candidate.
- **Primary** `D_A^v(y)=hypot(v_Ax_fork(2)-v_Ax_C05_original(2),v_Ay_fork(2)-v_Ay_C05_original(2))` in m/s; **secondary** final A position norm difference in m. Independently verify **signed x/y vectors**, not just their displayed norms. Free-flight nominal signed clearance `y-1` m is a counterfactual geometry diagnostic, NOT actual penetration.
- Analytic reference: for y<1, s=sqrt(1-y*y), t_hit=1-.5*s, n=(s,y), j=2*s N·s, A signed post velocity difference=-j*n (m/s), A terminal position difference=(2-t_hit)*(-j*n) (m). For y==1 ONE `grazing_zero_impulse` event at t=1s and j=0; for y>1 NO EVENT and impulse/time `null`. Predicted counts: 5 impulse, 1 tangency, 5 no-contact. Total momentum=(0,0) kg m/s and total kinetic energy=1J, with the frozen SI componentwise tolerance `abs(error)<=1e-9*max(1,abs(reference))`; input choices, classification and 0-v-null are exact and never approximated. Off-grid events are stored event records, NOT fabricated sample rows.
- Existing independently verified *original* C05, C06 and C07 supply identity, impact and grazing comparisons respectively; normalize ONLY `world_id` for C06/C07 physical state/event equality. Common producer comparisons are not replacements for independent analytical verification.

## Immutable requests: exact canonical bytes and digests

Eight allowed request keys: `schema_version,operation,source_family,source_world_id,candidate_y_b_decimal,fork_id,expected_source_commit_sha,expected_frozen_protocol_sha`. Emit `json.dumps(request, sort_keys=True, separators=(',', ':'), allow_nan=False)` UTF-8 followed by exactly **one LF byte (0x0A)**. No CRLF, extra spaces or extra lines. Original source SHA and F022 freeze SHA are required constants. The request's own claims never confer trust.

| y_B | fork_id | SHA256 of exact canonical request bytes |
|---|---|---|
| 0.95 | V003-Y095 | 57c94a0dbcd474da5d985a7feb5b6bf3609e73e07751e4cc24751e19ce5baeff |
| 0.96 | V003-Y096 | d11c7a99544efd02fb6d7a0ca9a8e91f469a7a1d5ebcfbc4a5267e30872efdf8 |
| 0.97 | V003-Y097 | bf26386b743043421658a64e9bcea0902fca56565a85a6d65c1b4dd71dc2796a |
| 0.98 | V003-Y098 | ffea73dc4fd83feebb9f6537a510b00afc05caabe51fc534bbe1e5c437b07547 |
| 0.99 | V003-Y099 | ed943c86e037af97d57ae2702331b75e3c8f42c391034dbf9a3a43c77f743b44 |
| 1.00 | V003-Y100 | 0b4911b8deb7882d6c92b474e77cca193d6c3190f66c6dfc5961bf163d817f60 |
| 1.01 | V003-Y101 | 680e7366d781ce7f8e61272e91616ee70ce92f711b457a17b267ce2edd0daac7 |
| 1.02 | V003-Y102 | e9e1f5f1123c6540f3a3e94741f3de1fc84f1c06605af878b8756488e01751c6 |
| 1.03 | V003-Y103 | 63857fea662ab3bd08a2d553261174cac778516f06ab97e6a9993e5aad079b7c |
| 1.04 | V003-Y104 | 0e375fafde7888f2c6f0c2320863cdd530a976189f1ac1d2e972c4377f4bc3bf |
| 1.05 | V003-Y105 | 9163ad3e75893913e1ef4c7bb5b802c1b106acdf8ece13e2d5eb66e769d78ec4 |

## Contract, authority, UI and rejection hard stops

- Contracts: `v003.fork-request.v1`, `v003.derived.v1`, `v003.lab.v1`, `v003.workspace.layout.v1` (as reviewed before freeze). The request must map its decimal to exactly one `fork_id`; raw derived manifest must bind its embedded request y and request SHA to **that same fork id and scenario y**, must reproduce all on-disk raw records exactly, and stays `unverified_derived`. Independent oracle receipt stays outside producer output. Source-to-view verifier must recompute every copied row and mechanical contrast from pinned original and independent derived oracle BEFORE rendering. No derived result can appear as `f022.archive.v1` or in unchanged `v002.view.v1`.
- UI EXACTLY six V002 owners: Setup, Cells, dominant Arena, Evidence, System/Data, bottom fixed Timeline. PREPARE_REQUEST has an externally verified original and 11-choice request export only, with ungenerated derived explicitly labeled `NOT GENERATED`; VERIFIED_COMPARISON requires the whole independent 3-oracle trust chain, a 16-field input display, and a separate at-most-one changed-field index. No off-grid sample interpolation, browser-to-Python simulation control, seventh panel, local-agent/policy/learning input, or new physics.
- MUST REJECT: wrong/noncanonical request byte digest, mismatch across `fork_id`/request decimal/scenario Y, a second changed physical input, wrong/missing original full-roster source anchor, missing/overwritten output root, malformed/nonfinite/duplicate events and rows, rehashed edited physical states/events and their derivative contrast, mismatched on-disk and embedded raw data, false receipt/projection/signed delta, tangency-v-null substitutions, and any unverified browser publication.
- Engineering PASS requires 11 complete cases and negative controls, from-disk independent math verifier **not importing F022 producer/shared TOI**, projection/source authority checker, two clean same-environment byte-identical roots, CPython 3.11+3.12 semantic CI plus inherited regressions, unchanged original bytes, and human 6-panel browser inspection. Source/archive procurement in CI must honor pinned pre-existing artifact and hashes.
- Independent verdicts: engineering PASS/FAIL/INCONCLUSIVE; H3a,H3b1,H3b2,H3c,H3d SUPPORTED/REFUTED/INCONCLUSIVE/UNEXECUTED; researcher UI PASS/FAIL/INCONCLUSIVE; researcher final adoption separate. Null, failure or stop outcomes are preserved append-only; successful passive contact is NEVER autonomous assembly, biological evolution or robot learning.

## Execution boundary

This document freezes *design*, not success. Next deliverable is a **separate** V003 implementation PR against accepted main after merging reviewed design PR #94. No unauthorized physics, original archive rewrites, new modules beyond necessary isolated V003 responsibility, new panels or experimental tuning after observations. Record the freeze-containing Git SHA in Issue #93 before implementation or any V003 primary fork. All code, architecture, data flow, findings and README changes in implementation PR remain reviewable and scientific adoption is not automatic.
