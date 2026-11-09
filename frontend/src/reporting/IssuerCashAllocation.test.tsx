import {it,expect,vi} from 'vitest';
import {render,screen,fireEvent,within,waitFor} from '@testing-library/react';
import apple from '../../public/research-data/AAPL.json';
import meta from '../../public/research-data/META.json';
import googl from '../../public/research-data/GOOGL.json';
import ap from '../../public/cash-allocation/AAPL.json';
import mp from '../../public/cash-allocation/META.json';
import gp from '../../public/cash-allocation/GOOGL.json';
import {validateReport} from './model';
import {validateAllocation,allocationModel,reportFlowKeys} from './cashAllocationModel';
import type {CashAllocationReport,CashFact,AllocationMode} from './cashAllocationModel';
import {CashAllocation,flowLayout} from './CashAllocation';
const histories={AAPL:validateReport(apple,'AAPL'),META:validateReport(meta,'META'),GOOGL:validateReport(googl,'GOOGL')};
const packages={AAPL:ap,META:mp,GOOGL:gp};
const load=async(t:string,h:typeof histories.AAPL)=>validateAllocation(packages[t as keyof typeof packages],t,h);
it('reconciles every issuer period and all reported annual component ties',()=>{
 for(const ticker of ['AAPL','META','GOOGL'] as const){const p=validateAllocation(packages[ticker],ticker,histories[ticker]);for(const mode of ['annual','quarterly','ttm'] as AllocationMode[])for(const r of p[mode]){const m=allocationModel(r,ticker);expect(m.sources.reduce((s,n)=>s+n.value,0)).toBe(m.uses.reduce((s,n)=>s+n.value,0));expect(r.values.opening!+r.values.change!).toBe(r.values.closing);const height=Math.max(500,80+Math.max(m.sources.length,m.uses.length)*68);for(const nodes of [flowLayout(m.sources,m.pool,height),flowLayout(m.uses,m.pool,height)])expect(nodes.every(n=>n.y>=0&&n.y+n.h<=height)).toBe(true);}for(const a of p.annual)for(const k of reportFlowKeys(p))expect(p.quarterly.filter(q=>q.id.startsWith(a.id+'-')).reduce((sum,q)=>sum+(q.values[k]??0),0)).toBe(a.values[k]??0);}
 expect(ap.quarterly).toHaveLength(24);expect(mp.quarterly).toHaveLength(23);expect(ap.ttm[0].id).toBe('FY2021-Q4');expect(mp.ttm[0].id).toBe('FY2021-Q4');
});
it('retains issuer-specific cash captions, lease financing and absent statement captions',()=>{
 const p=validateAllocation(mp,'META',histories.META),r=p.annual.at(-1)!,m=allocationModel(r,'META');
 expect(r.values.financeLeasePayments).toBe(-2524000000);expect(m.nodes.find(n=>n.id==='heldAssets')!.value).toBe(2432000000);expect(m.nodes.find(n=>n.id==='venture')!.value).toBe(2554000000);
 expect(m.nodes.find(n=>n.id==='awards')!.label).toBe('Equity-award tax payments');
 const q2=mp.quarterly.find(q=>q.id==='FY2021-Q2')!;expect(q2.values.otherPurchases).toBeNull();
 expect(Object.values(mp.reported_periods).some(r=>Object.keys(r.excluded_note_facts).includes('otherPurchases'))).toBe(true);
 const a=validateAllocation(ap,'AAPL',histories.AAPL);expect(a.annual.at(-1)!.values.fx).toBeNull();expect(a.ppe[1].date).toBe('2026-09-26');expect(a.ppe[1].values.net).toBe(52084000000);expect(p.ppe[1].values.net).toBe(176400000000);
});
it('rejects wrong company, lease double counting, wrong fiscal dates and transplanted PP&E categories',()=>{
 for(const ticker of ['AAPL','META']as const){for(const mutate of [(p:CashAllocationReport)=>{p.ticker='GOOGL';},(p:CashAllocationReport)=>{p.quarterly[0].end='2021-03-31';p.quarterly[0].start='2021-01-01';if(ticker==='META')p.quarterly[0].end='2021-03-30';},(p:CashAllocationReport)=>{p.ppe[0].date='2025-12-31';if(ticker==='META')p.ppe[0].date='2025-09-27';},(p:CashAllocationReport)=>{p.ppe[0].values.net+=1;},(p:CashAllocationReport)=>{p.ppe_categories![0].id='technical';},(p:CashAllocationReport)=>{p.ppe[0].servers_network_share_approx=.6;},(p:CashAllocationReport)=>{const r=Object.values(p.reported_periods)[0];(r.evidence.cfo as CashFact).source_url='https://www.sec.gov/Archives/edgar/data/1652044/not-issuer.xml';},(p:CashAllocationReport)=>{p.annual[0].values.financeLeasePayments=-100;}]){const broken=structuredClone(packages[ticker]) as unknown as CashAllocationReport;mutate(broken);expect(()=>validateAllocation(broken,ticker,histories[ticker])).toThrow();}}
});
it('shows Apple actual dates, switches all companies cleanly and keeps PP&E independently selected',async()=>{
 const view=render(<CashAllocation ticker="AAPL" history={histories.AAPL} loadAllocation={load}/>);
 await screen.findByRole('heading',{name:'What the investment has built'});expect(document.querySelector('.ca-ppe')!.textContent).toContain('September 26, 2026');expect(screen.getByLabelText('Cash balance reconciliation').textContent).toContain('Not separately reported');expect(document.querySelector('.ca-ppe')!.textContent).toContain('Machinery, equipment & internal-use software');expect(document.querySelector('.ca-ppe')!.textContent).not.toContain('Approximately 60%');
 fireEvent.click(within(screen.getByRole('group',{name:'PP&E balance date'})).getByRole('button',{name:'2025'}));
 fireEvent.click(screen.getByRole('button',{name:'Quarterly'}));fireEvent.click(within(screen.getByRole('group',{name:'Cash allocation reporting years'})).getByRole('button',{name:'FY2021'}));fireEvent.click(screen.getByRole('button',{name:'FY2021 Q1'}));expect(document.querySelector('.ca-section-controls')!.textContent).toContain('2020-09-27 — 2020-12-26');expect(document.querySelector('.ca-ppe')!.textContent).toContain('September 27, 2025');
 view.rerender(<CashAllocation ticker="META" history={histories.META} loadAllocation={load}/>);await screen.findByText('Construction in progress',{selector:'.ca-ppe-breakdown span'});expect(document.querySelector('.ca-ppe')!.textContent).toContain('Finance-lease right-of-use assets');expect(document.querySelector('.ca-ppe')!.textContent).not.toContain('Machinery, equipment');expect(document.querySelector('.ca-section-controls')!.textContent).toContain('FY2025');
 view.rerender(<CashAllocation ticker="GOOGL" history={histories.GOOGL} loadAllocation={load}/>);await screen.findByText(/Approximately 60%/);expect(document.querySelector('.ca-ppe-total')!.textContent).toContain('$345.08B');
});
it('retries a failed issuer load and ignores a late response after switching between supported companies',async()=>{
 const fail=vi.fn(load).mockRejectedValueOnce(Error('offline'));const first=render(<CashAllocation ticker="META" history={histories.META} loadAllocation={fail}/>);fireEvent.click(await screen.findByRole('button',{name:'Retry cash allocation'}));await screen.findByRole('heading',{name:'What the investment has built'});first.unmount();
 let resolve!:(p:CashAllocationReport)=>void;const delayed=vi.fn(load).mockImplementationOnce(()=>new Promise(r=>{resolve=r;}));const view=render(<CashAllocation ticker="AAPL" history={histories.AAPL} loadAllocation={delayed}/>);view.rerender(<CashAllocation ticker="META" history={histories.META} loadAllocation={delayed}/>);await screen.findByText('Construction in progress',{selector:'.ca-ppe-breakdown span'});resolve(await load('AAPL',histories.AAPL));await waitFor(()=>expect(document.querySelector('.ca-ppe')!.textContent).toContain('Construction in progress'));expect(document.querySelector('.ca-ppe')!.textContent).not.toContain('Machinery, equipment');
});
