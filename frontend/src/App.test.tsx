import {it,expect,vi} from 'vitest';
import {render,screen,waitFor,fireEvent,within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App, {ResultReview} from './App';
import {request,ApiError} from './api';
import type {Catalog,CaseDoc,Result} from './model';
import fixture from '../../examples/valuation/synthetic-base.json';
const demo=fixture as CaseDoc;
const catalog:Catalog={schema_version:'local-ev-catalog-v1',entries:[{kind:'test-anchor',company:'TEST',identity:demo.anchor,revenue:'100',unit:'USD',precision:'INF',source_links:[],limitations:['Synthetic test metadata'],template:{...demo,wacc:null,terminal_growth:null,forecast_years:demo.forecast_years.map(y=>({...y,revenue_growth:null,operating_margin:null,forecast_tax_rate:null,d_and_a_percent_revenue:null,capex_percent_revenue:null,change_in_operating_nwc_percent_revenue:null})),terminal:{operating_margin:null,operating_tax_rate:null,d_and_a_percent_revenue:null,investment_percent_revenue:null,working_capital_cash_requirement_percent_revenue:null}}}],synthetic_demo:demo,timing_notice:'Retained synthetic test; later-filed timing',input_definitions:{}};
function result(ev='0'):Result{return {case_name:'Synthetic result',input_basis:'SYNTHETIC_FIXTURE',submitted_inputs:demo,limitations:['Synthetic; not investment approval'],stage_b:{timing:{analytical_t0:'2025-12-31',notice:'Later-filed information',information_cutoff:'NOT_ESTABLISHED_BY_CALCULATOR'},stage_a:{anchor:{},years:demo.forecast_years.map(y=>({period_index:y.period_index,fiscal_year_label:y.fiscal_year_label,revenue:'1000000',ebit:'-1000000',tax:'0',nopat:'-1000000',d_and_a:'0',investment:'0',working_capital_cash_requirement:'0',fcff:'-1000000'}))},years:demo.forecast_years.map(y=>({period_index:y.period_index,fiscal_year_label:y.fiscal_year_label,fcff:'-1000000',discount_factor:'0.8',pv_fcff:'-800000'})),terminal:{fcff:'0'},terminal_value:'0',pv_terminal_value:'4000000',pv_explicit_fcff:'-4000000',enterprise_value:ev}};}
async function selectDemo(){await waitFor(()=>expect((screen.getByRole('button',{name:'Load synthetic demonstration'}) as HTMLButtonElement).disabled).toBe(false));fireEvent.click(screen.getByRole('button',{name:'Load synthetic demonstration'}));}
function transport(fn:(path:string,body?:unknown)=>Promise<unknown>){return vi.fn(async(path:string,body?:unknown)=>path==='/api/v1/catalog'?catalog:fn(path,body)) as unknown as typeof request;}
const input=(label:string)=>screen.getByLabelText(label) as HTMLInputElement;
const set=(label:string,value:string)=>fireEvent.change(input(label),{target:{value}});
const openAnnual=()=>fireEvent.click(screen.getByText('Advanced annual editing'));

it('shows unset company quick inputs, missing terminal requirements and explicit metadata',async()=>{
 render(<App load={transport(async()=>({status:'valid'}))}/>);await waitFor(()=>expect((screen.getByLabelText('Company') as HTMLSelectElement).disabled).toBe(false));
 fireEvent.change(screen.getByLabelText('Company'),{target:{value:'test-anchor'}});
 for(const label of ['Annual revenue growth (%)','Operating margin (%)','WACC (%)','Terminal growth (%)','Operating tax rate (%)','Expense D&A / revenue (%)','Investment / revenue (%)','WC cash requirement / full revenue (%)'])expect(input(label).value).toBe('');
 expect(screen.getByText(/Missing terminal inputs: Operating margin/i)).toBeTruthy();expect(screen.getByText(/Case details required: case name, preparer, preparation time, rationale, scope/)).toBeTruthy();
 expect(input('Preparer').value).toBe('');expect(input('Scope and information-cutoff disclosure').value).toBe('');
 expect(screen.queryByRole('option',{name:/Synthetic/})).toBeNull();
});
it('keeps a quick draft unapplied and blocks transport until apply or discard',async()=>{
 let posts=0;render(<App load={transport(async()=>{posts++;return result();})}/>);await selectDemo();set('Annual revenue growth (%)','12.125');
 fireEvent.click(screen.getByRole('button',{name:'Calculate enterprise value'}));await screen.findByText('Inputs need attention');expect(posts).toBe(0);expect(input('Revenue growth Synthetic period 1 (%)').value).toBe('10');
 fireEvent.click(screen.getByRole('button',{name:'Discard Annual revenue growth draft'}));expect(input('Annual revenue growth (%)').value).toBe('10');
 fireEvent.click(screen.getByRole('button',{name:'Check inputs'}));await waitFor(()=>expect(posts).toBe(1));
});
it('applies a single row exactly after confirmation, without linking later draft edits',async()=>{
 render(<App load={transport(async()=>({status:'valid'}))}/>);await selectDemo();set('Annual revenue growth (%)','12.125');fireEvent.click(screen.getByRole('button',{name:'Apply Annual revenue growth to five years'}));
 expect(screen.getByRole('alertdialog',{name:'Replace annual inputs?'})).toBeTruthy();expect(input('Revenue growth Synthetic period 1 (%)').value).toBe('10');
 fireEvent.click(screen.getByRole('button',{name:'Replace annual inputs'}));
 for(let i=1;i<=5;i++)expect(input(`Revenue growth Synthetic period ${i} (%)`).value).toBe('12.125');
 set('Annual revenue growth (%)','13');expect(input('Revenue growth Synthetic period 1 (%)').value).toBe('12.125');expect(input('Operating margin Synthetic period 1 (%)').value).toBe('20');
});
it('bulk applies only explicitly supplied six values and preserves metadata/schema',async()=>{
 const sent:unknown[]=[];render(<App load={transport(async(_,body)=>{sent.push(body);return {status:'valid'};})}/>);await selectDemo();
 const entries=[['Annual revenue growth (%)','11'],['Operating margin (%)','21'],['Operating tax rate (%)','22'],['Expense D&A / revenue (%)','6'],['Investment / revenue (%)','12'],['WC cash requirement / full revenue (%)','-1']];
 entries.forEach(([k,v])=>set(k,v));fireEvent.click(screen.getByRole('button',{name:'Apply all six to five years'}));fireEvent.click(screen.getByRole('button',{name:'Replace annual inputs'}));
 fireEvent.click(screen.getByRole('button',{name:'Check inputs'}));await waitFor(()=>expect(sent).toHaveLength(1));
 const doc=sent[0] as CaseDoc;expect(doc.schema_version).toBe('analyst-case-v1');expect(doc).not.toHaveProperty('bridge');expect(doc).not.toHaveProperty('information_cutoff');expect(doc.analyst).toEqual(demo.analyst);
 expect(doc.forecast_years[4]).toMatchObject({revenue_growth:'0.11',operating_margin:'0.21',forecast_tax_rate:'0.22',d_and_a_percent_revenue:'0.06',capex_percent_revenue:'0.12',change_in_operating_nwc_percent_revenue:'-0.01'});expect(doc.terminal).toEqual(demo.terminal);
});
it('marks annual divergence, preserves collapse/reopen and requires overwrite confirmation',async()=>{
 render(<App load={transport(async()=>({status:'valid'}))}/>);await selectDemo();openAnnual();set('Revenue growth Synthetic period 2 (%)','18');
 expect(screen.getByText('Varies by year — annual inputs used')).toBeTruthy();openAnnual();openAnnual();expect(input('Revenue growth Synthetic period 2 (%)').value).toBe('18');
 fireEvent.click(screen.getByRole('button',{name:'Apply Annual revenue growth to five years'}));fireEvent.click(screen.getByRole('button',{name:'Keep annual edits'}));expect(input('Revenue growth Synthetic period 2 (%)').value).toBe('18');
});
it('copies terminal ratios once while keeping growth/WACC and subsequent annual edits independent',async()=>{
 render(<App load={transport(async()=>({status:'valid'}))}/>);await selectDemo();openAnnual();set('Operating margin Synthetic period 5 (%)','37');
 fireEvent.click(screen.getByRole('button',{name:'Use year-five operating ratios for the terminal year'}));expect(input('Terminal operating margin (%)').value).toBe('37');expect(input('Terminal operating tax (%)').value).toBe('25');expect(input('Terminal investment / revenue (%)').value).toBe('10');
 expect(input('WACC (%)').value).toBe('25');expect(input('Terminal growth (%)').value).toBe('5');set('Operating margin Synthetic period 5 (%)','44');expect(input('Terminal operating margin (%)').value).toBe('37');set('Terminal operating margin (%)','32');expect(input('Operating margin Synthetic period 5 (%)').value).toBe('44');
});
it('calls calculation-free check and explicit run with the unchanged synthetic case',async()=>{
 const calls:string[]=[];render(<App load={transport(async(path,body)=>{calls.push(path);expect(body).toEqual(demo);return path.endsWith('validate')?{status:'valid'}:result();})}/>);await selectDemo();
 const user=userEvent.setup();screen.getByRole('button',{name:'Check inputs'}).focus();await user.keyboard('{Enter}');await screen.findByText(/Input checks passed/);expect(calls).toEqual(['/api/v1/cases/validate']);
 fireEvent.click(screen.getByRole('button',{name:'Calculate enterprise value'}));await screen.findByText('Synthetic result');expect(calls.at(-1)).toBe('/api/v1/cases/run');
});
it('maps API field errors and preserves entries on resource/busy/deadline/connection failures',async()=>{
 let code='invalid_case';render(<App load={transport(async()=>{throw new ApiError(code,'Retry or correct',['forecast_years[0].forecast_tax_rate: invalid tax']);})}/>);await selectDemo();
 for(const next of ['invalid_case','request_too_large','busy','deadline_exceeded','connection_error','internal_error']){
  code=next;fireEvent.click(screen.getByRole('button',{name:'Check inputs'}));await screen.findByText(`${code}: Retry or correct`);
  expect(input('Operating tax Synthetic period 1 (%)').value).toBe('25');expect(input('Operating tax Synthetic period 1 (%)').getAttribute('aria-invalid')).toBe('true');
 }
 fireEvent.click(screen.getByRole('button',{name:/Operating tax — Synthetic period 1: invalid tax/}));expect(screen.getByText('Advanced annual editing').closest('details')?.open).toBe(true);
});
it('marks a result stale immediately on quick/annual edits',async()=>{
 render(<App load={transport(async()=>result())}/>);await selectDemo();fireEvent.click(screen.getByRole('button',{name:'Calculate enterprise value'}));await screen.findByText('Synthetic result');
 set('Annual revenue growth (%)','12');expect(screen.getByText(/STALE RESULT/)).toBeTruthy();fireEvent.click(screen.getByRole('button',{name:'Discard Annual revenue growth draft'}));openAnnual();set('Revenue growth Synthetic period 1 (%)','13');expect(screen.getByText(/STALE RESULT/)).toBeTruthy();
});
it('ignores obsolete and out-of-order responses after edits',async()=>{
 const replies:((r:unknown)=>void)[]=[];render(<App load={transport(()=>new Promise(resolve=>{replies.push(resolve);} ))}/>);await selectDemo();
 fireEvent.click(screen.getByRole('button',{name:'Calculate enterprise value'}));openAnnual();set('Revenue growth Synthetic period 1 (%)','12');fireEvent.click(screen.getByRole('button',{name:'Calculate enterprise value'}));
 const newer=result();newer.case_name='Newer submitted revision';replies[1](newer);await screen.findByText('Newer submitted revision');replies[0](result());await waitFor(()=>expect(screen.queryByText('Synthetic result')).toBeNull());expect(screen.queryByText(/STALE RESULT/)).toBeNull();
});
it('confirms company changes even for quick-only drafts and ignores old-company replies',async()=>{
 let resolve!:(r:unknown)=>void;render(<App load={transport(()=>new Promise(r=>{resolve=r;}))}/>);await selectDemo();fireEvent.click(screen.getByRole('button',{name:'Calculate enterprise value'}));
 fireEvent.change(screen.getByLabelText('Company'),{target:{value:'test-anchor'}});fireEvent.click(screen.getByRole('button',{name:'Keep editing'}));expect(input('Annual revenue growth (%)').value).toBe('10');
 fireEvent.change(screen.getByLabelText('Company'),{target:{value:'test-anchor'}});fireEvent.click(screen.getByRole('button',{name:'Discard and switch'}));resolve(result());await waitFor(()=>expect(screen.queryByText('Synthetic result')).toBeNull());
 set('Annual revenue growth (%)','9');fireEvent.click(screen.getByRole('button',{name:'Load synthetic demonstration'}));expect(screen.getByRole('alertdialog',{name:'Discard populated edits?'})).toBeTruthy();
});
it.each([['0','Undefined'],['-1000000','-400.00%'],['2000000','200.00%']])('shows signed/undefined contribution for EV %s', (ev,ratio)=>{
 render(<ResultReview result={result(ev)} stale={false}/>);expect(screen.getByText('Enterprise value · USD millions')).toBeTruthy();expect(screen.getByText(ratio)).toBeTruthy();expect(screen.getByRole('img',{name:/Revenue trend/})).toBeTruthy();expect(screen.getByText('Five-year forecast · USD millions')).toBeTruthy();
 expect(screen.getAllByText('-1.00').length).toBeGreaterThan(0);
});
it('rejects malformed quick-entry text without changing annual values',async()=>{
 render(<App load={transport(async()=>({status:'valid'}))}/>);await selectDemo();set('Operating tax rate (%)','25%');fireEvent.click(screen.getByRole('button',{name:'Apply Operating tax rate to five years'}));expect(input('Operating tax Synthetic period 1 (%)').value).toBe('25');expect(input('Operating tax rate (%)').value).toBe('25%');expect(screen.getByText('Inputs need attention')).toBeTruthy();
});
it('preserves unrounded annual strings beside display-only rounded tables',()=>{
 const r=result();r.stage_b.stage_a.years[0].revenue='1234567.123456789';const before=JSON.stringify(r);
 render(<ResultReview result={r} stale={false}/>);
 fireEvent.click(screen.getByText('Submitted assumptions, rationale and timing'));fireEvent.click(screen.getByText('Full-precision inputs and calculation trace'));
 const exact=screen.getByRole('region',{name:'Unrounded annual values in USD'});expect(within(exact).getByText('1234567.123456789')).toBeTruthy();expect(JSON.stringify(r)).toBe(before);
});
it('keeps company metadata blank until explicitly entered or time action selected',async()=>{
 render(<App load={transport(async()=>({status:'valid'}))}/>);await waitFor(()=>expect((screen.getByLabelText('Company') as HTMLSelectElement).disabled).toBe(false));fireEvent.change(screen.getByLabelText('Company'),{target:{value:'test-anchor'}});
 expect(input('Prepared at (ISO timestamp with UTC offset)').value).toBe('');fireEvent.click(screen.getByText('Case details (5 missing)'));fireEvent.click(screen.getByRole('button',{name:'Use current UTC time'}));
 expect(input('Prepared at (ISO timestamp with UTC offset)').value).toMatch(/^\d{4}-\d\d-\d\dT.*Z$/);expect(input('Preparer').value).toBe('');expect(input('Rationale — sources, estimates and consistency').value).toBe('');
});
it('confirms before discarding limitations-only company edits',async()=>{
 render(<App load={transport(async()=>({status:'valid'}))}/>);await waitFor(()=>expect((screen.getByLabelText('Company') as HTMLSelectElement).disabled).toBe(false));fireEvent.change(screen.getByLabelText('Company'),{target:{value:'test-anchor'}});
 set('Limitations — review retained wording (one per line)','User-authored limitation only');fireEvent.click(screen.getByRole('button',{name:'Load synthetic demonstration'}));expect(screen.getByRole('alertdialog',{name:'Discard populated edits?'})).toBeTruthy();fireEvent.click(screen.getByRole('button',{name:'Keep editing'}));expect(input('Limitations — review retained wording (one per line)').value).toBe('User-authored limitation only');
});
it('maps a limitation-array error beside its editable declaration',async()=>{
 render(<App load={transport(async()=>{throw new ApiError('invalid_case','Correct limitations',['case.limitations[0]: required nonempty text']);})}/>);await selectDemo();fireEvent.click(screen.getByRole('button',{name:'Check inputs'}));await screen.findByText('invalid_case: Correct limitations');
 expect(input('Limitations — review retained wording (one per line)').getAttribute('aria-invalid')).toBe('true');fireEvent.click(screen.getByRole('button',{name:/Limitations: required nonempty text/}));expect(screen.getByText('Case details (0 missing)').closest('details')?.open).toBe(true);
});
