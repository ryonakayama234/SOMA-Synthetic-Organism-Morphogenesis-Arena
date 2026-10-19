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
