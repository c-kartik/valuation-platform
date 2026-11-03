import {useEffect,useState} from 'react';
import {failureMessage,request} from '../api';
import {fixedUnit} from '../presentation';
import {ExportData} from './ExportData';

type Metric={amount_usd:string|null;status:string;scope:string;basis:string;cleared:boolean;source_urls:string[];parent_common_amount_usd?:string|null;parent_common_status?:string;open_items:string[]};
export type CashFlowReview={schema_version:'pilot-company-cashflows-v1';ticker:string;status:'OPEN';review_passed:boolean;notice:string;unresolved_scope_items:string[];periods:{fiscal_year:number;annual_start:string;annual_end:string;accession:string;revenue_usd:string;reported_cash_fcf_usd:string;identified_net_borrowing_usd:string;fcff:Metric;fcfe:Metric}[]};
const decimal=(value:unknown)=>typeof value==='string'&&/^-?\d+(?:\.\d+)?$/.test(value)&&Number.isFinite(Number(value));
export function checkCashFlows(value:CashFlowReview,ticker:string){
 if(value?.schema_version!=='pilot-company-cashflows-v1'||value.ticker!==ticker||value.status!=='OPEN'||value.review_passed!==false||!Array.isArray(value.unresolved_scope_items)||!value.unresolved_scope_items.every(s=>typeof s==='string')||!Array.isArray(value.periods)||value.periods.length!==5)throw Error('Incompatible cash-flow review');
 value.periods.forEach((p,i)=>{
  if(p.fiscal_year!==2021+i||typeof p.annual_end!=='string')throw Error('Incompatible annual period');
  for(const m of [p.fcff,p.fcfe])if(!m||!(m.amount_usd===null||decimal(m.amount_usd))||typeof m.status!=='string'||typeof m.scope!=='string'||!Array.isArray(m.open_items)||!Array.isArray(m.source_urls)||!m.source_urls.every(u=>typeof u==='string'&&/^https:\/\/www\.sec\.gov\//.test(u)))throw Error('Incompatible metric');
  if(p.fcfe.cleared||p.fcfe.parent_common_amount_usd!==null)throw Error('Unreviewed parent-common FCFE');
 });
 return value;
}
const money=(value:string|null)=>value===null?'Unavailable':fixedUnit(value,'1000000000',2)+'B';
export function HistoricalCashFlows({ticker,active,load=request}:{ticker:string;active:boolean;load?:typeof request}){
 const [data,setData]=useState<CashFlowReview|null>(null),[failure,setFailure]=useState(''),[retry,setRetry]=useState(0);
 useEffect(()=>{
  if(!active||!['AAPL','META','GOOGL'].includes(ticker))return;
  let live=true;const controller=new AbortController();setFailure('');
  void load<CashFlowReview>('/api/v1/cashflows/'+ticker,undefined,controller.signal).then(d=>{if(live)setData(checkCashFlows(d,ticker));}).catch(e=>{if(live)setFailure(failureMessage(e));});
  return()=>{live=false;controller.abort();};
 },[active,ticker,retry,load]);
 if(!['AAPL','META','GOOGL'].includes(ticker))return <p>Select a registered company to review filing-derived cash flows.</p>;
 return <section aria-label="Five-year FCFF and FCFE review" className="p-panel">
  <h2>Historical cash flows · {ticker}</h2>
  <p>FY2021–FY2025 · USD billions. Company review remains open.</p>
  {failure?<p role="alert">{failure} <button onClick={()=>setRetry(n=>n+1)}>Retry cash-flow review</button></p>:!data?<p role="status">Loading filing-derived cash flows…</p>:<>
   <p className="cv-issues">FCFE review amounts below are not cleared cash flows attributable to the parent’s common shareholders. Missing values are not zero.</p>
   <div className="cv-table-scroll"><table><caption>Five annual FCFF and FCFE records · status and ownership shown with each amount</caption><thead><tr><th>Year</th><th>FCFF · stated cash convention</th><th>FCFE · review calculation</th><th>Parent-common FCFE</th></tr></thead><tbody>{data.periods.map(p=><tr key={p.fiscal_year}><th>FY{p.fiscal_year}<small style={{display:'block'}}>{p.annual_end}</small></th><td>{money(p.fcff.amount_usd)}<small style={{display:'block'}}>{p.fcff.amount_usd===null?'Missing interest disclosure':'Available under stated cash convention'}</small></td><td>{money(p.fcfe.amount_usd)}<small style={{display:'block'}}>{p.fcfe.status==='CONSOLIDATED_BEFORE_NCI_ATTRIBUTION'?'Consolidated · before minority allocation':'Provisional · financing classification open'}</small></td><td>{money(p.fcfe.parent_common_amount_usd??null)}<small style={{display:'block'}}>{p.fcfe.parent_common_status==='UNAVAILABLE_ATTRIBUTION_NOT_DISCLOSED'?'Minority cash allocation missing':'Financing scope unresolved'}</small></td></tr>)}</tbody></table></div>
   <p>{data.notice}</p><p>Broader review remains open: {data.unresolved_scope_items.join(', ')}. Annual amount checks do not clear valuation, ownership or per-share inputs.</p>
   <details><summary>Calculation inputs, filing sources and open items</summary>{data.periods.map(p=><section key={p.fiscal_year}><h3>FY{p.fiscal_year}</h3><p>CFO less net cash PP&amp;E: {money(p.reported_cash_fcf_usd)}. Identified net borrowing: {money(p.identified_net_borrowing_usd)}.</p><p>FCFF basis: {p.fcff.basis}. FCFE scope: {p.fcfe.scope}. Open items: {[...p.fcff.open_items,...p.fcfe.open_items].join(', ')}.</p>{[...new Set([...p.fcff.source_urls,...p.fcfe.source_urls])].map(url=><p key={url}><a href={url} target="_blank" rel="noreferrer">SEC filing · {url.split('/').at(-1)}</a></p>)}</section>)}</details>
   <ExportData value={data} name={ticker+'-five-year-fcff-fcfe-review'}/>
  </>}
 </section>;
}
