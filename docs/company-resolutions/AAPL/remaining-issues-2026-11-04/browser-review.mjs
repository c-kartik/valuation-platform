import {createRequire} from 'node:module';import {readFile,writeFile,mkdir} from 'node:fs/promises';import path from 'node:path';import {fileURLToPath} from 'node:url';
const require=createRequire(import.meta.url),{chromium}=process.env.PLAYWRIGHT_MODULE?await import(process.env.PLAYWRIGHT_MODULE):require('playwright');
const here=path.dirname(fileURLToPath(import.meta.url)),base=process.argv[2]??'http://127.0.0.1:5193';
const old=JSON.parse(await readFile(path.join(here,'../operating-fcff-2026-11-04/adopted-history.json'),'utf8'));
const b=await chromium.launch({headless:true,...process.env.CHROME_EXECUTABLE?{executablePath:process.env.CHROME_EXECUTABLE}:{}}),p=await b.newPage({viewport:{width:1600,height:1100}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
try{
 await mkdir(path.join(here,'previews'),{recursive:true});await p.goto(base+'/workspace/');await p.selectOption('#canvas-company','aapl-fy2025');await p.locator('[data-bar-year="FY2025"][data-metric="fcff"]').waitFor();
 const chart=await p.locator('#dcf [data-scenario-bar="Reported"][data-metric="fcff"]').evaluateAll(ns=>ns.map(n=>n.dataset.value));
 if(JSON.stringify(chart)!==JSON.stringify(old.periods.map(x=>x.fcff.amount_usd)))throw Error('Historical FCFF changed');
 await p.getByRole('link',{name:'Cash flows',exact:true}).click();await p.getByText('Apple review decisions and remaining evidence',{exact:true}).waitFor();await p.getByText('Apple review decisions and remaining evidence',{exact:true}).click();
 const box=p.getByLabel('Apple resolution decisions'),text=await box.innerText();
 for(const s of ['132.42B','98.66B','80.40B','1.23B','14.77326B','Company review remains open','Historical and forecast policies recorded'])if(!text.includes(s))throw Error('Missing reviewed source/outcome '+s);
 if(await p.locator('#cash-flow-history').getByText('Provisional · financing classification open',{exact:true}).count()!==5)throw Error('FCFE qualifiers changed');
 await box.screenshot({path:path.join(here,'previews/platform-review.png')});
 const response=await p.request.get(base+'/api/v1/cashflows/AAPL');if(!response.ok())throw Error('API failed');const api=await response.json();
 if(api.current_resolution.company_complete!==false||api.current_resolution.anchor_support.fair_value_per_share_usd!==null||api.review_passed!==false)throw Error('False financial clearance');
 if(api.unresolved_scope_items.includes('A1')||api.unresolved_scope_items.includes('A7'))throw Error('Current list includes resolved/policy issues');
 if(!api.legacy_review_scope_items.includes('A1')||!api.legacy_review_scope_items.includes('A7'))throw Error('Legacy review lost');
 if(errors.length)throw Error(errors.join('\n'));
 await writeFile(path.join(here,'browser-results.json'),JSON.stringify({status:'PASS',historical_fcff_unchanged:chart,fcfe_provisional_rows:5,dated_source_values_visible:true,adopted_tax_policy_visible:true,company_complete:false,fair_value_per_share_usd:null,legacy_scope_preserved:true,javascript_errors:errors},null,2)+'\n');console.log('PASS: live Apple source/decision panel, unchanged FCFF and provisional FCFE, no false financial clearance.');
}finally{await b.close()}
