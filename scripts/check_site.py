"""Browser walkthrough check with screenshots (desktop 1440 px, mobile 390 px).

Requires the server: python -m ipo_ready.server   then   python scripts/check_site.py [--base URL]
Uses Playwright with the installed Microsoft Edge (channel 'msedge'), falling back to bundled Chromium.
Writes outputs/preview/*.png and outputs/preview/check_results.json.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "outputs" / "preview"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8765/")
    ap.add_argument("--pages", default="1,2,3")
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    a = ap.parse_args()
    out = a.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    results, errors = [], []

    def check(name, ok, detail=""):
        results.append({"check": name, "ok": bool(ok), "detail": detail})
        print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="msedge")
        except Exception:
            browser = p.chromium.launch()
        for label, vp in (("desktop", {"width": 1440, "height": 900}), ("mobile", {"width": 390, "height": 844})):
            ctx = browser.new_context(viewport=vp, device_scale_factor=1)
            page = ctx.new_page()
            portfolio_outage = False
            def record_console(message):
                url = message.location.get("url", "")
                allocation_url = "/api/portfolio/allocate?" in url
                expected_validation = "status of 400" in message.text and (
                    "/api/screen?query=Unknown+" in url or (allocation_url and "amount=12x" in url))
                expected_outage = portfolio_outage and allocation_url and "status of 503" in message.text
                if message.type == "error" and not (expected_validation or expected_outage):
                    errors.append(f"{label} console {message.type}: {message.text}")

            page.on("console", record_console)
            page.on("pageerror", lambda e: errors.append(f"{label} pageerror: {e}"))

            # ---- Page 1 ----
            page.goto(a.base, wait_until="domcontentloaded")
            page.wait_for_selector(".kpi")
            name = page.text_content("#co-name")
            check(f"{label}: home opens Page 1 with default unlisted company", "Indian Gas Exchange" in name, name)
            check(f"{label}: nav marks Page 1 current", page.get_attribute('nav.main a[aria-current="page"]', "href") == "index.html")
            igx = page.request.get(a.base + "data/current/company/igx.json").json()
            cash_flow_available = "cash_flow" in igx
            catalogue_available = "ratios" in igx
            if catalogue_available:
                page.get_by_text("Choose ratios", exact=True).click()
                page.get_by_role("checkbox", name="Quick ratio", exact=True).check()
                page.get_by_text("Choose ratios", exact=True).click()
            kpis = page.locator(".kpi").count()
            qr = page.locator(".kpi:has(span.k:text-is(\"Quick ratio\"))").inner_text()
            review_repaired = igx["metrics"]["FY2026"]["quick_ratio"].get("inventory_state") == "assumed_nil"
            quick_ratio_text = "Withheld pending review" if cash_flow_available and not review_repaired else "×"
            check(f"{label}: KPI grid shows the expected quick ratio state",
                  kpis >= 10 and quick_ratio_text in qr, qr.replace("\n", " | "))
            if review_repaired:
                page.locator('.kpi:has(span.k:text-is("Quick ratio"))').click()
                check(f"{label}: quick ratio opens issuer balance sheet and inventory note",
                      page.locator('#drawer-body a[href$="#page=5"]').count() == 2
                      and page.locator('#drawer-body a[href$="#page=54"]').count() == 1)
                page.click("#drawer-close")
            inv = page.locator(".kpi:has(span.k:text-is(\"Inventory\"))").inner_text()
            check(f"{label}: inventory shows honest 'Not applicable' state", "Not applicable" in inv, inv.replace("\n", " | "))
            no_overflow = page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1")
            check(f"{label}: no horizontal page overflow", no_overflow)
            peer_target = page.get_attribute("#company-peers", "href")
            check(f"{label}: the home company links to its reviewed peer coverage",
                  peer_target == ("compare.html?add=igx&period=FY2026#workspace" if catalogue_available
                                  else "compare.html?company=igx#peer-coverage"))
            check(f"{label}: IGX reconciliation cites the employee share trust scope",
                  page.locator('#recon a[href$="#page=55"]').count() == 1)
            check(f"{label}: unlisted discovery excludes the NSE listing-status conflict",
                  page.locator('#discovery .disc[data-id="nse"]').count() == 0)
            page.screenshot(path=str(out / f"page1-{label}.png"), full_page=True)

            # evidence drawer from a KPI
            page.locator(".kpi:has(span.k:text-is(\"Revenue from operations\"))").click()
            page.wait_for_selector("#drawer[open]")
            dtxt = page.inner_text("#drawer-body")
            check(f"{label}: KPI opens evidence with source URL and hash",
                  ("wwipl.com" in dtxt or "igxindia.com" in dtxt) and "SHA-256" in dtxt)
            if label == "desktop":
                page.screenshot(path=str(out / "page1-desktop-evidence.png"))
            page.click("#drawer-close")

            if cash_flow_available:
                statements = page.locator("#statements")
                cash = statements.locator("#statement-body")
                statements.get_by_role("button", name="Balance Sheet").click()
                check(f"{label}: Balance Sheet opens on Page 1", "Total assets" in cash.inner_text())
                statements.get_by_role("button", name="Profit & Loss").click()
                check(f"{label}: Profit & Loss opens on Page 1", "Revenue from operations" in cash.inner_text())
                cash_tab = statements.get_by_role("button", name="Cash Flow", exact=True)
                cash_tab.click()
                for fy, opening, closing in (("FY2024", "18.736", "15.464"), ("FY2025", "15.464", "13.217"),
                                             ("FY2026", "13.217", "3.957")):
                    page.select_option("#sel-period", fy)
                    check(f"{label}: {fy} issuer cash reconciles with disclosed balances",
                          cash.locator("[data-reconciliation]").get_attribute("data-reconciliation") == "reconciled"
                          and cash.locator('[data-line="opening"]').inner_text().endswith(opening)
                          and cash.locator('[data-line="closing"]').inner_text().endswith(closing))
                cash.locator('[data-line="cfo"] button').click()
                check(f"{label}: issuer cash evidence opens the original filing",
                      page.locator('#drawer-body a[href$="#page=7"]').count() == 1
                      and "1,566.85 INR million" in page.inner_text("#drawer-body"))
                page.click("#drawer-close")
                cash.get_by_text("Compare with WWIPL", exact=True).click()
                check(f"{label}: provider and issuer values show their 0.205 crore gap",
                      all(value in cash.locator(".cash-compare").inner_text() for value in ("156.685", "156.89", "-0.205")))
                check(f"{label}: cash flow fits the page on this width",
                      page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"))
                cash.get_by_text("Cash flow details", exact=True).click()
                check(f"{label}: details show settlement, working capital, cash capex, leases and dividends",
                      all(value in cash.inner_text() for value in ("3.671", "138.628", "-0.698", "-0.831", "-11.250")))
                # Keep the sticky nav out of the cropped statement capture.
                screenshot_style = page.add_style_tag(content="header.site { position: static }")
                if label == "desktop":
                    statements.screenshot(path=str(out / "cash-flow-desktop-details.png"))
                cash.get_by_text("Cash flow details", exact=True).click()
                statements.screenshot(path=str(out / f"cash-flow-{label}.png"))
                screenshot_style.evaluate("style => style.remove()")
                page.select_option("#sel-period", "FY2022")
                check(f"{label}: older IGX looks partial and keeps missing balances and blank financing separate",
                      cash.locator("[data-reconciliation]").get_attribute("data-reconciliation") == "partial"
                      and "Unavailable" in cash.locator('[data-line="opening"]').inner_text()
                      and "Unavailable (blank)" in cash.locator('[data-line="cff"]').inner_text())
                page.select_option("#sel-company", "polymatech")
                page.wait_for_function("document.querySelector('#co-name').textContent.includes('Polymatech')")
                if review_repaired:
                    pe_card = page.locator('.kpi:has(span.k:text-is("P/E at quote"))')
                    pe_card.click()
                    check(f"{label}: Polymatech drawer distinguishes reported and proxy earnings",
                          all(token in page.inner_text("#drawer-body") for token in ("9.07", "3.82", "Reported basic EPS"))
                          and cash.locator("[data-reconciliation]").get_attribute("data-reconciliation") == "partial")
                    page.click("#drawer-close")
                page.goto(a.base + "?company=igx&period=FY2026&statement=cash-flow", wait_until="networkidle")
                check(f"{label}: the Cash Flow deep link restores its period and view",
                      "FY2026" in cash.locator("h3").inner_text() and
                      cash_tab.get_attribute("aria-pressed") == "true")

            # period change
            opts = page.eval_on_selector_all("#sel-period option", "els => els.map(e => e.value)")
            if len(opts) > 1:
                page.select_option("#sel-period", opts[1])
                page.wait_for_timeout(150)
                check(f"{label}: period switch updates KPIs", opts[1] in page.text_content("#kpi-aside"), page.text_content("#kpi-aside"))
                check(f"{label}: URL carries period", f"period={opts[1]}" in page.url, page.url)

            # chart view toggle
            page.get_by_text("Choose charts", exact=True).click()
            page.get_by_role("checkbox", name="Liquidity", exact=True).check()
            check(f"{label}: liquidity chart renders", page.locator('[data-chart="liquidity"] svg path').count() > 0)

            # discovery switches company
            first = page.locator("#discovery .disc").first
            target = first.get_attribute("data-id")
            first.click()
            page.wait_for_function(f"new URL(location.href).searchParams.get('company') === '{target}'")
            page.wait_for_timeout(200)
            check(f"{label}: discovery opens another unlisted company", target != "igx", page.text_content("#co-name"))

            # a lender: NPA expected, quick ratio inapplicable
            page.goto(a.base + "?company=herofincorp", wait_until="networkidle")
            page.wait_for_selector(".kpi")
            npa = page.locator(".kpi:has(span.k:text-is(\"NPA\"))").inner_text()
            check(f"{label}: lender shows NPA gap (expected but not disclosed)", "Not" in npa and "expected" in npa, npa.replace("\n", " | "))

            # agent live run (back on IGX)
            page.goto(a.base + "?company=igx", wait_until="networkidle")
            page.wait_for_selector(".kpi")
            if label == "desktop":
                page.click("#agent-run")
                page.wait_for_function("document.querySelector('#agent-status').textContent.includes('Ran just now') || document.querySelector('#agent-status').textContent.includes('unavailable')", timeout=60000)
                st = page.text_content("#agent-status")
                check("desktop: agent runs live through the Python API", "Ran just now" in st, st)
                page.locator("#agent details").first.evaluate("e => e.open = true")
                page.locator("#agent-h").scroll_into_view_if_needed()
                page.screenshot(path=str(out / "page1-desktop-agent.png"))

            # ---- direct URLs for Pages 2 and 3 ----
            for pg, fname in (("2", "compare.html"), ("3", "portfolio.html")):
                if pg not in a.pages.split(","):
                    continue
                route = fname + "?legacy=1" if pg == "3" and catalogue_available else fname
                r = page.goto(a.base + route, wait_until="networkidle")
                cur = page.get_attribute('nav.main a[aria-current="page"]', "href")
                check(f"{label}: Page {pg} direct URL opens", r.ok and cur == fname, f"HTTP {r.status}, current={cur}")
                if pg == "2":
                    if catalogue_available:
                        cols = page.locator("#compare-columns")
                        igx_column = cols.locator('[data-company="igx"]')
                        page.locator('#workspace-benchmarks [data-add="nse-iex"]').click()
                        iex_column = cols.locator('[data-company="nse-iex"]')
                        iex_column.wait_for()
                        operating = igx_column.locator('[data-compare-metric="revenue"]')
                        check(f"{label}: workspace brings in the reviewed IEX operating benchmark",
                              "Comparable with IEX" in operating.inner_text()
                              and "Comparable with IGX" in iex_column.locator('[data-compare-metric="revenue"]').inner_text()
                              and page.locator("#peer-coverage").count() == 0)
                        operating.get_by_role("button").click()
                        page.wait_for_selector("#drawer[open]")
                        check(f"{label}: displayed IGX operating revenue opens raw PDF evidence",
                              "610.05" in page.inner_text("#drawer-body")
                              and page.locator('#drawer-body a[href$="#page=6"]').count() == 1)
                        page.click("#drawer-close")
                        check(f"{label}: annual CFO keeps the reporting-perimeter distinction",
                              "reporting basis differs" in igx_column.locator('[data-compare-metric="cfo"]').inner_text())
                    else:
                        page.wait_for_selector("#peer-comparison table")
                        check(f"{label}: IGX opens with standalone operating benchmarks",
                              "2 of 4" in page.inner_text("#peer-status")
                              and page.locator("#peer-comparison thead th").count() == 4
                              and "Standalone" in page.inner_text("#peer-comparison thead"))
                        check(f"{label}: eight domains have multiple unlisted company choices",
                              page.locator("#peer-domain option").count() == 8
                              and all(count >= 2 for count in page.evaluate("""() => [...document.querySelector('#peer-domain').options].map(option => {
                                const domain = option.parentElement;
                                domain.value = option.value;
                                domain.dispatchEvent(new Event('change', { bubbles: true }));
                                return document.querySelector('#peer-company').options.length;
                              })""")))
                        page.select_option("#peer-domain", "exchanges")
                        page.locator('#peer-comparison button[data-row="0"][data-col="0"]').click()
                        page.wait_for_selector("#drawer[open]")
                        check(f"{label}: displayed IGX value opens raw PDF evidence",
                              "610.05" in page.inner_text("#drawer-body")
                              and page.locator('#drawer-body a[href$="#page=6"]').count() == 1)
                        page.click("#drawer-close")
                        page.locator("#peer-context summary").first.click()
                        check(f"{label}: candidacy view links the standalone statement",
                              "standalone basis" in page.inner_text('[data-symbol="IEX"]')
                              and page.locator('[data-symbol="IEX"] a[href$="/IEX/#profit-loss"]').count() == 1)
                        check(f"{label}: dated plans and reporting link to opened sources",
                              page.locator('#peer-context a[href$="#page=250"]').count() == 1
                              and "13.28 million MMBtu" in page.inner_text("#peer-context"))

                        page.select_option("#peer-domain", "healthcare")
                        page.locator("#peer-context summary").first.click()
                        check(f"{label}: pharmacy coverage explains the unverified issuer basis",
                              "No candidates" in page.inner_text("#peer-status")
                              and "Issuer reporting basis unverified" in page.inner_text('[data-symbol="MEDPLUS"]'))
                        page.select_option("#peer-company", "pharmed")
                        check(f"{label}: new pharmaceuticals company has two listed benchmarks",
                              "2 of 2" in page.inner_text("#peer-status")
                              and "Provider labels shares delisted" in page.inner_text("#peer-output"))
                        page.select_option("#peer-company", "grouppharma")
                        page.locator("#peer-context summary").first.click()
                        check(f"{label}: conflicting issuer profit withholds the comparison",
                              "Verified issuer revenue or profit is unavailable" in page.inner_text("#peer-context")
                              and page.locator("#peer-comparison table").count() == 0)
                        page.select_option("#peer-domain", "materials")
                        page.locator("#peer-context summary").first.click()
                        check(f"{label}: carbon cohort handles a mismatched year-end",
                              "1 of 3" in page.inner_text("#peer-status")
                              and "Different annual period" in page.inner_text('[data-symbol="RAIN"]'))
                        check(f"{label}: annual P/E explains losses in the carbon cohort",
                              "Loss-making" in page.inner_text("#peer-comparison tbody"))
                        page.select_option("#peer-domain", "technology")
                        check(f"{label}: semiconductor cohort preserves the choice in the URL",
                              "company=polymatech" in page.url and "No candidates" in page.inner_text("#peer-status"))
                        page.select_option("#peer-domain", "airports")
                        check(f"{label}: CIAL airport comparison uses the issuer’s consolidated P&L",
                              "1 of 1" in page.inner_text("#peer-status")
                              and page.locator('#peer-output a[href$="#page=127"]').count() == 1)
                        page.select_option("#peer-domain", "automotive")
                        check(f"{label}: Axles India links to a compatible automotive benchmark",
                              "1 of 2" in page.inner_text("#peer-status") and "AUTOAXLES" in page.inner_text("#peer-comparison thead"))
                        page.select_option("#peer-domain", "consumer")
                        page.select_option("#peer-company", "csk")
                        check(f"{label}: cricket franchise shows an honest no-candidate state",
                              "No listed candidates" in page.inner_text("#peer-status"))
                        page.select_option("#peer-domain", "exchanges")
                    page.wait_for_function("document.querySelector('#screen-status').textContent.includes('companies matched')")
                    summary = page.text_content("#screen-status")
                    check(f"{label}: screener has no horizontal page overflow",
                          page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"))
                    if cash_flow_available and not review_repaired:
                        check(f"{label}: CEO screen withholds Polymatech P/E", "0 of 24" in summary
                              and "7 undecided" in summary)
                    else:
                        check(f"{label}: default screen shows all three metrics without scrolling",
                              page.locator("#screen-output .tbl-wrap").evaluate("e => e.scrollWidth <= e.clientWidth + 1"))
                    page.locator("#screen-coverage summary").click()
                    evidence = page.locator("#screen-coverage a")
                    check(f"{label}: coverage explains gaps and links the NSE exclusion",
                          "available for" in page.inner_text("#screen-coverage-body")
                          and evidence.get_attribute("href").endswith("#page=18"))
                    page.locator("#screen-coverage summary").click()
                    page.evaluate("window.scrollTo(0, 0)")
                    page.screenshot(path=str(out / f"page{pg}-{label}.png"), full_page=True)

                    page.fill("#screen-query", "Market capitalization > 10000000")
                    page.get_by_role("button", name="Run screen").click()
                    page.wait_for_selector("#screen-output .notice")
                    check(f"{label}: empty screen offers a recovery step",
                          "Try widening" in page.inner_text("#screen-output"))

                    page.fill("#screen-query", "Unknown > 5")
                    with page.expect_response(lambda response: "/api/screen?query=Unknown+" in response.url) as validation:
                        page.get_by_role("button", name="Run screen").click()
                    page.wait_for_selector('#screen-query[aria-invalid="true"]')
                    check(f"{label}: invalid field gets a readable 400 response",
                          validation.value.status == 400 and "Unknown field" in page.inner_text("#screen-status"))

                    page.get_by_role("button", name="Use CEO example").click()
                    page.wait_for_function("document.querySelector('#screen-status').textContent.includes('companies matched')")
                    check(f"{label}: example restores results after an invalid query", page.text_content("#screen-status") == summary)
                    if cash_flow_available and not review_repaired:
                        page.fill("#screen-query", "Market capitalization > 10000")
                        page.get_by_role("button", name="Run screen").click()
                    link = page.locator("#screen-output tbody th a").first
                    link.wait_for()
                    result_href, result_name = link.get_attribute("href"), link.inner_text()
                    link.click()
                    page.wait_for_selector(".kpi")
                    actual, expected = urlsplit(page.url), urlsplit(result_href)
                    check(f"{label}: result opens the matching company evidence page",
                          actual.path == "/" + expected.path
                          and parse_qs(actual.query).get("company") == parse_qs(expected.query)["company"]
                          and result_name == page.inner_text("#co-name"), actual.path + "?" + actual.query)
                    continue
                page.wait_for_selector('[data-instrument="MCX"]')
                page.wait_for_selector("#portfolio-holdings table")
                igx_scenario = page.request.get(a.base + "api/portfolio/allocate?company=igx").json()
                check(f"{label}: the allocation API explains why the IGX lot is skipped",
                      igx_scenario["unlisted"]["state"] == "minimum_lot_exceeds_limit"
                      and all(s in page.inner_text("#portfolio-scenario-result")
                              for s in ("₹5,00,000", "One dealer lot costs", "The scenario limit", f'{igx_scenario["scenario"]["stress_loss_pct"]}%')))
                legend = page.locator(".portfolio-legend tbody tr")
                check(f"{label}: the pie and risk legend show the Python risk weights",
                      page.locator("#portfolio-pie").evaluate("e => getComputedStyle(e).backgroundImage.startsWith('conic-gradient')")
                      and legend.count() == 3
                      and all(legend.nth(i).locator("td").first.inner_text() == f'{igx_scenario["scenario"]["risk_mix"][band]["weight_pct"]}%'
                              for i, band in enumerate(("low", "medium", "high"))))
                page.get_by_role("button", name="Baseline", exact=True).click()
                check(f"{label}: baseline switch updates the holdings table and pie label",
                      page.locator('#portfolio-holdings [data-holding="igx"]').count() == 0
                      and page.inner_text("#portfolio-pie-label") == "Baseline risk mix")
                page.get_by_role("button", name="Scenario", exact=True).click()
                check(f"{label}: portfolio names all four instruments and records their latest close date",
                      page.locator("#portfolio-instruments article").count() == 4
                      and "NSE closes through" in page.inner_text("#portfolio-status")
                      and page.locator('[data-instrument="GOLDBEES"]').count() == 1)
                check(f"{label}: bond has a dated coupon and a weekly risk gap",
                      all(s in page.inner_text('[data-instrument="FRSB2020T"]')
                          for s in ("8.05%", "2026", "no exchange series")))
                page.locator('[data-instrument="MCX"] .portfolio-evidence').click()
                page.wait_for_selector("#drawer[open]")
                check(f"{label}: MCX risk evidence links the confirmed split and NSE close",
                      page.locator('#drawer-body a[href$="CML72042.pdf"]').count() == 1
                      and page.locator('#drawer-body a[href*="sec_bhavdata_full"]').count() == 1)
                page.click("#drawer-close")
                check(f"{label}: IGX opens with a dated quote, dealer lot and history gap",
                      page.locator("#portfolio-company").input_value() == "igx"
                      and all(s in page.inner_text("#portfolio-company-detail")
                              for s in ("500 shares", "Captured", "No verified trade series"))
                      and page.locator('#portfolio-company option[value="nse"]').count() == 0)
                page.locator("#portfolio-method summary").click()
                check(f"{label}: methodology gives price and coverage limits",
                      all(s in page.inner_text("#portfolio-method-body") for s in ("weekly closes", "missing weeks", "intraweek")))
                page.locator("#portfolio-method summary").click()
                check(f"{label}: Page 3 fits the viewport", page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"))
                page.evaluate("window.scrollTo(0, 0)")
                page.screenshot(path=str(out / f"page{pg}-{label}.png"), full_page=True)
                page.select_option("#portfolio-company", "ncdex")
                page.wait_for_function("document.querySelector('#portfolio-scenario-result').textContent.includes('dealer lot fits')")
                ncdex_scenario = page.request.get(a.base + "api/portfolio/allocate?company=ncdex").json()
                check(f"{label}: NCDEX selection refreshes the calculated scenario and its baseline",
                      all(f"{ncdex_scenario[side]['stress_loss_pct']}%" in page.inner_text("#portfolio-scenario-result")
                          for side in ("scenario", "baseline"))
                      and parse_qs(urlsplit(page.get_attribute("#portfolio-scenario-json", "href")).query)["company"] == ["ncdex"]
                      and "25,300" in page.inner_text('#portfolio-holdings [data-holding="ncdex"]'))
                page.locator("#portfolio-assumptions summary").click()
                check(f"{label}: assumptions expose exit haircut, shock and original evidence",
                      all(s in page.inner_text("#portfolio-assumptions") for s in ("35% price fall", "25% haircut", "₹4,111.25", "Restricted capital"))
                      and page.get_attribute(".portfolio-lot-note a", "href") == "#portfolio-unlisted")
                page.uncheck("#portfolio-include")
                page.wait_for_function("document.querySelector('.portfolio-lot-note')?.textContent.includes('excludes')")
                check(f"{label}: excluding unlisted resets that position to zero and matches the baseline",
                      page.locator('#portfolio-holdings [data-holding="ncdex"] td').nth(1).inner_text() == "₹0"
                      and all(row.locator("td").first.inner_text() == row.locator("td").last.inner_text() for row in legend.all())
                      and "include_unlisted=false" in page.url)
                page.check("#portfolio-include")
                page.select_option("#portfolio-company", "haldia")
                page.wait_for_function("document.querySelector('#portfolio-scenario-result').textContent.includes('after source checks')")
                check(f"{label}: portfolio withholds suspect quote and links matching company",
                      "Withheld after source checks" in page.inner_text("#portfolio-company-detail")
                      and "Unavailable" in page.inner_text("#portfolio-company-detail")
                      and page.get_attribute("#portfolio-company-detail a", "href") == "index.html?company=haldia"
                      and parse_qs(urlsplit(page.url).query).get("company") == ["haldia"])
                page.select_option("#portfolio-company", "igx")
                page.fill("#portfolio-amount", "1250000")
                calculate = page.get_by_role("button", name="Calculate allocation")
                calculate.click()
                page.wait_for_function("document.querySelector('.portfolio-result-context')?.textContent.includes('₹12,50,000')")
                check(f"{label}: submitting a new amount updates the selected scenario",
                      "Balanced" in page.inner_text(".portfolio-result-context") and "amount=1250000" in page.url)
                page.select_option("#portfolio-tolerance", "growth")
                page.wait_for_function("document.querySelector('#portfolio-scenario-result').textContent.includes('exchange cap reduced the MCX target')")
                check(f"{label}: the growth profile shows one IGX lot and the combined exchange cap",
                      "₹2,44,000" in page.inner_text('#portfolio-holdings [data-holding="igx"]')
                      and page.locator('#portfolio-holdings [data-holding="MCX"] td').first.inner_text() == "19"
                      and "tolerance=growth" in page.url)
                if label == "desktop":
                    page.locator("#portfolio-scenario").screenshot(path=str(out / "page3-desktop-growth.png"))
                scenario_url = page.url
                page.reload(wait_until="networkidle")
                page.wait_for_selector("#portfolio-holdings table")
                check(f"{label}: the scenario link restores the controls and growth holdings",
                      page.locator("#portfolio-amount").input_value() == "1250000"
                      and page.locator("#portfolio-tolerance").input_value() == "growth"
                      and page.locator("#portfolio-company").input_value() == "igx"
                      and page.locator("#portfolio-include").is_checked()
                      and page.locator('#portfolio-holdings [data-holding="MCX"] td').first.inner_text() == "19")
                page.fill("#portfolio-amount", "12x")
                with page.expect_response(lambda response: "amount=12x" in response.url) as invalid_amount:
                    calculate.click()
                page.wait_for_selector('#portfolio-amount[aria-invalid="true"]')
                check(f"{label}: invalid amount shows Python validation and keeps the last valid URL",
                      invalid_amount.value.status == 400 and "₹1 to ₹10 crore" in page.inner_text("#portfolio-scenario-message")
                      and page.locator("#portfolio-holdings table").count() == 0 and page.url == scenario_url)
                page.fill("#portfolio-amount", "1.01")
                page.locator("#portfolio-amount").press("Enter")
                page.wait_for_selector('#portfolio-holdings [data-holding="CASH"]')
                check(f"{label}: ₹1.01 remains all cash and plots a single low-risk slice",
                      "₹1.01" in page.inner_text('#portfolio-holdings [data-holding="CASH"]')
                      and page.inner_text('[data-risk-band="low"] td:first-of-type') == "100.00%"
                      and not page.locator('#portfolio-amount[aria-invalid="true"]').count())
                allocation_route = "**/api/portfolio/allocate?*"
                portfolio_outage = True
                page.route(allocation_route, lambda route: route.fulfill(status=503, json={"error": "fixture"}))
                calculate.click()
                page.wait_for_function("document.querySelector('#portfolio-scenario-message').textContent.includes('Allocation is unavailable')")
                check(f"{label}: an allocation outage leaves instrument and company evidence available",
                      page.locator('[data-instrument="MCX"] .portfolio-evidence').is_visible()
                      and page.locator('#portfolio-company-detail .portfolio-evidence').is_visible()
                      and page.locator("#portfolio-scenario-json").is_hidden())
                page.unroute(allocation_route)
                calculate.click()
                page.wait_for_selector("#portfolio-holdings table")
                portfolio_outage = False
                check(f"{label}: calculating again restores the scenario after the endpoint recovers",
                      "₹1.01" in page.inner_text(".portfolio-result-context") and page.locator("#portfolio-scenario-json").is_visible())
                page.goto(a.base + "portfolio.html?legacy=1&company=pharmed", wait_until="networkidle")
                check(f"{label}: direct unlisted selection preserves the delisted source label",
                      page.locator("#portfolio-company").input_value() == "pharmed"
                      and "Provider labels shares delisted" in page.inner_text("#portfolio-company-detail"))
            ctx.close()
        browser.close()
    check("no console or page errors", not errors, "; ".join(errors[:5]))
    (out / "check_results.json").write_text(json.dumps({"ran_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "base": a.base,
                                                        "results": results, "errors": errors}, indent=2), encoding="utf-8")
    failed = [r for r in results if not r["ok"]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed; screenshots in {out}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
