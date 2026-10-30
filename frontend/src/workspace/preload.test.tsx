import {it,expect,vi} from 'vitest';
import {renderHook,act,waitFor,render,screen,fireEvent,within} from '@testing-library/react';
import {useWorkspace} from './useWorkspace';
import {generatedRates,applyEstimates,inheritedRate,estimateRefreshRows} from './preload';
import type {PreloadProfile} from './preload';
import type {Catalog,CaseDoc,Draft,Result} from '../model';
import {annual,terminal,makeDraft} from '../model';
import {request} from '../api';
import {Workspace} from './Workspace';
import {FullModel} from './FullModel';
import fixture from '../../../examples/valuation/synthetic-base.json';
// Finite software-only fixtures. No company estimates or financial outputs are authenticated here.
const template={...structuredClone(fixture),anchor:{...fixture.anchor,kind:'googl-fy2025',cik:1652044},forecast_years:fixture.forecast_years.map(y=>({...y,...Object.fromEntries(annual.map(([k])=>[k,null]))})),terminal:Object.fromEntries(terminal.map(([k])=>[k,null])),wacc:null,terminal_growth:null} as unknown as CaseDoc;
const meta={...structuredClone(template),anchor:{...template.anchor,kind:'meta-fy2025',cik:1326801}};
const catalog={schema_version:'local-ev-catalog-v1',entries:[template,meta].map(t=>({kind:t.anchor.kind,company:t===template?'GOOGL':'META',identity:t.anchor,revenue:'402836000000',unit:'USD',precision:'-6',source_links:[],limitations:[],template:t})),synthetic_demo:fixture as CaseDoc,timing_notice:'Synthetic metadata',input_definitions:{}} as Catalog;
function profile(value='0.1'):PreloadProfile{
 const draft=makeDraft(template),fields=Object.fromEntries([...Object.keys(draft.rates),'exit_ev_ebit_multiple'].map(path=>[path,{value:path==='exit_ev_ebit_multiple'?null:value,status:path==='exit_ev_ebit_multiple'?'MISSING_EVIDENCE':'CONFIGURED_CONVENTION',classification:['FORECAST_ESTIMATE'],basis:'SYNTHETIC_TEST_CONFIGURATION',unit:'fraction',rule:'synthetic-fixture-v1',operands:{value},sources:[],periods:[],limitation:'Synthetic UI fixture only'}]));
 const rates=Object.fromEntries(Object.entries(fields).map(([p,f])=>[p,f.value]));
 return {schema_version:'preload-profile-v1',economic_hash:'a'.repeat(64),generated_at:'2026-10-30T00:00:00Z',economic:{issuer:{ticker:'GOOGL',issuer:'Software fixture',listing_class:'A'},anchor:template.anchor,anchor_revenue:'402836000000',dates:{model_origin:'2025-12-31',information_review:'2026-10-30',timing:'Synthetic source labels; not actual company forecasts'},fields,scenarios:{Base:rates,Bear:{...rates},Bull:{...rates}},policy:{version:'synthetic-v1'},configuration:{bear_growth_offset:'-0.02',bull_growth_offset:'0.02',bear_margin_offset:'-0.02',bull_margin_offset:'0.02',bear_wacc_offset:'0.01',bull_wacc_offset:'-0.01'},configuration_provenance:{owner:'Synthetic fixture'},sources:[],observations:[],diagnostics:['Software-only fixture'],optional_bridge:{status:'UNSUPPORTED_PREPARATION',reason:'No financial selections'}}};
}
function transport(get:()=>Promise<PreloadProfile>=async()=>profile()) {return vi.fn(async(path:string)=>path==='/api/v1/catalog'?catalog:path==='/api/v1/preloads/googl'?get():Promise.reject(Error('Unexpected financial execution'))) as unknown as typeof request;}
async function start(load=transport()) {const h=renderHook(()=>useWorkspace(load));await waitFor(()=>expect(h.result.current.catalog).not.toBeNull());act(()=>h.result.current.select('googl-fy2025'));await waitFor(()=>expect(h.result.current.company?.preload?.profile).toBeDefined());return {...h,load};}
it('populates only a fresh GOOGL session, with no calculation, and keeps other issuers unset',async()=>{
 const h=await start();expect(h.result.current.session?.draft.rates.wacc).toBe('10');expect(h.result.current.session?.ev.result).toBeNull();expect(h.load).toHaveBeenCalledTimes(2);
 act(()=>h.result.current.select('meta-fy2025'));expect(h.result.current.session?.draft.rates.wacc).toBe('');act(()=>h.result.current.select('googl-fy2025'));expect(h.result.current.session?.draft.rates.wacc).toBe('10');
});
it('tracks equal-value override identity and resets one annual field without flattening other overrides',async()=>{
 const h=await start();let draft=structuredClone(h.result.current.session!.draft);draft.rates['forecast_years[2].revenue_growth']='17.1234567890123456789';act(()=>h.result.current.editDraft(draft,true,['forecast_years[2].revenue_growth']));draft=structuredClone(h.result.current.session!.draft);act(()=>h.result.current.editDraft(draft,true,['wacc']));
 expect(h.result.current.session!.overrides).toContain('wacc');expect(h.result.current.session!.overrides).toContain('forecast_years[2].revenue_growth');act(()=>h.result.current.resetEstimate(['wacc']));expect(h.result.current.session!.overrides).not.toContain('wacc');expect(h.result.current.session!.draft.rates['forecast_years[2].revenue_growth']).toBe('17.1234567890123456789');
});
it('reviews old/new/active values before explicit adoption and preserves overrides including equality',async()=>{
 let candidate=profile();const h=await start(transport(async()=>candidate));const draft=structuredClone(h.result.current.session!.draft);draft.rates.wacc='15';act(()=>h.result.current.editDraft(draft,true,['wacc']));candidate=profile('0.2');candidate.economic_hash='b'.repeat(64);
 await act(()=>h.result.current.refreshPreload());expect(h.result.current.session!.draft.rates.terminal_growth).toBe('10');expect(h.result.current.company!.preload!.candidate!.economic_hash).toBe('b'.repeat(64));
 const rows=estimateRefreshRows(profile(),candidate,h.result.current.session!.draft,['wacc']);expect(rows.find(r=>r.path==='wacc')).toMatchObject({previous:'0.1',candidate:'0.2',active:'15',overridden:true});
 act(()=>h.result.current.adoptPreload());expect(h.result.current.session!.draft.rates.wacc).toBe('15');expect(h.result.current.session!.draft.rates.terminal_growth).toBe('20');expect(h.result.current.session!.ev.phase).toBe('incomplete');expect(h.result.current.session!.ev.result).toBeNull();
});
it('keeps diagnostic scenario inheritance separate from explicit overrides and shared method drafts',async()=>{
 const h=await start();let d=structuredClone(h.result.current.session!.draft);d.rates['forecast_years[0].revenue_growth']='15';act(()=>h.result.current.editDraft(d,true,['forecast_years[0].revenue_growth']));expect(h.result.current.company!.cases.Bear.draft.rates['forecast_years[0].revenue_growth']).toBe('13');
 act(()=>h.result.current.selectCase('Bear'));d=structuredClone(h.result.current.session!.draft);d.rates['forecast_years[0].revenue_growth']='13';act(()=>h.result.current.editDraft(d,true,['forecast_years[0].revenue_growth']));act(()=>h.result.current.selectCase('Base'));d=structuredClone(h.result.current.session!.draft);d.rates['forecast_years[0].revenue_growth']='18';act(()=>h.result.current.editDraft(d,true,['forecast_years[0].revenue_growth']));expect(h.result.current.company!.cases.Bear.draft.rates['forecast_years[0].revenue_growth']).toBe('13');expect(h.result.current.company!.cases.Bull.draft.rates['forecast_years[0].revenue_growth']).toBe('20');
 act(()=>h.result.current.setTerminalMethod('exit_multiple'));expect(h.result.current.session!.draft.rates.exit_ev_ebit_multiple).toBe('');act(()=>h.result.current.setTerminalMethod('perpetual_growth'));expect(h.result.current.session!.draft.rates.terminal_growth).toBe('10');
});
it('does not overwrite typing while initial profile loads and ignores a late response after company switching',async()=>{
 let resolve!:(p:PreloadProfile)=>void;const load=transport(()=>new Promise(r=>{resolve=r;})),h=renderHook(()=>useWorkspace(load));await waitFor(()=>expect(h.result.current.catalog).not.toBeNull());act(()=>h.result.current.select('googl-fy2025'));await waitFor(()=>expect(resolve).toBeDefined());const d=structuredClone(h.result.current.session!.draft);d.rates.wacc='12';act(()=>h.result.current.editDraft(d,true,['wacc']));await act(async()=>resolve(profile()));expect(h.result.current.session!.draft.rates.wacc).toBe('12');expect(h.result.current.company!.preload!.candidate).toBeDefined();
 act(()=>h.result.current.select('meta-fy2025'));expect(h.result.current.session!.draft.rates.wacc).toBe('');
});
it('retains entries on an unavailable refresh, and retries explicitly',async()=>{
 let fail=false;const h=await start(transport(async()=>{if(fail)throw Error('API unavailable');return profile();}));fail=true;await act(()=>h.result.current.refreshPreload());expect(h.result.current.company!.preload!.status).toBe('failed');expect(h.result.current.session!.draft.rates.wacc).toBe('10');fail=false;await act(()=>h.result.current.refreshPreload());expect(h.result.current.company!.preload!.candidate).toBeDefined();
});
it('keeps stale field values visible in provenance while blocking their automatic population',()=>{
 const p=profile();p.economic.fields.wacc.status='STALE';expect(generatedRates(p,'Base').wacc).toBe('');expect(p.economic.fields.wacc.value).toBe('0.1');
 const d=makeDraft(template);d.rates.wacc='12';expect(applyEstimates(d,p,'Base',['wacc']).rates.wacc).toBe('12');expect(inheritedRate(p,'Bear','wacc','10')).toBe('11');
});
it('exposes per-driver provenance and no automatic calculations in the actual workspace component',async()=>{
 const load=transport();render(<Workspace load={load}/>);await waitFor(()=>expect((screen.getByLabelText('Company') as HTMLSelectElement).disabled).toBe(false));fireEvent.change(screen.getByLabelText('Company'),{target:{value:'googl-fy2025'}});await screen.findByText('Editable GOOGL starting estimate');expect((screen.getByLabelText('WACC',{exact:true}) as HTMLInputElement).value).toBe('10');expect(load).toHaveBeenCalledTimes(2);expect(screen.getAllByText(/Starting estimate & source/).length).toBeGreaterThan(5);expect(screen.getByText('Full Model · history, annual inputs & calculations')).toBeTruthy();
});
it('uses returned operands and submitted rates for stale Full Model explanations and exports',async()=>{
 const create=vi.spyOn(URL,'createObjectURL').mockImplementation(()=> 'blob:full-model-test');
 const d=makeDraft(fixture as CaseDoc);d.rates.wacc='99';const submitted=structuredClone(d.doc);submitted.forecast_years[0].operating_margin='0.2';
 const y={period_index:1,fiscal_year_label:'Synthetic period 1',revenue:'110000000',ebit:'22000000',tax:'5500000',nopat:'16500000',d_and_a:'5500000',investment:'11000000',working_capital_cash_requirement:'2200000',fcff:'8800000'};
 const result={case_name:'Synthetic',input_basis:'SYNTHETIC_TEST',submitted_inputs:submitted,limitations:[],stage_b:{stage_a:{anchor:{revenue:'100000000'},years:Array.from({length:5},(_,i)=>({...y,period_index:i+1,fiscal_year_label:`Synthetic period ${i+1}`}))},years:Array.from({length:5},()=>({pv_fcff:'7040000',discount_factor:'0.8'})),pv_explicit_fcff:'35200000',pv_terminal_value:'64800000',enterprise_value:'100000000',terminal_value:'120000000',timing:{analytical_t0:'2025-12-31',notice:'Synthetic',information_cutoff:'unknown'}}} as unknown as Result;
 render(<FullModel draft={d} result={result} stale revision={2} overrides={[]} change={()=>{}}/>);const details=screen.getByText('Full Model · history, annual inputs & calculations').closest('details')!;details.open=true;fireEvent(details,new Event('toggle'));fireEvent.click(screen.getByRole('button',{name:'Synthetic period 1 EBIT explanation'}));expect(screen.getByRole('status').textContent).toContain('$110.00m revenue × 20.00% operating margin = $22.00m EBIT');expect(screen.getByText(/input revision 2/)).toBeTruthy();const blob=create.mock.calls.at(-1)![0] as Blob;const text=await new Promise<string>(resolve=>{const reader=new FileReader();reader.onload=()=>resolve(String(reader.result));reader.readAsText(blob);});expect(JSON.parse(text)).toEqual({input_revision:2,status:'stale',calculation:result,preload_profile:null,user_overrides:[]});create.mockRestore();
});
it('generates exact centered diagnostic axes in method units without clamping',async()=>{
 const {profileGrid}=await import('./preload');const p=profile();Object.assign(p.economic.configuration,{sensitivity_wacc_offset:'0.01',sensitivity_growth_offset:'0.005',sensitivity_multiple_offset:'2'});const d=makeDraft(template);d.rates.wacc='0.5';d.rates.terminal_growth='3';d.terminalMethod='perpetual_growth';
 expect(profileGrid(d,p)).toEqual({waccStart:'-0.5',waccEnd:'1.5',waccStep:'1',growthStart:'2.5',growthEnd:'3.5',growthStep:'0.5'});d.terminalMethod='exit_multiple';d.rates.exit_ev_ebit_multiple='15.1234567890123456789';expect(profileGrid(d,p).growthStart).toBe('13.1234567890123456789');expect(profileGrid(d,p).growthStep).toBe('2');
});
it('candidate adoption preserves a Base override and transforms only nonoverridden scenario followers',async()=>{
 let p=profile();const h=await start(transport(async()=>p));const draft=structuredClone(h.result.current.session!.draft);draft.rates.wacc='15';act(()=>h.result.current.editDraft(draft,true,['wacc']));p=profile('0.2');p.economic_hash='b'.repeat(64);await act(()=>h.result.current.refreshPreload());act(()=>h.result.current.adoptPreload());expect(h.result.current.company!.cases.Base.draft.rates.wacc).toBe('15');expect(h.result.current.company!.cases.Bear.draft.rates.wacc).toBe('16');expect(h.result.current.company!.cases.Bull.draft.rates.wacc).toBe('14');
});

it('preserves personal notes while updating machine provenance on adoption',()=>{const p=profile(),d=makeDraft(template);d.doc.preparation.notes='My personal rationale';const adopted=applyEstimates(d,p,'Base',[]);expect(adopted.doc.preparation.notes).toContain('My personal rationale');expect(adopted.doc.preparation.notes).toContain(p.economic_hash);const again=applyEstimates(adopted,p,'Base',[]);expect(again.doc.preparation.notes).toBe(adopted.doc.preparation.notes);});

it('preserves a deliberately forked input snapshot during refreshed estimate adoption',()=>{const p=profile(),d=makeDraft(template);d.rates=generatedRates(p,'Base');d.rates.wacc='12.34567890123456789';d.rates['forecast_years[2].revenue_growth']='16';const next=applyEstimates(d,profile('0.2'),'Exploratory 1',Object.keys(d.rates).filter(k=>d.rates[k].trim()));expect(next.rates).toEqual(d.rates);});
