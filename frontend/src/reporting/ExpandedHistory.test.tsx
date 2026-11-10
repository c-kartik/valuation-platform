import {it,expect,vi} from 'vitest';
import {render,screen,fireEvent,waitFor,cleanup} from '@testing-library/react';
import {QuarterlyOverview} from './QuarterlyOverview';
import {validateReport} from './model';
import {validateOverviewHistory} from './overviewHistory';
import {validateMix} from './revenueMixModel';
import {validateAllocation} from './cashAllocationModel';
import {validateBridgeHistory} from './cashBridgePeriods';
import gh from '../../public/research-data/GOOGL.json';
import ah from '../../public/research-data/AAPL.json';
import mh from '../../public/research-data/META.json';
import ge from '../../public/cash-bridge/GOOGL.json';
import ae from '../../public/cash-bridge/AAPL.json';
import me from '../../public/cash-bridge/META.json';
import gm from '../../public/revenue-mix-expanded/GOOGL.json';
import am from '../../public/revenue-mix-expanded/AAPL.json';
import mm from '../../public/revenue-mix-expanded/META.json';
import gc from '../../public/cash-allocation/GOOGL.json';
import ac from '../../public/cash-allocation/AAPL.json';
import mc from '../../public/cash-allocation/META.json';
const fixtures={GOOGL:{old:gh,extended:ge,mix:gm,cash:gc},AAPL:{old:ah,extended:ae,mix:am,cash:ac},META:{old:mh,extended:me,mix:mm,cash:mc}};
const load=async(t:string)=>{const f=fixtures[t as keyof typeof fixtures];return validateOverviewHistory(f.extended,t,validateReport(f.old,t));};
it('validates full FY2021 histories and preserves every original observation, revenue detail and cash period',async()=>{
 for(const [ticker,f] of Object.entries(fixtures)){
  const h=await load(ticker),mix=validateMix(f.mix,ticker,h),cash=validateAllocation(f.cash,ticker,h);
  expect(h.rows[0].id).toBe('FY2021-Q1');expect(h.rows.slice(0,4).map(r=>r.quarter)).toEqual([1,2,3,4]);
  expect(h.rows.slice(-20)).toEqual(f.old.rows);expect(mix.rows).toHaveLength(h.rows.length);
  expect(validateBridgeHistory(f.extended,h,cash).rows).toHaveLength(h.rows.length);
  for(const r of mix.rows){expect(mix.series.reduce((n,s)=>n+r.values[s.id as keyof typeof r.values],0)).toBe(r.total);}
 }
 expect(mm.notes.some(n=>n.includes('FY2021 Q1–Q3'))).toBe(true);
});
it('both historical charts navigate from Q1 to the true latest quarter for all issuers',async()=>{
 vi.stubGlobal('fetch',vi.fn(async(input:string)=>{const ticker=input.split('/').at(-1)!.replace('.json','') as keyof typeof fixtures,f=fixtures[ticker];const body=input.includes('revenue-mix-expanded')?f.mix:input.includes('cash-allocation')?f.cash:f.extended;return {ok:true,json:async()=>body};}));
 try{for(const ticker of ['GOOGL','AAPL','META'] as const){
  const h=await load(ticker);render(<QuarterlyOverview ticker={ticker} loadReport={load}/>);
  const trends=await screen.findByRole('slider',{name:'Explore historical quarters'}),mix=await screen.findByRole('slider',{name:'Explore revenue mix quarters'});
  expect(trends.getAttribute('aria-valuemax')).toBe(String(h.rows.length-1));expect(mix.getAttribute('aria-valuemax')).toBe(String(h.rows.length-1));
  fireEvent.keyDown(trends,{key:'Home'});expect(document.querySelector('.qr-readout-quarter')!.textContent).toContain('FY2021 Q1');expect(document.querySelector('.rm-table')!.textContent).toContain('FY2021 Q1');
  fireEvent.keyDown(mix,{key:'End'});await waitFor(()=>expect(document.querySelector('.qr-readout-quarter')!.textContent).toContain(h.rows.at(-1)!.id.replace('-',' ')));
  expect(mix.getAttribute('aria-valuenow')).toBe(String(h.rows.length-1));cleanup();
 }}finally{vi.unstubAllGlobals();}
});
it('rejects incomplete starts, altered accepted amounts and contradictory source operands',()=>{
 for(const mutate of [(p:typeof ge)=>{p.rows.shift();},(p:typeof ge)=>{p.rows[0].values.cfo+=1;},(p:typeof ge)=>{p.rows[0].evidence.revenue.operands[0].value+=1;}]){const broken=structuredClone(ge);mutate(broken);expect(()=>validateOverviewHistory(broken,'GOOGL',validateReport(gh,'GOOGL'))).toThrow();}
});
