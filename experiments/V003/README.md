# V003 implementation workbench — Causal Fork Lab

**IMPLEMENTATION CANDIDATE ONLY; NOT ADOPTED.** Frozen design [FROZEN_V1](FROZEN_V1.md), [Issue #93](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/93), design [PR #94](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/94). This branch is separate from the design and stacked on frozen design commit `46860b42846e434a54c10e906c2212d2c24e4ab3`.

One capability: take an externally pinned, independently verified **pre-existing original F022 13-world archive**, select C05, accept ONLY its 11 frozen B-initial-Y request files, reuse unchanged `soma.f022.simulate` to write separately named **UNVERIFIED** derived roots, then recheck them from disk with a separately coded analytic physics oracle before researcher-only projection. The primary A terminal velocity contrast and secondary A position contrast are in-model passive mechanics only. No new physics, F023, joining, motor, resource, cell policy, reward, learned control, or seventh panel.

**Immutable source:** 2026-10-25 F022 successful GitHub Actions run `40176213718`, artifact `12592745454`, implementation SHA `824a8621944ea438388c54949a2b65719be2e419`. Original ZIP/5 physical file digests and source provenance are pinned in FROZEN_V1; expiration or other root means STOP. Never generate a replacement original during V003.

**Evidence order:** original source full-roster independent verifier + external per-file SHA -> request canonical SHA -> existing F022 physics -> raw derived file family `v003.derived.v1` with `unverified_derived` status -> separate from-disk V003 closed-form verifier receipt -> source-to-view semantic verifier -> `v003.lab.v1` -> exactly six UI owners.

The implementation PR must not be merged into `main` until the design PR, exact-head CI/review, independently verified full 11-run primary results, adversarial tamper checks, two-root same-environment reproduction, real browser UX testing, and the researcher's **separate** technical/scientific/human adoption decisions are recorded. Code or screenshot alone is not an admission.


## Runnable CLI sequence — candidate implementation, not adopted

Prerequisites: Python 3.11/3.12 Linux, `pip install 'jsonschema>=4.22,<5'`; externally obtained **pre-existing** F022 original 5 files from workflow 40176213718 artifact 12592745454 (NOT a newly rerun F022 source). Original hashes and commit identity must match [FROZEN_V1](FROZEN_V1.md). Replace `/path/to/preexisting-f022` with the immutable local directory. The production entry points do not edit original files.

```bash
ORIGINAL=/path/to/preexisting-f022
BASE=/tmp/soma-v003-candidate
mkdir -p "$BASE/receipts"
python -m experiments.V003.verify --original-root "$ORIGINAL" --source-receipt "$BASE/receipts/source.json"
python -m experiments.V003.run_suite --export-requests "$BASE/requests"
python -m experiments.V003.prepare --original-root "$ORIGINAL" --source-receipt "$BASE/receipts/source.json" --out "$BASE/prepare.html"
python -m experiments.V003.run_suite --original-root "$ORIGINAL" --source-receipt "$BASE/receipts/source.json" --request "$BASE/requests/V003-Y099.json" --out "$BASE/Y099"
python -m experiments.V003.verify --original-root "$ORIGINAL" --source-receipt "$BASE/receipts/source.json" --derived-root "$BASE/Y099" --derived-receipt "$BASE/receipts/Y099.json"
python -m experiments.V003.project --original-root "$ORIGINAL" --source-receipt "$BASE/receipts/source.json" --derived-root "$BASE/Y099" --derived-receipt "$BASE/receipts/Y099.json" --out "$BASE/Y099-view"
python -m experiments.V003.verify_view --original-root "$ORIGINAL" --source-receipt "$BASE/receipts/source.json" --derived-root "$BASE/Y099" --derived-receipt "$BASE/receipts/Y099.json" --view "$BASE/Y099-view/view.json"
```

These commands **would** generate one derived candidate (Y099) and its separately checked view; the code is only an implementation candidate until source-bound CI passes. Run all eleven frozen request files and two clean roots for acceptance; no eleventh-world extrapolation or non-frozen parameter edits permitted. `prepare.html` is ORIGINAL-ONLY (never claims newly generated V003 data); `Y099-view/index.html` should be shown only after independent checks. Neither browser document can run Python or send agent commands. The CI workflow uploads original-derived receipts, eleven offline verified views, original-only request-preparation page and browser screenshots; source ZIP is deliberately never relabeled V003 physical evidence. Same user and AI doing internal review is not external peer review.
