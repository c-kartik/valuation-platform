import Decimal from 'decimal.js';
const MoneyDecimal=Decimal.clone({precision:30,rounding:Decimal.ROUND_HALF_UP});
export const billions=(n:number)=>new MoneyDecimal(Math.abs(n)).div(1e9).toFixed(2);
export type Metric='revenue'|'operating_income'|'net_income'|'cfo'|'cash_capex'|'sbc'|'fcf'|'other_operating'|'operating_margin'|'fcf_margin';
export type Operand={value:number;concept:string;start:string;end:string;filed:string;accession:string;source_url:string};
export type Quarter={id:string;fiscal_year:number;quarter:number;start:string;end:string;values:Record<Metric,number|null>;evidence:Record<string,{classification:string;method:string;operands:Operand[]}>};
export type QuarterlyReport={schema_version:1;policy:string;ticker:string;company:string;as_of:string;currency:'USD';basis:string;source_snapshot_sha256:string;source_url:string;rows:Quarter[];limitations:string[];validation:{bridge_checks:number;annual_tie_outs:unknown[];discrete_quarter_checks:{quarter_id:string;metric:Metric;difference:number;derived:number;reported:Operand}[]}};
export const groups={cash:['revenue','cfo','cash_capex','fcf'],business:['revenue','operating_income','net_income'],margins:['operating_margin','fcf_margin']} as const;
export const labels:Record<Metric,string>={revenue:'Revenue',operating_income:'Operating income',net_income:'Net income',cfo:'Operating cash flow',cash_capex:'Cash capex',sbc:'Stock-based compensation',fcf:'Free cash flow',other_operating:'Other operating reconciliation',operating_margin:'Operating margin',fcf_margin:'FCF margin'};
export const money=(n:number|null)=>n===null?'Unavailable':`${n<0?'−':''}$${billions(n)}B`;
export function validateReport(value:unknown,ticker:string):QuarterlyReport{
 const p=value as QuarterlyReport;
 if(p?.schema_version!==1||p.ticker!==ticker||p.currency!=='USD'||!Array.isArray(p.rows)||p.rows.length!==20||!p.policy||!p.basis||!p.source_snapshot_sha256)throw Error('Unsupported quarterly dataset');
 for(const [i,r] of p.rows.entries()){
  if(!r.id||!/^\d{4}-\d{2}-\d{2}$/.test(r.end)||!r.evidence||Object.keys(labels).some(k=>r.values?.[k as Metric]!==null&&!Number.isFinite(r.values?.[k as Metric]))||r.values.cash_capex===null||r.values.cash_capex<0)throw Error('Incomplete quarterly observations');
  if(['revenue','operating_income','net_income','cfo','cash_capex','sbc','fcf','other_operating'].some(k=>!Number.isSafeInteger(r.values[k as Metric])))throw Error('Missing or unsafe financial amount');
  const v=r.values as Record<Metric,number>;
  if(v.cfo-v.cash_capex!==v.fcf||v.net_income+v.sbc+v.other_operating!==v.cfo)throw Error('Cash-flow reconciliation failed');
  if(i&&p.rows[i-1].end>=r.end)throw Error('Unordered reporting periods');
 }
 return p;
}
export async function fetchReport(ticker:string,signal:AbortSignal){
 const response=await fetch(`${(import.meta as ImportMeta & {env:{BASE_URL:string}}).env.BASE_URL}research-data/${ticker}.json`,{signal});
 if(!response.ok)throw Error('Quarterly dataset unavailable');
 return validateReport(await response.json(),ticker);
}
