---
id: FIND-F017
kind: validation
status: limited_adoption_approved_premerge
updated: 2026-10-22
issue: 57
---
# F017 — 追記型研究・実験台帳

## 2026-10-21: design candidate / ZERO empirical F017 data
- **Question:** Can receiver A, with unknown symbol-to-action mapping, acquire usable value from B's raw bit through own embodied terminal energy feedback and re-adapt after unannounced inversion?
- **Antecedent observed evidence:** F016's *fixed decoding* ideal 1D 24-trial comparison was limited-adopted. Source: [F016 findings](F016-validation.md), [post-main workflows](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39582766235). It does NOT demonstrate F017 learning.
- **Hypotheses:** H17a new-sequence learning advantage; H17b symmetry under symbol renaming; H17c experience necessity; H17d secret reversal recovery; H17e physical/ledger/record integrity.
- **Counterfactuals:** no bit, constant, scrambled, informative/no-learning, informative/no-feedback; independent policy/world PRNG, exact paired target sequence, non-reset reversal stage.
- **Theoretical precheck only:** Wolfram `J(p)=3p-1.05`, break-even vs 0.50 J A-only at `p>31/60`; this is NOT F017 observation. Physical target ±0.625m and 1J motor are inherited deliberately ideal F016 conditions.
- **Status:** proposal before independent design audit, freeze, implementation, CI, raw trace generation, measurements, or adoption. Counts and candidate thresholds are stated in SPEC+PLAN and must be reviewed before first simulator execution.

| Gate | Actual state |
|---|---|
| Pre-execution independent audit / frozen design | NOT DONE |
| F017 module, API or producer | NOT CREATED |
| Learning/reversal episode data | NONE |
| Source-bound raw traces + false-science negatives | NONE |
| Two-root byte replay / Python3.11+3.12 CI | NOT RUN |
| Empirical H17a,b,c,d,e classification | UNEXECUTED |
| Limited scientific adoption / main merge | NOT AUTHORIZED |

**Append, never overwrite:** date, reviewed base/design/source SHA, deterministic seeds, phase counts, paired outcomes, CI run URL, archived artifact hashes, failed/negative trials, independently audited claims, review and disposition. Existing F016 results remain distinct.


## 2026-10-21 pre-freeze external-literature check (no experiment)
AAMAS 2019 [Lowe et al., *On the Pitfalls of Measuring Emergent Communication*](https://ifaamas.org/Proceedings/aamas2019/pdfs/p693.pdf) distinguishes sender's positive signaling from recipient's positive listening. Added proposed **H17f** offline `do(symbol)` policy-fork test to detect causal behavioral influence, not just information–action correlation or outcome change. This is literature-derived experimental design, **NOT F017 observation**, and all F017 empirical gates remain UNEXECUTED.


## 2026-10-22 — post-freeze implementation candidate; observed H17a–f outcomes not yet authorized
- [Design PR #59](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/59) merged to main as PRE-EXPERIMENT frozen specification; body-emergence-first charter preserved. This entry does not alter any preregistered acceptance gate.
- [Implementation Draft #60](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/60) implements `soma/f017.py`, `experiments/F017/run_suite.py`, `verify.py`, `analyze.py`, rehashed-falsification test, 3.11/3.12 CI and immutable two-root artifact design. Planned 23,296 software worlds, NOT physical robots.
- An early implementation CI iteration failed source-inventory equivalence in verifier before results could be accepted. The producer/verifier source allowlists were brought into agreement; retain the error and corresponding Actions history rather than erase it. This is **SOFTWARE DIAGNOSTIC**, not H17 success/failure.
- **NO current numeric F017 claim in this entry:** inspect exact FINAL source SHA, CI, separately saved audits and bootstrap before appending observational verdicts. Formal acceptance/main merge reserved for later evidence decision.


## 2026-10-22 — FIRST F017 VERIFIED FULL SIMULATION and independent saved-world analysis

**OBSERVED, NOT WOLFRAM FEASIBILITY THEORY.** Frozen experimental design [PR #59](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/59) was merged BEFORE running this implementation. Frozen SPEC/PLAN contain 8 independent world-order seeds × 2 symbol encodings × 7 arms × 208 episodes = **23,296 real F007 numerical episode calls** (NOT robot hardware); six primary arms plus R no-memory diagnostic.

- Reviewed implementation exact source HEAD **`8694cd36a3ba657d2ca5b297b34553475068da5d`**. [GitHub Actions #39688112315](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39688112315) reports **all 17/17 workflows SUCCESS**. F017 Python **3.11 and 3.12 both SUCCESS** on the identical source SHA, including full inherited tests, optimized falsification tests, 23,296 world episodes each, independently verified saved F007 position/velocity/motor work, F002 A/B ledger and 0 residual, hidden B mapping, exact A-policy Q recurrences and independent A RNG reconstruction. Rehashed corrupted `net_uj` embedded in gzip and rehashed in manifest was independently rejected. Separate same-input evidence roots byte-replayed identically per Python version. Saved 3.11 archive [artifact #12387094551](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39688112315/artifacts/12387094551), saved 3.12 [artifact #12386599058](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39688112315/artifacts/12386599058).
- **Software failure history preserved:** earlier CI attempts [#39687424347](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39687424347) and [#39687751315](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39687751315) rejected producer/verifier source SHA inventory mismatch before accepting any F017 results. Corrected inventory to match both pipelines and attached new independent negative; the first fully passing final-source run above is the authoritative observed run. These software errors were not counted as hypotheses falsifications.

### Primary observed numeric contrasts (each arm initial frozen unseen holdout: 8×2×32=512 episodes)

| arm | hit / 512 | hit rate | mean net J / episode |
|---|---:|---:|---:|
| I informative B raw bit + receiver learns | 490 | 95.703125% | +1.82109375 |
| N no packet; receiver learns on None | 247 | 48.2421875% | +0.447265625 |
| K constant symbol 1 | 263 | 51.3671875% | +0.491015625 |
| S scrambled balanced symbol | 234 | 45.703125% | +0.32109375 |
| L informative but Q frozen/no learning | 271 | 52.9296875% | +0.537890625 |
| F informative but feedback withheld | 250 | 48.828125% | +0.41484375 |
| R secondary reset-Q every episode | 271 | 52.9296875% | +0.537890625 |

**Independent eight-world-seed paired bootstrap, 10k deterministic resamples (two symbol encodings bundled within each independent seed):** mean I−N net delta **+1.373828125 J**; exploratory 95% percentile interval **[+1.3328125,+1.420703125] J**. Relative to each primary negative control N/K/S/L/F, lower 95% bound >0; I holdout success >0.70 and each hit-rate difference >0.20. Two initial encoding-specific hit rates both **0.95703125**, not a hardcoded truth decoder. Only eight independent world seeds; intervals do not establish robustness to different physics/tasks.

### Unannounced reversal and causal receiver use

- Learned I pre-flip holdout: **0.95703125** hit rate and **+1.82109375 J** mean net.
- Secret bit inversion at fixed Q, immediate frozen probe: **0.0859375** hit rate, **−0.7921875 J** net.
- Same Q retained, after 64 training episodes per block under reversal, final unseen holdout: **0.9375** hit rate, **+1.7625 J** net. Do not confuse post-flip improvement with resetting the learner or researcher directly providing the reversed mapping.
- Off-world matched `do(symbol)` intervention on cloned Q policy: `D` for I before inversion, encoding0 **+0.8681640625**, encoding1 **−0.87744140625**; after inversion the causal direction reverses (see saved `causal_probes`). No-learning L/F have `D=0`. Thus learned reception *causally changes A's motor choice* in the ideal task; mere sender symbol–action correlations are not enough.

### Preregistered H17 candidate-gate classifications, SCOPE-LIMITED
- **H17a SUPPORTED**: informative signal + actual own-action feedback beats no-bit, constant, shuffled, frozen policy, no-feedback groups on unseen terminal action and net energy.
- **H17b SUPPORTED**: both unknown symbol assignments; symmetric label reversal effects.
- **H17c SUPPORTED**: accumulated feedback is needed, reset-Q arm does not acquire holdout advantage.
- **H17d SUPPORTED**: abrupt inversion disrupts policy, un-reset Q relearns by repeated embodied reward.
- **H17e SUPPORTED as source-bound software evidence only**: frozen raw F007/F002 physics/ledger, independent Q/RNG oracle, wrong-result rehash negatives, CI, two-root byte replay.
- **H17f SUPPORTED**: matched offline `do(symbol)` tests detect positive listening; no-feedback/frozen-Q lack signal-caused motor policy difference.

**Important exclusion**: The experiment intentionally supplies a nonlearning sender B, a 1-bit observability mask, fixed 1D attached two-cell world and reward schedule, external effective motor power, ideal zero-latency message, and no body choice. Therefore this is **receiver-side learned association in a constructed toy world**, NOT spontaneously evolved communication, spontaneous signal emission, physical radio, role choice, body/morphology formation, real metabolic survival, proof of generic semantics or external human peer review. Same-assistant independent source verifier is **not** human peer review. **Candidate limited adoption review may be considered only after documentation-inclusive final SHA CI. No F017 main merge or formal scientific adoption has been authorized here.** Append future review separately; never retroactively change frozen thresholds.

## 2026-10-22 — independent source-review correction BEFORE LIMITED ADOPTION
- The initial fully passing experiment on `8694cd36` measured positive listening using matched off-world **independent research-seeded** action noise, holding learned Q fixed. This detects a valid causal behavioral effect but did not literally clone the receiver's **trained RNG state** as the frozen H17f protocol stipulated. Preserve its original D numbers as historical observations; they must not be relabeled as trained-RNG-fork values.
- Corrective implementation **after** the first result and **without altering frozen hypotheses, sample counts, threshold values or F007 physics** now deep-clones the entire receiver (Q and actual PRNG checkpoint), takes matched 256 paired `do(symbol)` draws with original learner unchanged, and makes independently reconstructed saved-state RNG fingerprints a required audit field. `analyze.py` now also enforces the H17f *directional sign reversal* across both symbol encodings and the secret reversal, not just magnitude.
- This is a prospective **measurement-protocol fidelity repair**, transparently documented after first observation, NOT an independently preregistered replication or extra validation of physical generalization. Formal limited adoption requires fresh final-source 3.11/3.12 CI and new archived artifacts to confirm no changed outcome or gate failure. Until that run, **the corrected H17f result and integration are PENDING**.


## 2026-10-22 — FORMAL RESEARCH VERDICT: F017 LIMITED ADOPTION APPROVED (premerge source audit)

**Scientific decision: SUPPORT H17a,b,c,d,e,f IN THE FROZEN, DESIGNER-DEFINED F007 IDEAL 1D TASK AND ADOPT THE F017 RECEIVER-SIDE UNKNOWN-SYMBOL→EMBODIED-ACTION VALUE-LEARNING MODULE WITH THAT PRECISE SCOPE ONLY.** User researcher on 2026-10-22 expressly supported integration if the predefined meaning is actually met; do not extend the adopted claim to communication/body emergence.

### Final corrected causal-policy audit, not the initial off-world approximation
- Exact premerge full candidate HEAD `cc0fe6ed606c1c0e9f963d27ceea2c01967aae87`, [GitHub Actions #39693731056](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39693731056): **17/17 workflows SUCCESS**; 3.11 and 3.12 each completed **23,296** frozen F007 numerical worlds, saved-world independent Q/RNG/F002/kinematics auditor, rehashed malicious net-score rejection and two-root byte-for-byte replay. Final full-Q+RNG trained-checkpoint causal intervention audits succeeded on both Python versions. Archived [3.11 artifact #12389897730](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39693731056/artifacts/12389897730), [3.12 artifact #12389148653](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39693731056/artifacts/12389148653).
- **Observed physical task outcomes UNCHANGED by off-world causal probe repair:** I first holdout `490/512=0.95703125` hit, `+1.82109375 J` mean net; N no bit `247/512=0.482421875`, `+0.447265625 J`; I−N `+1.373828125 J`, paired 8-seed bootstrap exploratory CI95 `[+1.3328125,+1.420703125] J`. Other primary frozen controls K/S/L/F all >20 percentage points below I and paired delta CI lower bounds >0.
- Secret semantic reversal with **same Q, never reset**: immediate frozen probe `22/256=0.0859375`, `−0.7921875 J` net, then after per-block 64 continued feedback episodes, final holdout `480/512=0.9375`, `+1.7625 J` net. Both initial encodings separately `0.95703125` hit.
- **Corrected and independently verified full-PRNG-snapshot paired policy forks H17f:** mean `D=P(+2N|do(bit=1))-P(+2N|do(bit=0))` at first holdout `encoding0=+0.8671875`, `encoding1=−0.87060546875`; after secret inversion/final holdout `encoding0=−0.88037109375`, `encoding1=+0.884765625`. Matched `L/F` no-learning controls `D=0`; `D` values change sign both across encodings and across secret reversal. The original pre-repair independent-probe-noise figures above remain historical and must not be silently overwritten.

### Acceptance by the frozen gates
- **H17a SUPPORTED** (I unseen holdout ≥0.7; margin ≥0.2 vs N/K/S/L/F; independent seed-cluster paired net 95% lower >0).
- **H17b SUPPORTED** (both encoding labels learned, preferences invert).
- **H17c SUPPORTED** (no-feedback, frozen Q, constant/scrambled signals and reset-every-episode R do not reproduce learning).
- **H17d SUPPORTED** (secret inversion sharply worsens old policy; continued embodied feedback re-adapts the SAME policy).
- **H17e SUPPORTED as same-author independent saved-evidence integrity** (F007 ideal numeric world trace, F002 integer budget and sender fee, Q and actual PRNG update reconstruction, source/artifact hashes, false-score SHA-rehash rejection, byte replay, cross-version source-head CI). **NOT independent external human peer review.**
- **H17f SUPPORTED after documented protocol repair** (trained full Q+PRNG checkpoint forks, matched 256 off-world draws, exact signal-only intervention, sign reversal, no behavioral effect of signal for untrained controls). Original H17f seed method discrepancy transparently preserved and corrected before adoption.

### Exact scope and exclusions
**ADOPTED CAPABILITY:** `soma.f017.RawPeerSymbol` validation, `Receiver.observe/learn/end_without_learning` two-symbol (+None), two-action ε-greedy online receiver, A-local own acquired and spent energy reward, reversal without reset, **only when evaluated under original F007 fixed 1D linked A/B external effective motor and F002 sidecar, ideal B-origin direction sensor and exactly defined scenario**. Researcher assigns B as sender, all encodings, symbol transmission, physical coupling and 3 J reward. B **pays 0.05 J without modeled B-private return**; there is no demonstrated B incentive to send.

**NOT ADOPTED OR DEMONSTRATED:** B learning, invention of a signal/protocol, self-chosen communicator roles, voluntary sending, A/B mutually optimized benefits, sensor noise/dropout/delay, 2D/3D mechanics, uncertain connectivity, spontaneous aggregation/attachment/detachment, adaptive morphology, hardware locomotion/power generation, generalized semantic grounding or biological evolution. Testing all episodes from one artificially balanced paired 1D task is not generalization to unseen task families. Only eight independent investigator world seeds; holdouts have 512 task episodes but are not 512 independent environment models. No external human review.

**Integration decision:** LIMITED ADOPTION SCIENTIFICALLY APPROVED by this dated research review. Merge of implementation PR #60 into main is authorized if its final documentation-inclusive source SHA passes the same complete CI matrix with no source changes to F001–F016. New main needs post-merge workflow confirmation; keep the source-head evidence and initial protocol-repair sequence immutable. Do not alter frozen success thresholds after data.
