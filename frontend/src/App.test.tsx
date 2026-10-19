import {it,expect,vi} from 'vitest';
import {render,screen,waitFor,fireEvent} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App, {ResultReview} from './App';
import {request,ApiError} from './api';
import type {Catalog,CaseDoc,Result} from './model';
import fixture from '../../examples/valuation/synthetic-base.json';
const demo=fixture as CaseDoc;
const catalog:Catalog={schema_version:'local-ev-catalog-v1',entries:[{kind:'test-anchor',company:'TEST',identity:demo.anchor,revenue:'100',unit:'USD',precision:'INF',source_links:[],limitations:['Synthetic test metadata'],template:{...demo,wacc:null,terminal_growth:null,forecast_years:demo.forecast_years.map(y=>({...y,revenue_growth:null,operating_margin:null,forecast_tax_rate:null,d_and_a_percent_revenue:null,capex_percent_revenue:null,change_in_operating_nwc_percent_revenue:null})),terminal:{operating_margin:null,operating_tax_rate:null,d_and_a_percent_revenue:null,investment_percent_revenue:null,working_capital_cash_requirement_percent_revenue:null}}}],synthetic_demo:demo,timing_notice:'Retained synthetic test; later-filed timing',input_definitions:{}};
function result(ev='0'):Result{return {case_name:'Synthetic result',input_basis:'SYNTHETIC_FIXTURE',submitted_inputs:demo,limitations:['Synthetic; not investment approval'],stage_b:{timing:{analytical_t0:'2025-12-31',notice:'Later-filed information',information_cutoff:'NOT_ESTABLISHED_BY_CALCULATOR'},stage_a:{anchor:{},years:demo.forecast_years.map(y=>({period_index:y.period_index,fiscal_year_label:y.fiscal_year_label,revenue:'1000000',ebit:'-1000000',tax:'0',nopat:'-1000000',d_and_a:'0',investment:'0',working_capital_cash_requirement:'0',fcff:'-1000000'}))},years:demo.forecast_years.map(y=>({period_index:y.period_index,fiscal_year_label:y.fiscal_year_label,fcff:'-1000000',discount_factor:'0.8',pv_fcff:'-800000'})),terminal:{fcff:'0'},terminal_value:'0',pv_terminal_value:'4000000',pv_explicit_fcff:'-4000000',enterprise_value:ev}};}
async function selectDemo(){await screen.findByLabelText('Historical anchor');await waitFor(()=>expect((screen.getByLabelText('Historical anchor') as HTMLSelectElement).disabled).toBe(false));fireEvent.change(screen.getByLabelText('Historical anchor'),{target:{value:'demo'}});}
function transport(fn:(path:string,body?:unknown)=>Promise<unknown>){return vi.fn(async(path:string,body?:unknown)=>path==='/api/v1/catalog'?catalog:fn(path,body)) as unknown as typeof request;}
it('uses separate calculation-free validation and explicit EV-only run, with keyboard labels',async()=>{
 const calls:string[]=[];const load=transport(async(path,body)=>{calls.push(path);expect(body).toEqual(demo);return path.endsWith('validate')?{status:'valid',calculation_performed:false}:result();});
 render(<App load={load}/>);await selectDemo();
 const user=userEvent.setup();screen.getByRole('button',{name:'Validate'}).focus();await user.keyboard('{Enter}');
 await screen.findByText(/Structural validation passed/);expect(calls).toEqual(['/api/v1/cases/validate']);
 await user.click(screen.getByRole('button',{name:'Calculate enterprise value'}));await screen.findByText('Synthetic result');
 expect(calls.at(-1)).toBe('/api/v1/cases/run');expect(screen.getByText(/not equity or per-share value/i)).toBeTruthy();
});
it('shows API field errors and keeps entries on resource/busy/deadline/internal errors',async()=>{
 let code='invalid_case';const load=transport(async()=>{throw new ApiError(code,'Retry or correct',['forecast_years[0].forecast_tax_rate: invalid tax']);});
 render(<App load={load}/>);await selectDemo();
 for(const next of ['invalid_case','request_too_large','busy','deadline_exceeded','internal_error']){
  code=next;fireEvent.click(screen.getByRole('button',{name:'Validate'}));await screen.findByText(`${code}: Retry or correct`);
  const field=screen.getByLabelText('Operating tax Synthetic period 1 (%)') as HTMLInputElement;
  expect(field.value).toBe('25');expect(field.getAttribute('aria-invalid')).toBe('true');
 }
});
it('marks completed results stale immediately after editing without terminal copying',async()=>{
 render(<App load={transport(async()=>result())}/>);await selectDemo();fireEvent.click(screen.getByRole('button',{name:'Calculate enterprise value'}));await screen.findByText('Synthetic result');
 fireEvent.change(screen.getByLabelText('Operating margin Synthetic period 5 (%)'),{target:{value:'44'}});
 expect(screen.getByText(/STALE RESULT/)).toBeTruthy();expect((screen.getByLabelText('Terminal operating margin (%)') as HTMLInputElement).value).toBe('30');
});
it('ignores an obsolete response after an edit and preserves the changed input',async()=>{
 let resolve!:(r:unknown)=>void;const load=transport(()=>new Promise(r=>{resolve=r;}));render(<App load={load}/>);await selectDemo();
 fireEvent.click(screen.getByRole('button',{name:'Calculate enterprise value'}));
 fireEvent.change(screen.getByLabelText('Revenue growth Synthetic period 1 (%)'),{target:{value:'12'}});
 resolve(result());await waitFor(()=>expect(screen.queryByText('Synthetic result')).toBeNull());
 expect((screen.getByLabelText('Revenue growth Synthetic period 1 (%)') as HTMLInputElement).value).toBe('12');
});
it('requires discard confirmation and ignores old-company responses',async()=>{
 let resolve!:(r:unknown)=>void;render(<App load={transport(()=>new Promise(r=>{resolve=r;}))}/>);await selectDemo();
 fireEvent.click(screen.getByRole('button',{name:'Calculate enterprise value'}));
 fireEvent.change(screen.getByLabelText('Historical anchor'),{target:{value:'test-anchor'}});
 expect(screen.getByRole('alertdialog')).toBeTruthy();fireEvent.click(screen.getByRole('button',{name:'Keep editing'}));expect((screen.getByLabelText('Historical anchor') as HTMLSelectElement).value).toBe('demo');
 fireEvent.change(screen.getByLabelText('Historical anchor'),{target:{value:'test-anchor'}});fireEvent.click(screen.getByRole('button',{name:'Discard and switch'}));
 resolve(result());await waitFor(()=>expect(screen.queryByText('Synthetic result')).toBeNull());
 expect((screen.getByLabelText('Revenue growth Synthetic period 1 (%)') as HTMLInputElement).value).toBe('');expect((screen.getByLabelText('Preparer') as HTMLInputElement).value).toBe('');
});
it.each(['0','-1000000'])('shows raw signed EV %s with labeled units and defers ratios',ev=>{
 render(<ResultReview result={result(ev)} stale={false}/>);
 expect(screen.getByText('Enterprise value · USD millions')).toBeTruthy();expect(screen.getByText('Annual components · USD millions (discount factors are unitless)')).toBeTruthy();
 expect(screen.getByText(/Terminal contribution ratio: not supplied/)).toBeTruthy();expect(screen.getByText(/Zero-EV ratios would be undefined/)).toBeTruthy();
 expect(screen.getAllByText('-1.00').length).toBeGreaterThan(0);expect(screen.getByText('+ Discounted terminal value (USD millions)')).toBeTruthy();
});

it('ignores an older run that finishes after a newer edited run',async()=>{
 const replies:((r:unknown)=>void)[]=[];
 render(<App load={transport(()=>new Promise(resolve=>{replies.push(resolve);} ))}/>);await selectDemo();
 fireEvent.click(screen.getByRole('button',{name:'Calculate enterprise value'}));
 fireEvent.change(screen.getByLabelText('Revenue growth Synthetic period 1 (%)'),{target:{value:'12'}});
 fireEvent.click(screen.getByRole('button',{name:'Calculate enterprise value'}));
 const newer=result();newer.case_name='Newer submitted revision';replies[1](newer);
 await screen.findByText('Newer submitted revision');replies[0](result());
 await waitFor(()=>expect(screen.queryByText('Synthetic result')).toBeNull());
 expect(screen.getByText('Newer submitted revision')).toBeTruthy();expect(screen.queryByText(/STALE RESULT/)).toBeNull();
});
it('rejects malformed percentage entry before transport, keeping its exact text',async()=>{
 let posts=0;render(<App load={transport(async()=>{posts++;return {status:'valid'};})}/>);await selectDemo();
 fireEvent.change(screen.getByLabelText('Constant WACC (%)'),{target:{value:'10%'}});
 fireEvent.click(screen.getByRole('button',{name:'Validate'}));
 await screen.findByText('Request needs attention');expect(posts).toBe(0);
 expect((screen.getByLabelText('Constant WACC (%)') as HTMLInputElement).value).toBe('10%');
});
