/** Deterministic independent perturbations of immutable reference requests. */
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
const directory=resolve(root,'frontend/src/browser-engine/fixtures');
const baseline=JSON.parse(await readFile(resolve(directory,'parity.json'),'utf8'));
const get=name=>structuredClone(baseline.find(f=>f.name===name).body);
const cases=[];const add=(name,path,body,intent='valid')=>cases.push({name,path,body,intent});
const change=(name,base,fn,path='/api/v1/cases/run',intent='valid')=>{const body=get(base);fn(body);add(name,path,body,intent);};
let seed=0x5ec2026;const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed;};
const choice=values=>values[random()%values.length];
for(const ticker of ['AAPL','META','GOOGL'])for(const horizon of [5,10])for(let i=0;i<3;i++){
 change(`${ticker}-perturbed-analyst-${horizon}-${i}`,`${ticker}-analyst-Base-${horizon}`,d=>{
  Object.assign(d.assumptions,{operating_cash_reserve_ratio:choice(['0','0.01','0.025','0.05']),rsu_vesting_fraction:choice(['0','0.25','0.75','1']),additional_claims_usd:choice(['0','123456789','10000000000']),historical_other_financing_fraction:choice(['0','0.3','1']),cost_of_equity:choice(['0.08','0.11','0.16']),pre_tax_cost_of_debt:choice(['0','0.035','0.08'])});
  if(ticker!=='AAPL')d.assumptions.additional_assets_usd=choice(['0','123456789','2000000000']);
  if(ticker==='GOOGL'){d.assumptions.historical_minority_cash_share=choice(['0','0.1','0.4']);d.assumptions.nci_claim_usd=choice(['0','123456789','3400000000']);}
 },ticker==='AAPL'?'/api/v1/apple/analyst/run':'/api/v1/analyst/run');
}
for(const horizon of [5,10])for(const method of ['gordon','exit'])for(let variant=0;variant<3;variant++){
 change(`signed-operating-${method}-${horizon}-${variant}`,`synthetic-${method}-${horizon}-equity`,d=>{
  d.forecast_years.forEach((row,i)=>{row.operating_margin=choice(['-0.30','0','0.12','0.38']);row.change_in_operating_nwc_percent_revenue=choice(['-0.08','0','0.04']);row.forecast_tax_rate=choice(['0','0.25','1']);row.revenue_growth=choice(['-0.2','0','0.05','0.2']);});
  // Exit contract requires strictly positive final EBIT; all earlier losses remain.
  if(method==='exit')d.forecast_years.at(-1).operating_margin='0.20';
  d.bridge.components.find(x=>x.role==='FINANCING_CLAIM').amount=variant===2?'100000':'20';
 });
}
change('gordon-zero-growth','synthetic-gordon-5-ev',d=>{d.forecast_years.forEach(y=>y.revenue_growth='0');d.terminal_valuation.terminal_growth='0';});
change('gordon-revenue-collapse','synthetic-gordon-10-ev',d=>{d.forecast_years[2].revenue_growth='-1';});
change('gordon-negative-equity','synthetic-equity',d=>{d.bridge.components[2].amount='1000000';});
function zero(d){const c=d.source.case;for(const y of c.forecast_years)for(const k of Object.keys(y))if(!['period_index','fiscal_year_label','revenue_growth'].includes(k))y[k]='0';for(const k of Object.keys(c.terminal))c.terminal[k]='0';return c;}
for(const amount of ['0','10'])change('reverse-flat-'+amount,'synthetic-reverse-ev',d=>{zero(d);d.target.amount=amount;},'/api/v1/reverse/run');
change('reverse-not-certified','synthetic-reverse-ev',d=>{const c=zero(d);c.wacc='0.25';c.terminal_growth='0.05';c.forecast_years[0].d_and_a_percent_revenue='1.25';c.forecast_years[1].capex_percent_revenue='0.625';d.growth_bounds={lower:'0',upper:'1'};d.target.amount='55';},'/api/v1/reverse/run');
for(const amount of ['100000','-100000'])change('reverse-unreachable-'+amount,'synthetic-reverse-ev',d=>d.target.amount=amount,'/api/v1/reverse/run');
for(const bound of ['0','0.20','-1']){
 const body=get('synthetic-reverse-ev');body.growth_bounds.lower=bound==='-1'?'-1':'0';
 add('reverse-endpoint-'+bound,'/api/v1/reverse/run',body,'endpoint:'+bound);
}
const decreasing=get('synthetic-reverse-equity');{const c=zero(decreasing);for(const y of c.forecast_years)y.capex_percent_revenue='0.08';c.terminal.investment_percent_revenue='0.18';c.wacc='0.25';c.terminal_growth='0.05';}
add('reverse-decreasing','/api/v1/reverse/run',decreasing,'decreasing:0.07');
const invalid=(name,base,fn,path)=>change(name,base,fn,path??'/api/v1/cases/run','reject');
invalid('reject-unknown-schema','synthetic-base',d=>d.schema_version='analyst-case-v999');
invalid('reject-unknown-top-key','synthetic-base',d=>d.unknown_key='x');
invalid('reject-unknown-row-key','synthetic-base',d=>d.forecast_years[0].unknown_key='x');
invalid('reject-json-number-rate','synthetic-base',d=>d.wacc=0.1);
invalid('reject-invalid-annual-date','synthetic-base',d=>d.anchor.annual_end='2025-02-30');
invalid('reject-period-duplicate','synthetic-base',d=>d.forecast_years[1].period_index=1);
invalid('reject-overlap-selected','synthetic-equity',d=>d.bridge.components[0].overlap_references.push('asset-b'));
invalid('reject-overlaps-forecast','synthetic-equity',d=>d.bridge.components[0].overlaps_forecast=true);
invalid('reject-coverage-missing-population','synthetic-equity',d=>d.bridge.coverage[0].population_ids=[]);
invalid('reject-duplicate-component-id','synthetic-equity',d=>d.bridge.components[1].component_id=d.bridge.components[0].component_id);
invalid('reject-share-date','synthetic-equity',d=>d.bridge.shares.observation_date='2024-12-31');
invalid('reject-share-class','synthetic-equity',d=>d.bridge.shares.class_id='');
invalid('reject-source-cutoff','synthetic-sensitivity-ev',d=>d.source.information_cutoff='2020-01-01','/api/v1/sensitivity/run');
invalid('reject-scenario-anchor-mismatch','synthetic-scenarios-ev',d=>d.scenarios[1].case.anchor.annual_end='2024-12-31','/api/v1/scenarios/run');
invalid('reject-scenario-cutoff-mismatch','synthetic-scenarios-ev',d=>d.scenarios[1].information_cutoff='2026-11-01','/api/v1/scenarios/run');
invalid('reject-scenario-duplicate-label','synthetic-scenarios-ev',d=>d.scenarios[1].label='Bear','/api/v1/scenarios/run');
invalid('reject-sensitivity-descending','synthetic-sensitivity-ev',d=>d.wacc_values=['0.2','0.1'],'/api/v1/sensitivity/run');
invalid('reject-sensitivity-duplicate','synthetic-sensitivity-ev',d=>d.terminal_growth_values=['0.01','0.01'],'/api/v1/sensitivity/run');
invalid('reject-sensitivity-too-many','synthetic-sensitivity-ev',d=>d.wacc_values=Array.from({length:12},(_,i)=>(i+1)/100).map(String),'/api/v1/sensitivity/run');
invalid('reject-fcfe-finance-negative','synthetic-fcfe-5',d=>d.financing_years[0].cash_debt_issued_usd='-1','/api/v1/fcfe/run');
invalid('reject-fcfe-finance-duplicate','synthetic-fcfe-5',d=>d.financing_years[1].period_index=1,'/api/v1/fcfe/run');
invalid('reject-fcfe-financed-assets-exceed','synthetic-fcfe-5',d=>d.financing_years[0].new_finance_asset_funding_usd='100000','/api/v1/fcfe/run');
invalid('reject-fcfe-debt-negative','synthetic-fcfe-5',d=>d.financing_years[0].principal_repaid_usd='1','/api/v1/fcfe/run');
invalid('reject-fcfe-unfunded-interest','synthetic-fcfe-5',d=>d.financing_years[0].interest_expense_usd='1','/api/v1/fcfe/run');
invalid('reject-fcfe-terminal-identity','synthetic-fcfe-5',d=>d.terminal_financing.cash_debt_issued_usd='1','/api/v1/fcfe/run');
invalid('reject-fcfe-terminal-negative','synthetic-fcfe-5',d=>{d.opening_debt_usd='100';d.terminal_financing.interest_expense_usd='100';},'/api/v1/fcfe/run');
async function api(path,body){const r=await fetch('http://127.0.0.1:8135'+path,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body),signal:AbortSignal.timeout(60000)});return {status:r.status,expected:await r.json()};}
const fixtures=[];const unexpected=[];
for(const item of cases){
 if(item.intent.startsWith('endpoint:')||item.intent.startsWith('decreasing:')){
  const growth=item.intent.split(':')[1],body=structuredClone(item.body.source.case);body.forecast_years.forEach(y=>y.revenue_growth=growth);const result=await api('/api/v1/cases/run',body);if(result.status!==200)throw Error('Target construction failed: '+item.name);item.body.target.amount=item.body.target.metric==='ENTERPRISE_VALUE'?result.expected.stage_b.enterprise_value:result.expected.stage_c.value_per_share;
 }
 const result=await api(item.path,item.body);if(![200,422].includes(result.status))throw Error('Unexpected service status '+item.name+': '+JSON.stringify(result));
 fixtures.push({name:item.name,path:item.path,body:item.body,expected:result.expected,status:result.status});
 if((item.intent==='reject')!==(result.status===422))unexpected.push({name:item.name,intent:item.intent,status:result.status,error:result.expected.error??result.expected.status});
}
await mkdir(directory,{recursive:true});const bytes=JSON.stringify(fixtures,null,2)+'\n';await writeFile(resolve(directory,'extra-parity.json'),bytes);
const index={schema_version:'extra-parity-manifest-v1',seed:'0x05ec2026',fixture_count:fixtures.length,sha256:createHash('sha256').update(bytes).digest('hex'),successful:fixtures.filter(f=>f.status===200).length,rejected:fixtures.filter(f=>f.status===422).length,error_codes:Object.fromEntries([...new Set(fixtures.filter(f=>f.status===422).map(f=>f.expected.error.code))].map(code=>[code,fixtures.filter(f=>f.expected.error?.code===code).length])),unexpected};
await writeFile(resolve(directory,'extra-parity-manifest.json'),JSON.stringify(index,null,2)+'\n');console.log(JSON.stringify(index));
