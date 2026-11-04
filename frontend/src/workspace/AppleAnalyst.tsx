import {useEffect,useRef,useState} from 'react';
import Decimal from 'decimal.js';
import {ApiError,failureMessage,request,Revisions} from '../api';
import type {Result} from '../model';
import {fixedUnit,readableMoney} from '../presentation';
import {operatingCase} from './FcfeForecast';
import {ExportData} from './ExportData';
import './AppleAnalyst.css';

const D=Decimal.clone({precision:80});
export type AppleAssumptions={operating_cash_reserve_ratio:string;cost_of_equity:string;pre_tax_cost_of_debt:string;rsu_vesting_fraction:string;additional_claims_usd:string;historical_other_financing_fraction:string};
export const appleDefaults:AppleAssumptions={operating_cash_reserve_ratio:'0.02',cost_of_equity:'0.08935',pre_tax_cost_of_debt:'0.0565',rsu_vesting_fraction:'1',additional_claims_usd:'0',historical_other_financing_fraction:'0'};
export type AppleAnalystResult={schema_version:'apple-analyst-result-v1';ticker:'AAPL';policy_version:string;model_origin:string;assumptions:AppleAssumptions;
 readiness:{id:string;label:string;status:'ANALYST_READY_WITH_QUALIFICATIONS';detail:string}[];
 historical:{fiscal_year:number;fcff_usd:string;fcfe_usd:string;economic_fcfe_usd:string;other_financing_usd:string}[];
 fcff:{enterprise_value_usd:string;equity_value_usd:string;value_per_share_usd:string;wacc:string};
 fcfe:{operating_equity_value_usd:string;equity_value_usd:string;value_per_share_usd:string;cost_of_equity:string;years:{fiscal_year_label:string;fcff_usd:string;fcfe_usd:string;interest_expense_usd:string;net_borrowing_usd:string;opening_debt_usd:string;closing_debt_usd:string}[];terminal:Record<string,unknown>};
 bridge:{gross_cash_usd:string;operating_reserve_usd:string;eligible_cash_usd:string;debt_claims_usd:string;valuation_shares:string;additional_claims_usd:string};
 qualifications:string[];source_urls:string[];sensitivities:{label:string;fcff_value_per_share_usd:string;fcfe_value_per_share_usd:string}[]};
const numeric=(v:unknown):v is string=>typeof v==='string'&&/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(v)&&new D(v).isFinite();
const object=(v:unknown):v is Record<string,unknown>=>v!==null&&typeof v==='object'&&!Array.isArray(v);
function amounts(v:unknown,keys:string[]){return object(v)&&keys.every(k=>numeric(v[k]));}
export function checkAppleAnalyst(data:AppleAnalystResult,result:Result,assumptions:AppleAssumptions){
 const fail=()=>{throw Error('The Apple analyst result could not be matched to the submitted model.');};
 if(data?.schema_version!=='apple-analyst-result-v1'||data.ticker!=='AAPL'||typeof data.policy_version!=='string'||data.model_origin!==result.submitted_inputs.anchor.annual_end)fail();
 if(!object(data.assumptions)||Object.entries(assumptions).some(([k,v])=>!numeric(data.assumptions[k as keyof AppleAssumptions])||!new D(data.assumptions[k as keyof AppleAssumptions]).eq(v)))fail();
 if(!Array.isArray(data.readiness)||data.readiness.length!==5||new Set(data.readiness.map(r=>r.id)).size!==5||data.readiness.some(r=>!r||typeof r.id!=='string'||typeof r.label!=='string'||typeof r.detail!=='string'||r.status!=='ANALYST_READY_WITH_QUALIFICATIONS'))fail();
 if(!Array.isArray(data.historical)||data.historical.length!==5||data.historical.some((y,i)=>y.fiscal_year!==2021+i||!amounts(y,['fcff_usd','fcfe_usd','economic_fcfe_usd','other_financing_usd'])))fail();
 if(!amounts(data.fcff,['enterprise_value_usd','equity_value_usd','value_per_share_usd','wacc'])||!amounts(data.fcfe,['operating_equity_value_usd','equity_value_usd','value_per_share_usd','cost_of_equity']))fail();
 if(!new D(data.fcff.enterprise_value_usd).eq(result.stage_b.enterprise_value)||!new D(data.fcff.wacc).eq(result.submitted_inputs.wacc!))fail();
 if(!Array.isArray(data.fcfe.years)||data.fcfe.years.length!==result.stage_b.stage_a.years.length||data.fcfe.years.some((y,i)=>y.fiscal_year_label!==result.stage_b.stage_a.years[i].fiscal_year_label||!amounts(y,['fcff_usd','fcfe_usd','interest_expense_usd','net_borrowing_usd','opening_debt_usd','closing_debt_usd'])||!new D(y.fcff_usd).eq(result.stage_b.stage_a.years[i].fcff))||!amounts(data.fcfe.terminal,['fcff_usd'])||!result.stage_b.terminal||!new D(String(data.fcfe.terminal.fcff_usd)).eq(result.stage_b.terminal.fcff))fail();
 if(!amounts(data.bridge,['gross_cash_usd','operating_reserve_usd','eligible_cash_usd','debt_claims_usd','valuation_shares','additional_claims_usd'])||!Array.isArray(data.qualifications)||!data.qualifications.every(s=>typeof s==='string')||!Array.isArray(data.source_urls)||!data.source_urls.every(s=>typeof s==='string'&&/^https:\/\//.test(s))||!Array.isArray(data.sensitivities)||!data.sensitivities.every(s=>typeof s.label==='string'&&amounts(s,['fcff_value_per_share_usd','fcfe_value_per_share_usd'])))fail();
 return data;
}
type Form=Record<keyof AppleAssumptions,string>;
const initialForm:Form={operating_cash_reserve_ratio:'2',cost_of_equity:'8.935',pre_tax_cost_of_debt:'5.65',rsu_vesting_fraction:'100',additional_claims_usd:'0',historical_other_financing_fraction:'0'};
const controls:[keyof AppleAssumptions,string][]=[['operating_cash_reserve_ratio','Operating cash reserve (% of revenue)'],['cost_of_equity','Cost of equity (%)'],['pre_tax_cost_of_debt','Pre-tax cost of debt (%)'],['rsu_vesting_fraction','Existing RSUs assumed to vest (%)'],['additional_claims_usd','Additional claims (USD millions)'],['historical_other_financing_fraction','Other financing treated as debt cash flow (%)']];
function readForm(form:Form):AppleAssumptions{
 return Object.fromEntries(controls.map(([key,label])=>{
  const raw=form[key].trim();if(!numeric(raw))throw Error('Enter a decimal number for '+label+'.');
  return [key,new D(raw).times(key==='additional_claims_usd'?'1000000':'0.01').toFixed()];
 })) as AppleAssumptions;
}
export function AppleAnalyst({result,stale,busy,active=true,label='Base',load=request}:{result:Result;stale:boolean;busy:boolean;active?:boolean;label?:string;load?:typeof request}){
 const [form,setForm]=useState<Form>(initialForm),[pending,setPending]=useState(false),[failure,setFailure]=useState(''),[details,setDetails]=useState<string[]>([]);
 const [saved,setSaved]=useState<{data:AppleAnalystResult;binding:string;formKey:string}|null>(null);
 const revision=useRef(new Revisions()),controller=useRef<AbortController|null>(null),attempts=useRef(new Set<string>());
 const base=operatingCase(result.submitted_inputs),binding=JSON.stringify(base),formKey=JSON.stringify(form);
 const unsupported=(base.terminal_valuation as {method?:string}|undefined)?.method==='exit_multiple';
 const isApple=result.submitted_inputs.anchor.kind==='aapl-fy2025';
 const outdated=stale||saved?.binding!==binding||saved?.formKey!==formKey;
 const submitted=useRef({result,binding,formKey,form,base});submitted.current={result,binding,formKey,form,base};
 function stop(){revision.current.edit();controller.current?.abort();setPending(false);}
 useEffect(()=>{stop();setFailure('');setDetails([]);return()=>{revision.current.edit();controller.current?.abort();};},[binding,stale]);
 useEffect(()=>()=>{revision.current.edit();controller.current?.abort();},[]);
 async function calculate(){
  if(stale||busy||unsupported||!isApple)return;
  const snapshot=submitted.current,token=revision.current.begin();controller.current?.abort();const abort=new AbortController();controller.current=abort;setPending(true);setFailure('');setDetails([]);
  try{
   const assumptions=readForm(snapshot.form);
   const body={schema_version:'apple-analyst-request-v1',base_case:snapshot.base,assumptions};
   const data=await load<AppleAnalystResult>('/api/v1/apple/analyst/run',body,abort.signal);
   if(revision.current.current(token)&&submitted.current.binding===snapshot.binding&&submitted.current.formKey===snapshot.formKey)setSaved({data:checkAppleAnalyst(data,snapshot.result,assumptions),binding:snapshot.binding,formKey:snapshot.formKey});
  }catch(e){if(revision.current.current(token)){setFailure(e instanceof ApiError?failureMessage(e):e instanceof Error?e.message:failureMessage(e));setDetails(e instanceof ApiError?e.details:[]);}}
  finally{if(revision.current.current(token))setPending(false);}
 }
 useEffect(()=>{
  if(!active||stale||busy||unsupported||!isApple||formKey!==JSON.stringify(initialForm))return;
  const key=binding+formKey;if(attempts.current.has(key))return;
  const timer=setTimeout(()=>{attempts.current.add(key);void calculate();},0);return()=>clearTimeout(timer);
 },[active,binding,stale,busy,unsupported,formKey,isApple]);
 function edit(key:keyof Form,value:string){stop();setFailure('');setDetails([]);setForm(old=>({...old,[key]:value}));}
 const data=saved?.data;
 if(!isApple)return null;
 return <section className="apple-analyst" aria-labelledby="apple-analyst-heading"><h2 id="apple-analyst-heading">Apple · analyst valuation</h2>
  <p>Historical cash flows, financing and share valuation under disclosed analyst conventions. {label} · {result.stage_b.stage_a.years.length}-year forecast.</p>
  {stale&&<p role="status">Operating assumptions changed. Update valuation before recalculating Apple outputs.</p>}
  {unsupported&&<p role="status">Choose Perpetual growth to calculate the paired FCFF and FCFE analyst valuations.</p>}
  {data&&outdated&&<p className="apple-stale" role="status">Previous Apple analyst results · stale. Recalculate to reflect the current model and assumptions.</p>}
  <details><summary>Analyst assumptions · editable</summary><div className="apple-assumptions">{controls.map(([key,name])=><label key={key}>{name}<input inputMode="decimal" aria-label={name} value={form[key]} onChange={e=>edit(key,e.target.value)}/></label>)}</div><p>Changes apply when recalculated. Historical Other financing is an explicit classification assumption, not a newly reported fact.</p></details>
  <div className="apple-actions"><button disabled={stale||busy||pending||unsupported} onClick={()=>void calculate()}>Calculate Apple analyst outputs</button>{pending&&<><span role="status">Calculating Apple outputs…</span><button onClick={stop}>Cancel Apple calculation</button></>}</div>
  {failure&&<div role="alert"><p>{failure}</p>{details.map(s=><p key={s}>{s}</p>)}</div>}
  {data&&<div aria-label="Apple analyst results"><div className="apple-value-cards"><section aria-label="FCFF fair value per share"><h3>FCFF fair value per share</h3><strong>${fixedUnit(data.fcff.value_per_share_usd,'1',2)}</strong><p>{readableMoney(data.fcff.enterprise_value_usd)} enterprise value · {readableMoney(data.fcff.equity_value_usd)} equity value</p><small>WACC {fixedUnit(data.fcff.wacc,'0.01',2)}%</small></section><section aria-label="FCFE fair value per share"><h3>FCFE fair value per share</h3><strong>${fixedUnit(data.fcfe.value_per_share_usd,'1',2)}</strong><p>{readableMoney(data.fcfe.equity_value_usd)} equity value</p><small>Cost of equity {fixedUnit(data.fcfe.cost_of_equity,'0.01',2)}% · debt is not subtracted again</small></section></div>
   <p><b>Different financing assumptions:</b> FCFF uses the selected WACC target weights; FCFE assumes flat debt during the explicit forecast. These values are not expected to match. FCFE minus FCFF: ${fixedUnit(new D(data.fcfe.value_per_share_usd).minus(data.fcff.value_per_share_usd).toFixed(),'1',2)} per share.</p>
   <p>Fiscal-end analytical origin {data.model_origin}, using later-filed information. These are valuation estimates, not current market prices.</p>
   <details><summary>Five outputs · readiness and qualifications</summary><ul>{data.readiness.map(r=><li key={r.id}><b>{r.label}</b> · Analyst-ready with qualifications<p>{r.detail}</p></li>)}</ul></details>
   <details><summary>Five-year historical FCFF and FCFE</summary><p>Standardized historical calculations. Economic FCFE retains SBC as an expense; the CFO-based series preserves its cash-statement basis.</p><div className="cv-table-scroll"><table><thead><tr><th>Year</th><th>FCFF</th><th>FCFE · CFO basis</th><th>Economic FCFE</th><th>Reported Other financing</th></tr></thead><tbody>{data.historical.map(y=><tr key={y.fiscal_year}><th>FY{y.fiscal_year}</th>{[y.fcff_usd,y.fcfe_usd,y.economic_fcfe_usd,y.other_financing_usd].map((v,i)=><td key={i}>{fixedUnit(v,'1000000000',2)}B</td>)}</tr>)}</tbody></table></div></details>
   <details><summary>FCFE forecast and financing</summary><div className="cv-table-scroll"><table><thead><tr><th>Year</th><th>FCFE</th><th>Interest</th><th>Net borrowing</th><th>Closing debt</th></tr></thead><tbody>{data.fcfe.years.map(y=><tr key={y.fiscal_year_label}><th>{y.fiscal_year_label}</th>{[y.fcfe_usd,y.interest_expense_usd,y.net_borrowing_usd,y.closing_debt_usd].map((v,i)=><td key={i}>{fixedUnit(v,'1000000000',2)}B</td>)}</tr>)}</tbody></table></div><p>Eligible cash {readableMoney(data.bridge.eligible_cash_usd)} after operating reserve {readableMoney(data.bridge.operating_reserve_usd)}. Financing claims {readableMoney(data.bridge.debt_claims_usd)}. Valuation shares {fixedUnit(data.bridge.valuation_shares,'1000000000',4)}B.</p></details>
   <details><summary>Sensitivity · value per share</summary><div className="cv-table-scroll"><table><thead><tr><th>Assumption</th><th>FCFF</th><th>FCFE</th></tr></thead><tbody>{data.sensitivities.map((s,i)=><tr key={i}><th>{s.label}</th><td>${fixedUnit(s.fcff_value_per_share_usd,'1',2)}</td><td>${fixedUnit(s.fcfe_value_per_share_usd,'1',2)}</td></tr>)}</tbody></table></div></details>
   <details><summary>Methodology and filing sources</summary>{data.qualifications.map((s,i)=><p key={i}>{s}</p>)}{data.source_urls.map(url=><p key={url}><a href={url} target="_blank" rel="noreferrer">Source · {url.split('/').at(-1)}</a></p>)}<small>Policy {data.policy_version}. Earlier evidence-review records retain their original findings; this analyst output applies the disclosed conventions above.</small></details>
   <ExportData value={{status:outdated?'stale':'current',selected_case:label,analyst_result:data}} name="apple-analyst-valuation"/>
  </div>}
 </section>;
}
