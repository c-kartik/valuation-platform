import {fetchReport,validateReport} from './model';
import type {QuarterlyReport} from './model';
/** Expanded descriptive view; the original fixed 20-quarter packages stay intact. */
export function validateOverviewHistory(value:unknown,ticker:string,baseline:QuarterlyReport):QuarterlyReport{
 const p=value as QuarterlyReport,count=ticker==='AAPL'?24:23;
 if(!Array.isArray(p?.rows)||p.rows.length!==count||p.rows[0]?.id!=='FY2021-Q1'||p.source_snapshot_sha256!==baseline.source_snapshot_sha256||p.as_of!==baseline.as_of)throw Error('Incomplete FY2021 historical coverage');
 validateReport({...p,rows:p.rows.slice(0,20)},ticker);
 validateReport({...p,rows:p.rows.slice(-20)},ticker);
 if(JSON.stringify(p.rows.slice(-20))!==JSON.stringify(baseline.rows))throw Error('Original historical observations changed');
 return p;
}
export async function fetchOverviewReport(ticker:string,signal:AbortSignal){
 const baseline=await fetchReport(ticker,signal);
 const response=await fetch(`${(import.meta as ImportMeta & {env:{BASE_URL:string}}).env.BASE_URL}cash-bridge/${ticker}.json`,{signal});
 if(!response.ok)throw Error('Expanded historical dataset unavailable');
 return validateOverviewHistory(await response.json(),ticker,baseline);
}
