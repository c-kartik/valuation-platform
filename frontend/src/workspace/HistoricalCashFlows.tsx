import {useEffect,useState} from 'react';
import {failureMessage,request} from '../api';
import {fixedUnit} from '../presentation';
import {ExportData} from './ExportData';
import {AppleResolution,checkAppleResolution} from './AppleResolution';
import type {AppleResolutionData} from './AppleResolution';

type Metric={amount_usd:string|null;status:string;scope:string;basis:string;cleared:boolean;source_urls:string[];operands?:Record<string,string>;qualifications?:string[];parent_common_amount_usd?:string|null;parent_common_status?:string;open_items:string[]};
type Readiness={schema_version:'cashflow-consumer-readiness-v1';counts:{available_stated_convention:number;provisional_financing:number;missing_required_input:number;parent_common_fcfe_available:number};gates:{id:string;label:string;status:string;detail:string}[];financial_review_status:'OPEN';history_gap_disables_manual_forecast:false;amounts_changed:boolean;prior_clearance_flags_changed:false};
export type CashFlowReview={schema_version:'pilot-company-cashflows-v1';ticker:string;status:'OPEN';review_passed:boolean;notice:string;unresolved_scope_items:string[];current_resolution?:AppleResolutionData;readiness?:Readiness;periods:{fiscal_year:number;annual_start:string;annual_end:string;accession:string;revenue_usd:string;reported_cash_fcf_usd:string;identified_net_borrowing_usd:string;fcff:Metric;fcfe:Metric}[]};
const decimal=(value:unknown)=>typeof value==='string'&&/^-?\d+(?:\.\d+)?$/.test(value)&&Number.isFinite(Number(value));
export function checkCashFlows(value:CashFlowReview,ticker:string){
 if(value?.schema_version!=='pilot-company-cashflows-v1'||value.ticker!==ticker||value.status!=='OPEN'||value.review_passed!==false||!Array.isArray(value.unresolved_scope_items)||!value.unresolved_scope_items.every(s=>typeof s==='string')||!Array.isArray(value.periods)||value.periods.length!==5)throw Error('Incompatible cash-flow review');
 value.periods.forEach((p,i)=>{
  if(p.fiscal_year!==2021+i||typeof p.annual_end!=='string')throw Error('Incompatible annual period');
  for(const m of [p.fcff,p.fcfe])if(!m||!(m.amount_usd===null||decimal(m.amount_usd))||typeof m.status!=='string'||typeof m.scope!=='string'||!Array.isArray(m.open_items)||!Array.isArray(m.source_urls)||!m.source_urls.every(u=>typeof u==='string'&&/^https:\/\/www\.sec\.gov\//.test(u)))throw Error('Incompatible metric');
  if(p.fcfe.cleared||p.fcfe.parent_common_amount_usd!==null)throw Error('Unreviewed parent-common FCFE');
  if(p.fcfe.status!==(ticker==='GOOGL'?'CONSOLIDATED_BEFORE_NCI_ATTRIBUTION':'PROVISIONAL_FINANCING_SCOPE_UNRESOLVED')||p.fcfe.scope!==(ticker==='GOOGL'?'CONSOLIDATED_BEFORE_NCI_ATTRIBUTION':'IDENTIFIED_FINANCING_ONLY'))throw Error('Incompatible financing or ownership scope');
 });
 if(value.readiness){const r=value.readiness;
  const available=value.periods.filter(p=>p.fcff.amount_usd!==null).length+(ticker==='GOOGL'?5:0);
  if(r.schema_version!=='cashflow-consumer-readiness-v1'||r.financial_review_status!=='OPEN'||r.history_gap_disables_manual_forecast!==false||r.amounts_changed!==value.periods.every(p=>p.fcff.basis==='STANDARDIZED_EBIT_CURRENT_NWC_CASH_PPE')||r.prior_clearance_flags_changed!==false||r.counts.available_stated_convention!==available||r.counts.provisional_financing!==(ticker==='GOOGL'?0:5)||r.counts.missing_required_input!==10-available-r.counts.provisional_financing||r.counts.parent_common_fcfe_available!==0||!Array.isArray(r.gates)||r.gates.map(g=>g.id).join(',')!=='history,parent_cash,comparison,forecast,parent_value,per_share'||r.gates.some(g=>typeof g.label!=='string'||typeof g.detail!=='string')||r.gates.map(g=>g.status).join(',')!=='SCOPED_AVAILABILITY,UNAVAILABLE,NOT_CLEARED,REVIEW_SEPARATELY,REVIEW_SEPARATELY,REVIEW_SEPARATELY')throw Error('Incompatible consumer readiness');
 }
 if(value.current_resolution){if(ticker!=='AAPL')throw Error('Apple resolution attached to another issuer');checkAppleResolution(value.current_resolution);}
 return value;
}
const money=(value:string|null)=>value===null?'Unavailable':fixedUnit(value,'1000000000',2)+'B';
export function HistoricalCashFlows({ticker,active,load=request}:{ticker:string;active:boolean;load?:typeof request}){
 const [data,setData]=useState<CashFlowReview|null>(null),[failure,setFailure]=useState(''),[retry,setRetry]=useState(0);
 useEffect(()=>{
  setData(null);setFailure('');
  if(!active||!['AAPL','META','GOOGL'].includes(ticker))return;
  let live=true;const controller=new AbortController();setFailure('');
  void load<CashFlowReview>('/api/v1/cashflows/'+ticker,undefined,controller.signal).then(d=>{if(live)setData(checkCashFlows(d,ticker));}).catch(e=>{if(live)setFailure(failureMessage(e));});
  return()=>{live=false;controller.abort();};
 },[active,ticker,retry,load]);
 if(!['AAPL','META','GOOGL'].includes(ticker))return <p>Select a registered company to review filing-derived cash flows.</p>;
 return <section aria-label="Five-year FCFF and FCFE review" className="p-panel">
  <h2>Historical cash flows · {ticker}</h2>
  <p>FY2021–FY2025 · USD billions. Earlier evidence review · current analyst valuations and adopted assumptions are in DCF.</p>
  {failure?<p role="alert">{failure} <button onClick={()=>setRetry(n=>n+1)}>Retry cash-flow review</button></p>:!data||data.ticker!==ticker?<p role="status">Loading filing-derived cash flows…</p>:<>
   <p className="cv-issues">{ticker==='AAPL'?'This preserves the original exact-reconstruction review. Apple’s current analyst FCFE estimate, qualifications and both share valuations are shown in DCF.':ticker==='GOOGL'?'Consolidated FCFE is available under the stated cash convention, before minority allocation. Parent-common cash remains unavailable.':'FCFE calculations remain provisional until financing classification is resolved.'} Missing values are not zero.</p>
   <div className="cv-table-scroll"><table><caption>Five annual FCFF and FCFE records · status and ownership shown with each amount</caption><thead><tr><th>Year</th><th>FCFF · stated method</th><th>FCFE · review calculation</th><th>Parent-common FCFE</th></tr></thead><tbody>{data.periods.map(p=><tr key={p.fiscal_year}><th>FY{p.fiscal_year}<small style={{display:'block'}}>{p.annual_end}</small></th><td>{money(p.fcff.amount_usd)}<small style={{display:'block'}}>{p.fcff.amount_usd===null?'Missing interest disclosure':p.fcff.basis==='STANDARDIZED_EBIT_CURRENT_NWC_CASH_PPE'?'Standardized operating-income method':'Available under stated cash convention'}</small></td><td>{money(p.fcfe.amount_usd)}<small style={{display:'block'}}>{p.fcfe.status==='CONSOLIDATED_BEFORE_NCI_ATTRIBUTION'?'Consolidated · before minority allocation':'Provisional · financing classification open'}</small></td><td>{money(p.fcfe.parent_common_amount_usd??null)}<small style={{display:'block'}}>{p.fcfe.parent_common_status==='UNAVAILABLE_ATTRIBUTION_NOT_DISCLOSED'?'Minority cash allocation missing':'Financing scope unresolved'}</small></td></tr>)}</tbody></table></div>
   {data.readiness&&<section aria-label="Separate availability and valuation checks"><h3>Availability and valuation checks</h3><p>{data.readiness.counts.available_stated_convention} historical calculations available under stated conventions · {data.readiness.counts.provisional_financing} provisional · {data.readiness.counts.missing_required_input} missing required inputs. Manual forecasts use their own inputs and validation.</p><dl>{data.readiness.gates.map(g=><div key={g.id}><dt>{g.label}</dt><dd>{g.detail}</dd></div>)}</dl></section>}
   <p>{data.notice}</p>{ticker==='AAPL'&&data.periods[0].fcff.basis==='STANDARDIZED_EBIT_CURRENT_NWC_CASH_PPE'&&<p>All five Apple FCFF observations use the same standardized method. The previous CFO-based series and its FY2024–25 gaps are retained in the export. Current tax accruals and mixed Other current balances are included by convention; these are not separately reported FCFF figures.</p>}<p>Broader review remains open: {data.unresolved_scope_items.join(', ')}. Annual amount checks do not clear valuation, ownership or per-share inputs.</p>
   <details><summary>Calculation inputs, filing sources and open items</summary>{data.periods.map(p=><section key={p.fiscal_year}><h3>FY{p.fiscal_year}</h3><p>CFO less net cash PP&amp;E: {money(p.reported_cash_fcf_usd)}. Identified net borrowing: {money(p.identified_net_borrowing_usd)}.</p>{p.fcff.operands&&<p>FCFF inputs (USD): {Object.entries(p.fcff.operands).map(([k,v])=>`${k}: ${v}`).join('; ')}.</p>}{p.fcff.qualifications?.map(q=><p key={q}>{q}</p>)}<p>FCFF basis: {p.fcff.basis}. FCFE scope: {p.fcfe.scope}. Open items: {[...p.fcff.open_items,...p.fcfe.open_items].join(', ')}.</p>{[...new Set([...p.fcff.source_urls,...p.fcfe.source_urls])].map(url=><p key={url}><a href={url} target="_blank" rel="noreferrer">SEC filing · {url.split('/').at(-1)}</a></p>)}</section>)}</details>
   {data.current_resolution&&<AppleResolution data={data.current_resolution}/>}
   <ExportData value={data} name={ticker+'-five-year-fcff-fcfe-review'}/>
  </>}
 </section>;
}
