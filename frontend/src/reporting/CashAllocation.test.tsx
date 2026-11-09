import {it,expect,vi} from 'vitest';
import {render,screen,fireEvent,within,waitFor} from '@testing-library/react';
import cash from '../../public/cash-allocation/GOOGL.json';
import googl from '../../public/research-data/GOOGL.json';
import apple from '../../public/research-data/AAPL.json';
import {validateReport} from './model';
import {allocationModel,validateAllocation} from './cashAllocationModel';
import type {CashAllocationReport,AllocationMode} from './cashAllocationModel';
import {CashAllocation,flowLayout} from './CashAllocation';
const history=validateReport(googl,'GOOGL');
const load=async()=>validateAllocation(cash,'GOOGL',history);
it('validates all periods against source operands and balances every pooled flow',()=>{
 const report=validateAllocation(cash,'GOOGL',history);
 for(const mode of ['annual','quarterly','ttm']as AllocationMode[])for(const row of report[mode]){
  const m=allocationModel(row);expect(m.sources.reduce((n,s)=>n+s.value,0)).toBe(m.uses.reduce((n,s)=>n+s.value,0));
  expect(m.sources.every(n=>n.value>0)).toBe(true);expect(m.uses.every(n=>n.value>0)).toBe(true);
  const height=Math.max(500,80+Math.max(m.sources.length,m.uses.length)*68);
  for(const nodes of [flowLayout(m.sources,m.pool,height),flowLayout(m.uses,m.pool,height)]){
   expect(nodes.every(n=>n.y>=0&&n.y+n.h<=height)).toBe(true);
   for(let i=1;i<nodes.length;i++)expect(nodes[i].cy-nodes[i-1].cy).toBeGreaterThanOrEqual(65.99);
  }
 }
 const r=report.annual.at(-1)!,m=allocationModel(r);expect(m.business).toBe(93039000000);expect(m.returns).toBe(55758000000);expect(m.pool).toBe(197250000000);
 const old=allocationModel(report.annual[0]);expect(old.sources.find(n=>n.id==='retained')?.label).toBe('Cash drawn before FX');
 expect(allocationModel(report.annual[3]).sources.some(n=>n.id==='securities')).toBe(true);
 expect(report.annual[0].values.dividends).toBeNull();
});
it('rejects wrong issuers, cohort drift, TTM tampering, unsafe inputs and contradictory evidence',()=>{
 expect(()=>validateAllocation(cash,'AAPL',validateReport(apple,'AAPL'))).toThrow();
 const changes:((p:CashAllocationReport)=>void)[]=[p=>{p.as_of='2026-11-10';},p=>{p.quarterly[0].end='2021-12-30';},p=>{p.ttm[0].values.ppe!+=1;},p=>{p.annual[0].values.dividends=0;},p=>{p.ppe[1].values.net+=1;},p=>{p.ppe[0].evidence.net.instant='2025-12-31';},p=>{Object.values(p.reported_periods)[0].values.cfo=NaN;},p=>{(Object.values(p.reported_periods)[0].evidence.cfo as {value:number}).value+=1;},p=>{p.sources[Object.keys(p.sources)[0]].sha256='bad';}];
 for(const mutate of changes){const broken=structuredClone(cash) as unknown as CashAllocationReport;mutate(broken);expect(()=>validateAllocation(broken,'GOOGL',history)).toThrow();}
});
it('shows the approved annual flow and keeps PP&E selection independent of cash periods',async()=>{
 render(<CashAllocation ticker="GOOGL" history={history} loadAllocation={load}/>);
 await screen.findByRole('img',{name:/Pooled cash sources of \$197.25B/});
 const detail=screen.getByRole('region',{name:'Selected cash allocation detail'});
 expect(detail.textContent).toContain('$91.45B');
 fireEvent.click(screen.getByRole('button',{name:/Shareholder returns/}));expect(detail.textContent).toContain('$45.71B');expect(detail.textContent).toContain('$10.05B');
 const balanceGroup=screen.getByRole('group',{name:'PP&E balance date'});fireEvent.click(within(balanceGroup).getByRole('button',{name:'2024'}));
 const ppe=screen.getByLabelText('Property and equipment reconciliation');expect(ppe.textContent).toContain('$171.04B');
 fireEvent.click(screen.getByRole('button',{name:'Quarterly'}));expect(within(screen.getByRole('group',{name:'Cash allocation reporting periods'})).getAllByRole('button')).toHaveLength(4);expect(ppe.textContent).toContain('$171.04B');
 fireEvent.click(within(screen.getByRole('group',{name:'Cash allocation reporting years'})).getByRole('button',{name:'FY2021'}));
 for(const q of [1,2,3,4]){const button=screen.getByRole('button',{name:`FY2021 Q${q}`});expect(button.hasAttribute('disabled')).toBe(false);fireEvent.click(button);expect(document.querySelector('.ca-section-controls')!.textContent).toContain(`FY2021 Q${q}`);}
 fireEvent.click(screen.getByRole('button',{name:'Trailing 12 months'}));expect(within(screen.getByRole('group',{name:'Cash allocation reporting periods'})).getAllByRole('button')).toHaveLength(4);
 fireEvent.click(within(screen.getByRole('group',{name:'Cash allocation reporting years'})).getByRole('button',{name:'FY2021'}));
 expect(screen.getByRole('button',{name:'FY2021 Q1 unavailable'}).hasAttribute('disabled')).toBe(true);
 expect(screen.getByRole('button',{name:'FY2021 Q4'}).getAttribute('aria-pressed')).toBe('true');
 fireEvent.click(screen.getByRole('button',{name:'Annual'}));fireEvent.click(screen.getByRole('button',{name:'FY2021'}));expect(screen.getByRole('button',{name:/Cash drawn before FX/})).toBeTruthy();
 fireEvent.click(within(balanceGroup).getByRole('button',{name:'2025'}));expect(ppe.textContent).toContain('$246.60B');expect(document.querySelector('.ca-section-controls')!.textContent).toContain('FY2021');
});
it('isolates failed loads, supports retry and removes Alphabet data on company change',async()=>{
 const failed=vi.fn(load).mockRejectedValueOnce(Error('offline'));const view=render(<CashAllocation ticker="GOOGL" history={history} loadAllocation={failed}/>);
 fireEvent.click(await screen.findByRole('button',{name:'Retry cash allocation'}));await screen.findByRole('heading',{name:'What the investment has built'});expect(failed).toHaveBeenCalledTimes(2);
 view.rerender(<CashAllocation ticker="MSFT" history={validateReport(apple,'AAPL')} loadAllocation={failed}/>);expect(screen.queryByRole('heading',{name:'Where the cash went'})).toBeNull();
 view.unmount();let resolve!:(r:CashAllocationReport)=>void;const delayed=vi.fn(load).mockImplementationOnce(()=>new Promise(r=>{resolve=r;}));const late=render(<CashAllocation ticker="GOOGL" history={history} loadAllocation={delayed}/>);late.rerender(<CashAllocation ticker="MSFT" history={history} loadAllocation={delayed}/>);resolve(await load());await waitFor(()=>expect(screen.queryByRole('heading',{name:'Where the cash went'})).toBeNull());
});
