# V002 implementation candidate — frozen source-verified read-only 2D observatory

**STATUS: IMPLEMENTATION CANDIDATE / latest-head CI & Codex review gate / NO HUMAN BROWSER ACCEPTANCE / NOT YET ADOPTED.**
Parent [#86](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/86), [Draft PR #89](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/89), frozen preregistration SHA `4ba05357a426edaa7ec6e9d1d5f905ad64893de8`; frozen [machine-readable view contract](../../contracts/v002.view.v1.schema.json).

## Exact one-way evidence path
- Two **same-family** F022 or F023 saved-source folders, strictly unmodified; pass independently inspected exact `implementation_commit_sha` from original source checkout and review admission as `--expected-*-sha`, never derive trust from the archived manifest.
- `project.py`: F022/F023 independent original on-disk oracles run first. Read-only scene/rows projection, complete physical input diff, phase/time pointers and strict JSON Schema.
- `verify_view.py`: **second independent** source-to-derived verifier reads actual original saved rows again, checks timestamps, row indices, all projected facts, provenance/expected SHA, full frozen inputs and flags. Publish refuses a mutation **before** renaming final output.
- `viewer.py`: offline static `index.html` from the verified `view.json`; only the original **six** panel responsibilities. Arena has two read-only XY panes with physically scaled disk radii and *separate symbolic* crosshair/letter centre annotations. Source event pre/post is inspectable independently of synchronized saved frames; no interpolation. Setup shows all initial field values, including equal fields. F022 cell ledgers show NOT MODELED, not zero.
- `tests/test_v002.py` and `browser_smoke.py`: freeze-case controls, no-source-write proof, altered-view prepublication refusal, wrong source SHA, F022/F023 same-family, Chromium DOM/SVG/event semantics. The latter is an **automated browser smoke**, not human researcher acceptance.
- `.github/workflows/v002.yml`: Python 3.11/3.12 source+view tests, original F022/F023 rehashed-archive negative attacks, two-root JSON/HTML replay checks, Playwright headless Chromium smoke, optional illustrative screenshot artifact.

## WSL2/Linux reproduction from repository root

```bash
python -m pip install 'jsonschema>=4.22,<5'
sha="$(git rev-parse HEAD)"
python -m experiments.F022.run_suite --out /tmp/v002-f022-original
python -m experiments.V002.project \
  --left-root /tmp/v002-f022-original --right-root /tmp/v002-f022-original \
  --left-world C13 --right-world C01 \
  --expected-left-sha "$sha" --expected-right-sha "$sha" \
  --trusted-left-anchor "reviewed-checkout:$sha" \
  --trusted-right-anchor "reviewed-checkout:$sha" --out /tmp/v002-c13-c01
python -m experiments.V002.verify_view --view /tmp/v002-c13-c01/view.json \
  --left-root /tmp/v002-f022-original --right-root /tmp/v002-f022-original \
  --expected-left-sha "$sha" --expected-right-sha "$sha" \
  --trusted-left-anchor "reviewed-checkout:$sha" --trusted-right-anchor "reviewed-checkout:$sha"
```

Open `/tmp/v002-c13-c01/index.html` **offline in a browser**. To run automated Chromium checks, install `playwright` and its Chromium browser and run `python -m experiments.V002.browser_smoke --f022 path/index.html --f023 path/index.html --out screenshots` using **separate generated F022 C13/C01 and F023 Q02/Q04** outputs as done by dedicated CI.

**No V002 formal technical acceptance or main integration** until the exact implementation HEAD's Python CI, Codex critical review, original and derived semantic tamper tests, browser evaluation and append-only findings have been examined. Browser screenshots are illustration, not saved-source physics evidence. New physics, agent observation/policy path and seventh panel remain forbidden.
