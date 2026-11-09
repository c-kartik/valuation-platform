import type {QuarterlyReport,Operand} from './model';
export type MixSeries={id:string;label:string;role?:string};
export type MixOperand=Operand&{namespace:string;context_ids:string[];dimensions:{axis:string;axis_namespace:string;member:string;member_namespace:string}[]};
export type MixQuarter={id:string;start:string;end:string;fiscal_year:number;quarter:number;total:number;values:Record<string,number>;evidence:Record<string,{method:string;operands:MixOperand[]}>;total_evidence:MixOperand[]};
export type RevenueMixReport={schema_version:1;policy:string;ticker:string;as_of:string;currency:'USD';kind:string;basis:string;notes:string[];source_manifest_sha256:string;series:MixSeries[];detail:{parent:string|null;series:MixSeries[]};rows:MixQuarter[];validation:{quarter_total_checks:number;operand_total_checks:number;parent_detail_checks:number;direct_quarter_checks:{quarter:string;series:string;derived:number;reported:number;difference:number}[]}};
export function validateMix(value:unknown,ticker:string,history:QuarterlyReport):RevenueMixReport{
 const p=value as RevenueMixReport;
 if(p?.schema_version!==1||p.policy!=='filing-dimensional-revenue-mix-v1'||p.ticker!==ticker||p.currency!=='USD'||p.as_of!==history.as_of||!p.source_manifest_sha256||!Array.isArray(p.rows)||p.rows.length!==history.rows.length||!Array.isArray(p.series)||!p.series.length||!p.detail||!Array.isArray(p.detail.series))throw Error('Unsupported revenue-mix package');
 const all=[...p.series,...p.detail.series],ids=all.map(s=>s.id);
 if(new Set(ids).size!==ids.length||all.some(s=>!s.id||!s.label)||p.detail.series.length&&!p.series.some(s=>s.id===p.detail.parent))throw Error('Invalid revenue hierarchy');
 for(const [i,r]of p.rows.entries()){
  const h=history.rows[i];
  if(r.id!==h.id||r.fiscal_year!==h.fiscal_year||r.quarter!==h.quarter||r.start!==h.start||r.end!==h.end||r.total!==h.values.revenue||!Number.isSafeInteger(r.total)||r.total<=0||ids.some(k=>!Number.isSafeInteger(r.values?.[k])))throw Error('Revenue periods or amounts contradict history');
  if(p.series.reduce((n,s)=>n+r.values[s.id],0)!==r.total)throw Error('Revenue mix does not reconcile');
  if(p.detail.series.length&&p.detail.series.reduce((n,s)=>n+r.values[s.id],0)!==r.values[p.detail.parent!])throw Error('Revenue detail does not reconcile');
  if(!Array.isArray(r.total_evidence)||![1,2].includes(r.total_evidence.length)||r.total_evidence.some(o=>!Number.isSafeInteger(o.value))||r.total_evidence[0].value-(r.total_evidence[1]?.value??0)!==r.total)throw Error('Missing consolidated evidence');
  for(const s of all){
   if(s.role!=='adjustment'&&r.values[s.id]<0)throw Error('Negative operating revenue');
   const e=r.evidence?.[s.id];
   if(!e?.method||!Array.isArray(e.operands)||![1,2].includes(e.operands.length)||e.operands.some(o=>!Number.isSafeInteger(o.value)||!o.source_url.startsWith('https://www.sec.gov/Archives/edgar/data/')||!o.accession||!o.context_ids?.length))throw Error('Missing revenue evidence');
   if(e.operands.length!==r.total_evidence.length||e.operands.some((o,j)=>o.start!==r.total_evidence[j].start||o.end!==r.total_evidence[j].end||o.accession!==r.total_evidence[j].accession||o.filed>p.as_of)||e.operands[0].value-(e.operands[1]?.value??0)!==r.values[s.id])throw Error('Evidence contradicts revenue amount');
  }
 }
 return p;
}
export async function fetchMix(ticker:string,history:QuarterlyReport,signal:AbortSignal){
 const response=await fetch(`${(import.meta as ImportMeta & {env:{BASE_URL:string}}).env.BASE_URL}revenue-mix/${ticker}.json`,{signal});
 if(!response.ok)throw Error('Revenue mix unavailable');
 return validateMix(await response.json(),ticker,history);
}
export function displaySeries(report:RevenueMixReport,expanded:boolean):MixSeries[]{
 return report.series.flatMap(s=>expanded&&s.id===report.detail.parent?report.detail.series:[s]);
}
export function yoy(report:RevenueMixReport,index:number,key:string):number|null{
 const current=report.rows[index],prior=report.rows.find(r=>r.fiscal_year===current.fiscal_year-1&&r.quarter===current.quarter);
 if(!prior||prior.values[key]<=0||report.series.find(s=>s.id===key)?.role==='adjustment')return null;
 return (current.values[key]/prior.values[key]-1)*100;
}
