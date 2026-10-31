/** Exact percentage-axis construction and transport types; no valuation formulas. */
import Decimal from 'decimal.js';
import {percentageToFraction,InputErrors,entryErrors,methodOf,multipleString} from '../model';
import type {Draft,Errors,EditableDoc,Result} from '../model';
import type {EquityDraft} from '../equity';
import {equityErrors} from '../equity';
import {requestFor} from './scenarios';
const D=Decimal.clone({precision:220,rounding:Decimal.ROUND_HALF_EVEN});
export type GridSettings={waccStart:string;waccEnd:string;waccStep:string;growthStart:string;growthEnd:string;growthStep:string};
export const blankSettings=():GridSettings=>({waccStart:'',waccEnd:'',waccStep:'',growthStart:'',growthEnd:'',growthStep:''});
export const settingLabels:Record<keyof GridSettings,string>={waccStart:'WACC start (%)',waccEnd:'WACC end (%)',waccStep:'WACC step (percentage points)',growthStart:'Terminal growth start (%)',growthEnd:'Terminal growth end (%)',growthStep:'Terminal growth step (percentage points)'};
export type SensitivityDoc={schema_version:'investor-sensitivity-request-v1'|'investor-sensitivity-request-v2'|'investor-sensitivity-request-v3';sensitivity_name:string;source:{kind:'single_case';case:EditableDoc;analytical_date:string;information_cutoff:string|null};wacc_values:string[];terminal_growth_values?:string[];exit_ev_ebit_multiple_values?:string[]};
export type Cell={wacc:string;terminal_growth?:string;exit_ev_ebit_multiple?:string;status:'VALID'|'INVALID';reason:string|null;metrics:Record<string,string|null>;changes:unknown};
export type SensitivityResult={schema_version:string;submitted_inputs:SensitivityDoc;selected_case:EditableDoc;selection:{analytical_date:string;information_cutoff:string|null;source_kind:string;scenario_label:string|null};reference_result:Result;reference_metrics:Record<string,string|null>;wacc_values:string[];terminal_growth_values?:string[];exit_ev_ebit_multiple_values?:string[];cells:Cell[][];held_fixed:string;limitations:string[]};
export type GridState={generated?:boolean;settings:GridSettings;cutoff:string;equity:boolean;phase:'empty'|'incomplete'|'calculating'|'current'|'stale'|'failed';result:SensitivityResult|null;errors:Errors;failure:string;equityCurrent:boolean;inspected:[number,number]|null;previousPhase?:GridState['phase']};
export const newGrid=():GridState=>({settings:blankSettings(),cutoff:'',equity:false,phase:'empty',result:null,errors:{},failure:'',equityCurrent:false,inspected:null});
export const staleGrid=(g:GridState):GridState=>({...g,phase:g.result?'stale':'incomplete',errors:{},failure:'',equityCurrent:false,inspected:null});
export function ratePercent(raw:string):string{return new D(raw).times('100').toFixed();}
export function axes(settings:GridSettings,exit=false):{wacc_values:string[];terminal_growth_values:string[]}{
 const errors:Errors={};
 function axis(prefix:'wacc'|'growth'){
  const keys=[`${prefix}Start`,`${prefix}End`,`${prefix}Step`] as (keyof GridSettings)[];
  const rates=keys.map(k=>{try{const v=prefix==='growth'&&exit?multipleString(settings[k]):percentageToFraction(settings[k]);if(v===null)throw Error(prefix==='growth'&&exit?'Required. Enter an EV/EBIT multiple, e.g. 15.':'Required. Enter percentage units; 10 means 10%.');return new D(v);}catch(e){errors[k]=(e as Error).message;return null;}});
  if(rates.some(v=>v===null))return [];
  const [start,end,step]=rates as Decimal[];
  if(!step.gt(0)){errors[keys[2]]='Step must be greater than zero.';return [];}
  if(end.lt(start)){errors[keys[1]]='End must be at least start.';return [];}
  if(!end.minus(start).mod(step).isZero()){errors[keys[1]]='End must be reached exactly by the step; no truncated endpoint.';return [];}
  const values:string[]=[];
  for(let value=start;value.lte(end);value=value.plus(step)){if(values.length===11){errors[keys[2]]='Maximum 11 values per axis (121 cells). Increase step or narrow range.';return [];}values.push(value.toFixed());}
  return values;
 }
 const wacc_values=axis('wacc'),terminal_growth_values=axis('growth');if(Object.keys(errors).length)throw new InputErrors(errors);return {wacc_values,terminal_growth_values};
}
export function sensitivityRequest(draft:Draft,base:Draft,bridge:EquityDraft,grid:GridState,unknownCutoff=false):SensitivityDoc{
 const errors=entryErrors(draft);if(!grid.cutoff&&!unknownCutoff)errors.cutoff='Enter a declared information cutoff; it is not verified source availability.';
 if(grid.equity)for(const [key,value]of Object.entries(equityErrors(bridge,draft.doc.anchor.annual_end)))errors[`bridge.${key}`]=value;
 let rates:ReturnType<typeof axes>|undefined;try{rates=axes(grid.settings,methodOf(draft)==='exit_multiple');}catch(e){Object.assign(errors,(e as InputErrors).fields);}
 if(Object.keys(errors).length)throw new InputErrors(errors);
 const exit=methodOf(draft)==='exit_multiple';
 return {schema_version:exit?'investor-sensitivity-request-v3':unknownCutoff?'investor-sensitivity-request-v2':'investor-sensitivity-request-v1',sensitivity_name:`${draft.doc.case_name} · ${exit?'WACC/multiple':'WACC/g'} sensitivity`,source:{kind:'single_case',case:requestFor(draft,base,bridge,grid.equity),analytical_date:draft.doc.anchor.annual_end,information_cutoff:grid.cutoff||null},...(exit?{wacc_values:rates!.wacc_values,exit_ev_ebit_multiple_values:rates!.terminal_growth_values}:rates!)};
}

/** Explicit diagnostic action, derived only from the entered case. No automatic execution. */
export function smallGrid(draft:Draft):GridSettings{
 const w=new D(percentageToFraction(draft.rates.wacc)!),g=new D(percentageToFraction(draft.rates.terminal_growth)!);
 if(!w.isFinite()||!g.isFinite()||w.lte(0))throw new InputErrors({waccStart:'Enter a valid discount rate first.'});
 const step=D.min(new D('0.01'),w.div(2)),gstep=D.min(new D('0.005'),g.plus(1).div(2));
 return {waccStart:ratePercent(w.minus(step).toFixed()),waccEnd:ratePercent(w.plus(step).toFixed()),waccStep:ratePercent(step.toFixed()),growthStart:ratePercent(g.minus(gstep).toFixed()),growthEnd:ratePercent(g.plus(gstep).toFixed()),growthStep:ratePercent(gstep.toFixed())};
}

export const columnValues=(r:SensitivityResult)=>r.exit_ev_ebit_multiple_values??r.terminal_growth_values!;

/** Five diagnostic display points, preserving full spans without silent clamps. */
export function reviewGrid(draft:Draft):GridSettings{
 const exit=methodOf(draft)==='exit_multiple',w=new D(draft.rates.wacc),t=new D(exit?draft.rates.exit_ev_ebit_multiple:draft.rates.terminal_growth),span=new D(exit?'2':'0.5');
 if(!w.isFinite()||!t.isFinite())throw new InputErrors({waccStart:'Enter complete active operands first.'});
 return {waccStart:w.minus(1).toFixed(),waccEnd:w.plus(1).toFixed(),waccStep:'0.5',growthStart:t.minus(span).toFixed(),growthEnd:t.plus(span).toFixed(),growthStep:span.div(2).toFixed()};
}
