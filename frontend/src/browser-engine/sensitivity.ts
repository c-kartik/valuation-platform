import {D,clone,number,keys,requireInput,text,type Doc} from './decimal';
import {runCase,selectedMethod,type EngineData} from './case';
import {sourceCase} from './scenarios';
export function metrics(result:Doc):Doc{
 const b=result.stage_b,ev=new D(b.enterprise_value),exit=b.terminal_method==='exit_multiple';
 return {enterprise_value:b.enterprise_value,pv_explicit_fcff:b.pv_explicit_fcff,pv_terminal_value:b.pv_terminal_value,...(exit?{[b.years.length===5?'year_five_ebit':'final_year_ebit']:b.terminal_basis.year_five_ebit??b.terminal_basis.final_year_ebit}:{terminal_revenue:b.terminal.revenue,terminal_fcff:b.terminal.fcff}),terminal_value:b.terminal_value,terminal_contribution:ev.isZero()?null:new D(b.pv_terminal_value).div(ev).toString(),terminal_contribution_note:ev.isZero()?'undefined: EV is zero':'Signed terminal PV / EV; negative or >100% ratios are retained (offsetting PVs); negative EV is an arithmetic ratio.',equity_value:result.stage_c?.equity_value??null,value_per_share:result.stage_c?.value_per_share??null};
}
export function validateSensitivity(doc:Doc,data:EngineData){
 const exit=doc.schema_version==='investor-sensitivity-request-v3',axis=exit?'exit_ev_ebit_multiple_values':'terminal_growth_values';keys(doc,['schema_version','sensitivity_name','source','wacc_values',axis],'sensitivity');requireInput(['analyst-sensitivity-request-v1','investor-sensitivity-request-v1','investor-sensitivity-request-v2','investor-sensitivity-request-v3'].includes(doc.schema_version),'sensitivity: unsupported schema');text(doc.sensitivity_name,'sensitivity_name');
 const source=sourceCase(doc,data,['investor-sensitivity-request-v2','investor-sensitivity-request-v3'].includes(doc.schema_version));
 for(const k of ['wacc_values',axis]){requireInput(Array.isArray(doc[k])&&doc[k].length>=1&&doc[k].length<=11,k+': 1 to 11 explicit values required');doc[k].forEach((v:any,i:number)=>{const n=number(v,k);requireInput(k==='terminal_growth_values'?n.gt(-1):n.gt(0),k+': value outside range');if(i)requireInput(n.gt(doc[k][i-1]),k+': strictly increasing unique values required');});}
 requireInput((selectedMethod(source.case).method==='exit_multiple')===exit,'sensitivity: selected method and axis mismatch');requireInput(exit||new D(doc.wacc_values.at(-1)).gt(doc[axis][0]),'sensitivity: all cells invalid');return {exit,axis,...source};
}
export function runSensitivity(doc:Doc,data:EngineData):Doc{
 const {exit,axis,case:original,selection}=validateSensitivity(doc,data),reference=runCase(original,data),referenceMetrics=metrics(reference),changeKeys=original.bridge?['enterprise_value','equity_value','value_per_share']:['enterprise_value'];
 const cells=doc.wacc_values.map((wacc:string)=>doc[axis].map((g:string)=>{
  const cell:Doc={wacc:new D(wacc).toString(),[exit?'exit_ev_ebit_multiple':'terminal_growth']:new D(g).toString()};
  if(!exit&&new D(g).gte(wacc))return {...cell,status:'INVALID',reason:'terminal growth >= WACC',metrics:Object.fromEntries(Object.keys(referenceMetrics).map(k=>[k,null])),changes:null};
  const c=clone(original);c.wacc=wacc;if(exit)c.terminal_valuation.exit_ev_ebit_multiple=g;else if(c.terminal_valuation)c.terminal_valuation.terminal_growth=g;else c.terminal_growth=g;
  const m=metrics(runCase(c,data)),changes:Doc={};for(const k of changeKeys){const ref=new D(referenceMetrics[k]),delta=new D(m[k]).minus(ref);changes[k]={absolute:delta.toString(),fractional_change:ref.isZero()?null:delta.div(ref).toString(),note:ref.isZero()?'undefined: reference is zero':'absolute change / signed reference; fraction, not percent units'};}
  return {...cell,status:'VALID',reason:null,metrics:m,changes};
 }));
 return {schema_version:doc.schema_version.replace('-request-','-results-'),sensitivity_name:doc.sensitivity_name,submitted_inputs:clone(doc),selected_case:clone(original),selection,reference_result:reference,reference_metrics:referenceMetrics,wacc_values:doc.wacc_values.map((v:string)=>new D(v).toString()),[axis]:doc[axis].map((v:string)=>new D(v).toString()),cells,...clone(data.metadata.sensitivity[exit?'exit':'growth']),semantic_input_review:'NOT_ASSESSED_BY_CALCULATOR'};
}
