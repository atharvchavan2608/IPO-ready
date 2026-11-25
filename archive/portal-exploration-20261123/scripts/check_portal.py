"""Optional browser verification; requires installed Playwright and Chrome."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT=Path('outputs/portal')
OUT.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
    browser=pw.chromium.launch(channel='chrome',headless=True)
    try:
        page=browser.new_page(viewport={'width':1440,'height':1050},device_scale_factor=1)
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8766',wait_until='networkidle')
        page.locator('#app').wait_for(state='visible')
        assert page.locator('#company-name').inner_text()=='Indian Gas Exchange'
        assert '61.01' in page.locator('#metrics').inner_text()
        page.screenshot(path=str(OUT/'dashboard-desktop.png'),full_page=True)
        page.select_option('#period','2024-03-31')
        assert 'Unavailable' in page.locator('#metrics').inner_text()
        assert '-8.24' in page.locator('#metrics').inner_text()
        page.locator('[data-evidence="fact:operating_revenue"]').first.click()
        assert '34.85' in page.locator('#fact-detail').inner_text()
        assert 'SHA' not in page.locator('#fact-detail').inner_text() or 'Evidence hash' in page.locator('#fact-detail').inner_text()
        page.get_by_role('button',name='Close evidence').click()
        page.select_option('#period','2026-03-31')
        page.locator('.nav-item[data-view="scenario"]').click()
        page.locator('#profit-pct').evaluate("el=>{el.value='50';el.dispatchEvent(new Event('input',{bubbles:true}));}")
        page.get_by_role('button',name='Calculate sensitivity').click()
        page.locator('#scenario-result').get_by_text('33.56',exact=True).wait_for()
        page.select_option('#unit','million')
        page.locator('#scenario-result').get_by_text('335.56',exact=True).wait_for()
        with page.expect_download() as download:
            page.locator('#export').click()
        saved=OUT/'downloaded-snapshot.json'
        download.value.save_as(str(saved))
        exported=json.loads(saved.read_text())
        assert exported['export_context']['scenario']['hypothetical_continuing_profit']=='33.5555'
        assert exported['export_context']['display_unit']=='INR million'
        page.locator('.nav-item[data-view="references"]').click()
        page.get_by_role('button',name='Open reference').click()
        assert page.locator('#company-status').inner_text()=='RECENT IPO REFERENCE'
        assert '166,013.10' in page.locator('#metrics').inner_text() or '1,66,013.10' in page.locator('#metrics').inner_text()
        page.locator('[data-company="igx"]').click()
        page.select_option('#unit','crore')
        page.set_viewport_size({'width':390,'height':844})
        page.screenshot(path=str(OUT/'dashboard-mobile.png'),full_page=True)
        for view in ['research','scenario','references','evidence']:
            page.locator(f'.nav-item[data-view="{view}"]').click()
            assert page.locator(f'#view-{view}').is_visible()
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'), view
        assert not errors,errors
        (OUT/'browser-check.json').write_text(json.dumps({'passed':True,'views':['research','scenario','references','evidence'],'desktop':[1440,1050],'mobile':[390,844],'browser_errors':errors,'scenario_profit_crore':'33.5555','checks':['period selection','negative cash conversion','evidence dialog','Python scenario','unit conversion','snapshot download','reference status','mobile overflow']},indent=2)+'\n')
        print('Portal browser checks passed; screenshots and downloaded snapshot retained.')
    finally: browser.close()
