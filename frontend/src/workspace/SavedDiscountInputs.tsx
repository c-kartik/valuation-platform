import {useEffect,useState} from 'react';
import {failureMessage,request} from '../api';
import {percentage,fixedUnit} from '../presentation';
type Snapshot={schema_version:'saved-discount-inputs-v1';ticker:string;economic_hash:string;status:string;cost_of_equity:string|null;cost_of_equity_percent:string|null;base_wacc:string|null;information_review:string;model_origin:string;automatic_adoption:false;scenario_wacc_offset_applied_to_cost_of_equity:false;operands:Record<string,string>;sources:{id:string;title:string;url:string;sha256:string}[];observed_macro_inputs:{key:string;end:string;value:string}[];limitations:string[]};
const decimal=(v:unknown)=>typeof v==='string'&&/^[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?$/.test(v)&&Number.isFinite(Number(v));
export function checkDiscountInputs(value:Snapshot,ticker:string,hash:string){
 if(value?.schema_version!=='saved-discount-inputs-v1'||value.ticker!==ticker||value.economic_hash!==hash||value.automatic_adoption!==false||value.scenario_wacc_offset_applied_to_cost_of_equity!==false||!['CONFIGURED_CONVENTION','UNAVAILABLE'].includes(value.status)||!Array.isArray(value.sources)||!Array.isArray(value.observed_macro_inputs)||!Array.isArray(value.limitations)||!value.limitations.every(s=>typeof s==='string'))throw Error('Saved discount assumptions do not match the submitted operating profile.');
 if(value.status==='CONFIGURED_CONVENTION'&&(!decimal(value.cost_of_equity)||!decimal(value.cost_of_equity_percent)||!decimal(value.base_wacc)||!value.operands||!['risk_free','erp','beta','spread','equity_weight','debt_weight','tax_shield'].every(k=>decimal(value.operands[k]))||value.sources.length!==2||!value.sources.every(s=>typeof s.url==='string'&&s.url.startsWith('https://')&&typeof s.sha256==='string'&&/^[a-f0-9]{64}$/.test(s.sha256))||value.observed_macro_inputs.length!==2))throw Error('Saved discount assumptions are incomplete.');
 if(value.status==='UNAVAILABLE'&&(value.cost_of_equity!==null||value.cost_of_equity_percent!==null))throw Error('Unavailable assumptions cannot supply a rate.');
 return value;
}
export function SavedDiscountInputs({ticker,profileHash,active,choose,load=request}:{ticker:string;profileHash?:string;active:boolean;choose:(percent:string)=>void;load?:typeof request}){
 const [data,setData]=useState<Snapshot|null>(null),[failure,setFailure]=useState(''),[retry,setRetry]=useState(0);
 useEffect(()=>{
  setData(null);setFailure('');
  if(!active||!profileHash||!['AAPL','META','GOOGL'].includes(ticker))return;
  let live=true;const c=new AbortController();
  void load<Snapshot>('/api/v1/discount-inputs/'+ticker,undefined,c.signal).then(d=>{if(live)setData(checkDiscountInputs(d,ticker,profileHash));}).catch(e=>{if(live)setFailure(failureMessage(e));});
  return()=>{live=false;c.abort();};
 },[active,ticker,profileHash,retry,load]);
 if(!profileHash||!active)return null;
 if(failure)return <p role="status">Saved discount assumptions could not be matched. Enter cost of equity manually or <button onClick={()=>setRetry(n=>n+1)}>Retry discount assumptions</button>.</p>;
 if(!data||data.ticker!==ticker||data.economic_hash!==profileHash)return <p role="status">Loading dated discount assumptions…</p>;
 return <section aria-label="Saved CAPM starting assumptions"><h3>Saved CAPM starting assumptions</h3><p>Reviewed {data.information_review} · model origin {data.model_origin}. These are dated assumptions, not live market capital costs.</p>{data.status==='CONFIGURED_CONVENTION'?<>
 <p>Cost of equity {percentage(data.cost_of_equity)} · Base WACC {percentage(data.base_wacc)}. Beta {fixedUnit(data.operands.beta,'1',2)} is a configured assumption.</p>
 <button onClick={()=>choose(data.cost_of_equity_percent!)}>Use saved CAPM cost of equity ({percentage(data.cost_of_equity)})</button>
 <details><summary>Rate inputs, dates and sources</summary><p>Risk-free rate {percentage(data.operands.risk_free)}; equity risk premium {percentage(data.operands.erp)}; beta {data.operands.beta}; credit spread {percentage(data.operands.spread)}; target equity / debt weights {percentage(data.operands.equity_weight)} / {percentage(data.operands.debt_weight)}; tax shield {percentage(data.operands.tax_shield)}.</p>{data.observed_macro_inputs.map(o=><p key={o.key}>{o.key==='treasury_10y'?'Treasury observation':'ERP observation'}: {o.end}.</p>)}{data.sources.map(s=><p key={s.id}><a href={s.url} target="_blank" rel="noreferrer">{s.title}</a></p>)}</details>
 </>:<p>The saved WACC inputs are missing, incompatible or stale. Review a cost of equity manually.</p>}{data.limitations.map(s=><p key={s}>{s}</p>)}</section>;
}
