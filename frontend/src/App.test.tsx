import {it,expect,vi} from 'vitest';
import {render,screen,waitFor,fireEvent,within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App, {ResultReview} from './App';
import {request,ApiError} from './api';
import {makeDraft} from './model';
import type {Catalog,CaseDoc,InvestorDoc,Result} from './model';
import fixture from '../../examples/valuation/synthetic-base.json';
const demo=fixture as CaseDoc;
const catalog:Catalog={schema_version:'local-ev-catalog-v1',entries:[{kind:'test-anchor',company:'TEST',identity:demo.anchor,revenue:'100',unit:'USD',precision:'INF',source_links:[],limitations:['Synthetic test metadata'],template:{...demo,wacc:null,terminal_growth:null,forecast_years:demo.forecast_years.map(y=>({...y,revenue_growth:null,operating_margin:null,forecast_tax_rate:null,d_and_a_percent_revenue:null,capex_percent_revenue:null,change_in_operating_nwc_percent_revenue:null})),terminal:{operating_margin:null,operating_tax_rate:null,d_and_a_percent_revenue:null,investment_percent_revenue:null,working_capital_cash_requirement_percent_revenue:null}}}],synthetic_demo:demo,timing_notice:'Retained synthetic test; later-filed timing',input_definitions:{}};
function result(ev='0'):Result{return {case_name:'Synthetic result',input_basis:'SYNTHETIC_FIXTURE',submitted_inputs:demo,limitations:['Synthetic; not investment approval'],stage_b:{timing:{analytical_t0:'2025-12-31',notice:'Later-filed information',information_cutoff:'NOT_ESTABLISHED_BY_CALCULATOR'},stage_a:{anchor:{},years:demo.forecast_years.map(y=>({period_index:y.period_index,fiscal_year_label:y.fiscal_year_label,revenue:'1000000',ebit:'-1000000',tax:'0',nopat:'-1000000',d_and_a:'0',investment:'0',working_capital_cash_requirement:'0',fcff:'-1000000'}))},years:demo.forecast_years.map(y=>({period_index:y.period_index,fiscal_year_label:y.fiscal_year_label,fcff:'-1000000',discount_factor:'0.8',pv_fcff:'-800000'})),terminal:{fcff:'0'},terminal_value:'0',pv_terminal_value:'4000000',pv_explicit_fcff:'-4000000',enterprise_value:ev}};}
async function selectDemo(){await waitFor(()=>expect((screen.getByRole('button',{name:'Load synthetic demonstration'}) as HTMLButtonElement).disabled).toBe(false));fireEvent.click(screen.getByRole('button',{name:'Load synthetic demonstration'}));}
function transport(fn:(path:string,body?:unknown)=>Promise<unknown>){return vi.fn(async(path:string,body?:unknown)=>path==='/api/v1/catalog'?catalog:fn(path,body)) as unknown as typeof request;}
const input=(label:string)=>screen.getByLabelText(label) as HTMLInputElement;
const set=(label:string,value:string)=>fireEvent.change(input(label),{target:{value}});
const openAnnual=()=>fireEvent.click(screen.getByText('Edit individual years'));

async function selectEmpty(){await waitFor(()=>expect((screen.getByLabelText('Company') as HTMLSelectElement).disabled).toBe(false));fireEvent.change(screen.getByLabelText('Company'),{target:{value:'test-anchor'}});}
const grow='Annual revenue growth (%)', margin='Operating profit margin (%)', tax='Operating tax rate (%)', wacc='Discount rate — WACC (%)';
const run=()=>fireEvent.click(screen.getByRole('button',{name:'Calculate enterprise value'}));
const copy=()=>fireEvent.click(screen.getByRole('button',{name:'Copy final-year assumptions'}));
function diverge(){openAnnual();set('Annual revenue growth Synthetic period 2 (%)','18');}

it('starts neutral with unset rates, optional details and no apply controls',async()=>{
 render(<App load={transport(async()=>({status:'valid'}))}/>);await selectEmpty();
 for(const label of [grow,margin,tax,wacc,'Long-term revenue growth (%)','D&A / revenue (%)','Investment / revenue (%)','Working-capital cash needs / revenue (%)']){
  expect(input(label).value).toBe('');expect(input(label).getAttribute('aria-invalid')).toBe('false');
 }
 expect(screen.queryByRole('alert')).toBeNull();expect(screen.queryByRole('region',{name:'Input issues'})).toBeNull();
 expect(screen.getByText('Analysis details').closest('details')?.open).toBe(false);expect(input('Optional personal notes').value).toBe('');
 expect(screen.queryByRole('button',{name:/Apply/})).toBeNull();expect(screen.queryByRole('button',{name:/Use .* for all five years/})).toBeNull();
});
it('updates one uniform field directly, retaining exact raw text and unrelated inputs',async()=>{
 const sent:InvestorDoc[]=[];render(<App load={transport(async(_,body)=>{sent.push(body as InvestorDoc);return result();})}/>);await selectDemo();
 set(grow,'12.125');for(let i=1;i<=5;i++)expect(input(`Annual revenue growth Synthetic period ${i} (%)`).value).toBe('12.125');
 run();await screen.findByText('Synthetic result');expect(sent[0].forecast_years.every(y=>y.revenue_growth==='0.12125')).toBe(true);
 expect(sent[0].forecast_years[0].operating_margin).toBe('0.20');expect(sent[0].terminal).toEqual(demo.terminal);expect(sent[0].preparation.notes).toBeNull();
});
it.each(['-','.','12%',''])('never submits an older valid rate while %s is displayed',async(value)=>{
 const posts=vi.fn(async()=>result());render(<App load={transport(posts)}/>);await selectDemo();set(grow,value);run();
 await screen.findByRole('region',{name:'Input issues'});expect(posts).not.toHaveBeenCalled();
 for(let i=1;i<=5;i++)expect(input(`Annual revenue growth Synthetic period ${i} (%)`).value).toBe(value);
 set(grow,'11.00');run();await screen.findByText('Synthetic result');expect((posts.mock.calls[0] as unknown[])[1]).toMatchObject({forecast_years:[expect.objectContaining({revenue_growth:'0.1100'}),expect.anything(),expect.anything(),expect.anything(),expect.anything()]});
});
it('shows varying years honestly and blocks an unconfirmed replacement',async()=>{
 const posts=vi.fn(async()=>result());render(<App load={transport(posts)}/>);await selectDemo();diverge();
 expect(input(grow).value).toBe('');expect(screen.getByText(/Varies by year/)).toBeTruthy();openAnnual();openAnnual();expect(input('Annual revenue growth Synthetic period 2 (%)').value).toBe('18');
 set(grow,'13');run();await screen.findByRole('region',{name:'Input issues'});expect(posts).not.toHaveBeenCalled();expect(input('Annual revenue growth Synthetic period 2 (%)').value).toBe('18');
});
it('confirms the field and all years, keeps safe focus, and cancels without changing the annual path',async()=>{
 render(<App load={transport(async()=>({status:'valid'}))}/>);await selectDemo();diverge();set(grow,'13');
 const trigger=screen.getByRole('button',{name:'Use Annual revenue growth for all five years'});trigger.focus();fireEvent.click(trigger);
 const dialog=screen.getByRole('alertdialog',{name:'Replace annual inputs?'});
 expect(dialog.textContent).toContain('Annual revenue growth of 13%');for(let i=1;i<=5;i++)expect(dialog.textContent).toContain(`Synthetic period ${i}`);
 expect(document.activeElement).toBe(within(dialog).getByRole('button',{name:'Keep annual edits'}));
 const user=userEvent.setup();await user.tab();expect(document.activeElement).toBe(within(dialog).getByRole('button',{name:'Replace annual inputs'}));await user.tab();expect(document.activeElement).toBe(within(dialog).getByRole('button',{name:'Keep annual edits'}));
 fireEvent(dialog,new Event('cancel',{bubbles:true,cancelable:true}));expect(screen.queryByRole('alertdialog')).toBeNull();expect(document.activeElement).toBe(trigger);
 expect(input('Annual revenue growth Synthetic period 1 (%)').value).toBe('10');expect(input('Annual revenue growth Synthetic period 2 (%)').value).toBe('18');expect(input(grow).value).toBe('');
 set(grow,'14');fireEvent.click(trigger);fireEvent.click(screen.getByRole('button',{name:'Replace annual inputs'}));
 for(let i=1;i<=5;i++)expect(input(`Annual revenue growth Synthetic period ${i} (%)`).value).toBe('14');expect(input('Operating profit margin Synthetic period 2 (%)').value).toBe('20');expect(input('Long-term operating profit margin (%)').value).toBe('30');
});
it('uses touched/left errors without initial red errors and clears a correction without hiding other issues',async()=>{
 render(<App load={transport(async()=>({status:'valid'}))}/>);await selectDemo();set(grow,'-');expect(input(grow).getAttribute('aria-invalid')).toBe('false');fireEvent.blur(input(grow));expect(input(grow).getAttribute('aria-invalid')).toBe('true');
 expect(input(grow).getAttribute('aria-describedby')).toContain('quick.revenue_growth-error');set(tax,'bad');fireEvent.blur(input(tax));
 set(grow,'11');expect(input(grow).getAttribute('aria-invalid')).toBe('false');expect(input(tax).getAttribute('aria-invalid')).toBe('true');
});
it('reveals all entry blockers concisely on submit and navigates to the first field',async()=>{
 const posts=vi.fn();render(<App load={transport(posts)}/>);await selectEmpty();run();
 const summary=await screen.findByRole('region',{name:'Input issues'});expect(summary.textContent).toContain('13 input issue(s)');expect(screen.getByText('All input issues')).toBeTruthy();
 await waitFor(()=>expect(document.activeElement).toBe(input(grow)));expect(posts).not.toHaveBeenCalled();expect(input('Optional personal notes').getAttribute('aria-invalid')).toBe('false');
 set(grow,'10');expect(input(grow).getAttribute('aria-invalid')).toBe('false');expect(input(margin).getAttribute('aria-invalid')).toBe('true');
});
it('expands a closed long-term editor and focuses its blocking error',async()=>{
 render(<App load={transport(async()=>({status:'valid'}))}/>);await selectDemo();set('Long-term operating profit margin (%)','');run();
 await waitFor(()=>expect(document.activeElement).toBe(input('Long-term operating profit margin (%)')));expect(screen.getByText('Edit long-term operating ratios').closest('details')?.open).toBe(true);
});
it('expands annual editing for a varying-year error',async()=>{
 render(<App load={transport(async()=>({status:'valid'}))}/>);await selectDemo();openAnnual();set('Annual revenue growth Synthetic period 2 (%)','-');openAnnual();run();
 await waitFor(()=>expect(document.activeElement).toBe(input('Annual revenue growth Synthetic period 2 (%)')));expect(screen.getByText('Edit individual years').closest('details')?.open).toBe(true);
});
it('keeps numerical domain validation in the calculation-free API and translates percentage errors',async()=>{
 render(<App load={transport(async(path,body)=>{
  expect(path).toBe('/api/v1/cases/validate');if((body as InvestorDoc).forecast_years[0].forecast_tax_rate==='1.50')throw new ApiError('invalid_case','Invalid',['forecast_years[0].forecast_tax_rate: Forecast tax rate must be between 0 and 1']);return {status:'valid'};
 })}/>);await selectDemo();set(tax,'150');fireEvent.blur(input(tax));
 await waitFor(()=>expect(input(tax).getAttribute('aria-invalid')).toBe('true'));expect(document.getElementById('quick.forecast_tax_rate-error')?.textContent).toBe('Operating tax must be between 0% and 100%.');
 set(tax,'25');fireEvent.blur(input(tax));await waitFor(()=>expect(input(tax).getAttribute('aria-invalid')).toBe('false'));
});
it('confirms populated long-term replacements and keeps later annual edits independent',async()=>{
 render(<App load={transport(async()=>({status:'valid'}))}/>);await selectDemo();const trigger=screen.getByRole('button',{name:'Copy final-year assumptions'});trigger.focus();copy();
 const dialog=screen.getByRole('alertdialog',{name:'Replace long-term assumptions?'});expect(dialog.textContent).toContain('Synthetic period 5');expect(dialog.textContent).toContain('Long-term operating profit margin');
 fireEvent.click(screen.getByRole('button',{name:'Keep long-term assumptions'}));expect(document.activeElement).toBe(trigger);expect(input('Long-term operating profit margin (%)').value).toBe('30');
 copy();fireEvent.click(screen.getByRole('button',{name:'Replace long-term assumptions'}));expect(input('Long-term operating profit margin (%)').value).toBe('20');expect(input('Long-term operating tax rate (%)').value).toBe('25');
 expect(input(wacc).value).toBe('25');expect(input('Long-term revenue growth (%)').value).toBe('5');
 set(margin,'33');expect(input('Long-term operating profit margin (%)').value).toBe('20');expect(screen.getByText(/Differs from final year:/)).toBeTruthy();
});
it('does not copy missing inputs or silently supply terminal assumptions',async()=>{
 render(<App load={transport(async()=>({status:'valid'}))}/>);await selectEmpty();copy();expect(screen.queryByRole('alertdialog')).toBeNull();expect(input('Long-term operating profit margin (%)').value).toBe('');
 for(const [label,value] of [[grow,'10'],[margin,'20'],[tax,'25'],['D&A / revenue (%)','5'],['Investment / revenue (%)','10'],['Working-capital cash needs / revenue (%)','2']])set(label,value);
 expect(input('Long-term operating profit margin (%)').value).toBe('');copy();expect(screen.queryByRole('alertdialog')).toBeNull();expect(input('Long-term operating profit margin (%)').value).toBe('20');expect(input(wacc).value).toBe('');
});
it('preserves anonymous metadata, notes and assumptions through service failure and retry',async()=>{
 let fail=true;const sent:InvestorDoc[]=[];render(<App load={transport(async(_,body)=>{sent.push(structuredClone(body) as InvestorDoc);if(fail)throw new ApiError('busy','Retry later');return result();})}/>);await selectDemo();
 set('Optional personal notes','  My text\nonly  ');run();await screen.findByText('busy: Retry later');expect(screen.queryByRole('region',{name:'Input issues'})).toBeNull();expect(input('Optional personal notes').value).toBe('  My text\nonly  ');expect(input(margin).value).toBe('20');
 fail=false;run();await screen.findByText('Synthetic result');expect(sent[0]).toEqual(sent[1]);expect(sent[1].preparation.provenance).toBe('ANONYMOUS_INVESTOR');expect(sent[1]).not.toHaveProperty('analyst');
 set('Optional personal notes','');run();await waitFor(()=>expect(sent).toHaveLength(3));expect(sent[2].preparation.notes).toBeNull();expect(sent[2].preparation.timestamp_utc).toBe(sent[1].preparation.timestamp_utc);
});
it('marks quick and notes edits stale, and ignores obsolete calculation replies',async()=>{
 const replies:((r:unknown)=>void)[]=[];render(<App load={transport(()=>new Promise(resolve=>replies.push(resolve)))}/>);await selectDemo();run();set(grow,'12');run();
 const newer=result();newer.case_name='Newer result';replies[1](newer);await screen.findByText('Newer result');replies[0](result());await waitFor(()=>expect(screen.queryByText('Synthetic result')).toBeNull());
 set('Optional personal notes','Edit');expect(screen.getByText(/STALE RESULT/)).toBeTruthy();
});
it('does not apply an obsolete background field check after editing',async()=>{
 let reject!:(e:unknown)=>void;render(<App load={transport(()=>new Promise((_,r)=>{reject=r;}))}/>);await selectDemo();set(tax,'150');fireEvent.blur(input(tax));set(tax,'25');
 reject(new ApiError('invalid_case','Old',['forecast_years[0].forecast_tax_rate: Forecast tax rate must be between 0 and 1']));await waitFor(()=>expect(input(tax).getAttribute('aria-invalid')).toBe('false'));
});
it('keeps company-switch confirmation and safe focus without discarding notes',async()=>{
 render(<App load={transport(async()=>({status:'valid'}))}/>);await selectDemo();set('Optional personal notes','Keep me');const company=screen.getByLabelText('Company');company.focus();fireEvent.change(company,{target:{value:'test-anchor'}});
 fireEvent.click(screen.getByRole('button',{name:'Keep editing'}));expect(document.activeElement).toBe(company);expect(input('Optional personal notes').value).toBe('Keep me');
});
it.each([['0','Undefined'],['-1000000','-400.00%'],['2000000','200.00%']])('keeps signed/undefined financial presentation for EV %s',(ev,ratio)=>{
 render(<ResultReview result={result(ev)} stale={false}/>);expect(screen.getByText(ratio)).toBeTruthy();expect(screen.getByText('Operating business value; excludes the cash/debt/share bridge.')).toBeTruthy();
});
it('preserves raw result strings and explicit anonymous notes/timing',()=>{
 const r=result();r.submitted_inputs=makeDraft(demo).doc;r.submitted_inputs.preparation.notes='  Personal words\nonly  ';r.stage_b.stage_a.years[0].revenue='1234567.123456789';const before=JSON.stringify(r);
 render(<ResultReview result={r} stale={false}/>);fireEvent.click(screen.getByText('Assumptions, limitations & provenance'));fireEvent.click(screen.getByText('Full-precision inputs and calculation trace'));
 expect(screen.getByText(/Personal words/,{selector:'p'}).textContent).toContain('  Personal words\nonly  ');expect(screen.getByText(/No investment rationale supplied/)).toBeTruthy();expect(within(screen.getByRole('region',{name:'Unrounded annual values in USD'})).getByText('1234567.123456789')).toBeTruthy();expect(JSON.stringify(r)).toBe(before);
});

it('keeps blur calculation-free, has one calculation action and runs only explicitly',async()=>{
 const paths:string[]=[];render(<App load={transport(async(path)=>{paths.push(path);return path.endsWith('validate')?{status:'valid'}:result();})}/>);await selectDemo();
 set(grow,'11');fireEvent.blur(input(grow));await waitFor(()=>expect(paths).toEqual(['/api/v1/cases/validate']));
 expect(screen.queryByRole('button',{name:'Check inputs'})).toBeNull();expect(screen.queryByText('Synthetic result')).toBeNull();
 run();await screen.findByText('Synthetic result');expect(paths.at(-1)).toBe('/api/v1/cases/run');
});

it('retains a touched annual-cell error when clearing it restores a uniform blank row',async()=>{
 render(<App load={transport(async()=>({status:'valid'}))}/>);await selectEmpty();openAnnual();
 const label='Annual revenue growth Synthetic period 1 (%)';set(label,'1');set(label,'');fireEvent.blur(input(label));
 expect(input(label).getAttribute('aria-invalid')).toBe('true');expect(input(grow).getAttribute('aria-invalid')).toBe('true');
 expect(input('Annual revenue growth Synthetic period 2 (%)').getAttribute('aria-invalid')).toBe('false');expect(input(margin).getAttribute('aria-invalid')).toBe('false');
 set(grow,'10');expect(input(label).getAttribute('aria-invalid')).toBe('false');
});

it('keeps other touched annual errors visible when correcting one year creates variation',async()=>{
 render(<App load={transport(async()=>({status:'valid'}))}/>);await selectDemo();set(grow,'-');fireEvent.blur(input(grow));openAnnual();
 set('Annual revenue growth Synthetic period 1 (%)','10');fireEvent.blur(input('Annual revenue growth Synthetic period 1 (%)'));
 expect(input('Annual revenue growth Synthetic period 1 (%)').getAttribute('aria-invalid')).toBe('false');
 expect(input('Annual revenue growth Synthetic period 2 (%)').getAttribute('aria-invalid')).toBe('true');expect(input('Annual revenue growth Synthetic period 5 (%)').getAttribute('aria-invalid')).toBe('true');
});

it('keeps percentage help keyboard-accessible and explains investment and signed full-revenue WC',async()=>{
 render(<App load={transport(async()=>({status:'valid'}))}/>);await selectEmpty();
 const help=screen.getByLabelText('Help: Investment / revenue (%)');expect(help.closest('details')?.open).toBe(false);
 help.focus();expect(document.activeElement).toBe(help);fireEvent.click(help);expect(help.closest('details')?.open).toBe(true);
 expect(screen.getByText(/Cash PP&E \+ non-overlapping/).textContent).toContain('excludes finance-lease principal');
 const wc=screen.getByLabelText('Help: Working-capital cash needs / revenue (%)');fireEvent.click(wc);
 expect(screen.getByText(/Uses full annual forecast revenue/).textContent).toContain('Positive uses cash; negative releases cash');
 expect(input('Investment / revenue (%)').getAttribute('aria-describedby')).toContain('quick.capex_percent_revenue-help');
});
it('retains precise source/timing and financial limitations without internal ordinary-screen wording',async()=>{
 const c=structuredClone(catalog);c.entries[0].source_links=['https://www.sec.gov/test'];c.entries[0].limitations=[
 'Actual-input review, operating/tax/investment/venture scope and execution remain pending; see docs/phase2-meta-base-input-review.md.',
 'No bridge/share intake; historical debt/reinvestment/D&A limitations and unbounded omissions remain unchanged.'
 ];
 c.entries[0].template.limitations=[...c.entries[0].limitations];
 render(<App load={vi.fn(async()=>c) as unknown as typeof request}/>);await selectEmpty();
 const data=screen.getByText('Data & methodology').closest('details')!;expect(data.open).toBe(false);fireEvent.click(screen.getByText('Data & methodology'));
 expect(screen.getByRole('link',{name:'SEC filing source 1'}).getAttribute('href')).toBe('https://www.sec.gov/test');
 expect(data.textContent).toContain('Source precision INF');expect(data.textContent).toContain('later-filed information');expect(data.textContent).toContain('unbounded omissions');
 const ordinary=document.body.cloneNode(true) as HTMLElement;ordinary.querySelectorAll('pre').forEach(node=>node.remove());
 expect(ordinary.textContent).not.toMatch(/Phase 1|retained company|source bindings|docs\/phase2|No bridge\/share intake/i);
 expect(document.querySelector('pre')?.textContent).toContain('docs/phase2-meta-base-input-review.md');
 expect(c.entries[0].template.limitations[0]).toContain('docs/phase2-meta-base-input-review.md');
 expect(screen.getByText('Edit individual years').closest('details')?.open).toBe(false);
 expect(screen.getByText('Analysis details').closest('details')?.open).toBe(false);
});

it('keeps EV-only requests independent of optional bridge entry and discards bridge state on company switch',async()=>{
 const sent:InvestorDoc[]=[];render(<App load={transport(async(_,body)=>{sent.push(body as InvestorDoc);return result();})}/>);await selectDemo();run();await screen.findByText('Synthetic result');
 expect(sent[0].schema_version).toBe('investor-case-v1');expect(sent[0]).not.toHaveProperty('bridge');
 const bridge=screen.getByText('Add cash, debt & shares');expect(bridge.closest('details')?.open).toBe(false);fireEvent.click(bridge);set('Eligible cash & investments (USD millions)','1.25');
 fireEvent.change(screen.getByLabelText('Company'),{target:{value:'test-anchor'}});fireEvent.click(screen.getByRole('button',{name:'Discard and switch'}));
 expect(screen.queryByText('Add cash, debt & shares')).toBeNull();expect(input(grow).value).toBe('');expect(sent).toHaveLength(1);
});
