# V002 implementation candidate — frozen source-verified read-only 2D observatory

**STATUS: SOURCE HEAD CI/CODE REVIEW PASS / HUMAN INTERACTIVE ACCEPTANCE NOT YET EVIDENCED / NOT ADOPTED.**
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


## Verified existing PR-code run and pending acceptance gate (2026-10-27)
[Exact-code-HEAD GitHub Actions run 40455089755](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/40455089755) at `ed2974d0e28808d86567f8ebb5694898758497f4`: 24/24 workflows successful; dedicated V002 Python 3.11 and 3.12 jobs individually passed 6 V002 tests and 269 full discovered tests; byte-identical two-root source/view replay and independent source/view oracles passed; Chromium headless smoke passed for F022 C13/C01 and F023 Q02/Q04. [Screenshots](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/40455089755) are available as workflow artifact `v002-browser-screenshots` (ID 12711874203). Visual inspection by the assistant confirms displayed labels and physical-radius-with-symbolic-crosshair separation, **not** actual human interactive usability acceptance.
**STOP before main/adoption:** Researcher's manual interaction and comprehension check has not been evidenced. Preserve `Draft`, keep the untouched frozen contract, have an independent reviewer reconcile historical P1/P2 review threads and check exact-final-HEAD CI after this documentation update, then record explicit limited technical adoption versus scientific support (separate gates). No new physical data/model or agent feedback is authorized by a successful screenshot.


## 2026-10-27 — revised compact six-slot UI prototype (separate design + implementation Draft)
The prior vertically stacked interface was rejected by the researcher for excessive length and unclear panel intentions despite green technical CI. Follow the **contract-first** [design PR #90](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/90) and machine map [`v002.workspace.layout.v1`](../../contracts/v002.workspace.layout.v1.json); candidate code is isolated on [stacked UI PR #91](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/91), not merged into parent viewer yet. Six owners only; dominant recessed grayscale centre Arena, left setup/individual cells, right audit/schema and disabled future placeholders, fixed-bottom historical Timeline with internal scrolling and sample stepping. No live stream, seventh panel, unrecorded XY interpolation, physics/policy feedback, modified v1 archive/schema, or extra logical module.
The first Chromium layout/scroll trial ran on [Actions 40505968565](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/40505968565); [screenshots artifact 12734732812](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/actions/runs/40505968565) shows *example verified archive projections*, not independent scientific or human usability proof. Later small table/label polish and exact contracted header geometry must pass their own exact SHA before review. The prior V002 source-observer acceptance gate is still open; new layout needs explicit human usability approval prior to integration.

## 2026-10-27 — integrated candidate: CI pass, real offline manual browser review enabled
The new six-panel layout was positively received from a visual screenshot. Design PR #90 and UI PR #91 were merged only into the **candidate V002 branch** at `c23554c5a5e96552d4893cc92b42af867868fdff`; the exact integrated head passed **24/24 Actions**, an exact-sha Codex review reported **zero findings**, and all original eight review threads remain resolved. This is technical evidence only, not human hands-on approval and not a main merge.
Dedicated V002 CI now uploads four verified offline `index.html` + `view.json` pairs as `v002-offline-manual-review` for C13/C01 (off-grid TOI), C05/C06 (miss/hit), C07/C08 (grazing/separation) and F023 Q02/Q04 (private energy acceptance/rejection). Instructions and the evidence/acceptance boundary are in [REVIEW_GATE.md](REVIEW_GATE.md). The production frozen JSON schema, F022/F023 source cases and six owner mapping remain unchanged. The packaging branch's exact-head CI must pass before declaring the artifacts downloadable.
**STOP:** candidate PR #89 stays Draft/not main-adopted pending actual researcher HTML interaction and a recorded PASS/FAIL/INCONCLUSIVE verdict.
