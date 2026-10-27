# V002 — offline human UI review

**Candidate only.** These are verified, archived, read-only 2D views. Opening HTML does not start a physical simulation. Automated browser checks and screenshots are not human interactive acceptance.

## Open the actual controls
1. Download the **v002-offline-manual-review** artifact from the latest successful V002 workflow for [PR #89](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/89), and unzip it.
2. Double-click an `index.html` inside one of the four case folders on a desktop browser (Windows supported). At 1500×950, all six panels should remain visible without vertically growing the overall page. **Arena** is central; **Timeline** is fixed at the bottom.
3. In **Timeline**, select a saved sample time or use the ◀/▶ controls. Scroll the old event history **inside** Timeline and select a recorded contact or action. An exact off-grid event must not create an interpolated frame in Arena.
4. In **Setup**, scroll the full original input field map (`=` unchanged, `Δ` different), including unchanged fields. **Evidence** reveals source verifier/trust provenance. Unimplemented System/Data slots are disabled reservations, not simulated behaviour.
5. Confirm that each data type belongs in the intended panel and that short labels are sufficient without instructions filling the screen.

## Four source control pairs

| Folder | What must be preserved |
| --- | --- |
| `F022-C13-vs-C01` | The C13 contact at **0.095 s** is an exact archived event, not a saved grid frame. Other world: **NO_RECORDED_SNAPSHOT_AT_TIME**. F022 motor and ledger: **NOT MODELED**. At large world scale real disk radii can be subpixel; center crosshairs are symbolic. |
| `F022-C05-vs-C06` | C05 missed: zero *recorded contact rows*, no fake null-time event. C06 has a real recorded contact. |
| `F022-C07-vs-C08` | `grazing_zero_impulse` is different from a separating no-contact case. Complete Setup inputs may differ in more than one field; do not infer a single cause. |
| `F023-Q02-vs-Q04` | F023 private action and ledger per A/B, Q02 A accepted with **200 µJ**, Q04 A rejected with **insufficient_private_budget** at **199 µJ**. At t=0 the stored sample is *post-action*. |

## Record a real researcher verdict
After interacting with the HTML, record **PASS / FAIL / INCONCLUSIVE** and concrete observations under [issue #86](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/86). Include exact checkout SHA from `BUILD.txt`, browser and screen size, the pairs and controls tried, whether exact event vs saved sample was understandable, and anything difficult or misleading.

Visual praise alone does not establish that the offline browser controls were tried. Do not merge parent V002 PR #89 to `main` until the frozen human browser acceptance gate is satisfied.

`SHA256SUMS.txt` helps detect accidental changes inside the downloaded ZIP; it cannot independently establish trust in the original sources. Authoritative source and derived-view oracles ran in the referenced GitHub Actions checkout before publication. No new panel, source archive write, agent observation input, interpolation, or new physical claim is authorized.
