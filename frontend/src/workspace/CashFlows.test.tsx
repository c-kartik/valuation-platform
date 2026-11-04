import {it,expect,vi,afterEach} from 'vitest';
import {render,screen,fireEvent,waitFor,act} from '@testing-library/react';
import {HistoricalCashFlows,checkCashFlows} from './HistoricalCashFlows';
import type {CashFlowReview} from './HistoricalCashFlows';
import {FcfeForecast} from './FcfeForecast';
import {request} from '../api';
import type {Result} from '../model';
import fixture from '../test-fixtures/fcfe-result.json';
import projection from '../../../docs/company-resolutions/implementation-2026-11-03/platform-cashflows.json';
import readiness from '../test-fixtures/cashflow-readiness.json';
import appleOperating from '../test-fixtures/apple-operating-cashflows.json';
import resolution from '../../../docs/company-resolutions/AAPL/remaining-issues-2026-11-04/platform-resolution.json';
afterEach(()=>vi.unstubAllGlobals());
it('shows all five standardized Apple FCFF values with explicit method and preserves FCFE qualification',async()=>{
 const load=vi.fn(async()=>structuredClone(appleOperating)) as unknown as typeof request;
 render(<HistoricalCashFlows ticker="AAPL" active load={load}/>);
 await screen.findByText('115.68B');expect(screen.getByText('95.12B')).toBeTruthy();
 expect(screen.getAllByText('Standardized operating-income method')).toHaveLength(5);
 expect(screen.queryByText('Missing interest disclosure')).toBeNull();
 expect(screen.getAllByText('Provisional · financing classification open')).toHaveLength(5);
 expect(screen.getByText(/All five Apple FCFF observations use the same standardized method/)).toBeTruthy();
 expect(screen.getByText(/Current tax accruals and mixed Other current balances are included by convention/)).toBeTruthy();
 expect(checkCashFlows(structuredClone(appleOperating) as CashFlowReview,'AAPL')).toBeTruthy();
});
it('shows consolidated history separately from parent equity and per-share readiness',async()=>{
 const data={...structuredClone(projection.companies.GOOGL),readiness:structuredClone(readiness.GOOGL)};
 const load=vi.fn(async()=>data) as unknown as typeof request;
 render(<HistoricalCashFlows ticker="GOOGL" active load={load}/>);
 await screen.findByRole('region',{name:'Separate availability and valuation checks'});
 expect(screen.getByText(/10 historical calculations available under stated conventions/)).toBeTruthy();
 expect(screen.getByText(/Consolidated FCFE is available under the stated cash convention/)).toBeTruthy();
 expect(screen.getAllByText('Unavailable')).toHaveLength(5);
 expect(screen.getByText('Fair value per share')).toBeTruthy();
 expect(screen.getByText(/Manual forecasting remains available/)).toBeTruthy();
 expect(screen.queryByText('Verified')).toBeNull();
});
it('rejects overstated readiness counts and parent-common or financing relabeling',()=>{
 const data={...structuredClone(projection.companies.AAPL),readiness:structuredClone(readiness.AAPL)} as CashFlowReview;
 expect(checkCashFlows(data,'AAPL')).toBe(data);
 data.readiness!.counts.available_stated_convention=10;
 expect(()=>checkCashFlows(data,'AAPL')).toThrow('Incompatible consumer readiness');
 data.readiness=structuredClone(readiness.AAPL) as CashFlowReview['readiness'];
 data.periods[0].fcfe.status='CONSOLIDATED_BEFORE_NCI_ATTRIBUTION';
 expect(()=>checkCashFlows(data,'AAPL')).toThrow('Incompatible financing or ownership scope');
});
it('loads only the selected history view and preserves ownership, missing values and negative amounts',async()=>{
 const load=vi.fn(async()=>structuredClone(projection.companies.AAPL)) as unknown as typeof request;
 const v=render(<HistoricalCashFlows ticker="AAPL" active={false} load={load}/>);expect(load).not.toHaveBeenCalled();
 v.rerender(<HistoricalCashFlows ticker="AAPL" active load={load}/>);await screen.findAllByText('FY2025');expect(load).toHaveBeenCalledTimes(1);
 expect(screen.getAllByText('Missing interest disclosure')).toHaveLength(2);expect(screen.getAllByText('Provisional · financing classification open')).toHaveLength(5);expect(screen.queryByText('Verified')).toBeNull();
 const p=structuredClone(projection.companies.AAPL) as CashFlowReview;p.periods[0].fcfe.parent_common_amount_usd='1';expect(()=>checkCashFlows(p,'AAPL')).toThrow();
});
it('does not display a late response for another issuer',async()=>{
 let complete!:(d:unknown)=>void;
 const load=vi.fn((path:string)=>path.endsWith('AAPL')?new Promise(r=>complete=r):Promise.resolve(structuredClone(projection.companies.GOOGL))) as unknown as typeof request;
 const v=render(<HistoricalCashFlows key="AAPL" ticker="AAPL" active load={load}/>);
 v.rerender(<HistoricalCashFlows key="GOOGL" ticker="GOOGL" active load={load}/>);await screen.findAllByText('Consolidated · before minority allocation');
 await act(async()=>complete(structuredClone(projection.companies.AAPL)));
 expect(screen.getByText('Historical cash flows · GOOGL')).toBeTruthy();expect(screen.queryByText('Provisional · financing classification open')).toBeNull();
});
it('hides the prior issuer immediately while the next issuer response is delayed without a remount',async()=>{
 let complete!:(d:unknown)=>void;
 const load=vi.fn((path:string)=>path.endsWith('AAPL')?Promise.resolve(structuredClone(projection.companies.AAPL)):new Promise(r=>complete=r)) as unknown as typeof request;
 const v=render(<HistoricalCashFlows ticker="AAPL" active load={load}/>);
 await screen.findAllByText('105.62B');
 v.rerender(<HistoricalCashFlows ticker="GOOGL" active load={load}/>);
 expect(screen.queryByText('105.62B')).toBeNull();expect(screen.getByRole('status').textContent).toMatch(/Loading/);
 await act(async()=>complete(structuredClone(projection.companies.GOOGL)));
 expect(screen.queryByText('105.62B')).toBeNull();expect(screen.getAllByText('Consolidated · before minority allocation')).toHaveLength(5);
});
function result():Result{return {submitted_inputs:fixture.submitted_inputs.base_case,stage_b:{stage_a:{years:fixture.years.map(y=>({fiscal_year_label:y.fiscal_year_label}))}}} as unknown as Result;}
it('requires explicit financing, keeps cost equity separate, and discards late FCFE on edits',async()=>{
 let complete!:(d:unknown)=>void;
 const load=vi.fn(()=>new Promise(r=>complete=r)) as unknown as typeof request;
 render(<FcfeForecast result={result()} stale={false} busy={false} load={load}/>);
 fireEvent.click(screen.getByText('FCFE forecast · explicit financing and cost of equity'));
 fireEvent.click(screen.getByText('Calculate FCFE equity value'));
 expect((await screen.findByRole('alert')).textContent).toMatch(/Complete every financing input/);expect(load).not.toHaveBeenCalled();
 for(const [label,value] of [['Cost of equity (%)','10'],['Opening debt (USD millions)','0'],['FCFE terminal growth (%)','0']])fireEvent.change(screen.getByLabelText(label),{target:{value}});
 fireEvent.click(screen.getByText('Declare all financing entries zero'));fireEvent.click(screen.getByText('Calculate FCFE equity value'));
 const body=vi.mocked(load).mock.calls[0][1] as Record<string,unknown>;expect(body.cost_of_equity).toBe('0.1');expect(body.scope).toBe('CONSOLIDATED_BEFORE_NCI_ATTRIBUTION');
 fireEvent.change(screen.getByLabelText('Cost of equity (%)'),{target:{value:'11'}});
 await act(async()=>complete(structuredClone(fixture)));
 expect(screen.queryByRole('region',{name:'FCFE result'})).toBeNull();
});
it('accepts authoritative FCFE and rejects fake per-share certification at the transport boundary',async()=>{
 vi.stubGlobal('fetch',vi.fn(async()=>new Response(JSON.stringify(fixture),{status:200})));
 await expect(request('/api/v1/fcfe/run',fixture.submitted_inputs)).resolves.toHaveProperty('equity_value_usd');
 const bad={...fixture,value_per_share:'123'};vi.stubGlobal('fetch',vi.fn(async()=>new Response(JSON.stringify(bad),{status:200})));
 await expect(request('/api/v1/fcfe/run',{})).rejects.toHaveProperty('code','service_unavailable');
});

it('exposes source-bound Apple decisions without clearing FCFE or per-share output',async()=>{
 const d={...structuredClone(appleOperating),current_resolution:structuredClone(resolution)} as CashFlowReview;
 const load=vi.fn(async()=>d) as unknown as typeof request;
 render(<HistoricalCashFlows ticker="AAPL" active load={load}/>);
 await screen.findByText('Apple review decisions and remaining evidence');
 fireEvent.click(screen.getByText('Apple review decisions and remaining evidence'));
 expect(screen.getByText(/Gross cash and marketable securities: 132.42B/)).toBeTruthy();
 expect(screen.getByText(/Term-debt disclosed fair value: 80.40B/)).toBeTruthy();
 expect(screen.getAllByText('Provisional · financing classification open')).toHaveLength(5);
 expect(screen.getByText(/Company review remains open. The decisions below/)).toBeTruthy();
 expect(checkCashFlows(d,'AAPL')).toBe(d);
 const bad=structuredClone(d);(bad.current_resolution as unknown as {company_complete:boolean}).company_complete=true;
 expect(()=>checkCashFlows(bad,'AAPL')).toThrow('Incompatible Apple resolution');
 const wrong=structuredClone(d);wrong.current_resolution!.anchor_support.fair_value_per_share_usd='175' as unknown as null;
 expect(()=>checkCashFlows(wrong,'AAPL')).toThrow('Incompatible Apple resolution');
});
