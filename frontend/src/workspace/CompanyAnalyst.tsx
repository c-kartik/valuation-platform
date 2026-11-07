import {useEffect,useRef,useState} from 'react';
import Decimal from 'decimal.js';
import {ApiError,failureMessage,request,Revisions} from '../api';
import type {Result} from '../model';
import {fixedUnit,readableMoney} from '../presentation';
import {operatingCase} from './FcfeForecast';
import {ExportData} from './ExportData';
import './AppleAnalyst.css';

const D=Decimal.clone({precision:80});
export type CompanyAssumptions={operating_cash_reserve_ratio:string;cost_of_equity:string;pre_tax_cost_of_debt:string;rsu_vesting_fraction:string;additional_claims_usd:string;additional_assets_usd:string;historical_other_financing_fraction:string;nci_claim_usd:string;historical_minority_cash_share:string};
export type CompanyTicker='META'|'GOOGL';
export type CompanyProfile={schema_version:'company-analyst-profile-v1';ticker:CompanyTicker;name:string;policy_version:string;model_origin:string;defaults:CompanyAssumptions};
export type CompanyAnalystResult={schema_version:'company-analyst-result-v1';ticker:CompanyTicker;name:string;policy_version:string;model_origin:string;assumptions:CompanyAssumptions;
 readiness:{id:string;label:string;status:'ANALYST_READY_WITH_QUALIFICATIONS';detail:string}[];
 historical:{fiscal_year:number;fcff_usd:string;fcfe_usd:string;economic_fcfe_usd:string;other_financing_usd:string;consolidated_fcfe_usd:string}[];
 fcff:{enterprise_value_usd:string;equity_value_usd:string;value_per_share_usd:string;wacc:string};
 fcfe:{operating_equity_value_usd:string;equity_value_usd:string;value_per_share_usd:string;cost_of_equity:string;years:{fiscal_year_label:string;fcff_usd:string;fcfe_usd:string;interest_expense_usd:string;net_borrowing_usd:string;opening_debt_usd:string;closing_debt_usd:string}[];terminal:Record<string,unknown>};
 bridge:{gross_cash_usd:string;operating_reserve_usd:string;eligible_cash_usd:string;debt_claims_usd:string;valuation_shares:string;additional_claims_usd:string;additional_assets_usd:string;nci_claim_usd:string};
 qualifications:string[];source_urls:string[];sensitivities:{label:string;fcff_value_per_share_usd:string;fcfe_value_per_share_usd:string}[]};
const numeric=(v:unknown):v is string=>typeof v==='string'&&/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(v)&&new D(v).isFinite();
const object=(v:unknown):v is Record<string,unknown>=>v!==null&&typeof v==='object'&&!Array.isArray(v);
function amounts(v:unknown,keys:string[]){return object(v)&&keys.every(k=>numeric(v[k]));}
export function checkCompanyAnalyst(data:CompanyAnalystResult,result:Result,assumptions:CompanyAssumptions,profile:CompanyProfile){
 const fail=()=>{throw Error('The company analyst result could not be matched to the submitted model.');};
 if(data?.schema_version!=='company-analyst-result-v1'||data.ticker!==profile.ticker||data.name!==profile.name||data.policy_version!==profile.policy_version||data.model_origin!==profile.model_origin||data.model_origin!==result.submitted_inputs.anchor.annual_end)fail();
 if(!object(data.assumptions)||Object.entries(assumptions).some(([k,v])=>!numeric(data.assumptions[k as keyof CompanyAssumptions])||!new D(data.assumptions[k as keyof CompanyAssumptions]).eq(v)))fail();
 if(!Array.isArray(data.readiness)||data.readiness.length!==5||new Set(data.readiness.map(r=>r.id)).size!==5||data.readiness.some(r=>!r||typeof r.id!=='string'||typeof r.label!=='string'||typeof r.detail!=='string'||r.status!=='ANALYST_READY_WITH_QUALIFICATIONS'))fail();
 if(!Array.isArray(data.historical)||data.historical.length!==5||data.historical.some((y,i)=>y.fiscal_year!==2021+i||!amounts(y,['fcff_usd','fcfe_usd','economic_fcfe_usd','other_financing_usd','consolidated_fcfe_usd'])))fail();
 if(!amounts(data.fcff,['enterprise_value_usd','equity_value_usd','value_per_share_usd','wacc'])||!amounts(data.fcfe,['operating_equity_value_usd','equity_value_usd','value_per_share_usd','cost_of_equity']))fail();
 if(!new D(data.fcfe.cost_of_equity).eq(assumptions.cost_of_equity)||!new D(data.fcff.enterprise_value_usd).eq(result.stage_b.enterprise_value)||!new D(data.fcff.wacc).eq(result.submitted_inputs.wacc!))fail();
 if(!Array.isArray(data.fcfe.years)||data.fcfe.years.length!==result.stage_b.stage_a.years.length||data.fcfe.years.some((y,i)=>y.fiscal_year_label!==result.stage_b.stage_a.years[i].fiscal_year_label||!amounts(y,['fcff_usd','fcfe_usd','interest_expense_usd','net_borrowing_usd','opening_debt_usd','closing_debt_usd'])||!new D(y.fcff_usd).eq(result.stage_b.stage_a.years[i].fcff))||!amounts(data.fcfe.terminal,['fcff_usd'])||!result.stage_b.terminal||!new D(String(data.fcfe.terminal.fcff_usd)).eq(result.stage_b.terminal.fcff))fail();
 if(!amounts(data.bridge,['gross_cash_usd','operating_reserve_usd','eligible_cash_usd','debt_claims_usd','valuation_shares','additional_claims_usd','additional_assets_usd','nci_claim_usd'])||!Array.isArray(data.qualifications)||!data.qualifications.every(s=>typeof s==='string')||!Array.isArray(data.source_urls)||!data.source_urls.every(s=>typeof s==='string'&&/^https:\/\//.test(s))||!Array.isArray(data.sensitivities)||!data.sensitivities.every(s=>typeof s.label==='string'&&amounts(s,['fcff_value_per_share_usd','fcfe_value_per_share_usd'])))fail();
 if(!new D(data.bridge.nci_claim_usd).eq(assumptions.nci_claim_usd)||!new D(data.bridge.additional_assets_usd).eq(assumptions.additional_assets_usd)||!new D(data.bridge.additional_claims_usd).eq(assumptions.additional_claims_usd))fail();
 return data;
}
type Form=Record<keyof CompanyAssumptions,string>;
const emptyForm:Form={operating_cash_reserve_ratio:'',cost_of_equity:'',pre_tax_cost_of_debt:'',rsu_vesting_fraction:'',additional_claims_usd:'',additional_assets_usd:'',historical_other_financing_fraction:'',nci_claim_usd:'',historical_minority_cash_share:''};
const controls:[keyof CompanyAssumptions,string][]=[['operating_cash_reserve_ratio','Operating cash reserve (% of revenue)'],['cost_of_equity','Cost of equity (%)'],['pre_tax_cost_of_debt','Pre-tax cost of debt (%)'],['rsu_vesting_fraction','Existing RSUs assumed to vest (%)'],['additional_claims_usd','Additional claims (USD millions)'],['additional_assets_usd','Non-operating investments / other assets (USD millions)'],['historical_other_financing_fraction','Other financing treated as debt cash flow (%)'],['nci_claim_usd','Minority-interest equity claim (USD millions)'],['historical_minority_cash_share','Historical cash flow allocated to minority interests (%)']];
const moneyInput=(key:keyof CompanyAssumptions)=>key==='additional_claims_usd'||key==='additional_assets_usd'||key==='nci_claim_usd';
function profileForm(defaults:CompanyAssumptions):Form{return Object.fromEntries(controls.map(([key])=>[key,new D(defaults[key]).times(moneyInput(key)?'0.000001':'100').toFixed()])) as Form;}
export function checkCompanyProfile(value:CompanyProfile,ticker:CompanyTicker,result:Result){
 if(!value||value.schema_version!=='company-analyst-profile-v1'||value.ticker!==ticker||typeof value.name!=='string'||!value.name||typeof value.policy_version!=='string'||!value.policy_version||value.model_origin!==result.submitted_inputs.anchor.annual_end||!amounts(value.defaults,controls.map(([key])=>key)))throw Error('The analyst profile could not be matched to the selected company.');
 return value;
}
function readForm(form:Form):CompanyAssumptions{
 return Object.fromEntries(controls.map(([key,label])=>{
  const raw=form[key].trim();if(!numeric(raw))throw Error('Enter a decimal number for '+label+'.');
  return [key,new D(raw).times(moneyInput(key)?'1000000':'0.01').toFixed()];
 })) as CompanyAssumptions;
}
export function CompanyAnalyst({ticker,result,stale,busy,active=true,label='Base',load=request,capture}:{capture?:(value:import('./modelSnapshot').AnalystSnapshot)=>void;ticker:CompanyTicker;result:Result;stale:boolean;busy:boolean;active?:boolean;label?:string;load?:typeof request}){
 const [form,setForm]=useState<Form>(emptyForm),[profile,setProfile]=useState<CompanyProfile|null>(null),[profilePending,setProfilePending]=useState(false),[profileRetry,setProfileRetry]=useState(0);
 const [pending,setPending]=useState(false),[failure,setFailure]=useState(''),[details,setDetails]=useState<string[]>([]);
 const [saved,setSaved]=useState<{data:CompanyAnalystResult;binding:string;formKey:string}|null>(null);
 const revision=useRef(new Revisions()),controller=useRef<AbortController|null>(null),attempts=useRef(new Set<string>()),profileRevision=useRef(new Revisions());
 const base=operatingCase(result.submitted_inputs),binding=JSON.stringify(base),formKey=JSON.stringify(form);
 const unsupported=(base.terminal_valuation as {method?:string}|undefined)?.method==='exit_multiple';
 const correctIssuer=result.submitted_inputs.anchor.kind===(ticker==='META'?'meta-fy2025':'googl-fy2025');
 const currentProfile=profile?.ticker===ticker&&profile.model_origin===result.submitted_inputs.anchor.annual_end?profile:null;
 const name=currentProfile?.name??(ticker==='META'?'Meta Platforms':'Alphabet');
 const outdated=stale||saved?.binding!==binding||saved?.formKey!==formKey;
 useEffect(()=>{capture?.({form,status:pending?'calculating':!saved?'not_calculated':outdated?'stale':'current',result:saved?.data??null,resultForm:saved?JSON.parse(saved.formKey):null,profile:currentProfile});},[capture,form,saved,pending,outdated,currentProfile]);
 const submitted=useRef({result,binding,formKey,form,base,ticker,profile:currentProfile});submitted.current={result,binding,formKey,form,base,ticker,profile:currentProfile};
 useEffect(()=>{
  if(!correctIssuer)return;
  const token=profileRevision.current.begin(),abort=new AbortController();
  setProfilePending(true);setProfile(null);setSaved(null);setForm(emptyForm);setFailure('');setDetails([]);
  void load<CompanyProfile>('/api/v1/analyst/'+ticker,undefined,abort.signal).then(value=>{
   if(profileRevision.current.current(token)){const checked=checkCompanyProfile(value,ticker,result);setProfile(checked);setForm(profileForm(checked.defaults));}
  }).catch(e=>{if(profileRevision.current.current(token)){setFailure(e instanceof ApiError?failureMessage(e):e instanceof Error?e.message:failureMessage(e));}}).finally(()=>{if(profileRevision.current.current(token))setProfilePending(false);});
  return()=>{profileRevision.current.edit();abort.abort();};
 },[ticker,result.submitted_inputs.anchor.annual_end,load,correctIssuer,profileRetry]);
 function stop(){revision.current.edit();controller.current?.abort();setPending(false);}
 useEffect(()=>{stop();setFailure('');setDetails([]);return()=>{revision.current.edit();controller.current?.abort();};},[ticker,binding,stale]);
 useEffect(()=>()=>{revision.current.edit();controller.current?.abort();},[]);
 async function calculate(){
  if(stale||busy||unsupported||!correctIssuer||!currentProfile)return;
  const snapshot=submitted.current,token=revision.current.begin();controller.current?.abort();const abort=new AbortController();controller.current=abort;setPending(true);setFailure('');setDetails([]);
  try{
   const assumptions=readForm(snapshot.form);
   const body={schema_version:'company-analyst-request-v1',ticker:snapshot.ticker,base_case:snapshot.base,assumptions};
   const data=await load<CompanyAnalystResult>('/api/v1/analyst/run',body,abort.signal);
   if(revision.current.current(token)&&submitted.current.binding===snapshot.binding&&submitted.current.formKey===snapshot.formKey)setSaved({data:checkCompanyAnalyst(data,snapshot.result,assumptions,snapshot.profile!),binding:snapshot.binding,formKey:snapshot.formKey});
  }catch(e){if(revision.current.current(token)){setFailure(e instanceof ApiError?failureMessage(e):e instanceof Error?e.message:failureMessage(e));setDetails(e instanceof ApiError?e.details:[]);}}
  finally{if(revision.current.current(token))setPending(false);}
 }
 useEffect(()=>{
  if(!active||stale||busy||unsupported||!correctIssuer||!currentProfile||formKey!==JSON.stringify(profileForm(currentProfile.defaults)))return;
  const key=ticker+binding+formKey;if(attempts.current.has(key))return;
  const timer=setTimeout(()=>{attempts.current.add(key);void calculate();},0);return()=>clearTimeout(timer);
 },[active,binding,stale,busy,unsupported,formKey,correctIssuer,currentProfile,ticker]);
 function edit(key:keyof Form,value:string){stop();setFailure('');setDetails([]);setForm(old=>({...old,[key]:value}));}
 const data=saved?.data.ticker===ticker?saved.data:undefined;
 if(!correctIssuer)return null;
 return <section className="apple-analyst" aria-labelledby="company-analyst-heading"><h2 id="company-analyst-heading">{name} · analyst valuation</h2>
  <p>Historical cash flows, financing and share valuation under disclosed analyst conventions. {label} · {result.stage_b.stage_a.years.length}-year forecast.</p>
  {stale&&<p role="status">Operating assumptions changed. Update valuation before recalculating {name} outputs.</p>}
  {unsupported&&<p role="status">Choose Perpetual growth to calculate the paired FCFF and FCFE analyst valuations.</p>}
  {data&&outdated&&<p className="apple-stale" role="status">Previous {name} analyst results · stale. Recalculate to reflect the current model and assumptions.</p>}
  <details><summary>Analyst assumptions · editable</summary><div className="apple-assumptions">{controls.filter(([key])=>ticker==='GOOGL'||!['nci_claim_usd','historical_minority_cash_share'].includes(key)).map(([key,name])=><label key={key}>{name}<input inputMode="decimal" aria-label={name} value={form[key]} disabled={!currentProfile} onChange={e=>edit(key,e.target.value)}/></label>)}</div><p>Changes apply when recalculated. Historical Other financing is an explicit classification assumption, not a newly reported fact.</p></details>
  <div className="apple-actions"><button disabled={stale||busy||pending||unsupported||!currentProfile} onClick={()=>void calculate()}>Calculate {name} analyst outputs</button>{pending&&<><span role="status">Calculating {name} outputs…</span><button onClick={stop}>Cancel {name} calculation</button></>}</div>
  {profilePending&&<p role="status">Loading {name} analyst assumptions…</p>}{failure&&<div role="alert"><p>{failure}</p>{details.map(s=><p key={s}>{s}</p>)}{!currentProfile&&<button onClick={()=>setProfileRetry(v=>v+1)}>Retry analyst assumptions</button>}</div>}
  {data&&<div aria-label={name+' analyst results'}><div className="apple-value-cards"><section aria-label="FCFF fair value per share"><h3>FCFF fair value per share</h3><strong>${fixedUnit(data.fcff.value_per_share_usd,'1',2)}</strong><p>{readableMoney(data.fcff.enterprise_value_usd)} enterprise value · {readableMoney(data.fcff.equity_value_usd)} equity value</p><small>WACC {fixedUnit(data.fcff.wacc,'0.01',2)}%</small></section><section aria-label="FCFE fair value per share"><h3>FCFE fair value per share</h3><strong>${fixedUnit(data.fcfe.value_per_share_usd,'1',2)}</strong><p>{readableMoney(data.fcfe.equity_value_usd)} equity value</p><small>Cost of equity {fixedUnit(data.fcfe.cost_of_equity,'0.01',2)}% · debt is not subtracted again</small></section></div>
   <p><b>Different financing assumptions:</b> FCFF uses the selected WACC target weights; FCFE assumes flat debt during the explicit forecast. These values are not expected to match. FCFE minus FCFF: ${fixedUnit(new D(data.fcfe.value_per_share_usd).minus(data.fcff.value_per_share_usd).toFixed(),'1',2)} per share.</p>
   <p>Fiscal-end analytical origin {data.model_origin}, using later-filed information. These are valuation estimates, not current market prices.</p>
   <details><summary>Five outputs · readiness and qualifications</summary><ul>{data.readiness.map(r=><li key={r.id}><b>{r.label}</b> · Analyst-ready with qualifications<p>{r.detail}</p></li>)}</ul></details>
   <details><summary>Five-year historical FCFF and FCFE</summary><p>Standardized historical calculations. Economic FCFE retains SBC as an expense; the CFO-based series preserves its cash-statement basis.</p>{ticker==='GOOGL'&&<p><b>Historical FCFE is a consolidated proxy when minority cash allocation is 0%; it is not verified parent cash.</b> A nonzero minority cash-flow share produces an analyst parent-common allocation estimate. The minority cash-flow share is an assumption, not a separately disclosed cash-flow amount. Consolidated FCFE remains visible for comparison. The minority-interest equity claim is deducted once in each valuation; debt is not subtracted again from FCFE equity value.</p>}<div className="cv-table-scroll"><table><thead><tr><th>Year</th><th>FCFF</th><th>{ticker==='GOOGL'&&new D(data.assumptions.historical_minority_cash_share).isZero()?'Unallocated consolidated FCFE proxy':'Parent-common FCFE · estimate'}</th><th>Consolidated FCFE</th><th>Economic FCFE</th><th>Reported Other financing</th></tr></thead><tbody>{data.historical.map(y=><tr key={y.fiscal_year}><th>FY{y.fiscal_year}</th>{[y.fcff_usd,y.fcfe_usd,y.consolidated_fcfe_usd,y.economic_fcfe_usd,y.other_financing_usd].map((v,i)=><td key={i}>{fixedUnit(v,'1000000000',2)}B</td>)}</tr>)}</tbody></table></div></details>
   <details><summary>FCFE forecast and financing</summary><div className="cv-table-scroll"><table><thead><tr><th>Year</th><th>FCFE</th><th>Interest</th><th>Net borrowing</th><th>Closing debt</th></tr></thead><tbody>{data.fcfe.years.map(y=><tr key={y.fiscal_year_label}><th>{y.fiscal_year_label}</th>{[y.fcfe_usd,y.interest_expense_usd,y.net_borrowing_usd,y.closing_debt_usd].map((v,i)=><td key={i}>{fixedUnit(v,'1000000000',2)}B</td>)}</tr>)}</tbody></table></div><p>Eligible cash {readableMoney(data.bridge.eligible_cash_usd)} after operating reserve {readableMoney(data.bridge.operating_reserve_usd)}. Financing claims {readableMoney(data.bridge.debt_claims_usd)}. Non-operating investments / other assets {readableMoney(data.bridge.additional_assets_usd)}; carrying-value proxy under an editable analyst assumption, not a verified fair value. Minority-interest equity claim {readableMoney(data.bridge.nci_claim_usd)}, deducted once from each valuation. Valuation shares {fixedUnit(data.bridge.valuation_shares,'1000000000',4)}B.</p></details>
   <details><summary>Sensitivity · value per share</summary><div className="cv-table-scroll"><table><thead><tr><th>Assumption</th><th>FCFF</th><th>FCFE</th></tr></thead><tbody>{data.sensitivities.map((s,i)=><tr key={i}><th>{s.label}</th><td>${fixedUnit(s.fcff_value_per_share_usd,'1',2)}</td><td>${fixedUnit(s.fcfe_value_per_share_usd,'1',2)}</td></tr>)}</tbody></table></div></details>
   <details><summary>Methodology and filing sources</summary>{data.qualifications.map((s,i)=><p key={i}>{s}</p>)}{data.source_urls.map(url=><p key={url}><a href={url} target="_blank" rel="noreferrer">Source · {url.split('/').at(-1)}</a></p>)}<small>Policy {data.policy_version}. Earlier evidence-review records retain their original findings; this analyst output applies the disclosed conventions above.</small></details>
   <ExportData value={{status:outdated?'stale':'current',selected_case:label,analyst_result:data}} name={ticker.toLowerCase()+'-analyst-valuation'}/>
  </div>}
 </section>;
}
