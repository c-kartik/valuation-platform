import {it,expect,vi} from 'vitest';
import {renderHook,act,waitFor,render,screen,fireEvent} from '@testing-library/react';
import Decimal from 'decimal.js';
import {makeDraft,buildRequest,entryErrors,requiredPaths,multipleDisplay,fractionToPercentage} from '../model';
import type {CaseDoc,Catalog,EditableDoc,MethodDoc,Result} from '../model';
import {request} from '../api';
import {emptyEquity} from '../equity';
import {useWorkspace} from './useWorkspace';
import {axes,newGrid,sensitivityRequest} from './sensitivity';
import {scenarioRequest} from './scenarios';
import {reverseRequest,newReverse} from './reverse';
import {TerminalComparison} from './TerminalComparison';
import {SensitivityPanel} from './SensitivityPanel';
import {AssumptionSummary} from './AssumptionSummary';
import {ValuationBreakdown} from './ValuationBreakdown';
import fixture from '../../../examples/valuation/synthetic-base.json';
const demo=fixture as CaseDoc;
const catalog:Catalog={schema_version:'fixture',entries:[],synthetic_demo:demo,timing_notice:'Synthetic only',input_definitions:{}};
function reply(doc:EditableDoc):Result{
 const method=doc.schema_version==='investor-case-v3'?doc.terminal_valuation.method:'perpetual_growth';
 const b:Result['stage_b']={terminal_method:method,timing:{analytical_t0:doc.anchor.annual_end,notice:'Later-filed information · synthetic test',information_cutoff:'UNKNOWN'},stage_a:{anchor:{...doc.anchor,revenue:'100'},years:doc.forecast_years.map((y,i)=>({period_index:i+1,fiscal_year_label:y.fiscal_year_label,revenue:'110',ebit:'22',tax:'5.5',nopat:'16.5',d_and_a:'5.5',investment:'11',working_capital_cash_requirement:'2.2',fcff:'8.8'}))},years:doc.forecast_years.map((_,i)=>({period_index:i+1,discount_factor:'0.8',pv_fcff:'7.04'})),terminal:{fcff:'30.438639'},terminal_value:'152.193195',pv_terminal_value:'49.8706661376',pv_explicit_fcff:'27.7063942144',enterprise_value:'77.5770603520'};
 if(method==='exit_multiple'){
  // Synthetic transport fixture, not a JS calculation engine.
  delete (b as Partial<typeof b>).terminal;b.terminal_basis={metric:'EBIT',definition:'SBC and service leases expensed once',period_index:5,fiscal_year_label:doc.forecast_years[4].fiscal_year_label,year_five_ebit:'32.2102',wacc:doc.wacc!,exit_ev_ebit_multiple:(doc as MethodDoc).terminal_valuation.method==='exit_multiple'?((doc as MethodDoc).terminal_valuation as {exit_ev_ebit_multiple:string}).exit_ev_ebit_multiple:'15'};
  Object.assign(b,{terminal_value:'483.153',pv_terminal_value:'158.31957504',enterprise_value:'186.0259692544'});
 }
 return {case_name:doc.case_name,input_basis:doc.input_basis,submitted_inputs:structuredClone(doc),limitations:['Synthetic transport fixture only'],stage_b:b};
}
async function ready(run:(d:EditableDoc)=>Promise<Result>=async d=>reply(d)){
 const load=vi.fn(async(path:string,body?:unknown)=>path==='/api/v1/catalog'?structuredClone(catalog):run(body as EditableDoc)) as unknown as typeof request;
 const h=renderHook(()=>useWorkspace(load));await waitFor(()=>expect(h.result.current.catalog).not.toBeNull());act(()=>h.result.current.select('demo'));return {h,load};
}
it('uses 32 exit operands, preserves opposite drafts and exact strings without requiring them',()=>{
 const d=makeDraft(demo);d.terminalMethod='exit_multiple';d.rates.exit_ev_ebit_multiple='15.500000000000000001';d.rates.terminal_growth='bad';for(const k of Object.keys(d.rates).filter(p=>p.startsWith('terminal.')))d.rates[k]='';
 expect(requiredPaths(d)).toHaveLength(32);expect(entryErrors(d)).toEqual({});const body=buildRequest(d) as MethodDoc;
 expect(body.terminal_valuation).toEqual({method:'exit_multiple',exit_ev_ebit_multiple:'15.500000000000000001'});expect(body).not.toHaveProperty('terminal_growth');expect(body).not.toHaveProperty('terminal');expect(body.comparison_terminal_valuation).toMatchObject({terminal_growth:null});
 d.terminalMethod='perpetual_growth';expect(requiredPaths(d)).toHaveLength(37);expect(entryErrors(d)).toHaveProperty('terminal_growth');d.rates.terminal_growth='5';for(const[k,v]of Object.entries(demo.terminal))d.rates['terminal.'+k]=fractionToPercentage(v);d.rates.exit_ev_ebit_multiple='bad';expect(entryErrors(d)).toEqual({});expect(()=>buildRequest(d)).not.toThrow();
});
it('keeps method choice shared, inherits multiples and preserves explicit same-value overrides and reset',async()=>{
 const {h}=await ready();act(()=>h.result.current.setTerminalMethod('exit_multiple'));expect(Object.values(h.result.current.company!.cases).every(c=>c.draft.terminalMethod==='exit_multiple')).toBe(true);
 act(()=>h.result.current.editScenarioRate('Base',['exit_ev_ebit_multiple'],'15'));act(()=>h.result.current.editScenarioRate('Bear',['exit_ev_ebit_multiple'],'15'));act(()=>h.result.current.editScenarioRate('Base',['exit_ev_ebit_multiple'],'18'));
 expect(h.result.current.company!.cases.Bear!.draft.rates.exit_ev_ebit_multiple).toBe('15');expect(h.result.current.company!.cases.Bull!.draft.rates.exit_ev_ebit_multiple).toBe('18');
 const set=scenarioRequest(h.result.current.company!.cases,emptyEquity(),'',false,true);expect(set.schema_version).toBe('investor-scenario-set-v3');expect(set.scenarios.map(e=>(e.case as MethodDoc).terminal_valuation)).toEqual([{method:'exit_multiple',exit_ev_ebit_multiple:'15'},{method:'exit_multiple',exit_ev_ebit_multiple:'18'},{method:'exit_multiple',exit_ev_ebit_multiple:'18'}]);
 act(()=>h.result.current.resetOverrides('Bear'));expect(h.result.current.company!.cases.Bear!.draft.rates.exit_ev_ebit_multiple).toBe('18');
});
it('cancels method changes during requests, rejects late results, preserves drafts and stales multiple edits',async()=>{
 const pending:{body:EditableDoc;resolve:(r:Result)=>void}[]=[];const {h}=await ready(d=>new Promise(resolve=>pending.push({body:d,resolve})));
 let first!:Promise<void>;act(()=>{first=h.result.current.calculate('ev');});act(()=>h.result.current.setTerminalMethod('exit_multiple'));act(()=>h.result.current.editScenarioRate('Base',['exit_ev_ebit_multiple'],'15'));
 await act(async()=>{pending[0].resolve(reply(pending[0].body));await first;});expect(h.result.current.session!.ev.result).toBeNull();
 let second!:Promise<void>;act(()=>{second=h.result.current.calculate('ev');});await act(async()=>{pending[1].resolve(reply(pending[1].body));await second;});expect(h.result.current.session!.ev.phase).toBe('current');expect(h.result.current.session!.ev.result!.stage_b.terminal_method).toBe('exit_multiple');
 act(()=>h.result.current.editScenarioRate('Base',['exit_ev_ebit_multiple'],'16'));expect(h.result.current.session!.ev.phase).toBe('stale');expect(h.result.current.session!.ev.result!.stage_b.terminal_basis!.exit_ev_ebit_multiple).toBe('15');act(()=>h.result.current.setTerminalMethod('perpetual_growth'));expect(h.result.current.session!.draft.rates.terminal_growth).toBe('5');act(()=>h.result.current.setTerminalMethod('exit_multiple'));expect(h.result.current.session!.draft.rates.exit_ev_ebit_multiple).toBe('16');
});
it('requires explicit exit axes, uses × units, preserves per-method settings and blocks reverse',async()=>{
 const {h}=await ready();act(()=>h.result.current.editGrid('growthStart','1'));act(()=>h.result.current.setTerminalMethod('exit_multiple'));expect(h.result.current.session!.grid.settings.growthStart).toBe('');act(()=>h.result.current.editScenarioRate('Base',['exit_ev_ebit_multiple'],'15'));
 const d=h.result.current.session!.draft,g=newGrid();expect(()=>sensitivityRequest(d,d,emptyEquity(),g,true)).toThrow();g.settings={waccStart:'10',waccEnd:'12',waccStep:'1',growthStart:'12.5',growthEnd:'17.5',growthStep:'2.5'};
 const body=sensitivityRequest(d,d,emptyEquity(),g,true);expect(body.exit_ev_ebit_multiple_values).toEqual(['12.5','15','17.5']);expect(body.wacc_values).toEqual(['0.1','0.11','0.12']);expect(body).not.toHaveProperty('terminal_growth_values');try{reverseRequest(d,d,emptyEquity(),newReverse());throw Error('should reject');}catch(e){expect((e as {fields:Record<string,string>}).fields.terminal_method).toContain('does not support exit multiples');}
 act(()=>h.result.current.editGrid('growthStart','12.5'));act(()=>h.result.current.setTerminalMethod('perpetual_growth'));expect(h.result.current.session!.grid.settings.growthStart).toBe('1');act(()=>h.result.current.setTerminalMethod('exit_multiple'));expect(h.result.current.session!.grid.settings.growthStart).toBe('12.5');
});
it('shows inline ×, fiscal basis, current/stale EBIT and method-aware completeness',async()=>{
 const {h}=await ready();act(()=>h.result.current.setTerminalMethod('exit_multiple'));const c=h.result.current.company!.cases.Base;
 const view=render(<AssumptionSummary label="Base" caseState={c} change={()=>{}} editBridge={()=>{}} setMethod={()=>{}}/>);expect(screen.getByText('31/32 entered')).toBeTruthy();expect(screen.getByLabelText('Year-five EV/EBIT').parentElement!.textContent).toContain('×');expect(screen.queryByLabelText('Terminal growth')).toBeNull();expect(screen.getByText(/Synthetic period 5 · Applies your multiple/)).toBeTruthy();
 const result=reply({...buildRequest({...c.draft,rates:{...c.draft.rates,exit_ev_ebit_multiple:'15'}})} as MethodDoc);view.rerender(<AssumptionSummary label="Base" caseState={{...c,ev:{...c.ev,result,phase:'stale'}}} change={()=>{}} editBridge={()=>{}}/>);expect(screen.getByText(/Year-five EBIT:.*previous calculation · stale/)).toBeTruthy();
});
it('renders both-method exact cross-checks, unavailable reasons and signed composition without fabricated FCFF',()=>{
 const d=makeDraft(demo);d.terminalMethod='exit_multiple';d.rates.exit_ev_ebit_multiple='15';const exit=reply(buildRequest(d)),gordon=reply(buildRequest({...d,terminalMethod:'perpetual_growth'}));
 exit.terminal_comparison={selected_method:'exit_multiple',submitted_inputs:buildRequest(d) as MethodDoc,results:{exit_multiple:{status:'CURRENT',stage_b:exit.stage_b},perpetual_growth:{status:'CURRENT',stage_b:gordon.stage_b}},ev_difference_exit_minus_perpetual:'108.4489089024',implied_year_five_ev_ebit:{value:'4.725',reason:null}};
 const view=render(<><TerminalComparison result={exit} stale={false}/><ValuationBreakdown result={exit} stale={false}/></>);expect(screen.getByText(/4.72×/)).toBeTruthy();expect(screen.getByText(/not market upside\/downside/)).toBeTruthy();expect(screen.queryByText(/Terminal FCFF/)).toBeNull();expect(screen.getByText(/Final-year EBIT.*15×/)).toBeTruthy();
 exit.terminal_comparison.results.perpetual_growth={status:'AWAITING_INPUTS',reason:'Terminal assumptions unset'};exit.terminal_comparison.ev_difference_exit_minus_perpetual=null;exit.terminal_comparison.implied_year_five_ev_ebit={value:null,reason:'Positive EBIT required'};
 view.rerender(<TerminalComparison result={exit} stale={false}/>);expect(screen.getByText(/Positive EBIT required/)).toBeTruthy();expect(screen.getAllByText('Awaiting inputs')).toHaveLength(4);view.rerender(<TerminalComparison result={exit} stale/>);expect(screen.getByText('Previous comparison · stale')).toBeTruthy();expect(screen.queryByText(/implied year-five EV/)).toBeNull();
});
it('keeps multiple conversion and display isolated from caller Decimal precision',()=>{
 const old=Decimal.precision;Decimal.set({precision:2});try{expect(multipleDisplay('15.555')).toBe('15.56×');expect(axes({waccStart:'10',waccEnd:'11',waccStep:'1',growthStart:'15.000000000000000001',growthEnd:'15.000000000000000003',growthStep:'0.000000000000000001'},true).terminal_growth_values).toEqual(['15.000000000000000001','15.000000000000000002','15.000000000000000003']);expect(Decimal.precision).toBe(2);}finally{Decimal.set({precision:old});}
});
it('accepts exact exit API/export data without a fabricated terminal year and rejects malformed comparisons',async()=>{
 const d=makeDraft(demo);d.terminalMethod='exit_multiple';d.rates.exit_ev_ebit_multiple='15.500000000000000001';const doc=buildRequest(d) as MethodDoc,r=reply(doc);
 r.terminal_comparison={selected_method:'exit_multiple',submitted_inputs:doc,results:{exit_multiple:{status:'CURRENT',stage_b:r.stage_b},perpetual_growth:{status:'AWAITING_INPUTS',reason:'Not supplied'}},ev_difference_exit_minus_perpetual:null};
 const original=globalThis.fetch;globalThis.fetch=async()=>new Response(JSON.stringify(r),{status:200});
 try{const result=await request<Result>('/api/v1/cases/run',doc);expect(result).toEqual(r);expect(result.stage_b).not.toHaveProperty('terminal');expect(result.stage_b.terminal_basis!.exit_ev_ebit_multiple).toBe('15.500000000000000001');delete r.terminal_comparison.results.exit_multiple!.stage_b;await expect(request('/api/v1/cases/run',doc)).rejects.toMatchObject({code:'service_unavailable'});}finally{globalThis.fetch=original;}
});
