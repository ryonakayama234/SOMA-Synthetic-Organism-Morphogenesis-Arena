---
id: F012
kind: validation
status: unexecuted
updated: 2026-10-20
---
# F012 experiment record

## Design-only pre-experiment state

**UNEXECUTED.** This evidence record was created in the design-only preregistration branch, before any F012 simulation. No measurements, green CI, peer review or formal scientific acceptance are claimed. Frozen hypotheses, 48 initial case definitions, all model limits and negative controls are specified in [SPEC](../topics/F012-finite-energy/SPEC.md) and [PLAN](../experiments/F012/PLAN.md). Append actual tested SHA, measured observations, negative cases, independent oracle and CI artifacts in the implementation PR without rewriting this historical record.

## 2026-10-20 F012 implementation and actual GitHub software-model observations — **candidate, not adopted**

**Chronology:** Original SPEC/PLAN and the above UNEXECUTED section were committed *before* F012 model code in design-only [Draft PR #39](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/39), commit `47b4163e9c13c0108ca8fabb408669fd6db813cd`; implementation stacked in [Draft #40](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/40). Reference adopted main `c8992a0236177c4ce3c8de71db09c78c755b05b7`. Neither PR merged; F011 conditional adoption and A:no-contact full-period INCONCLUSIVE are unchanged.

**First CI failure is preserved:** implementation SHA `df905f28a7d700d65b018159d5b209f190e8008a`, F012 workflow [#39359997156](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39359997156) failed Python3.11/3.12. The independent verifier incorrectly compared the *post-step* CSV position with the *pre-step* state. The F012 model unit tests in that run were individually green, proving why CI green tests alone cannot substitute for an independent source verifier. At `a638d977621d399734314e3916571342ad846d0d` this indexing mistake was fixed without changing the physical parameters, original preregistration or observed raw traces. Existing failure record remains available.

**Successful source/evidence checkpoint:** `ebcd033e82d2b8ce547c9359b0e2220a1c4eb4bf`, [F012 workflow #39360370185](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39360370185): Python 3.11 and 3.12 BOTH passed 170 full-regression tests, 6 optimized F012 unit tests, frozen 48 normal runs, independent step-by-step CSV oracle of passive forces, positive relative work, gate, exact integer ledger, mechanical/ground energy and momentum, all published comparison fields and strict trusted source/config. Each version published 98 original files and 98 fresh replay files with same bytes within that Python version. [3.11 raw ZIP artifact](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39360370185/artifacts/12236902354) and [3.12 raw ZIP artifact](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39360370185/artifacts/12236554581). This is evidence for THAT exact source HEAD; a later commit must be checked again. Cross-Python byte identity has NOT been separately proven.

### Frozen C directional case — actual model outputs at finest dt=0.0025 s (T=9.6s)

| Initial work budget | Final COM displacement (m) | Last 1.2s (m) | Previous 1.2s (m) | End-stroke period return (m) | Actual spent (µJ) | Accepted/rejected motor steps | Persistent drift preregistered gate |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0 J | 0.0000000000 | 0 | 0 | 0 | 0 | 0 / 3840 | NOT SUPPORTED: no actuation |
| 1 J | +1.0275049752 | 0 | 0 | 0 | 1000000 | 1308 / 2532 | NOT SUPPORTED: later no motion |
| 3 J | +3.0524230509 | +0.22456814 | +0.35838137 | +0.06201153 | 3000000 | 2627 / 1213 | NOT SUPPORTED: relative stroke return >0.01m |
| 10 J | +3.5023819308 | +0.50935005 | +0.50035855 | +0.00191658 | 4275244 | 3840 / 0 | SUPPORTED for **model-only** persistence |

These values are from the actual GitHub CI runner's frozen-condition output on `ebcd033e` and are **not physical robot measurements**, **not Wolfram forecasts**. At 10 J, the positive-work sum was 4.27397124 J and per-step ceil spending was 4.275244 J. Thus 10 J is sufficiently generous for this *fixed numerical trajectory*, and the measured final COM agrees with F011's +3.5023819308m. The F011 net signed motor work near 2.2104 J is NOT the positive-work budget and must not substitute for it.

**Nontrivial negative result:** 3 J shows substantial displacement yet violates end-shape recurrence; claiming sustained periodic locomotion would be false. In addition, accepted/rejected per-step commands are discontinuous with finite budget and change with dt. The predeclared final-position medium/fine dt gate is met in this case, but that coarse global bound alone does **not** prove detailed command history/trajectory convergence near the 3 J exhaustion boundary. Do not interpret a large COM displacement as proof of stable locomotion, efficient locomotion or spontaneous control.

### Scientific classification, limited to fixed one-dimensional discrete world
- **H12a SUPPORTED (model only)**: exact 0/1/3/10 J integer budget accounting; 0-J cells remain static; no negative balances; rejected motor does not suppress passive ground/spring.
- **H12b PARTIALLY SUPPORTED**: finite budget changes displacement and drive acceptance; 10 J meets the explicitly predeclared persistent C/D criteria. 1 J and 3 J do NOT SUPPORT persistent final-two-period motion under the full preregistered gates; these are valid negative outcomes, not program failures.
- **H12c SUPPORTED (model only)**: isotropic B has zero COM motion; no-command E is static for frozen 48-case suite.
- **H12d SUPPORTED (model only)**: C/D mirrored COM and identical integer spending for matched budget/dt, checked in independent oracle and production regression.
- **H12e INCONCLUSIVE as to non-monotonic improvement / efficiency advantage**: the four frozen budgets cannot establish a general efficiency optimum or explain a physical energy tradeoff. No hidden budget sweep was performed.
- **H12f SUPPORTED for frozen arithmetic**: raw trace impulse and known nonzero semi-implicit mechanical defect checked against the expected identity, nonpositive ground work, positive-work quantization and source-bound replay. This does not validate real friction/contact or electricity.

### Independent mathematics and limits

Before numerical implementation, Wolfram's rational first-step reference (C, dt=.01, u=+1N) was: `vA=4019/500000 m/s`, `vB=-269/125000 m/s`, COM step displacement `2943/100000000 m`, signed motor work `1019/10000000 J`, linear-relative-power positive mechanical work `1019/20000000 J`, ceil charge **51 µJ**. This reference matches the F012 first-step regression; it is an independently evaluated mathematical prediction under the frozen discrete assumptions.

The verifier is an independently written computational expression and uses **no import** of F012/F011/F005 production simulation, but it was designed and reviewed by the **same AI assistant system**; this is not an independent human or external institution's peer review. Artifact SHA is file-integrity provenance, not independent execution identity, and the existing per-version two-root publication is not power-loss atomic. F012 simulation includes no real electrical motor physics, self-observation, learned behavior, morphology choice, physical joining, 2D contact, or real robot experiment.

**Pending decision / review:** Formal scientific adoption and design/implementation PR merge into main require the researcher's **fresh explicit authorization**. This findings append itself requires an exact updated HEAD CI check; do not cite an older CI as proof of the final documentation-inclusive commit. The post-check stronger saved-summary forgery test and cross-version artifact-byte comparison must be classified separately from the prior successful checkpoint until individually verified.
