---
id: FIND-F010
kind: finding
status: preregistered_not_executed
updated: 2026-10-19
---
# F010 — active local response / identifiability boundary

## Design preregistration (2026-10-19)
Issue [#31](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/31); [SPEC](../topics/F010-local-identifiability/SPEC.md), [PLAN](../experiments/F010/PLAN.md). Frozen Wolfram rational theory: linked and force-adaptive hidden unlinked traces both have alpha=.5, beta=0; constant unknown force -1 N yields alpha=1, beta=-1; baseline has alpha=1, beta=0. One input cannot distinguish linked and constant force. A=C local equivalence remains even with three inputs. These are **mathematical reference values**, NOT SOMA F010 observations.

| Gate | State |
| --- | --- |
| New F010 code, CI, actual numerical experiment | UNEXECUTED |
| Independent saved-data oracle / evidence / replay | UNEXECUTED |
| Separate AI numerical/software review | UNEXECUTED |
| Independent human/external peer review | UNEXECUTED |
| Researcher limited adoption and main merge | NOT AUTHORIZED |

Do not edit the frozen references after collecting data. Append timestamped implementation observations, failures, CI SHA/run URL and interpretation later. The F007/F008/F009 adopted code and historical evidence must not be modified. V001 draft work remains separate.

## Implementation candidate created after design preregistration (2026-10-19; results unverified)

Stacked implementation branch proposes `soma/f010.py`, the fixed F007 A–E × three-force runner, F008 local projection, all-row researcher-only independent Fraction oracle, test module and 3.11/3.12 workflow. The raw evidence run and final HEAD Actions **have not been observed at time of this entry**; formal acceptance has **not** occurred. Expected signatures and exact numerical values remain those preregistered above. Record any CI failures, corrections and real outputs in later dated additions. Human/external independent review not performed.

## 2026-10-19 first candidate CI and deliberate hardening failure (not adoption)

Implementation PR #33 HEAD `432ad44d2f2ba6e9347f1c205fd65214383fbdb6`: [F010 Actions #39228116684](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39228116684) succeeded on Python3.11 and Python3.12, **151 full tests, 7 F010 optimized tests**, 15 independent A–E F007 runs (60 A-local intervals), all 107 evidence files and the independent Fraction/saved-F007 oracle, and 107-file same-byte replay. A-linked/C-adaptive complete local CSVs matched exactly; all F010 signatures matched the preregistered Wolfram rational predictions. These results are model/software consistency only; the artifact was produced on that commit and does not verify later changes.

**Preserved test failure:** after adding extra negative tests for rehashed tampering, HEAD `4a2e24b05781f12b52d43083a968c51d21818fb0` [Actions #39228305764](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39228305764) failed both versions during full regressions: `test_rehashed_local_and_science_claim_forgery_rejected` generated invalid JSON (`JSONDecodeError: Extra data`) because the *test fixture* wrote literal backslash-n at EOF instead of an actual newline. This is **test implementation failure**, not evidence contradicting H010. Follow-up commit replaces the fixture's double escape; its CI remains to be checked. Do not report the failure run as passing. Preobserved thresholds, formulas and controls are unchanged.

## 2026-10-19 audited F010 run after negative-fixture correction (PR #33; NOT ADOPTED)

**Exact implementation commit**: `c370562a17c5eba16d2e2d699f255db5f87f8990`. [Actual GitHub Actions #39228478362](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39228478362) **success** on Python 3.11 and 3.12 independently: **153/153 full regressions**, **9/9 F010 optimized tests**, 15 F007 independently reset 1D trials (=5 A–E × u=2,1,.5 N), 60 A-local acceleration intervals, **107 raw evidence files + 107 byte-identical replays** per job. Frozen A–D Fraction independent raw-world/local oracle and saved-summary semantic checks passed, A-linked/C-adaptive `local.csv` are **byte-identical at all three forces**, E zero applied force correctly yielded `inconclusive`. F negative tests checked forbidden world input, rejected/missing excitation, nonaffine holdout, clock/velocity tamper, numerical forged CSV **with recomputed manifest SHA**, scientific topology claim **with recomputed SHA**, non-replace and overlapping destinations. F001–F010 all 10 workflow runs for **the same PR HEAD** succeeded; existing F001–F009 sources and V001 PR branches were not modified.

[Python 3.11 uploaded evidence artifact #12176375858](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39228478362/artifacts/12176375858) / [Python 3.12 artifact #12176660649](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/39228478362/artifacts/12176660649). These are CI outputs from **c370562**, not from any subsequent findings/documentation commit.

### Scientific decision per frozen H010a–f

| H010 | Actual software-model observation | Judgment |
| --- | --- | --- |
| a, linked | a(u=2,1,.5)=(1,.5,.25) m/s², fitted (alpha,beta)=(.5,0) | **SUPPORTED within fixed F007 ideal 1D** |
| b, unlinked + constant unknown -1N | a=(1,0,-.5), fitted (1,-1); first input identical to a, second separates | **SUPPORTED under constant-disturbance assumption** |
| c, unlinked + input-dependent -u/2 N | a=(1,.5,.25), fitted (.5,0), **identical complete A-local rows (including battery) with case a** | **SUPPORTED as an indistinguishability counterexample**. Topology **INCONCLUSIVE** |
| d, unlinked no unknown force | a=(2,1,.5), fitted (1,0) | **SUPPORTED within fixed model** |
| e, A battery 0 or unexcited | applied=0, detector/inference unexcited/inconclusive; insufficient force variety negative test | **INCONCLUSIVE by design**, correct gate |
| f, tamper / rehashed scientific forgery / byte replay | Rejected and 107-file same-byte replay | **SUPPORTED for fixed saved evidence**, not cryptographic actor authentication |

The third 0.5 N level was held out from the two-level fit. `alpha=1/2` denotes a **response class**, NOT identification of mechanical coupling: the input-dependent hidden force is a constructive counterexample for *any* input within this same 1D affine model, and three sampled forces do not resolve it. Results support a mathematical/software **identifiability boundary**, **not** a newly evolved morphology, self-body schema, real motor propulsion or a generalized learning agent. F007 is an external effective-force and ideal work/battery model with no physical reaction mechanism; F009's modeled ground reaction remains separate. No noise robustness, arbitrary dt/parameter generalization, realtime self-generated interventions, sensor-specific powertrain, hardware or physics-world validation.

### Review independence and residual gates

Existing F007 saved oracle checks all world F007 rows; F010 verifier **does not import F010 estimator or F007 simulator** and independently derives Fraction small-rational trajectories and every A-local field from authenticated-to-checkout raw bytes; Wolfram preregistered analytic fractions were evaluated *before* new F010 execution. Nevertheless, this is a separate *method*, not a separate independent **human/research laboratory** or actor; independent peer review is **NOT PERFORMED**. Source checkout SHA/manifest checks are not attacker/signer identity guarantees; publication of 2 evidence destinations is not a power-loss-atomic transaction. A PR draft is not adoption.

**Next gate**: repeat CI on the eventual HEAD containing this findings entry; inspect 3.11/3.12 and older workflows, confirm draft stacking and preserved main. Researcher must make a fresh explicit **limited acceptance / no-acceptance decision** and separately authorize any main merge. Do NOT close Issue #31 or treat candidate as formally adopted ahead of these gates. If human review remains unavailable, mark that limitation openly rather than claiming it occurred.

## 2026-10-19 independent reviewer hardening (verification pending at this entry)

After inspecting final candidate PR #33 at `b3cc710`, a separate reviewer identified two genuine implementation contract gaps: the F010 local estimator did not reject nonzero motor-command/applied-force mismatches despite the frozen PLAN's explicit excitation gate, and the paired evidence publisher did not roll back its first published destination on an ordinary second-rename exception. The code now checks equality for **every** typed A-local row and returns `inconclusive` when excitation was rejected/partially applied; a synthetic nonzero partial-force case and a single-step rejection are regression tests. Paired publication now rolls back the first directory on a normal second-publication failure, with fault-injection checking no remaining partial output and no damage to existing evidence. True crash/power-loss atomicity between two directories remains **not guaranteed**.

The preregistered hypotheses, tolerance, expected results, F007/F008 model, and historical failed-run record are unchanged. This paragraph records implementation changes **before** fresh CI is examined; the new HEAD is not yet a verified run or formal adoption. User has explicitly delegated limited-adoption and merge judgment conditioned on correction and passing final verification. A later dated decision must name exact CI HEAD and actual merge SHAs.
