---
id: FIND-F017
kind: validation
status: unexecuted_design_candidate
updated: 2026-10-21
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
