import {it,expect,vi} from 'vitest';
import {render,screen,fireEvent,within,waitFor} from '@testing-library/react';
import {CashAnalysis} from './CashAnalysis';
import {bridgeForPeriod,validateBridgeHistory} from './cashBridgePeriods';
import {validateReport} from './model';
import {validateAllocation} from './cashAllocationModel';
import gh from '../../public/research-data/GOOGL.json';
import ah from '../../public/research-data/AAPL.json';
import mh from '../../public/research-data/META.json';
import ga from '../../public/cash-allocation/GOOGL.json';
import aa from '../../public/cash-allocation/AAPL.json';
import ma from '../../public/cash-allocation/META.json';
import gb from '../../public/cash-bridge/GOOGL.json';
import ab from '../../public/cash-bridge/AAPL.json';
import mb from '../../public/cash-bridge/META.json';
const fixtures={GOOGL:{h:gh,a:ga,b:gb},AAPL:{h:ah,a:aa,b:ab},META:{h:mh,a:ma,b:mb}};
const loadAllocation=async(t:string)=>{const f=fixtures[t as keyof typeof fixtures];return validateAllocation(f.a,t,validateReport(f.h,t));};
const loadBridge=async(t:string)=>{const f=fixtures[t as keyof typeof fixtures];return validateBridgeHistory(f.b,validateReport(f.h,t),await loadAllocation(t));};
it('reconciles every annual, quarter and TTM bridge with allocation for all three issuers, including FY2021',async()=>{
 for(const t of ['GOOGL','AAPL','META'] as const){const a=await loadAllocation(t),b=await loadBridge(t);for(const mode of ['annual','quarterly','ttm'] as const)for(const period of a[mode]){const row=bridgeForPeriod(b,period);expect(row.values.cfo).toBe(period.values.cfo);expect(row.values.cash_capex).toBe(-period.values.ppe!);expect(row.values.net_income+row.values.sbc+row.values.other_operating).toBe(row.values.cfo);}}
});
it('one selector updates both graphs, retains PP&E independence and resets on issuer changes',async()=>{
 const view=render(<CashAnalysis ticker="GOOGL" history={validateReport(gh,'GOOGL')} loadAllocation={loadAllocation} loadBridge={loadBridge}/>);
 await screen.findByRole('region',{name:'Period for both cash-flow charts'});
 expect(screen.getAllByRole('button',{name:'Annual'})).toHaveLength(1);
 const bridge=screen.getByRole('region',{name:'From earnings to cash'}),allocation=screen.getByRole('region',{name:'Where the cash went'});
 expect(bridge.textContent).toContain('FY2025');expect(allocation.textContent).toContain('FY2025');
 const ppe=screen.getByRole('group',{name:'PP&E balance date'});fireEvent.click(within(ppe).getByRole('button',{name:'2024'}));
 fireEvent.click(screen.getByRole('button',{name:'Quarterly'}));fireEvent.click(screen.getByRole('button',{name:'FY2021'}));
 for(const q of [1,2,3,4]){fireEvent.click(screen.getByRole('button',{name:`FY2021 Q${q}`}));expect(bridge.textContent).toContain(`FY2021 Q${q}`);expect(allocation.textContent).toContain(`FY2021 Q${q}`);}
 expect(within(ppe).getByRole('button',{name:'2024'}).getAttribute('aria-pressed')).toBe('true');
 fireEvent.click(screen.getByRole('button',{name:'Trailing 12 months'}));expect(bridge.textContent).toContain('TTM ending');expect(allocation.textContent).toContain('TTM ending');
 view.rerender(<CashAnalysis ticker="AAPL" history={validateReport(ah,'AAPL')} loadAllocation={loadAllocation} loadBridge={loadBridge}/>);
 await waitFor(()=>expect(screen.getByRole('button',{name:'Annual'}).getAttribute('aria-pressed')).toBe('true'));
 expect(screen.getByRole('region',{name:'From earnings to cash'}).textContent).toContain('FY2026');
});
it('rejects missing bridge quarters, contradictory observations and mismatched snapshots',async()=>{
 const a=await loadAllocation('GOOGL'),h=validateReport(gh,'GOOGL');
 for(const mutate of [(p:typeof gb)=>{p.rows.shift();},(p:typeof gb)=>{p.rows[0].values.net_income+=1;},(p:typeof gb)=>{p.source_snapshot_sha256='bad';}]){const broken=structuredClone(gb);mutate(broken);expect(()=>validateBridgeHistory(broken,h,a)).toThrow();}
});
it('retries failed shared loads without showing a stale company',async()=>{
 const fail=vi.fn(loadBridge).mockRejectedValueOnce(Error('offline'));
 render(<CashAnalysis ticker="GOOGL" history={validateReport(gh,'GOOGL')} loadAllocation={loadAllocation} loadBridge={fail}/>);
 fireEvent.click(await screen.findByRole('button',{name:'Retry cash-flow analysis'}));await screen.findByRole('region',{name:'From earnings to cash'});expect(fail).toHaveBeenCalledTimes(2);
});
