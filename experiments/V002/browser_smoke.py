"""Real Chromium/Playwright DOM+SVG acceptance smoke for verified offline V002 HTML.

Screenshots illustrate UI operation only and are not source science evidence.
This executable is intentionally excluded from normal Python unittest discovery.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright


PANEL_TITLES = ("Setup", "Arena", "Cells", "Timeline", "Evidence", "System/Data")


def check_one(browser, path: Path, *, f023: bool, out: Path):
    page = browser.new_page(viewport={"width": 1500, "height": 950},
                            device_scale_factor=1)
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(path.resolve().as_uri(), wait_until="load")
    assert page.title() == "SOMA · V002 Counterfactual Observatory (read-only)"
    assert page.locator("main > section").count() == 6, "six existing panel owners"
    for title in PANEL_TITLES:
        assert any(title in x for x in page.locator("main h2").all_text_contents()), title
    assert page.locator("#arena .scene").count() == 2
    assert page.locator("#arena svg").count() == 2
    assert page.locator("#arena svg circle").count() == 4, "two disks per saved world"
    assert page.locator("#arena svg").first.get_attribute("viewBox") == "0 0 600 420"
    assert "X (m)" in page.locator("#arena").inner_text()
    assert "Y (m)" in page.locator("#arena").inner_text()
    assert "unchanged" in page.locator("#diff").inner_text(), "complete input map"
    assert page.locator("#diff tr").count() == (22 if f023 else 16)
    assert "PASS" in page.locator("#evidence").inner_text()
    assert "read-only" in page.locator("body").inner_text().lower()
    if f023:
        assert "insufficient_private_budget" in page.locator("#cells").inner_text()
        page.locator("#eventPicker").select_option("0")
        assert "EXACT_POST_SAMPLE_AT_TIME" in page.locator("#eventNote").inner_text()
        assert "not a synchronized pre-event" in page.locator("#eventNote").inner_text()
    else:
        assert "NOT MODELED" in page.locator("#cells").inner_text()
        # Frozen C13 vs C01: huge world-scale; physical 0.5 m disks must be
        # SUB-PIXEL SVG radii, not artificially enlarged overlapping circles.
        radius = float(page.locator("#arena .scene").first.locator("svg circle").first.get_attribute("r"))
        assert 0.0 < radius < 1.0, f"falsely inflated disk radius {radius}"
        page.locator("#eventPicker").select_option("0")
        assert "NO_RECORDED_SNAPSHOT_AT_TIME" in page.locator("#eventNote").inner_text()
        assert "0.095" in page.locator("#eventNote").inner_text()
    page.locator("#sampleTime").select_option("0.5")
    assert page.locator("#arena .scene").count() == 2
    assert "sample t=0.5 s" in page.locator("#arena").inner_text()
    assert not errors, f"browser JS runtime error(s): {errors}"
    out.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(out / ("f023-Q02-Q04.png" if f023 else "f022-C13-C01.png")),
                    full_page=True)
    page.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--f022", type=Path, required=True)
    ap.add_argument("--f023", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            check_one(browser, a.f022, f023=False, out=a.out)
            check_one(browser, a.f023, f023=True, out=a.out)
        finally:
            browser.close()
    print("V002_BROWSER_SMOKE_PASS: 6 panels, 2 XY scenes, exact events,"
          " radius scale, frozen source inputs, F022 N/A, F023 ledgers")


if __name__ == "__main__":
    main()
