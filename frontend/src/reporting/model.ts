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
 if(p?.schema_version!==1||p.policy!=='quarterly-reported-usd-v1'||p.ticker!==ticker||p.currency!=='USD'||!Array.isArray(p.rows)||p.rows.length!==20||!p.policy||!p.basis||!p.source_snapshot_sha256)throw Error('Unsupported quarterly dataset');
 for(const [i,r] of p.rows.entries()){
  if(!r.id||!/^\d{4}-\d{2}-\d{2}$/.test(r.end)||!r.evidence||Object.keys(labels).some(k=>r.values?.[k as Metric]!==null&&!Number.isFinite(r.values?.[k as Metric]))||r.values.cash_capex===null||r.values.cash_capex<0)throw Error('Incomplete quarterly observations');
  if(['revenue','operating_income','net_income','cfo','cash_capex','sbc','fcf','other_operating'].some(k=>!Number.isSafeInteger(r.values[k as Metric])))throw Error('Missing or unsafe financial amount');
  const v=r.values as Record<Metric,number>;
  if(v.cfo-v.cash_capex!==v.fcf||v.net_income+v.sbc+v.other_operating!==v.cfo)throw Error('Cash-flow reconciliation failed');
  const start=Date.parse(r.start+'T00:00:00Z'),end=Date.parse(r.end+'T00:00:00Z');
  if(!Number.isFinite(start)||!Number.isFinite(end)||new Date(start).toISOString().slice(0,10)!==r.start||new Date(end).toISOString().slice(0,10)!==r.end||end-start<69*86400000||end-start>109*86400000||!Number.isInteger(r.fiscal_year)||!Number.isInteger(r.quarter)||r.quarter<1||r.quarter>4||r.id!==`FY${r.fiscal_year}-Q${r.quarter}`)throw Error('Invalid fiscal quarter');
  if(i&&(Date.parse(p.rows[i-1].end+'T00:00:00Z')+86400000!==start||r.quarter!==(p.rows[i-1].quarter%4)+1||r.fiscal_year!==p.rows[i-1].fiscal_year+(r.quarter===1?1:0)))throw Error('Nonconsecutive reporting periods');
  for(const [ratio,numerator]of [['operating_margin','operating_income'],['fcf_margin','fcf']] as const){
   const expected=v.revenue?v[numerator]/v.revenue:null;
   if(r.values[ratio]!==expected)throw Error('Margin does not reconcile');
  }
  for(const key of ['revenue','operating_income','net_income','cfo','cash_capex','sbc']as const){
   const e=r.evidence[key],ops=e?.operands;
   if(!Array.isArray(ops)||ops.length!==(r.quarter===1?1:2)||ops.some(o=>!Number.isSafeInteger(o.value)||!o.source_url.startsWith('https://www.sec.gov/Archives/edgar/data/')||!o.accession||!o.concept.startsWith('us-gaap:')||!o.filed||o.filed>p.as_of)||ops[0].end!==r.end||ops[0].value-(ops[1]?.value??0)!==v[key])throw Error('Reported operands do not reconcile');
   if(r.quarter===1?ops[0].start!==r.start:ops[0].start!==ops[1].start||Date.parse(ops[1].end+'T00:00:00Z')+86400000!==start)throw Error('Wrong YTD subtraction period');
  }
 }
 return p;
}
export async function fetchReport(ticker:string,signal:AbortSignal){
 const response=await fetch(`${(import.meta as ImportMeta & {env:{BASE_URL:string}}).env.BASE_URL}research-data/${ticker}.json`,{signal});
 if(!response.ok)throw Error('Quarterly dataset unavailable');
 return validateReport(await response.json(),ticker);
}
