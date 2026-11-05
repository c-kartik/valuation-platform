import {D,clone,number,keys,requireInput,text,day,same,numericPolicy,sum,type Doc} from './decimal';
import {validateBridge,runBridge} from './bridge';
export type EngineData={anchors:Doc;policies:Doc;metadata:Doc;routes?:Doc};
export const annualRates=['revenue_growth','operating_margin','forecast_tax_rate','d_and_a_percent_revenue','capex_percent_revenue','change_in_operating_nwc_percent_revenue'];
export const terminalRates=['operating_margin','operating_tax_rate','d_and_a_percent_revenue','investment_percent_revenue','working_capital_cash_requirement_percent_revenue'];
const timingNotice='Analytical t=0 at the anchor fiscal end using later-filed information; not a contemporaneous historical-information backtest or a current market-date valuation.';
const supported=['analyst-case-v1','analyst-case-v2','analyst-case-v3','analyst-case-v4','investor-case-v1','investor-case-v2','investor-case-v3','investor-case-v4'];
export function terminalMethod(raw:Doc,wacc:string){
 requireInput(raw&&typeof raw==='object','terminal_valuation: method-specific object required');
 if(raw.method==='exit_multiple'){keys(raw,['method','exit_ev_ebit_multiple'],'terminal_valuation');requireInput(number(raw.exit_ev_ebit_multiple,'exit_ev_ebit_multiple').gt(0),'exit_ev_ebit_multiple: positive multiple required');return;}
 keys(raw,['method','terminal_growth','terminal'],'terminal_valuation');requireInput(raw.method==='perpetual_growth','terminal_valuation: supported method required');
 const g=number(raw.terminal_growth,'terminal_growth');requireInput(g.gt(-1)&&g.lt(wacc),'terminal_growth: must be greater than -1 and less than WACC');
 keys(raw.terminal,terminalRates,'terminal');for(const k of terminalRates)number(raw.terminal[k],'terminal.'+k);
 number(raw.terminal.operating_tax_rate,'terminal.operating_tax_rate',0,1);number(raw.terminal.d_and_a_percent_revenue,'terminal.d_and_a_percent_revenue',0);number(raw.terminal.investment_percent_revenue,'terminal.investment_percent_revenue',0);
}
export function selectedMethod(doc:Doc):Doc{return doc.terminal_valuation??{method:'perpetual_growth',terminal_growth:doc.terminal_growth,terminal:doc.terminal};}
export function validateCase(doc:Doc,data:EngineData){
 requireInput(doc&&supported.includes(doc.schema_version),'case.schema_version: unsupported schema');
 const investor=doc.schema_version.startsWith('investor'),method=/v[34]$/.test(doc.schema_version),extended=doc.schema_version.endsWith('v4');
 const equity=doc.schema_version.endsWith('v2')||(method&&doc.calculation_scope==='EQUITY_PER_SHARE');
 keys(doc,['schema_version','case_name','input_basis',...(investor?['preparation']:['analyst','scope']),'limitations','conventions','anchor','forecast_years','wacc',...(method?['terminal_valuation','comparison_terminal_valuation']:['terminal_growth','terminal']),...(equity?['calculation_scope','bridge']:method?['calculation_scope']:[]),...(extended?['forecast_horizon']:[])],'case');
 text(doc.case_name,'case_name');if(!investor)text(doc.scope,'scope');
 requireInput(Array.isArray(doc.limitations)&&doc.limitations.length>0,'limitations: nonempty list required');doc.limitations.forEach((x:any)=>text(x,'limitations'));
 if(investor){keys(doc.preparation,['provenance','timestamp_utc','notes'],'preparation');requireInput(doc.preparation.provenance==='ANONYMOUS_INVESTOR','preparation: anonymous provenance required');requireInput(typeof doc.preparation.timestamp_utc==='string'&&/(Z|\+00:00)$/.test(doc.preparation.timestamp_utc)&&!isNaN(Date.parse(doc.preparation.timestamp_utc)),'preparation: UTC timestamp required');requireInput(doc.preparation.notes===null||(typeof doc.preparation.notes==='string'&&doc.preparation.notes.trim()&&doc.preparation.notes.length<=2048),'preparation.notes: invalid notes');}
 else {keys(doc.analyst,['author','timestamp_utc','rationale'],'analyst');Object.values(doc.analyst).forEach(v=>text(v,'analyst'));requireInput(/(Z|\+00:00)$/.test(doc.analyst.timestamp_utc)&&!isNaN(Date.parse(doc.analyst.timestamp_utc)),'analyst: UTC timestamp required');}
 keys(doc.conventions,['forecast','discounting'],'conventions');requireInput(['meta-base-fcff-v1','manual-fcff-v1'].includes(doc.conventions.forecast),'conventions.forecast: unsupported convention');
 keys(doc.anchor,['kind','cik','accession','form','annual_start','annual_end'],'anchor');
 const anchor=data.anchors[doc.anchor.kind];requireInput(anchor,'anchor.kind: no reviewed anchor available');
 for(const k of ['cik','accession','form','annual_start','annual_end'])requireInput(doc.anchor[k]===anchor[k],'anchor.'+k+': pinned identity mismatch; no automatic refresh');
 requireInput(doc.input_basis===(doc.anchor.kind==='synthetic-fixture-v1'?'SYNTHETIC_FIXTURE':'MANUAL_INPUT'),'input_basis: incorrect anchor basis');
 if(['googl-fy2025','aapl-fy2025'].includes(doc.anchor.kind)){requireInput(doc.conventions.forecast==='manual-fcff-v1','conventions.forecast: shared convention required');if(equity)requireInput(doc.bridge?.convention_version==='manual-equity-bridge-v1','bridge: shared convention required');}
 const horizon=extended?10:5;requireInput(!extended||doc.forecast_horizon===10,'forecast_horizon: v4 requires 10');
 requireInput(Array.isArray(doc.forecast_years)&&doc.forecast_years.length===horizon,'forecast_years: explicit ordered horizon required');
 const labels=new Set();for(const [i,y] of doc.forecast_years.entries()){
  keys(y,['period_index','fiscal_year_label',...annualRates],`forecast_years[${i}]`);requireInput(y.period_index===i+1,'forecast_years: consecutive indices required');text(y.fiscal_year_label,'fiscal_year_label');requireInput(!labels.has(y.fiscal_year_label),'forecast_years: unique labels required');labels.add(y.fiscal_year_label);
  annualRates.forEach(k=>number(y[k],`forecast_years[${i}].${k}`));number(y.revenue_growth,'revenue_growth',-1);number(y.forecast_tax_rate,'forecast_tax_rate',0,1);number(y.d_and_a_percent_revenue,'d_and_a_percent_revenue',0);number(y.capex_percent_revenue,'capex_percent_revenue',0);
 }
 requireInput(number(doc.wacc,'wacc').gt(0),'wacc: must be positive');const m=selectedMethod(doc);terminalMethod(m,doc.wacc);
 const exit=m.method==='exit_multiple';requireInput(doc.conventions.discounting===(exit?(extended?'fiscal-end-terminal-ev-ebit-v2':'fiscal-end-year-five-ev-ebit-v1'):'fiscal-end-annual-gordon-v1'),'conventions.discounting: incompatible convention');
 if(exit)requireInput(new D(doc.forecast_years[horizon-1].operating_margin).gt(0)&&doc.forecast_years.every((y:Doc)=>new D(y.revenue_growth).gt(-1)),'exit_ev_ebit_multiple: final-year EBIT must be positive');
 if(method){requireInput(['ENTERPRISE_VALUE','EQUITY_PER_SHARE'].includes(doc.calculation_scope),'calculation_scope: unsupported scope');const c=doc.comparison_terminal_valuation;requireInput(c===null||(c&&typeof c==='object'&&!Array.isArray(c)),'comparison_terminal_valuation: object or null required');if(c){const allowed=c.method==='exit_multiple'?['method','exit_ev_ebit_multiple']:['method','terminal_growth','terminal'];requireInput(Object.keys(c).every(k=>allowed.includes(k)),'comparison_terminal_valuation: unknown fields');if(c.terminal)requireInput(Object.keys(c.terminal).every(k=>terminalRates.includes(k)),'comparison terminal: unknown fields');}}
 if(equity){requireInput(doc.calculation_scope==='EQUITY_PER_SHARE','calculation_scope: equity required');validateBridge(doc.bridge,doc);}
}
export function operatingYear(index:number,label:string,revenue:any,r:Doc){
 const rev=new D(revenue),ebit=rev.times(r.operating_margin),tax=D.max(ebit,0).times(r.forecast_tax_rate??r.operating_tax_rate),nopat=ebit.minus(tax),da=rev.times(r.d_and_a_percent_revenue),investment=rev.times(r.capex_percent_revenue??r.investment_percent_revenue),wc=rev.times(r.change_in_operating_nwc_percent_revenue??r.working_capital_cash_requirement_percent_revenue);
 return {period_index:index,fiscal_year_label:label,revenue:rev.toString(),ebit:ebit.toString(),tax:tax.toString(),nopat:nopat.toString(),d_and_a:da.toString(),investment:investment.toString(),working_capital_cash_requirement:wc.toString(),fcff:nopat.plus(da).minus(investment).minus(wc).toString()};
}
export function valueStage(doc:Doc,anchor:Doc,method:Doc):Doc{
 const exit=method.method==='exit_multiple',n=doc.forecast_years.length,years:Doc[]=[];let revenue=new D(anchor.revenue);
 for(const y of doc.forecast_years){revenue=revenue.times(new D(1).plus(y.revenue_growth));years.push(operatingYear(y.period_index,y.fiscal_year_label,revenue,y));}
 if(exit&&!new D(years[n-1].ebit).gt(0))throw new Error(`exit_ev_ebit_multiple: exit multiple unsupported: year-${n} EBIT must be strictly positive`);
 const assumptions={schema_version:n===10?'2':'1',company_cik:doc.anchor.cik,anchor_accession_number:doc.anchor.accession,anchor_fiscal_end:doc.anchor.annual_end,forecast_years:clone(doc.forecast_years),wacc:new D(doc.wacc).toString(),...(!exit?{terminal_growth:new D(method.terminal_growth).toString()}:{})};
 for(const y of assumptions.forecast_years)for(const k of annualRates)y[k]=new D(y[k]).toString();
 const stageA={schema:'stage-a-forecast-v1',convention_version:doc.conventions.forecast,numeric_policy:numericPolicy,semantic_input_review:'NOT_ASSESSED_BY_CALCULATOR',anchor:clone(anchor),assumptions,years};
 const base=new D(1).plus(doc.wacc),discounted=years.map(y=>{const factor=new D(1).div(base.pow(y.period_index));return {period_index:y.period_index,fiscal_year_label:y.fiscal_year_label,fcff:y.fcff,discount_factor:factor.toString(),pv_fcff:new D(y.fcff).times(factor).toString()};});
 const terminal=exit?undefined:operatingYear(n+1,'Terminal year',revenue.times(new D(1).plus(method.terminal_growth)),method.terminal);
 const tv=exit?new D(years[n-1].ebit).times(method.exit_ev_ebit_multiple):new D(terminal!.fcff).div(new D(doc.wacc).minus(method.terminal_growth));
 const pv=tv.div(base.pow(n)),explicit=sum(discounted.map(y=>y.pv_fcff));
 return {schema:exit?'stage-b-exit-enterprise-value-v1':'stage-b-enterprise-value-v1',convention_version:exit?(n===5?'fiscal-end-year-five-ev-ebit-v1':'fiscal-end-terminal-ev-ebit-v2'):'fiscal-end-annual-gordon-v1',...(exit?{terminal_method:'exit_multiple'}:{}),numeric_policy:numericPolicy,timing:{analytical_t0:doc.anchor.annual_end,basis:'anchor_fiscal_end_analytical',annual_discount_exponents:Array.from({length:n},(_,i)=>i+1),terminal_value_discount_exponent:n,information_cutoff:'NOT_ESTABLISHED_BY_CALCULATOR',notice:timingNotice},semantic_input_review:'NOT_ASSESSED_BY_CALCULATOR',stage_a:stageA,
 ...(exit?{terminal_basis:{metric:'EBIT',definition:'Operating profit including SBC and operating-lease service costs; no earnings add-backs',period_index:n,fiscal_year_label:years[n-1].fiscal_year_label,[n===5?'year_five_ebit':'final_year_ebit']:years[n-1].ebit,wacc:new D(doc.wacc).toString(),exit_ev_ebit_multiple:new D(method.exit_ev_ebit_multiple).toString()}}:{terminal_assumptions:{...Object.fromEntries(terminalRates.map(k=>[k,new D(method.terminal[k]).toString()])),convention_version:doc.conventions.forecast},terminal}),
 years:discounted,terminal_value:tv.toString(),pv_terminal_value:pv.toString(),pv_explicit_fcff:explicit.toString(),enterprise_value:explicit.plus(pv).toString()};
}
export function runCase(doc:Doc,data:EngineData):Doc{
 validateCase(doc,data);const investor=doc.schema_version.startsWith('investor'),method=/v[34]$/.test(doc.schema_version),anchor=data.anchors[doc.anchor.kind],stage=valueStage(doc,anchor,selectedMethod(doc));
 const limitations=[...doc.limitations,investor?'Anonymous investor preparation; no verified identity or supplied investment rationale. Optional personal notes are not evidence or approval. Preparation timestamp is not a valuation date, information cutoff or evidence review. Forecast inputs are user-entered and not independently reviewed.':'Analyst identity, rationale and scope are submitted declarations, not authenticated approval.',`No economic consistency, evidence completeness or actual ${['meta-fy2025','synthetic-fixture-v1'].includes(doc.anchor.kind)?'META':'company'} execution approval is inferred.`,'Enterprise value only; no bridge/share inputs or automatic historical forecasts.'];
 if(!['meta-fy2025','synthetic-fixture-v1'].includes(doc.anchor.kind))limitations[limitations.length-2]='No economic consistency, evidence completeness or company execution approval is inferred.';
 const result:Doc={schema_version:investor?'investor-case-enterprise-value-v1':'analyst-case-enterprise-value-v1',case_name:doc.case_name,input_basis:doc.input_basis,submitted_inputs:clone(doc),semantic_input_review:'NOT_ASSESSED_BY_CALCULATOR',limitations,stage_b:stage};
 if(doc.bridge){result.stage_c=runBridge(stage,doc.bridge);result.calculation_scope='EQUITY_PER_SHARE';result.schema_version=doc.schema_version==='investor-case-v2'?'investor-case-equity-per-share-v1':'analyst-case-equity-per-share-v1';limitations.splice(-1,1,...result.stage_c.limitations);}
 if(method){
  result.schema_version=(investor?'investor':'analyst')+'-case-result-'+(doc.schema_version.endsWith('v4')?'v4':'v3');const selected=selectedMethod(doc).method;stage.terminal_method=selected;
  const comp:Doc={selected_method:selected,submitted_inputs:clone(doc),results:{[selected]:{status:'CURRENT',stage_b:stage}},ev_difference_exit_minus_perpetual:null};
  const implied=(b:Doc)=>new D(b.terminal_value).gt(0)&&new D(b.stage_a.years.at(-1).ebit).gt(0)?{value:new D(b.terminal_value).div(b.stage_a.years.at(-1).ebit).toString(),reason:null}:{value:null,reason:'Positive terminal value and final-year EBIT required'};
  const key=doc.forecast_years.length===5?'implied_year_five_ev_ebit':'implied_final_year_ev_ebit';if(selected==='perpetual_growth')comp[key]=implied(stage);
  const opposite=selected==='exit_multiple'?'perpetual_growth':'exit_multiple';
  try{const raw=doc.comparison_terminal_valuation;requireInput(raw?.method===opposite,'Opposite method inputs not supplied');terminalMethod(raw,doc.wacc);const other=valueStage(doc,anchor,raw);other.terminal_method=opposite;comp.results[opposite]={status:'CURRENT',stage_b:other};if(opposite==='perpetual_growth')comp[key]=implied(other);comp.ev_difference_exit_minus_perpetual=new D(comp.results.exit_multiple.stage_b.enterprise_value).minus(comp.results.perpetual_growth.stage_b.enterprise_value).toString();}
  catch(e){comp.results[opposite]={status:'AWAITING_INPUTS',reason:doc.comparison_terminal_valuation===null?'Case input errors:\n- Opposite method inputs not supplied':(e instanceof Error?e.message:'Invalid comparison inputs')};}
  result.terminal_comparison=comp;
 }
 return result;
}
