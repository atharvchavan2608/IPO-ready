// Local demo smoke test. Optional: pass the installed Playwright module path.
const {chromium} = require(process.argv[2] || 'playwright');
(async () => {
  const browser = await chromium.launch({headless:true,channel:'chrome'});
  try {
    const page = await browser.newPage({viewport:{width:1360,height:1000}});
    const errors=[];
    page.on('pageerror',e=>errors.push(String(e)));
    const target=process.argv[3] ? require('node:url').pathToFileURL(require('node:path').resolve(process.argv[3])).href : 'http://127.0.0.1:8765';
    await page.goto(target);
    await page.getByText('Analysis complete · FY21',{exact:false}).waitFor();
    await page.screenshot({path:'outputs/poc/dashboard-desktop.png',fullPage:true});
    await page.selectOption('#period','9M Dec-2021');
    await page.click('#run');
    await page.getByText('Analysis complete · 9M Dec-2021',{exact:false}).waitFor();
    if(!(await page.locator('.cards').innerText()).includes('0.029x')) throw Error('Interim ratio mismatch');
    const downloadEvent = page.waitForEvent('download');
    await page.click('#download');
    const download = await downloadEvent;
    await download.saveAs('outputs/poc/downloaded-report.json');
    await page.setViewportSize({width:390,height:844});
    await page.screenshot({path:'outputs/poc/dashboard-mobile.png',fullPage:true});
    if(await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth)) throw Error('Mobile horizontal overflow');
    let invalidPeriod='covered by Python unit test in offline mode';
    if(!process.argv[3]){
      const bad=await page.request.get('http://127.0.0.1:8765/api/report?period=invalid');
      if(bad.status()!==400) throw Error('Invalid period accepted');
      invalidPeriod=bad.status();
    }
    if(errors.length) throw Error(errors.join('\n'));
    console.log(JSON.stringify({browserErrors:errors,download:download.suggestedFilename(),invalidPeriod,mobileOverflow:false,target}));
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exit(1)});
