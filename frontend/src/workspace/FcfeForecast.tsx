import {useEffect,useRef,useState} from 'react';
import Decimal from 'decimal.js';
import {failureMessage,request,Revisions,ApiError} from '../api';
import type {Result} from '../model';
import {readableMoney,fixedUnit} from '../presentation';
import {ExportData} from './ExportData';
const D=Decimal.clone({precision:80});
const fields=['interest_expense_usd','cash_debt_issued_usd','new_finance_asset_funding_usd','principal_repaid_usd'] as const;
const labels=['Interest expense','Cash debt issued','New financed assets','Principal repaid'];
type Funding=Record<typeof fields[number],string>;
const blank=():Funding=>Object.fromEntries(fields.map(k=>[k,''])) as Funding;
export type FcfeResult={schema_version:'fcfe-forecast-result-v1';scope:string;submitted_inputs:unknown;years:({fiscal_year_label:string;fcfe_usd:string;net_borrowing_usd:string;closing_debt_usd:string;pv_fcfe_usd:string})[];terminal:Record<string,string>;equity_value_usd:string;pv_explicit_fcfe_usd:string;pv_terminal_equity_usd:string;limitations:string[]};
function numeric(s:string,scale:string){if(!/^-?\d+(?:\.\d+)?$/.test(s.trim()))throw Error('Complete every financing input with a decimal number. Enter 0 explicitly when appropriate.');return new D(s).times(scale).toFixed();}
export function operatingCase(input:Result['submitted_inputs']){
 const doc=structuredClone(input) as unknown as Record<string,unknown>;
 delete doc.bridge;
 if(doc.schema_version==='investor-case-v2'){doc.schema_version='investor-case-v1';delete doc.calculation_scope;}
 if(doc.schema_version==='investor-case-v3'||doc.schema_version==='investor-case-v4')doc.calculation_scope='ENTERPRISE_VALUE';
 return doc;
}
export function FcfeForecast({result,stale,busy,load=request}:{result:Result;stale:boolean;busy:boolean;load?:typeof request}){
 const [rate,setRate]=useState(''),[debt,setDebt]=useState(''),[growth,setGrowth]=useState('');
 const [scope,setScope]=useState('CONSOLIDATED_BEFORE_NCI_ATTRIBUTION');
 const [rows,setRows]=useState<Funding[]>(()=>result.stage_b.stage_a.years.map(blank)),[terminal,setTerminal]=useState<Funding>(blank);
 const [value,setValue]=useState<FcfeResult|null>(null),[failure,setFailure]=useState(''),[details,setDetails]=useState<string[]>([]),[pending,setPending]=useState(false);
 const revisions=useRef(new Revisions()),controller=useRef<AbortController|null>(null);
 useEffect(()=>()=>{revisions.current.edit();controller.current?.abort();},[]);
 function edit(action:()=>void){revisions.current.edit();controller.current?.abort();setPending(false);setValue(null);setFailure('');setDetails([]);action();}
 const base=operatingCase(result.submitted_inputs),terminalMethod=(base.terminal_valuation as {method?:string}|undefined)?.method;
 const unsupported=terminalMethod==='exit_multiple';
 async function calculate(){
  const token=revisions.current.begin();controller.current?.abort();const c=new AbortController();controller.current=c;setPending(true);setFailure('');setDetails([]);setValue(null);
  try{
   const convert=(r:Funding)=>Object.fromEntries(fields.map(k=>[k,numeric(r[k],'1000000')]));
   const body={schema_version:'fcfe-forecast-request-v1',base_case:base,scope,cost_of_equity:numeric(rate,'0.01'),opening_debt_usd:numeric(debt,'1000000'),terminal_growth:numeric(growth,'0.01'),financing_years:rows.map((r,i)=>({period_index:i+1,...convert(r)})),terminal_financing:convert(terminal)};
   const out=await load<FcfeResult>('/api/v1/fcfe/run',body,c.signal);
   if(revisions.current.current(token))setValue(out);
  }catch(e){if(revisions.current.current(token)){setFailure(e instanceof Error&&!(e instanceof ApiError)?e.message:failureMessage(e));setDetails(e instanceof ApiError?e.details:[]);}}
  finally{if(revisions.current.current(token))setPending(false);}
 }
 const fundingInputs=(r:Funding,set:(next:Funding)=>void,prefix:string)=>fields.map((k,j)=><td key={k}><input aria-label={prefix+' '+labels[j]} inputMode="decimal" value={r[k]} onChange={e=>edit(()=>set({...r,[k]:e.target.value}))}/></td>);
 return <details className="cv-secondary"><summary>FCFE forecast · explicit financing and cost of equity</summary>
  <p>Uses this submitted operating forecast. All financing entries are manual assumptions. No missing historical financing or minority allocation is filled automatically.</p>
  {stale&&<p role="status">Operating forecast is stale. Update valuation before calculating FCFE.</p>}
  {unsupported&&<p role="status">Choose Perpetual growth in the operating model first. This FCFE route requires independent terminal operating inputs.</p>}
  <label>Ownership scope <select value={scope} onChange={e=>edit(()=>setScope(e.target.value))}><option value="CONSOLIDATED_BEFORE_NCI_ATTRIBUTION">Consolidated · before minority allocation</option><option value="DECLARED_PARENT_COMMON">Parent common · user-declared assumption</option></select></label>
  <div className="fcfe-rates">{[['Cost of equity (%)',rate,setRate],['Opening debt (USD millions)',debt,setDebt],['FCFE terminal growth (%)',growth,setGrowth]].map(([label,v,set])=><label key={label as string}>{label as string}<input inputMode="decimal" value={v as string} onChange={e=>edit(()=>(set as (s:string)=>void)(e.target.value))}/></label>)}</div>
  <p>Financing amounts below: USD millions. Principal includes cash debt and finance-lease repayments once. New financed assets must be contained in operating investment. Terminal net borrowing must equal final-year debt × terminal growth for the stable capital structure assumption.</p>
  <button onClick={()=>edit(()=>{setRows(rows.map(()=>Object.fromEntries(fields.map(k=>[k,'0'])) as Funding));setTerminal(Object.fromEntries(fields.map(k=>[k,'0'])) as Funding);})}>Declare all financing entries zero</button>
  <div className="cv-table-scroll"><table><caption>Annual and terminal financing assumptions · enter each value explicitly</caption><thead><tr><th>Year</th>{labels.map(s=><th key={s}>{s}</th>)}</tr></thead><tbody>{rows.map((r,i)=><tr key={i}><th>{String(result.stage_b.stage_a.years[i].fiscal_year_label)}</th>{fundingInputs(r,next=>setRows(rows.map((old,j)=>j===i?next:old)),'Year '+(i+1))}</tr>)}<tr><th>Terminal year</th>{fundingInputs(terminal,setTerminal,'Terminal year')}</tr></tbody></table></div>
  <button disabled={stale||busy||pending||unsupported} onClick={()=>void calculate()}>Calculate FCFE equity value</button>{pending&&<><span role="status"> Calculating FCFE…</span><button onClick={()=>edit(()=>{})}>Cancel FCFE calculation</button></>}
  {failure&&<div role="alert"><p>{failure}</p>{details.map(s=><p key={s}>{s}</p>)}</div>}
  {value&&<section aria-label="FCFE result"><h3>FCFE equity value · {value.scope==='DECLARED_PARENT_COMMON'?'User-declared parent common':'Consolidated · before minority allocation'}</h3><strong>{readableMoney(value.equity_value_usd)}</strong><p>User assumptions · ownership and sustainability not independently certified. No debt is subtracted again. Value per share is not certified.</p><div className="cv-table-scroll"><table><thead><tr><th>Year</th><th>FCFE</th><th>Net borrowing</th><th>Closing debt</th></tr></thead><tbody>{value.years.map((y,i)=><tr key={i}><th>{y.fiscal_year_label}</th>{[y.fcfe_usd,y.net_borrowing_usd,y.closing_debt_usd].map((v,j)=><td key={j}>{fixedUnit(v,'1000000000',2)}B</td>)}</tr>)}</tbody></table></div>{value.limitations.map(s=><p key={s}>{s}</p>)}<ExportData value={value} name="manual-fcfe-forecast"/></section>}
 </details>;
}
