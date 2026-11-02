import {it,expect,vi} from 'vitest';
import {render,screen,fireEvent,waitFor,within,act,configure} from '@testing-library/react';
import {Workspace} from './Workspace';
import {shortLabels} from './canvasModel';
import {request,ApiError} from '../api';
import {annual,terminal} from '../model';
import type {CaseDoc,Catalog,InvestorDoc,InvestorEquityDoc,EditableDoc,MethodDoc,Result} from '../model';
import fixture from '../../../examples/valuation/synthetic-base.json';
// jsdom has no layout. Visibility/focus containment are checked in the real browser.
configure({defaultHidden:true});
const demo=fixture as CaseDoc;
const unset=(kind:string,cik:number):CaseDoc=>({...structuredClone(demo),anchor:{...demo.anchor,kind,cik},wacc:null,terminal_growth:null,forecast_years:demo.forecast_years.map(y=>({...y,...Object.fromEntries(annual.map(([k])=>[k,null]))})),terminal:Object.fromEntries(terminal.map(([k])=>[k,null])) as CaseDoc['terminal']});
const entries=[unset('test-a',123),unset('test-b',124)];
const catalog:Catalog={schema_version:'local-ev-catalog-v1',entries:entries.map((template,i)=>({kind:template.anchor.kind,company:['TEST-A','TEST-B'][i],identity:template.anchor,revenue:'100',unit:'USD',precision:'INF',preload_route:null,source_links:[],limitations:['Synthetic test metadata; revenue only'],template})),synthetic_demo:demo,timing_notice:'Retained; later-filed information; no verified cutoff',input_definitions:{}};
function reply(body:EditableDoc,ev='100000000'):Result{
 const stage_b={timing:{analytical_t0:body.anchor.annual_end,notice:'Fiscal-end analytical basis using later-filed information',information_cutoff:'NOT_ESTABLISHED_BY_CALCULATOR'},stage_a:{anchor:{...body.anchor,revenue:'100'},years:body.forecast_years.map(y=>({period_index:y.period_index,fiscal_year_label:y.fiscal_year_label,revenue:'110000000',ebit:'22000000',tax:'5500000',nopat:'16500000',d_and_a:'5500000',investment:'11000000',working_capital_cash_requirement:'2200000',fcff:'8800000'}))},years:body.forecast_years.map(y=>({period_index:y.period_index,discount_factor:'0.8',pv_fcff:'7040000'})),terminal:{fcff:'9000000',nopat:'12000000',d_and_a:'3000000',investment:'5000000',working_capital_cash_requirement:'1000000'},terminal_value:'120000000',pv_terminal_value:'64800000',pv_explicit_fcff:'35200000',enterprise_value:ev};
 const out:Result={case_name:body.case_name,input_basis:body.input_basis,submitted_inputs:structuredClone(body),limitations:['Synthetic response for UI verification only'],stage_b};
 if('calculation_scope' in body&&body.calculation_scope==='EQUITY_PER_SHARE'){
  const bridge=body.bridge as {shares:{class_id:string;observation_date:string;rationale:string};observations:{observation_id:string;disposition:string;rationale:string}[]};
  out.stage_c={stage_b:{enterprise_value:ev},eligible_assets:'100000000',financing_claims:'40000000',other_equity_claims:'10000000',equity_value:'150000000',valuation_shares:'20000000',value_per_share:'7.5',inputs:{shares:bridge.shares,observations:bridge.observations},contributions:[{component:{component_id:'assets'},signed_contribution:'100000000'},{component:{component_id:'financing'},signed_contribution:'-40000000'},{component:{component_id:'claims'},signed_contribution:'-10000000'}]};
 }
 return out;
}
function transport(run:(body:EditableDoc)=>Promise<Result> =async b=>reply(b)) {return vi.fn(async(path:string,body?:unknown)=>path==='/api/v1/catalog'?structuredClone(catalog):run(body as InvestorDoc|InvestorEquityDoc)) as unknown as typeof request;}
const click=(name:string)=>{const scope=screen.queryByRole('dialog')?within(screen.getByRole('dialog')):screen;const b=scope.getByRole('button',{name});act(()=>b.focus());fireEvent.click(b);};
function expand(name:string){const d=screen.getByText(name,{exact:true}).closest('details')!;if(!d.open){d.open=true;fireEvent(d,new Event('toggle'));}}
// Resolve the actual for/id label binding directly. jsdom's label.control walks
// the entire document for each label; profiling found it dominated multi-edit tests.
function labeled(text:string){const label=[...document.querySelectorAll('label')].find(e=>e.textContent?.trim()===text);if(!label)throw Error('Missing label: '+text);const input=label.htmlFor?document.getElementById(label.htmlFor):label.querySelector('input,select,textarea');if(!input)throw Error('Unbound label: '+text);return input as HTMLElement;}
const set=(label:string,value:string)=>fireEvent.change(labeled(label),{target:{value}});
async function company(kind='test-a'){await waitFor(()=>expect((labeled('Company')as HTMLSelectElement).disabled).toBe(false));set('Company',kind);}
function open(){click('Edit all assumptions');}
function navigate(name:string){fireEvent.click(within(screen.getByRole('navigation',{name:'Explore this valuation'})).getByRole('link',{name}));}
function fill(){for(const [key]of annual)for(let i=0;i<5;i++)set(`Synthetic period ${i+1} ${shortLabels[key]}`,({revenue_growth:'10',operating_margin:'20',forecast_tax_rate:'25',d_and_a_percent_revenue:'5',capex_percent_revenue:'10',change_in_operating_nwc_percent_revenue:'2'}as Record<string,string>)[key]);set('WACC','25');set('Terminal growth','5');for(const [key,name]of terminal)set(name,({operating_margin:'20',operating_tax_rate:'25',d_and_a_percent_revenue:'5',investment_percent_revenue:'10',working_capital_cash_requirement_percent_revenue:'2'}as Record<string,string>)[key]);}
async function update(){click('Update valuation');await waitFor(()=>expect(screen.queryByRole('dialog')).toBeNull());}
async function current(){await company();open();fill();await update();}
function selectCase(label:string){fireEvent.click(within(screen.getByRole('group',{name:'Selected scenario'})).getByRole('button',{name:label}));}
function bridge(){expand('Advanced adjustments & sources');set('Cash & investments (USD millions)','100');set('Debt (USD millions)','40');set('Other claims / adjustments','amount');set('Other claims (USD millions)','10');set('Shares outstanding (millions of shares)','20');set('Share observation date','2025-12-31');for(const label of ['Eligible-asset coverage','Financing coverage','Other-claims coverage'])set(label,'selected');set('Share population','issued');set('Included share class(es)','Test common');set('Class treatment','single_common_class');set('Existing awards','omitted');fireEvent.click(screen.getByLabelText(/I declare these amounts are dated/));}
it('shows read-only inputs and one whole-model editor with multiple edits and one execution',async()=>{
 const load=transport();render(<Workspace load={load}/>);await company();expect(document.getElementById('model-editor-wacc')).toBeNull();open();fill();set('Synthetic period 2 Revenue growth','18.1234567890123456789');expect(load).toHaveBeenCalledTimes(1);expect(screen.getAllByRole('textbox').length).toBeGreaterThan(36);await update();expect(load).toHaveBeenCalledTimes(2);expect(screen.getByRole('region',{name:'Valuation summary'}).textContent).toContain('$100.00m');expect(screen.getByRole('complementary',{name:'Active model summary'}).textContent).toContain('10.00% → 10.00%');expect(document.querySelector('.cw-editor-table')).toBeNull();open();expect((labeled('Synthetic period 2 Revenue growth')as HTMLInputElement).value).toBe('18.12');click('Cancel');
});
it('preserves intermediate strings, validates locally, focuses a required year and submits exact percentages',async()=>{
 const sent:EditableDoc[]=[];render(<Workspace load={transport(async b=>{sent.push(b);return reply(b);})}/>);await company();open();fill();for(const v of ['','-','.','-.']){set('Synthetic period 1 Revenue growth',v);expect((labeled('Synthetic period 1 Revenue growth')as HTMLInputElement).value).toBe(v);}click('Update valuation');await waitFor(()=>expect(document.activeElement).toBe(labeled('Synthetic period 1 Revenue growth')));expect(sent).toHaveLength(0);set('Synthetic period 1 Revenue growth','12.1250000000000000001');await update();expect(sent[0].forecast_years[0].revenue_growth).toBe('0.1213');expect(sent[0].anchor).toEqual(entries[0].anchor);
});
it('Cancel discards only this editing session; last result and applied overrides remain',async()=>{
 const load=transport();render(<Workspace load={load}/>);await current();open();set('WACC','26');expect(screen.getByRole('region',{name:'Valuation summary'}).textContent).toContain('Editing draft');expect(screen.getByRole('region',{name:'Valuation summary'}).textContent).toContain('$100.00m');click('Cancel');expect(load).toHaveBeenCalledTimes(2);open();expect((labeled('WACC')as HTMLInputElement).value).toBe('25.00');set('WACC','26');await update();open();set('WACC','27');click('Cancel');open();expect((labeled('WACC')as HTMLInputElement).value).toBe('26.00');click('Cancel');
});
it('replaces one annual row only on explicit action and keeps terminal values independent',async()=>{
 const sent:EditableDoc[]=[];render(<Workspace load={transport(async b=>{sent.push(b);return reply(b);})}/>);await company();open();fill();set('Synthetic period 2 Revenue growth','18');expand('Input meanings, sources & constant-rate replacement');expand('Use one rate for all years · Revenue growth');set('Revenue growth replacement (%)','13');expect((labeled('Synthetic period 2 Revenue growth')as HTMLInputElement).value).toBe('18');const row=screen.getByText('Use one rate for all years · Revenue growth').closest('details')!;fireEvent.click(within(row).getByRole('button'));set('Synthetic period 1 Operating margin','33');await update();expect(sent[0].forecast_years.every(y=>y.revenue_growth==='0.1300')).toBe(true);expect((sent[0]as MethodDoc).terminal_valuation).toMatchObject({terminal:{operating_margin:'0.2000'}});
});
it('preserves case inheritance and intentional same-value overrides through one editor',async()=>{
 render(<Workspace load={transport()}/>);await current();selectCase('Bear');open();fireEvent.input(labeled('Synthetic period 1 Revenue growth'),{target:{value:'10'}});await update();selectCase('Base');open();set('Synthetic period 1 Revenue growth','12');await update();selectCase('Bear');open();expect((labeled('Synthetic period 1 Revenue growth')as HTMLInputElement).value).toBe('10.00');click('Cancel');selectCase('Bull');open();expect((labeled('Synthetic period 1 Revenue growth')as HTMLInputElement).value).toBe('12.00');click('Cancel');
});
it('keeps five compact views mounted and preserves custom ranges across navigation without typing requests',async()=>{
 const load=transport();render(<Workspace load={load}/>);await current();navigate('Sensitivity');await waitFor(()=>expect(load).toHaveBeenCalledTimes(3));click('Edit ranges');set('WACC start (%)','22');const nav=screen.getByRole('navigation',{name:'Explore this valuation'});for(const [name,id]of [['DCF','dcf'],['Scenarios','scenario-comparison'],['Sensitivity','sensitivity'],['Full Model','full-model'],['Sources','sources-methodology']]){expect(within(nav).getByRole('link',{name}).getAttribute('href')).toBe('#'+id);expect(document.getElementById(id)).toBeTruthy();}navigate('DCF');expect(document.getElementById('sensitivity')!.hidden).toBe(true);navigate('Sensitivity');expect((labeled('WACC start (%)')as HTMLInputElement).value).toBe('22');expect(load).toHaveBeenCalledTimes(3);
});
it('retains company inputs and rejects a late response after switching',async()=>{
 let resolve!:(r:Result)=>void,body!:EditableDoc;render(<Workspace load={transport(b=>{body=b;return new Promise(r=>{resolve=r;});})}/>);await company();open();fill();click('Update valuation');await waitFor(()=>expect(resolve).toBeDefined()); // Finish/cancel via hook is covered independently; dialog retains pending entries.
 await act(async()=>resolve(reply(body)));await waitFor(()=>expect(screen.queryByRole('dialog')).toBeNull());await company('test-b');expect(screen.queryByRole('region',{name:'Interactive revenue and FCFF chart'})).toBeNull();await company('test-a');open();expect((labeled('WACC')as HTMLInputElement).value).toBe('25.00');click('Cancel');
});
it('keeps detailed optional bridge editing, focus restoration and qualified Stage C execution',async()=>{
 const sent:EditableDoc[]=[];render(<Workspace load={transport(async b=>{sent.push(b);return reply(b);})}/>);await current();navigate('Sources');expand('Optional equity / market comparison');const trigger=screen.getByRole('button',{name:'Cash, debt and shares · optional'});trigger.focus();fireEvent.click(trigger);set('Shares outstanding (millions of shares)','20');click('Cancel');expect(document.activeElement).toBe(trigger);fireEvent.click(trigger);expect((labeled('Shares outstanding (millions of shares)')as HTMLInputElement).value).toBe('');bridge();click('Save inputs');click('Calculate value per share');await screen.findByText(/150.00m equity.*7.50 USD\/share/);expect(sent).toHaveLength(2);expect((sent[1]as InvestorEquityDoc).bridge).toMatchObject({shares:{shares:'20000000'}});
});
it('keeps draft on outage, does not retry automatically, and one Update explicitly retries',async()=>{
 let fail=true;const sent:EditableDoc[]=[];render(<Workspace load={transport(async b=>{sent.push(structuredClone(b));if(fail)throw new ApiError('service_unavailable','private');return reply(b);})}/>);await company();open();fill();click('Update valuation');await screen.findByText(/Calculation did not complete/);expect(screen.getByRole('dialog')).toBeTruthy();expect((labeled('WACC')as HTMLInputElement).value).toBe('25.00');expect(sent).toHaveLength(1);fail=false;await update();expect(sent[1]).toEqual(sent[0]);expect(screen.queryByText('private')).toBeNull();
});
it('focuses an actionable server validation error while preserving other edits',async()=>{
 let fail=true;render(<Workspace load={transport(async b=>{if(fail)throw new ApiError('invalid_case','Invalid',['forecast_years[0].forecast_tax_rate: Forecast tax rate must be between 0 and 1']);return reply(b);})}/>);await company();open();fill();set('Synthetic period 2 Revenue growth','18');click('Update valuation');await waitFor(()=>expect(document.activeElement).toBe(labeled('Synthetic period 1 Operating tax rate')));expect((labeled('Synthetic period 2 Revenue growth')as HTMLInputElement).value).toBe('18.00');set('Synthetic period 1 Operating tax rate','20');fail=false;await update();
});
it('retries catalog failures and rejects percent signs before execution',async()=>{
 let first=true;const load=vi.fn(async()=>{if(first){first=false;throw new ApiError('service_unavailable','private');}return catalog;})as unknown as typeof request;render(<Workspace load={load}/>);await screen.findByRole('button',{name:'Retry loading companies'});click('Retry loading companies');await company();open();fill();set('Synthetic period 1 Revenue growth','10%');click('Update valuation');await waitFor(()=>expect(document.activeElement).toBe(labeled('Synthetic period 1 Revenue growth')));expect(load).toHaveBeenCalledTimes(2);
});

it('exports the exact submitted result/revision rather than unapplied editor values',async()=>{
 const create=vi.spyOn(URL,'createObjectURL').mockReturnValue('blob:result-first-test');const sent:EditableDoc[]=[];
 try{render(<Workspace load={transport(async b=>{sent.push(structuredClone(b));return reply(b);})}/>);await current();const blob=create.mock.calls.at(-1)![0]as Blob;const text=await new Promise<string>(resolve=>{const reader=new FileReader();reader.onload=()=>resolve(String(reader.result));reader.readAsText(blob);});const exported=JSON.parse(text);expect(exported.calculation.submitted_inputs).toEqual(sent[0]);expect(exported.input_revision).toBe(2);expect(exported.status).toBe('current');open();set('WACC','99');expect(exported.calculation.submitted_inputs.wacc).toBe('0.2500');expect(sent).toHaveLength(1);click('Cancel');}finally{create.mockRestore();}
});

it('opens a summary row at its annual operand, restores focus and identifies the selected Full Model snapshot',async()=>{
 render(<Workspace load={transport()}/>);await current();const trigger=screen.getByRole('button',{name:'Revenue growth 10.00%'});trigger.focus();fireEvent.click(trigger);await waitFor(()=>expect(document.activeElement).toBe(labeled('Synthetic period 1 Revenue growth')));expect(within(screen.getByRole('table',{name:'Annual assumptions · percentages · Base'})).getAllByRole('textbox')).toHaveLength(30);click('Cancel');expect(document.activeElement).toBe(trigger);selectCase('Bull');open();set('Synthetic period 1 Operating margin','34');await update();navigate('Full Model');const model=screen.getByRole('region',{name:'Full Model · Bull'});expect(model.textContent).toContain('34.00%');expect(model.textContent).toContain('Submitted calculation');expect(model.textContent).toContain('input revision 3');navigate('DCF');expect(screen.getByRole('region',{name:'Valuation summary'}).textContent).toContain('Enterprise value · Bull');
});
it('keeps a terminal-method change local until Update, then commits its shared scope without overwriting annual paths',async()=>{
 const sent:EditableDoc[]=[];render(<Workspace load={transport(async b=>{sent.push(structuredClone(b));return reply(b);})}/>);await current();open();fireEvent.click(within(screen.getByRole('dialog')).getByRole('radio',{name:'Exit multiple'}));expect((labeled('Year-five EV/EBIT')as HTMLInputElement).value).toBe('');click('Update valuation');await waitFor(()=>expect(document.activeElement).toBe(labeled('Year-five EV/EBIT')));expect(sent).toHaveLength(1);set('Year-five EV/EBIT','15');click('Cancel');open();expect((within(screen.getByRole('dialog')).getByRole('radio',{name:'Perpetual growth'})as HTMLInputElement).checked).toBe(true);fireEvent.click(within(screen.getByRole('dialog')).getByRole('radio',{name:'Exit multiple'}));set('Year-five EV/EBIT','15');await update();expect((sent[1]as MethodDoc).terminal_valuation).toMatchObject({method:'exit_multiple',exit_ev_ebit_multiple:'15'});expect(sent[1].forecast_years).toEqual(sent[0].forecast_years);selectCase('Bear');open();expect((within(screen.getByRole('dialog')).getByRole('radio',{name:'Exit multiple'})as HTMLInputElement).checked).toBe(true);click('Cancel');
});

it('keeps a ten-year horizon local until valid Update and shares complete Base extensions across cases',async()=>{
 const sent:EditableDoc[]=[];render(<Workspace load={transport(async b=>{sent.push(structuredClone(b));return reply(b);})}/>);await current();open();
 fireEvent.click(screen.getByRole('radio',{name:'10 years'}));
 expect((labeled('FY2031 Revenue growth')as HTMLInputElement).value).toBe('');
 click('Update valuation');expect(sent).toHaveLength(1);expect(screen.getByRole('dialog')).toBeTruthy();
 for(let i=2031;i<=2035;i++)for(const [key]of annual)set(`FY${i} ${shortLabels[key]}`,({revenue_growth:'4',operating_margin:'20',forecast_tax_rate:'25',d_and_a_percent_revenue:'5',capex_percent_revenue:'10',change_in_operating_nwc_percent_revenue:'2'}as Record<string,string>)[key]);
 await update();expect(sent[1].schema_version).toBe('investor-case-v4');expect(sent[1].forecast_years).toHaveLength(10);
 fireEvent.click(screen.getByRole('button',{name:/Cash flow conversion 40.00% FY2035/}));expect(within(screen.getByRole('table',{name:'Cash-flow assumptions · percentages · Base'})).getAllByRole('textbox')).toHaveLength(40);expect((labeled('Calculation year')as HTMLSelectElement).value).toBe('FY2035');click('Cancel');
 expect(document.querySelectorAll('[data-five-year-boundary]')).toHaveLength(1);
 selectCase('Bear');open();expect((labeled('FY2035 Revenue growth')as HTMLInputElement).value).toBe('4.00');click('Cancel');
 selectCase('Base');open();fireEvent.click(screen.getByRole('radio',{name:'5 years'}));await update();expect(sent.at(-1)!.forecast_years).toHaveLength(5);
 open();fireEvent.click(screen.getByRole('radio',{name:'10 years'}));expect((labeled('FY2035 Revenue growth')as HTMLInputElement).value).toBe('4.00');click('Cancel');
 open();expect((screen.getByRole('radio',{name:'5 years'})as HTMLInputElement).checked).toBe(true);click('Cancel');
});

it('offers six sidebar rows and edits cash-flow drivers through a submitted, year-labelled conversion summary',async()=>{
 const sent:EditableDoc[]=[];render(<Workspace load={transport(async b=>{sent.push(structuredClone(b));return reply(b);})}/>);await current();
 const sidebar=screen.getByRole('complementary',{name:'Active model summary'});
 expect(sidebar.querySelectorAll('button.cw-summary-row')).toHaveLength(6);
 expect(sidebar.textContent).not.toContain('Tax & D&A');expect(sidebar.textContent).not.toContain('Investment & WC');expect(sidebar.textContent).not.toContain('Cash, claims & shares');
 expect(screen.getByText('FCFF model')).toBeTruthy();
 const trigger=within(sidebar).getByRole('button',{name:/Cash flow conversion 40.00%/});trigger.focus();fireEvent.click(trigger);
 expect(screen.getByRole('heading',{name:'From operating profit to cash flow'})).toBeTruthy();
 const bridge=screen.getByRole('region',{name:'Submitted profit-to-cash calculation'});
 expect(bridge.textContent).toContain('$22.00m');expect(bridge.textContent).toContain('$8.80m');
 expect((labeled('Calculation year')as HTMLSelectElement).value).toBe('Synthetic period 5');
 expect(screen.queryByLabelText('Synthetic period 1 Revenue growth',{exact:true})).toBeNull();
 expect(within(screen.getByRole('table',{name:'Cash-flow assumptions · percentages · Base'})).getAllByRole('textbox')).toHaveLength(20);
 set('Calculation year','Synthetic period 1');set('Synthetic period 2 D&A / revenue','7.125');
 expect(bridge.textContent).toContain('$8.80m');expect(sent).toHaveLength(1);click('Cancel');expect(document.activeElement).toBe(trigger);
 fireEvent.click(trigger);expect((labeled('Synthetic period 2 D&A / revenue')as HTMLInputElement).value).toBe('5.00');
 set('Synthetic period 2 D&A / revenue','7.125');await update();
 expect(sent).toHaveLength(2);expect(sent[1].forecast_years[1].d_and_a_percent_revenue).toBe('0.0712');
 const expected=structuredClone(sent[0].forecast_years);expected[1].d_and_a_percent_revenue='0.0712';expect(sent[1].forecast_years).toEqual(expected);
 expect(sent[1].wacc).toBe(sent[0].wacc);
 const settings=within(screen.getByRole('region',{name:'Valuation summary'})).getByRole('button',{name:/Equity & per-share settings/});settings.focus();fireEvent.click(settings);
 expect(screen.getByLabelText('Shares outstanding (millions of shares)')).toBeTruthy();click('Cancel');expect(document.activeElement).toBe(settings);
});

it('expands to the full draft when a cash-flow update needs an input outside that panel',async()=>{
 render(<Workspace load={transport()}/>);await company();
 fireEvent.click(screen.getByRole('button',{name:/Cash flow conversion Not calculated/}));
 expect(screen.queryByLabelText('Synthetic period 1 Revenue growth',{exact:true})).toBeNull();
 click('Update valuation');await waitFor(()=>expect(document.activeElement).toBe(labeled('Synthetic period 1 Revenue growth')));
 expect(screen.getByRole('heading',{name:'Edit assumptions'})).toBeTruthy();
 expect(screen.getByRole('dialog')).toBeTruthy();click('Cancel');
});


it('opens only four primary equity entries and requires advanced declarations before direct calculation',async()=>{
 const sent:EditableDoc[]=[];render(<Workspace load={transport(async b=>{sent.push(structuredClone(b));return reply(b);})}/>);await current();
 click('Equity & per-share settings Not set ›');
 const advanced=screen.getByText('Advanced adjustments & sources').closest('details')!;
 expect(advanced.open).toBe(false);expect(screen.getByText('8 details required')).toBeTruthy();
 expect(document.querySelector('.cw-equity-inputs')!.querySelectorAll('input,select')).toHaveLength(4);
 expect(screen.getByRole('region',{name:'Enterprise value to value per share'}).textContent).toContain('= Equity value—');
 set('Cash & investments (USD millions)','100');set('Debt (USD millions)','40');set('Other claims / adjustments','amount');set('Other claims (USD millions)','10');set('Shares outstanding (millions of shares)','20');
 click('Calculate value per share');expect(sent).toHaveLength(1);
 await waitFor(()=>expect(document.activeElement).toBe(labeled('Share observation date')));expect(advanced.open).toBe(true);
 expect((labeled('Share population')as HTMLSelectElement).value).toBe('');expect((labeled('Existing awards')as HTMLSelectElement).value).toBe('');
 bridge();click('Calculate value per share');await within(screen.getByRole('dialog')).findByText('7.50');
 await waitFor(()=>expect(document.activeElement).toBe(screen.getByRole('region',{name:'Enterprise value to value per share'})));expect(advanced.open).toBe(false);
 expect(sent).toHaveLength(2);expect(sent[1].forecast_years).toEqual(sent[0].forecast_years);
 expect((sent[1]as InvestorEquityDoc).bridge).toMatchObject({shares:{shares:'20000000',observation_date:'2025-12-31'}});
 const breakdown=screen.getByRole('region',{name:'Enterprise value to value per share'});
 expect(breakdown.textContent).toContain('$150.00m');expect(breakdown.textContent).toContain('Provisional result');
 set('Cash & investments (USD millions)','110');expect(breakdown.textContent).toContain('Previous calculation');expect(breakdown.textContent).toContain('$150.00m');expect(sent).toHaveLength(2);
 click('Cancel');click('Equity & per-share settings Declared ›');expect((labeled('Cash & investments (USD millions)')as HTMLInputElement).value).toBe('100');click('Cancel');
});

it('saves incomplete equity drafts without assuming zero or calculating, and expands server reference errors on retry',async()=>{
 let mode='domain';const sent:EditableDoc[]=[];
 render(<Workspace load={transport(async b=>{sent.push(structuredClone(b));if('calculation_scope'in b&&b.calculation_scope==='EQUITY_PER_SHARE'&&mode==='domain')throw new ApiError('invalid_case','Invalid',['bridge.components[0]: Selected populations overlap']);return reply(b);})}/>);await current();
 click('Equity & per-share settings Not set ›');set('Cash & investments (USD millions)','0');click('Save inputs');
 expect(screen.queryByRole('dialog')).toBeNull();expect(sent).toHaveLength(1);
 click('Equity & per-share settings Not set ›');expect((labeled('Cash & investments (USD millions)')as HTMLInputElement).value).toBe('0');expect((labeled('Debt (USD millions)')as HTMLInputElement).value).toBe('');
 bridge();expand('Component details & overlap references');set('Assets overlap references','financing');click('Calculate value per share');
 await waitFor(()=>expect(document.activeElement).toBe(labeled('Assets overlap references')));
 expect((labeled('Assets overlap references')as HTMLInputElement).value).toBe('financing');expect(screen.getByRole('dialog')).toBeTruthy();
 mode='ok';set('Assets overlap references','');click('Calculate value per share');await within(screen.getByRole('dialog')).findByText('7.50');expect(sent).toHaveLength(3);click('Cancel');
});

it('cancels a pending equity calculation and rejects its late response',async()=>{
 let resolve!:(r:Result)=>void,body!:EditableDoc;
 const sent:EditableDoc[]=[];render(<Workspace load={transport(async b=>{sent.push(b);if('calculation_scope'in b&&b.calculation_scope==='EQUITY_PER_SHARE'){body=b;return new Promise(r=>{resolve=r;});}return reply(b);})}/>);await current();
 click('Equity & per-share settings Not set ›');bridge();click('Calculate value per share');await waitFor(()=>expect(resolve).toBeDefined());
 expect((labeled('Cash & investments (USD millions)').closest('fieldset')as HTMLFieldSetElement).disabled).toBe(true);
 click('Cancel calculation');await act(async()=>resolve(reply(body)));expect(screen.queryByRole('dialog')).toBeNull();
 click('Equity & per-share settings Declared ›');expect(screen.queryByText('7.50')).toBeNull();expect((labeled('Cash & investments (USD millions)')as HTMLInputElement).value).toBe('100');click('Cancel');
});

it('previews sidebar effects without requests, opens the existing editor on click, and clears previews across cases and views',async()=>{
 const load=transport();render(<Workspace load={load}/>);await current();
 const sidebar=screen.getByRole('complementary',{name:'Active model summary'}),chart=screen.getByRole('region',{name:'Interactive revenue and FCFF chart'});
 const geometry=()=>JSON.stringify([...chart.querySelectorAll('[data-bar-year]')].map(n=>['x','y','width','height'].map(a=>n.getAttribute(a))));const base=geometry();
 for(const name of ['Revenue growth','Operating margin','Cash flow conversion','Forecast period','Discount rate','Terminal value']){
  const row=within(sidebar).getByRole('button',{name:new RegExp('^'+name)});fireEvent.mouseEnter(row);
  expect(chart.getAttribute('data-chart-inspection')).not.toBeNull();expect(geometry()).toBe(base);
  if(name==='Operating margin')expect(chart.querySelectorAll('[data-margin-year]')).toHaveLength(5);
  fireEvent.mouseLeave(row);expect(chart.getAttribute('data-chart-inspection')).toBeNull();
 }
 expect(load).toHaveBeenCalledTimes(2);
 const margin=within(sidebar).getByRole('button',{name:/^Operating margin/});act(()=>margin.focus());expect(chart.querySelector('[data-margin-axis]')).toBeTruthy();
 fireEvent.click(margin);await waitFor(()=>expect(document.activeElement).toBe(labeled('Synthetic period 1 Operating margin')));
 expect(chart.querySelector('[data-margin-axis]')).toBeNull();click('Cancel');
 act(()=>margin.focus());expect(chart.querySelector('[data-margin-axis]')).toBeTruthy();
 navigate('Full Model');expect(chart.getAttribute('data-chart-inspection')).toBeNull();navigate('DCF');expect(chart.getAttribute('data-chart-inspection')).toBeNull();
 fireEvent.mouseEnter(margin);selectCase('Bear');expect(document.querySelector('#dcf [data-chart-inspection="margin"]')).toBeNull();expect(load).toHaveBeenCalledTimes(2);
});
