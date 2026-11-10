import {validateReport} from './model';
import type {QuarterlyReport} from './model';
import type {CashAllocationReport,CashPeriod} from './cashAllocationModel';
import type {BridgeObservation} from './CashBridge';
const keys=['net_income','sbc','cfo','cash_capex','fcf','other_operating'] as const;
export function validateBridgeHistory(value:unknown,history:QuarterlyReport,allocation:CashAllocationReport):QuarterlyReport{
 const p=value as QuarterlyReport;
 if(!Array.isArray(p?.rows)||p.rows.length!==allocation.quarterly.length||p.as_of!==history.as_of||p.source_snapshot_sha256!==history.source_snapshot_sha256)throw Error('Cash bridge history does not match the reviewed snapshot');
 // Two overlapping 20-quarter windows reuse the existing source/operand checks.
 validateReport({...p,rows:p.rows.slice(0,20)},history.ticker);
 validateReport({...p,rows:p.rows.slice(-20)},history.ticker);
 if(JSON.stringify(p.rows.slice(-20))!==JSON.stringify(history.rows))throw Error('Cash bridge changed accepted quarterly observations');
 for(const mode of ['annual','quarterly','ttm'] as const)for(const period of allocation[mode])bridgeForPeriod(p,period);
 return p;
}
export function bridgeForPeriod(history:QuarterlyReport,period:CashPeriod):BridgeObservation{
 const rows=history.rows.filter(r=>r.start>=period.start&&r.end<=period.end);
 if(!rows.length||rows[0].start!==period.start||rows.at(-1)!.end!==period.end)throw Error('Incomplete cash bridge period');
 const values=Object.fromEntries(keys.map(k=>[k,rows.reduce((sum,r)=>sum+r.values[k]!,0)])) as BridgeObservation['values'];
 if(!Object.values(values).every(Number.isSafeInteger)||values.cfo!==period.values.cfo||values.cash_capex!==-period.values.ppe!||values.cfo-values.cash_capex!==values.fcf||values.net_income+values.sbc+values.other_operating!==values.cfo)throw Error('Cash charts do not reconcile for the selected period');
 return {id:period.id,values};
}
export async function fetchBridgeHistory(ticker:string,history:QuarterlyReport,allocation:CashAllocationReport,signal:AbortSignal){
 const response=await fetch(`${(import.meta as ImportMeta & {env:{BASE_URL:string}}).env.BASE_URL}cash-bridge/${ticker}.json`,{signal});
 if(!response.ok)throw Error('Cash bridge history unavailable');
 return validateBridgeHistory(await response.json(),history,allocation);
}
