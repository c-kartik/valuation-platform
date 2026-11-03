import {it,expect,vi,afterEach} from 'vitest';
import {render,screen,fireEvent,waitFor,act} from '@testing-library/react';
import {HistoricalCashFlows,checkCashFlows} from './HistoricalCashFlows';
import type {CashFlowReview} from './HistoricalCashFlows';
import {FcfeForecast} from './FcfeForecast';
import {request} from '../api';
import type {Result} from '../model';
import fixture from '../test-fixtures/fcfe-result.json';
import projection from '../../../docs/company-resolutions/implementation-2026-11-03/platform-cashflows.json';
afterEach(()=>vi.unstubAllGlobals());
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
