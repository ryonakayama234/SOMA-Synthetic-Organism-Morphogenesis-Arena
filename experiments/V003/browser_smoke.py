"""Real Chromium checks of V003's six-owner offline UI; screenshots are NOT physics evidence."""
from __future__ import annotations
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

OWNERS={"setup","arena","cells","timeline","evidence","system"}

def inspect(prepare_html,verified_html,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True)
        page=browser.new_page(viewport={"width":1500,"height":950},device_scale_factor=1)
        for name,path in [("prepare",Path(prepare_html)),("verified",Path(verified_html))]:
            page.goto(path.resolve().as_uri())
            owners=set(page.locator("section[data-panel]").evaluate_all(
                "(nodes)=>nodes.map(el=>el.getAttribute('data-panel'))"))
            if owners!=OWNERS or page.locator("section[data-panel]").count()!=6:
                raise AssertionError("V003 must use exactly the six inherited owners")
            if page.locator("#candidate option").count()!=11:
                raise AssertionError("not the 11 preregistered y candidates")
            if not page.locator("body").evaluate("(e)=>e.scrollHeight<=e.clientHeight+1"):
                raise AssertionError("document body must not scroll at 1500x950")
            page.locator("#time-select").select_option("4")
            if page.locator("#world-original circle").count()!=2:
                raise AssertionError("original disk geometry absent")
            if name=="prepare":
                if page.locator("#world-derived circle").count()!=0:
                    raise AssertionError("unverified derived XY shown in preparation")
                if "NOT GENERATED" not in page.locator("#derived-status").inner_text():
                    raise AssertionError("missing derived non-observation label")
            else:
                if page.locator("#world-derived circle").count()!=2:
                    raise AssertionError("verified stored derived XY absent")
                if "VERIFIED COMPARISON" not in page.locator("#header-status").inner_text():
                    raise AssertionError("trust status absent")
                event_rows=page.locator("#timeline-list .time-row").filter(has_text="contact")
                if event_rows.count()!=1:
                    raise AssertionError("expected one genuine off-grid contact event")
                event_rows.first.click()
                if "ACTUAL ARCHIVED EVENT" not in page.locator("#event-detail").inner_text():
                    raise AssertionError("off-grid archived event inspector absent")
            with page.expect_download() as download:
                page.locator("#export").click()
            destination=out/(name+"-request.json")
            download.value.save_as(destination)
            from experiments.V003.run_suite import accept_request
            accept_request(destination)
            page.screenshot(path=str(out/(name+".png")),full_page=True)
        browser.close()
    return {"browser":"chromium","six_owners":True,"prepare_no_derived":True,
            "verified_real_event":True,"canonical_request_download":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--prepare",type=Path,required=True)
    p.add_argument("--verified",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    print(inspect(a.prepare,a.verified,a.out))
if __name__=="__main__": main()
