// Optional local browser check. Configure a Playwright module and installed
// browser path externally; no local-machine paths are embedded in the project.
import {writeFile,mkdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE??'playwright');
const out=new URL('../docs/company-resolutions/execution-2026-11-04/',import.meta.url);
await mkdir(new URL('previews/',out),{recursive:true});
const base=process.env.VALUATION_BROWSER_URL??'http://127.0.0.1:5192';
if(!/^http:\/\/127\.0\.0\.1:\d+$/.test(base))throw Error('Loopback test server required');
const browser=await chromium.launch({headless:true,...(process.env.BROWSER_EXECUTABLE?{executablePath:process.env.BROWSER_EXECUTABLE}:{})});
const page=await browser.newPage({viewport:{width:1480,height:1050}});
const errors=[];page.on('pageerror',e=>errors.push(e.message));
const checks=[];
try{
 await page.goto(base+'/workspace/');
 await page.getByRole('link',{name:'Cash flows',exact:true}).click();
 const company=page.getByRole('combobox',{name:'Company',exact:true});
 for(const ticker of ['AAPL','META','GOOGL']){
  await company.selectOption(ticker.toLowerCase()+'-fy2025');
  const panel=page.getByRole('region',{name:'Five-year FCFF and FCFE review'});
  await panel.getByRole('heading',{name:'Historical cash flows · '+ticker}).waitFor();
  await panel.getByRole('region',{name:'Separate availability and valuation checks'}).waitFor();
  const response=await page.request.get(base+'/api/v1/cashflows/'+ticker);assert.equal(response.status(),200);
  const d=await response.json();const text=await panel.innerText();
  assert.equal(d.status,'OPEN');assert.equal(d.review_passed,false);assert.equal(d.periods.length,5);
  assert(d.periods.every(p=>p.fcfe.parent_common_amount_usd===null));
  assert(text.includes((ticker==='AAPL'?'3':ticker==='META'?'5':'10')+' historical calculations available under stated conventions'));
  assert(text.includes(ticker==='GOOGL'?'Consolidated FCFE is available':'FCFE calculations remain provisional'));
  await panel.screenshot({path:fileURLToPath(new URL('previews/'+ticker+'-history.png',out))});
  await writeFile(new URL('runtime-'+ticker+'.json',out),JSON.stringify(d,null,2)+'\n');
  // History gaps must not block an independently validated manual forecast.
  const summary=page.getByText('FCFE forecast · explicit financing and cost of equity',{exact:true});
  await summary.waitFor({timeout:30000});await summary.click();
  const rate=page.getByLabel('Cost of equity (%)',{exact:true});assert.equal(await rate.inputValue(),'');
  const choose=page.getByRole('button',{name:/Use saved CAPM cost of equity/});
  await choose.waitFor({timeout:15000});await choose.click();
  assert.equal(await rate.inputValue(),({AAPL:'8.93500',META:'9.49000',GOOGL:'9.12000'})[ticker]);
  checks.push({ticker,history_rows:5,metric_records:10,history_ownership_and_readiness:'PASS',
   manual_forecast_visible:true,cost_equity_initially_blank:true,saved_rate_explicit_opt_in:'PASS'});
 }
 // Local report QA uses headless rendering directly, not the in-app browser.
 await page.goto(new URL('report.html',out).href);
 await page.screenshot({path:fileURLToPath(new URL('previews/report-opening.png',out))});
 await page.getByRole('heading',{name:'1. Apple: operating income reconciled to cash',exact:true}).scrollIntoViewIfNeeded();
 await page.screenshot({path:fileURLToPath(new URL('previews/report-apple.png',out))});
 await page.setViewportSize({width:430,height:932});await page.goto(new URL('report.html',out).href);
 await page.screenshot({path:fileURLToPath(new URL('previews/report-mobile.png',out))});
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 assert.deepEqual(errors,[]);
 await writeFile(new URL('browser-validation.json',out),JSON.stringify({verdict:'PASS',checks,metric_records:30,
   report_desktop_and_mobile_rendered:true,page_errors:errors,financial_review:'OPEN'},null,2)+'\n');
 console.log('PASS: 30 served metric records, three history views, blank manual rates and explicit saved-rate opt-in; report rendered on desktop/mobile.');
}finally{await browser.close();}
