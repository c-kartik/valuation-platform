import {useState} from 'react';
import {it,expect,vi} from 'vitest';
import {render,screen,fireEvent,waitFor} from '@testing-library/react';
import googl from '../../public/research-data/GOOGL.json';
import apple from '../../public/research-data/AAPL.json';
import meta from '../../public/research-data/META.json';
import gm from '../../public/revenue-mix/GOOGL.json';
import am from '../../public/revenue-mix/AAPL.json';
import mm from '../../public/revenue-mix/META.json';
import {RevenueMix} from './RevenueMix';
import {validateReport} from './model';
import {validateMix,displaySeries,yoy} from './revenueMixModel';
const histories={GOOGL:validateReport(googl,'GOOGL'),AAPL:validateReport(apple,'AAPL'),META:validateReport(meta,'META')};
const packages={GOOGL:gm,AAPL:am,META:mm};
const load=async(ticker:string,history:typeof histories.GOOGL)=>validateMix(packages[ticker as keyof typeof packages],ticker,history);
function Harness(){const [selected,setSelected]=useState(19);return <RevenueMix ticker="GOOGL" history={histories.GOOGL} selected={selected} onSelect={setSelected} loadMix={load}/>;}
it('reconciles all sixty quarters and replaces parent with detail without double counting',()=>{
 for(const ticker of ['GOOGL','AAPL','META'] as const){const p=validateMix(packages[ticker],ticker,histories[ticker]);for(const row of p.rows){expect(p.series.reduce((n,s)=>n+row.values[s.id],0)).toBe(row.total);expect(displaySeries(p,true).reduce((n,s)=>n+row.values[s.id],0)).toBe(row.total);}}
 const p=validateMix(gm,'GOOGL',histories.GOOGL);expect(displaySeries(p,true).map(s=>s.id)).not.toContain('services');expect(p.rows.some(r=>r.values.hedging<0)).toBe(true);expect(yoy(p,0,'cloud')).toBeNull();expect(yoy(p,19,'hedging')).toBeNull();expect(yoy(p,19,'cloud')).toBeCloseTo((gm.rows[19].values.cloud/gm.rows[15].values.cloud-1)*100);
});
it('rejects wrong issuer, periods, duplicate hierarchy, missing amounts and contradictory evidence',()=>{
 expect(()=>validateMix(gm,'AAPL',histories.AAPL)).toThrow();
 for(const mutate of [(p:typeof gm)=>{p.rows[0].values.cloud+=1;},(p:typeof gm)=>{p.rows[0].values.search+=1;},(p:typeof gm)=>{p.rows[0].end='2021-11-30';},(p:typeof gm)=>{p.rows[0].evidence.cloud.operands[0].value+=1;},(p:typeof gm)=>{p.series.push({...p.series[0]});}]){const broken=structuredClone(gm);mutate(broken);expect(()=>validateMix(broken,'GOOGL',histories.GOOGL)).toThrow();}
});
it('shows actual amounts, expands services and supports hover and keyboard selection',async()=>{
 render(<Harness/>);const chart=await screen.findByRole('slider',{name:'Explore revenue mix quarters'});expect(document.querySelector('.rm-table')!.textContent).toContain('$127.58B');
 fireEvent.click(screen.getByRole('button',{name:'Inside Google Services'}));expect(document.querySelector('.rm-table')!.textContent).toContain('Search & other');expect(document.querySelector('.rm-table')!.textContent).not.toContain('Google Services');
 fireEvent(chart,new MouseEvent('pointermove',{bubbles:true,clientX:48,clientY:80}));expect(screen.getByRole('tooltip').textContent).toContain('FY2021 Q4');fireEvent.pointerLeave(chart);expect(screen.queryByRole('tooltip')).toBeNull();
 fireEvent.keyDown(chart,{key:'Home'});expect(chart.getAttribute('aria-valuenow')).toBe('0');expect(document.querySelector('.rm-table')!.textContent).toContain('FY2021 Q4');fireEvent.keyDown(chart,{key:'End'});expect(chart.getAttribute('aria-valuenow')).toBe('19');fireEvent.keyDown(chart,{key:'Escape'});expect(screen.queryByRole('tooltip')).toBeNull();
});
it('uses Apple product labels and resets company detail without stale issuer data',async()=>{
 const v=render(<RevenueMix ticker="GOOGL" history={histories.GOOGL} selected={19} onSelect={()=>{}} loadMix={load}/>);fireEvent.click(await screen.findByRole('button',{name:'Inside Google Services'}));v.rerender(<RevenueMix ticker="AAPL" history={histories.AAPL} selected={19} onSelect={()=>{}} loadMix={load}/>);await screen.findByRole('rowheader',{name:'iPhone'});expect(document.querySelector('.rm-panel')!.textContent).toContain('Products & services');expect(screen.queryByRole('button',{name:'Segments'})).toBeNull();v.rerender(<RevenueMix ticker="META" history={histories.META} selected={19} onSelect={()=>{}} loadMix={load}/>);await screen.findByRole('button',{name:'Inside Family of Apps'});expect(document.querySelector('.rm-table')!.textContent).toContain('Reality Labs');
});
it('isolates failures, retries and ignores a late response from a previous issuer',async()=>{
 const failed=vi.fn(load).mockRejectedValueOnce(Error('offline'));const v=render(<RevenueMix ticker="GOOGL" history={histories.GOOGL} selected={19} onSelect={()=>{}} loadMix={failed}/>);fireEvent.click(await screen.findByRole('button',{name:'Retry revenue mix'}));await screen.findByRole('slider');expect(failed).toHaveBeenCalledTimes(2);v.unmount();
 let resolve!:(value:ReturnType<typeof validateMix>)=>void;const delayed=vi.fn(load).mockImplementationOnce(()=>new Promise(r=>{resolve=r;}));const next=render(<RevenueMix ticker="GOOGL" history={histories.GOOGL} selected={19} onSelect={()=>{}} loadMix={delayed}/>);next.rerender(<RevenueMix ticker="AAPL" history={histories.AAPL} selected={19} onSelect={()=>{}} loadMix={delayed}/>);await screen.findByRole('rowheader',{name:'iPhone'});resolve(validateMix(gm,'GOOGL',histories.GOOGL));await waitFor(()=>expect(document.querySelector('.rm-table')!.textContent).toContain('iPhone'));expect(document.querySelector('.rm-table')!.textContent).not.toContain('Google Services');
});
