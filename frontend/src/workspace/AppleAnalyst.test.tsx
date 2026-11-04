import {it,expect,vi} from 'vitest';
import {act,fireEvent,render,screen,waitFor} from '@testing-library/react';
import {ApiError,request} from '../api';
import type {Result} from '../model';
import {AppleAnalyst,appleDefaults,checkAppleAnalyst} from './AppleAnalyst';
import type {AppleAnalystResult} from './AppleAnalyst';
import fixture from '../test-fixtures/fcfe-result.json';

function operating(count=5):Result{
 const base=structuredClone(fixture.submitted_inputs.base_case) as unknown as Result['submitted_inputs'];
 base.anchor={...base.anchor,kind:'aapl-fy2025',cik:320193,annual_end:'2025-09-27'};base.case_name='Apple Base';
 base.wacc='0.0827275';
 if(count===10)base.forecast_years=[...base.forecast_years,...structuredClone(base.forecast_years)];
 base.forecast_years.forEach((y,i)=>{y.period_index=i+1;y.fiscal_year_label='FY'+(2026+i);});
 return {submitted_inputs:base,stage_b:{enterprise_value:'2500000000000',terminal:{fcff:'180000000000'},stage_a:{years:base.forecast_years.map(y=>({fiscal_year_label:y.fiscal_year_label,fcff:'130000000000'}))}}} as unknown as Result;
}
function reply(result=operating(),assumptions=appleDefaults):AppleAnalystResult{
 return {schema_version:'apple-analyst-result-v1',ticker:'AAPL',policy_version:'apple-analyst-v1',model_origin:'2025-09-27',assumptions:{...assumptions},
  readiness:['Historical FCFF','FCFF forecast and enterprise valuation','Historical FCFE','FCFE valuation','Fair value per share'].map((label,i)=>({id:'output-'+i,label,status:'ANALYST_READY_WITH_QUALIFICATIONS',detail:'Explicit conventions and sensitivity reviewed.'})),
  historical:Array.from({length:5},(_,i)=>({fiscal_year:2021+i,fcff_usd:'95000000000',fcfe_usd:'90000000000',economic_fcfe_usd:'82000000000',other_financing_usd:'-111000000'})),
  fcff:{enterprise_value_usd:'2500000000000',equity_value_usd:'2520000000000',value_per_share_usd:'168.25',wacc:'0.0827275'},
  fcfe:{operating_equity_value_usd:'2400000000000',equity_value_usd:'2500000000000',value_per_share_usd:'166.75',cost_of_equity:assumptions.cost_of_equity,terminal:{fcfe_usd:'180000000000',fcff_usd:'180000000000'},years:result.stage_b.stage_a.years.map(y=>({fiscal_year_label:String(y.fiscal_year_label),fcff_usd:'130000000000',fcfe_usd:'125000000000',interest_expense_usd:'5000000000',net_borrowing_usd:'2000000000',opening_debt_usd:'99000000000',closing_debt_usd:'101000000000'}))},
  bridge:{gross_cash_usd:'132420000000',operating_reserve_usd:'8322000000',eligible_cash_usd:'124098000000',debt_claims_usd:'99887000000',valuation_shares:'14924834000',additional_claims_usd:assumptions.additional_claims_usd},
  qualifications:['Existing awards use a stated dilution convention.'],source_urls:['https://www.sec.gov/Archives/edgar/data/320193/apple.htm'],sensitivities:[{label:'Higher operating reserve',fcff_value_per_share_usd:'167.25',fcfe_value_per_share_usd:'165.75'}]};
}
const transport=(fn:(body:any)=>unknown|Promise<unknown>)=>vi.fn(async(_path:string,body?:unknown)=>fn(body)) as unknown as typeof request;

it('loads five analyst outputs for the current Apple model and shows paired per-share values',async()=>{
 const result=operating(),load=transport(body=>reply(result,body.assumptions));
 render(<AppleAnalyst result={result} stale={false} busy={false} load={load}/>);
 await screen.findByText('$168.25');expect(screen.getByText('$166.75')).toBeTruthy();expect(load).toHaveBeenCalledTimes(1);
 expect((load as any).mock.calls[0][0]).toBe('/api/v1/apple/analyst/run');
 expect((load as any).mock.calls[0][1]).toMatchObject({schema_version:'apple-analyst-request-v1',assumptions:appleDefaults});
 expect(screen.getAllByText(/Analyst-ready with qualifications/)).toHaveLength(5);
 expect(screen.getByText(/debt is not subtracted again/)).toBeTruthy();expect(screen.getByText(/Fiscal-end analytical origin 2025-09-27/)).toBeTruthy();
 expect(screen.getByText(/These values are not expected to match/)).toBeTruthy();expect(screen.getByText(/FCFE minus FCFF: \$-1.50 per share/)).toBeTruthy();
});
it('edits assumptions without calculating on keystrokes, keeps prior values visibly stale, and submits exact units',async()=>{
 const result=operating(),load=transport(body=>reply(result,body.assumptions));
 render(<AppleAnalyst result={result} stale={false} busy={false} load={load}/>);await screen.findByText('$168.25');
 fireEvent.change(screen.getByLabelText('Operating cash reserve (% of revenue)'),{target:{value:'3.125'}});
 fireEvent.change(screen.getByLabelText('Additional claims (USD millions)'),{target:{value:'125.5'}});
 expect(screen.getByText(/Previous Apple analyst results · stale/)).toBeTruthy();expect(load).toHaveBeenCalledTimes(1);
 fireEvent.click(screen.getByRole('button',{name:'Calculate Apple analyst outputs'}));
 await waitFor(()=>expect(load).toHaveBeenCalledTimes(2));
 const body=(load as any).mock.calls[1][1];expect(body.assumptions.operating_cash_reserve_ratio).toBe('0.03125');expect(body.assumptions.additional_claims_usd).toBe('125500000');
 await waitFor(()=>expect(screen.queryByText(/Previous Apple analyst results · stale/)).toBeNull());
});
it('never shows a late response after the selected model changes, including a ten-year horizon',async()=>{
 let oldResolve!:(value:unknown)=>void;const first=operating(),next=operating(10);next.submitted_inputs.case_name='Apple Bull';
 const load=transport(body=>body.base_case.case_name==='Apple Base'?new Promise(r=>oldResolve=r):reply(next,body.assumptions));
 const view=render(<AppleAnalyst result={first} stale={false} busy={false} load={load}/>);
 await waitFor(()=>expect(load).toHaveBeenCalledTimes(1));
 view.rerender(<AppleAnalyst result={next} stale={false} busy={false} label="Bull" load={load}/>);await screen.findByText('$168.25');
 await act(async()=>oldResolve({...reply(first),fcff:{...reply(first).fcff,value_per_share_usd:'999'}}));
 expect(screen.queryByText('$999.00')).toBeNull();expect(screen.getByText(/Bull · 10-year forecast/)).toBeTruthy();
 expect(screen.getAllByText('FY2035')).toHaveLength(1);
});
it('waits while inactive or busy and leaves unsupported exit methods uncalculated',async()=>{
 const result=operating(),load=transport(body=>reply(result,body.assumptions));
 const view=render(<AppleAnalyst result={result} stale={false} busy={false} active={false} load={load}/>);expect(load).not.toHaveBeenCalled();
 view.rerender(<AppleAnalyst result={result} stale={false} busy active load={load}/>);expect(load).not.toHaveBeenCalled();
 const exit=structuredClone(result);(exit.submitted_inputs as any).terminal_valuation={method:'exit_multiple'};
 view.rerender(<AppleAnalyst result={exit} stale={false} busy={false} load={load}/>);expect(load).not.toHaveBeenCalled();expect(screen.getByText(/Choose Perpetual growth/)).toBeTruthy();
 expect((screen.getByRole('button',{name:'Calculate Apple analyst outputs'}) as HTMLButtonElement).disabled).toBe(true);
});
it('keeps current results visible but stale when operating assumptions are edited',async()=>{
 const result=operating(),load=transport(body=>reply(result,body.assumptions));const view=render(<AppleAnalyst result={result} stale={false} busy={false} load={load}/>);await screen.findByText('$168.25');
 view.rerender(<AppleAnalyst result={result} stale busy={false} load={load}/>);expect(screen.getByText('$168.25')).toBeTruthy();expect(screen.getByText(/Previous Apple analyst results · stale/)).toBeTruthy();expect(load).toHaveBeenCalledTimes(1);
});
it('offers an explicit retry after a busy response without an automatic retry loop',async()=>{
 const result=operating();let count=0;const load=transport(body=>{if(!count++)throw new ApiError('busy','busy');return reply(result,body.assumptions);});
 render(<AppleAnalyst result={result} stale={false} busy={false} load={load}/>);await screen.findByRole('alert');expect(load).toHaveBeenCalledTimes(1);
 fireEvent.click(screen.getByRole('button',{name:'Calculate Apple analyst outputs'}));await screen.findByText('$168.25');expect(load).toHaveBeenCalledTimes(2);
});
it('rejects a mismatched response and prevents a cancelled reply from appearing',async()=>{
 const result=operating(),wrong=reply(result);wrong.model_origin='2025-12-31';expect(()=>checkAppleAnalyst(wrong,result,appleDefaults)).toThrow(/could not be matched/);
 let resolve!:(v:unknown)=>void;const load=transport(()=>new Promise(r=>resolve=r));
 render(<AppleAnalyst result={result} stale={false} busy={false} load={load}/>);await screen.findByRole('button',{name:'Cancel Apple calculation'});fireEvent.click(screen.getByRole('button',{name:'Cancel Apple calculation'}));
 await act(async()=>resolve(reply(result)));expect(screen.queryByText('$168.25')).toBeNull();
});
it('does not mount the Apple controls or issue requests for other issuers',()=>{
 const result=operating();result.submitted_inputs.anchor.kind='meta-fy2025';const load=vi.fn() as unknown as typeof request;
 render(<AppleAnalyst result={result} stale={false} busy={false} load={load}/>);expect(screen.queryByText('Apple · analyst valuation')).toBeNull();expect(load).not.toHaveBeenCalled();
});
it('preserves an incomplete input and requires correction before sending a calculation',async()=>{
 const result=operating(),load=transport(body=>reply(result,body.assumptions));
 render(<AppleAnalyst result={result} stale={false} busy={false} active={false} load={load}/>);
 fireEvent.change(screen.getByLabelText('Cost of equity (%)'),{target:{value:'-.'}});
 fireEvent.click(screen.getByRole('button',{name:'Calculate Apple analyst outputs'}));
 await screen.findByRole('alert');expect(load).not.toHaveBeenCalled();expect((screen.getByLabelText('Cost of equity (%)') as HTMLInputElement).value).toBe('-.');
});
it('rejects stale FCFF totals, discount rates, annual cash flows, or terminal cash flows',()=>{
 const result=operating();
 for(const change of [(v:AppleAnalystResult)=>{v.fcff.enterprise_value_usd='1';},(v:AppleAnalystResult)=>{v.fcff.wacc='0.09';},(v:AppleAnalystResult)=>{v.fcfe.years[0].fcff_usd='1';},(v:AppleAnalystResult)=>{v.fcfe.terminal.fcff_usd='1';}]){
  const value=reply(result);change(value);expect(()=>checkAppleAnalyst(value,result,appleDefaults)).toThrow(/could not be matched/);
 }
});
