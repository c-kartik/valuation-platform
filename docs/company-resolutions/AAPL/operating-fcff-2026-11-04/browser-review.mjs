// Replay against the private local platform: node browser-review.mjs [base URL].
import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const require=createRequire(import.meta.url);
const {chromium}=process.env.PLAYWRIGHT_MODULE?await import(process.env.PLAYWRIGHT_MODULE):require('playwright');
const here=path.dirname(fileURLToPath(import.meta.url));
const data=JSON.parse(await readFile(path.join(here,'adopted-history.json'),'utf8'));
const expected=data.periods.map(p=>({year:`FY${p.fiscal_year}`,value:p.fcff.amount_usd,display:p.fcff.display_billions+'B'}));
const browser=await chromium.launch({headless:true,...process.env.CHROME_EXECUTABLE?{executablePath:process.env.CHROME_EXECUTABLE}:{}});
const page=await browser.newPage({viewport:{width:1600,height:1200}}),errors=[];
page.on('pageerror',e=>errors.push(e.message));
const base=process.argv[2]??'http://127.0.0.1:5193';
try{
 await mkdir(path.join(here,'previews'),{recursive:true});
 await page.goto(base+'/workspace/');await page.selectOption('#canvas-company','aapl-fy2025');
 await page.locator('[data-bar-year="FY2025"][data-metric="fcff"]').waitFor();
 const observed=await page.locator('#dcf [data-scenario-bar="Reported"][data-metric="fcff"]').evaluateAll(nodes=>nodes.map(n=>({year:n.dataset.barYear,value:n.dataset.value})));
 if(JSON.stringify(observed)!==JSON.stringify(expected.map(({year,value})=>({year,value}))))throw Error('Five historical chart bars differ');
 const readouts={};
 for(const p of expected.slice(-2)){
  await page.getByRole('button',{name:`combined: select ${p.year}`,exact:false}).focus();
  readouts[p.year]=await page.getByLabel('Selected year values').innerText();
  if(!readouts[p.year].includes(p.display)||readouts[p.year].includes('Unavailable'))throw Error('Missing year readout');
 }
 await page.locator('#dcf').screenshot({path:path.join(here,'previews/dcf-fy2025.png')});
 await page.getByRole('button',{name:'combined: select FY2027',exact:true}).focus();
 if(await page.locator('#dcf [data-base-trend="fcff"]').count())throw Error('Cross-basis FCFF trend must be absent');
 await page.getByRole('link',{name:'Scenarios',exact:true}).click();
 await page.locator('#scenario-comparison [data-metric="fcff"][data-scenario-bar="Reported"][data-bar-year="FY2025"]').waitFor();
 const scenarioHistory=await page.locator('#scenario-comparison [data-metric="fcff"][data-scenario-bar="Reported"]').evaluateAll(nodes=>nodes.map(n=>({year:n.dataset.barYear,value:n.dataset.value})));
 if(JSON.stringify(scenarioHistory)!==JSON.stringify(observed))throw Error('Scenario history differs');
 await page.getByRole('link',{name:'Cash flows',exact:true}).click();
 await page.getByRole('heading',{name:'Historical cash flows · AAPL'}).waitFor();
 const history=page.locator('#cash-flow-history');
 await history.getByRole('cell',{name:'115.68B Standardized operating-income method',exact:true}).waitFor();
 if(await history.getByText('Standardized operating-income method',{exact:true}).count()!==5)throw Error('Historical basis labels missing');
 if(await history.getByText('Provisional · financing classification open',{exact:true}).count()!==5)throw Error('FCFE qualifiers missing');
 if(await history.getByText('Missing interest disclosure',{exact:true}).count())throw Error('Current FCFF still unavailable');
 await history.screenshot({path:path.join(here,'previews/cashflows.png')});
 const response=await page.request.get(base+'/api/v1/cashflows/AAPL');
 if(!response.ok())throw Error('Cashflows API unavailable');const api=await response.json();
 for(let i=0;i<5;i++)if(api.periods[i].fcff.amount_usd!==expected[i].value)throw Error('API differs from graph');
 if(!api.periods.slice(-2).every(p=>p.legacy_cfo_fcff.amount_usd===null))throw Error('Legacy nulls changed');
 if(!api.notice.includes('17.782B')||!api.notice.includes('13.585B')||!api.notice.includes('355m'))throw Error('Qualifications missing');
 if(errors.length)throw Error(errors.join('\n'));
 await writeFile(path.join(here,'browser-results.json'),JSON.stringify({status:'PASS',five_historical_bars:observed,scenario_historical_bars:scenarioHistory,readouts,cross_basis_fcff_trend:false,history_method_labels:5,fcfe_provisional_labels:5,legacy_nulls_preserved:true,material_tax_and_da_qualifications:true,javascript_errors:errors},null,2)+'\n');
 console.log('PASS: live chart, historical table, API and preserved legacy data.');
}finally{await browser.close()}
