import {it,expect,vi} from 'vitest';
import {act,fireEvent,render,screen,waitFor} from '@testing-library/react';
import {ApiError,request} from '../api';
import type {Result} from '../model';
import {CompanyAnalyst,checkCompanyAnalyst,checkCompanyProfile} from './CompanyAnalyst';
import type {CompanyAnalystResult,CompanyAssumptions,CompanyProfile,CompanyTicker} from './CompanyAnalyst';
import fixture from '../test-fixtures/fcfe-result.json';
const defaults:CompanyAssumptions={operating_cash_reserve_ratio:'0.03',cost_of_equity:'0.105',pre_tax_cost_of_debt:'0.06',rsu_vesting_fraction:'1',additional_claims_usd:'0',additional_assets_usd:'34972000000',historical_other_financing_fraction:'0',nci_claim_usd:'0',historical_minority_cash_share:'0'};
function profile(ticker:CompanyTicker='META'):CompanyProfile{return {schema_version:'company-analyst-profile-v1',ticker,name:ticker==='META'?'Meta Platforms':'Alphabet',model_origin:'2025-12-31',policy_version:ticker+'-analyst-v1',defaults:{...defaults,...(ticker==='GOOGL'?{nci_claim_usd:'1000000000'}:{})}};}
function operating(ticker:CompanyTicker='META',count=5):Result{
 const base=structuredClone(fixture.submitted_inputs.base_case) as unknown as Result['submitted_inputs'];
 base.anchor={...base.anchor,kind:ticker==='META'?'meta-fy2025':'googl-fy2025',cik:ticker==='META'?1326801:1652044,annual_end:'2025-12-31'};base.case_name=ticker+' Base';base.wacc='0.09';
 if(count===10)base.forecast_years=[...base.forecast_years,...structuredClone(base.forecast_years)];
 base.forecast_years.forEach((y,i)=>{y.period_index=i+1;y.fiscal_year_label='FY'+(2026+i);});
 return {submitted_inputs:base,stage_b:{enterprise_value:'2500000000000',terminal:{fcff:'180000000000'},stage_a:{years:base.forecast_years.map(y=>({fiscal_year_label:y.fiscal_year_label,fcff:'130000000000'}))}}} as unknown as Result;
}
function reply(ticker:CompanyTicker='META',result=operating(ticker),assumptions=profile(ticker).defaults):CompanyAnalystResult{return {
 schema_version:'company-analyst-result-v1',ticker,name:profile(ticker).name,policy_version:profile(ticker).policy_version,model_origin:'2025-12-31',assumptions:{...assumptions},
 readiness:['Historical FCFF','FCFF forecast and enterprise valuation','Historical FCFE','FCFE valuation','Fair value per share'].map((label,i)=>({id:'output-'+i,label,status:'ANALYST_READY_WITH_QUALIFICATIONS',detail:'Disclosed assumptions tested.'})),
 historical:Array.from({length:5},(_,i)=>({fiscal_year:2021+i,fcff_usd:'90000000000',fcfe_usd:'85000000000',consolidated_fcfe_usd:'86000000000',economic_fcfe_usd:'80000000000',other_financing_usd:'-100000000'})),
 fcff:{enterprise_value_usd:'2500000000000',equity_value_usd:'2520000000000',value_per_share_usd:'168.25',wacc:'0.09'},
 fcfe:{operating_equity_value_usd:'2400000000000',equity_value_usd:'2500000000000',value_per_share_usd:'166.75',cost_of_equity:assumptions.cost_of_equity,terminal:{fcff_usd:'180000000000'},years:result.stage_b.stage_a.years.map(y=>({fiscal_year_label:String(y.fiscal_year_label),fcff_usd:'130000000000',fcfe_usd:'125000000000',interest_expense_usd:'5000000000',net_borrowing_usd:'0',opening_debt_usd:'99000000000',closing_debt_usd:'99000000000'}))},
 bridge:{gross_cash_usd:'132420000000',operating_reserve_usd:'8322000000',eligible_cash_usd:'124098000000',debt_claims_usd:'99887000000',valuation_shares:'14924834000',additional_claims_usd:assumptions.additional_claims_usd,additional_assets_usd:assumptions.additional_assets_usd,nci_claim_usd:assumptions.nci_claim_usd},
 qualifications:['Source amounts and judgment are separate.'],source_urls:['https://www.sec.gov/Archives/edgar/data/example.htm'],sensitivities:[{label:'Higher operating reserve',fcff_value_per_share_usd:'167.25',fcfe_value_per_share_usd:'165.75'}]
};}
const transport=(fn:(path:string,body:any)=>unknown|Promise<unknown>)=>vi.fn(async(path:string,body?:unknown)=>fn(path,body)) as unknown as typeof request;
const standard=(ticker:CompanyTicker='META',result=operating(ticker))=>transport((path,body)=>path.endsWith('/run')?reply(ticker,result,body.assumptions):profile(ticker));
it('loads issuer defaults from metadata, runs all five outputs and exposes both share values',async()=>{
 const load=standard();render(<CompanyAnalyst ticker="META" result={operating()} stale={false} busy={false} load={load}/>);await screen.findByText('$168.25');
 expect(screen.getByText('$166.75')).toBeTruthy();expect(screen.getAllByText(/Analyst-ready with qualifications/)).toHaveLength(5);
 expect((load as any).mock.calls.map((v:any)=>v[0])).toEqual(['/api/v1/analyst/META','/api/v1/analyst/run']);
 expect((load as any).mock.calls[1][1]).toMatchObject({schema_version:'company-analyst-request-v1',ticker:'META',assumptions:defaults});
 expect((screen.getByLabelText('Cost of equity (%)') as HTMLInputElement).value).toBe('10.5');
 expect(screen.queryByLabelText('Minority-interest equity claim (USD millions)')).toBeNull();
});
it('submits edited claim, asset and minority inputs in exact units without keystroke requests',async()=>{
 const result=operating('GOOGL'),load=standard('GOOGL',result);render(<CompanyAnalyst ticker="GOOGL" result={result} stale={false} busy={false} load={load}/>);await screen.findByText('$168.25');
 fireEvent.change(screen.getByLabelText('Minority-interest equity claim (USD millions)'),{target:{value:'125.5'}});
 fireEvent.change(screen.getByLabelText('Historical cash flow allocated to minority interests (%)'),{target:{value:'2.25'}});
 fireEvent.change(screen.getByLabelText('Non-operating investments / other assets (USD millions)'),{target:{value:'50.5'}});
 expect(load).toHaveBeenCalledTimes(2);expect(screen.getByText(/Previous Alphabet analyst results · stale/)).toBeTruthy();
 fireEvent.click(screen.getByRole('button',{name:'Calculate Alphabet analyst outputs'}));await waitFor(()=>expect(load).toHaveBeenCalledTimes(3));
 expect((load as any).mock.calls[2][1].assumptions).toMatchObject({nci_claim_usd:'125500000',historical_minority_cash_share:'0.0225',additional_assets_usd:'50500000'});
 await waitFor(()=>expect(screen.queryByText(/Previous Alphabet analyst results · stale/)).toBeNull());
 expect(screen.getByText(/not verified parent cash/)).toBeTruthy();expect(screen.getByText('Consolidated FCFE')).toBeTruthy();
});
it('ignores late metadata after switching issuer even when transport ignores abort',async()=>{
 let resolve!:(value:unknown)=>void;const load=transport((path,body)=>path==='/api/v1/analyst/META'?new Promise(r=>resolve=r):path.endsWith('/run')?reply('GOOGL',operating('GOOGL'),body.assumptions):profile('GOOGL'));
 const view=render(<CompanyAnalyst ticker="META" result={operating()} stale={false} busy={false} load={load}/>);await waitFor(()=>expect(resolve).toBeDefined());
 view.rerender(<CompanyAnalyst ticker="GOOGL" result={operating('GOOGL')} stale={false} busy={false} load={load}/>);await screen.findByText('$168.25');
 await act(async()=>resolve(profile('META')));expect(screen.getByText('Alphabet · analyst valuation')).toBeTruthy();expect(screen.queryByText('Meta Platforms · analyst valuation')).toBeNull();
 expect((load as any).mock.calls.filter((v:any)=>v[0].endsWith('/run')).every((v:any)=>v[1].ticker==='GOOGL')).toBe(true);
});
it('ignores cancelled calculations and late replies for changed operating horizons',async()=>{
 let resolve!:(value:unknown)=>void;const old=operating(),next=operating('META',10),load=transport((path,body)=>!path.endsWith('/run')?profile():body.base_case.forecast_years.length===5?new Promise(r=>resolve=r):reply('META',next,body.assumptions));
 const view=render(<CompanyAnalyst ticker="META" result={old} stale={false} busy={false} load={load}/>);await screen.findByRole('button',{name:'Cancel Meta Platforms calculation'});
 fireEvent.click(screen.getByRole('button',{name:'Cancel Meta Platforms calculation'}));await act(async()=>resolve(reply()));expect(screen.queryByText('$168.25')).toBeNull();
 view.rerender(<CompanyAnalyst ticker="META" result={next} stale={false} busy={false} label="Bull" load={load}/>);await screen.findByText('$168.25');expect(screen.getByText(/Bull · 10-year forecast/)).toBeTruthy();expect(screen.getByText('FY2035')).toBeTruthy();
});
it('waits when inactive or busy and requires perpetual growth',async()=>{
 const load=standard(),result=operating(),view=render(<CompanyAnalyst ticker="META" result={result} stale={false} busy={false} active={false} load={load}/>);
 await waitFor(()=>expect((screen.getByLabelText('Cost of equity (%)') as HTMLInputElement).value).toBe('10.5'));expect(load).toHaveBeenCalledTimes(1);
 view.rerender(<CompanyAnalyst ticker="META" result={result} stale={false} busy active load={load}/>);expect(load).toHaveBeenCalledTimes(1);
 const exit=structuredClone(result);(exit.submitted_inputs as any).terminal_valuation={method:'exit_multiple'};
 view.rerender(<CompanyAnalyst ticker="META" result={exit} stale={false} busy={false} load={load}/>);expect(screen.getByText(/Choose Perpetual growth/)).toBeTruthy();expect(load).toHaveBeenCalledTimes(1);
});
it('offers metadata and calculation retries without automatic retry storms',async()=>{
 let profiles=0,runs=0;const result=operating(),load=transport((path,body)=>{if(!path.endsWith('/run')){if(!profiles++)throw new ApiError('busy','busy');return profile();}if(!runs++)throw new ApiError('busy','busy');return reply('META',result,body.assumptions);});
 render(<CompanyAnalyst ticker="META" result={result} stale={false} busy={false} load={load}/>);await screen.findByRole('button',{name:'Retry analyst assumptions'});expect(load).toHaveBeenCalledTimes(1);
 fireEvent.click(screen.getByRole('button',{name:'Retry analyst assumptions'}));await waitFor(()=>expect(load).toHaveBeenCalledTimes(3));await screen.findByRole('alert');
 fireEvent.click(screen.getByRole('button',{name:'Calculate Meta Platforms analyst outputs'}));await screen.findByText('$168.25');expect(load).toHaveBeenCalledTimes(4);
});
it('rejects mismatched issuer, date, policy, annual FCFF, terminal FCFF, EV, WACC and assumptions',()=>{
 const result=operating(),p=profile();for(const mutate of [(v:CompanyAnalystResult)=>v.ticker='GOOGL',(v:CompanyAnalystResult)=>v.model_origin='2025-09-27',(v:CompanyAnalystResult)=>v.policy_version='old',(v:CompanyAnalystResult)=>v.fcfe.years[0].fcff_usd='1',(v:CompanyAnalystResult)=>v.fcfe.terminal.fcff_usd='1',(v:CompanyAnalystResult)=>v.fcff.enterprise_value_usd='1',(v:CompanyAnalystResult)=>v.fcff.wacc='0.1',(v:CompanyAnalystResult)=>v.assumptions.cost_of_equity='0.2',(v:CompanyAnalystResult)=>v.bridge.nci_claim_usd='1']){const data=reply();mutate(data);expect(()=>checkCompanyAnalyst(data,result,defaults,p)).toThrow(/could not be matched/);}
 expect(()=>checkCompanyProfile(profile('GOOGL'),'META',result)).toThrow(/could not be matched/);
});
it('keeps a changed operating model stale and never accepts its predecessor response',async()=>{
 let resolve!:(value:unknown)=>void;const first=operating(),next=operating('META',10),load=transport((path,body)=>!path.endsWith('/run')?profile():body.base_case.forecast_years.length===5?new Promise(r=>resolve=r):reply('META',next,body.assumptions));
 const view=render(<CompanyAnalyst ticker="META" result={first} stale={false} busy={false} load={load}/>);await waitFor(()=>expect(resolve).toBeDefined());
 view.rerender(<CompanyAnalyst ticker="META" result={next} stale={false} busy={false} load={load}/>);await screen.findByText('$168.25');
 const old=reply();old.fcff.value_per_share_usd='999';await act(async()=>resolve(old));expect(screen.queryByText('$999.00')).toBeNull();
 view.rerender(<CompanyAnalyst ticker="META" result={next} stale busy={false} load={load}/>);expect(screen.getByText(/Previous Meta Platforms analyst results · stale/)).toBeTruthy();
 expect((screen.getByRole('button',{name:'Calculate Meta Platforms analyst outputs'}) as HTMLButtonElement).disabled).toBe(true);
});
