import {D,clone,InputError,requireInput,type Doc} from './decimal';
import {runCase,validateCase,type EngineData} from './case';
import {runFcfe,validateFcfe} from './fcfe';
import {runAnalyst} from './analyst';
import {runScenarios,validateScenarios} from './scenarios';
import {runSensitivity,validateSensitivity} from './sensitivity';
import {runReverse,validateReverse} from './reverse';

export function checkBudget(value:unknown){
 const serialized=JSON.stringify(value);requireInput(typeof serialized==='string'&&new TextEncoder().encode(serialized).length<=262144,'request: exceeds input size limit');let nodes=0;
 function walk(v:any,depth:number,field=''){
  requireInput(++nodes<=4096&&depth<=24,'request: exceeds structure limit');
  if(typeof v==='number')requireInput(Number.isSafeInteger(v)&&Math.abs(v)<=1e12,'request: bounded integer required; use decimal strings for financial amounts');
  if(typeof v==='string'){
   const cap=['rationale','scope'].includes(field)?4096:field.endsWith('_id')||['accession','schema_version','kind','origin','role','unit','class_id'].includes(field)?128:field.endsWith('_references')?1024:2048;requireInput(v.length<=cap,'request: text exceeds size limit');
   if(/^-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?$/.test(v)){
    const [m,e='0']=v.split(/[eE]/),digits=m.replace(/[-.]/g,'').replace(/^0+/,''),exponent=Number(e)-(m.split('.')[1]?.length??0),n=new D(v);
    requireInput(v.length<=128&&digits.length<=64&&Math.abs(Number(e))<=100&&Math.abs(exponent)<=100&&Math.abs(n.e)<=100,'request: numeric budget is 64 digits and exponent magnitude at most 100');
   }
  }
  if(Array.isArray(v)){const cap=field==='components'||field.endsWith('_references')||field==='population_ids'?64:128;requireInput(v.length<=cap,'request: array too large');v.forEach(x=>walk(x,depth+1,field));}
  else if(v&&typeof v==='object'){requireInput(Object.getPrototypeOf(v)===Object.prototype||Object.getPrototypeOf(v)===null,'request: plain JSON objects required');requireInput(Object.keys(v).length<=64,'request: object too large');for(const [k,x] of Object.entries(v)){requireInput(k.length<=128&&!['__proto__','constructor','prototype'].includes(k),'request: unsafe key');walk(x,depth+1,k);}}
 }
 walk(value,0);
}
function runReview(doc:Doc,data:EngineData){
 const result=runCase(doc,data),a=result.stage_b.stage_a,start=new D(a.anchor.revenue),end=new D(a.years.at(-1).revenue),forecastCagr=start.gt(0)&&end.gte(0)?end.div(start).pow(new D(1).div(a.years.length)).minus(1).toString():null;
 const reasons:string[]=[];if(a.years.length!==5)reasons.push('UNSUPPORTED_REVERSE_HORIZON: certified market-implied growth remains five-year only.');if(result.stage_b.terminal_method==='exit_multiple')reasons.push('UNSUPPORTED_TERMINAL_METHOD: market-implied growth supports a separate explicit perpetual-growth analysis only.');
 reasons.push(doc.anchor.kind==='synthetic-fixture-v1'?'No market reference for synthetic examples.':'Opening-price reference unavailable in browser mode; no live market feed is configured.');if(!doc.bridge)reasons.push('Complete the dated cash, claims and share bridge to reconcile market equity to model EV.');
 return {schema_version:'investor-review-result-v1',result,review:{...clone(data.metadata.review),schema_version:'investor-market-review-v1',status:'UNAVAILABLE',reasons,market:null,model_ev:result.stage_b.enterprise_value,forecast_cagr:forecastCagr,market_cap:null,market_implied_ev:null,ev_relative_difference:null,market_implied_growth:null,growth_gap_percentage_points:null,reverse:null,equity_difference:null,per_share_difference:null}};
}
export function runRequest(path:string,body:Doc,data:EngineData):Doc{
 checkBudget(body);requireInput(body&&typeof body==='object'&&!Array.isArray(body),'request: JSON object required');const routes:Record<string,[(doc:Doc,data:EngineData)=>any,(doc:Doc,data:EngineData)=>Doc]>={cases:[validateCase,runCase],fcfe:[validateFcfe,runFcfe],scenarios:[validateScenarios,runScenarios],sensitivity:[validateSensitivity,runSensitivity],reverse:[validateReverse,runReverse]};
 if(path==='/api/v1/apple/analyst/run'||path==='/api/v1/analyst/run')return runAnalyst(body,data);
 if(path==='/api/v1/review/run')return runReview(body,data);
 const match=/^\/api\/v1\/(cases|fcfe|scenarios|sensitivity|reverse)\/(validate|run)$/.exec(path);requireInput(match,'Unsupported browser calculation route');const [validate,run]=routes[match[1]];
 if(match[2]==='validate'){
  const parsed=validate(body,data),selected=match[1]==='cases'?body:match[1]==='scenarios'?body.scenarios[0].case:parsed?.case;
  return {status:'valid',calculation_performed:false,...(match[1]!=='fcfe'?{calculation_scope:selected.bridge?'EQUITY_PER_SHARE':'ENTERPRISE_VALUE'}:{}),semantic_input_review:'NOT_ASSESSED_BY_CALCULATOR'};
 }
 const result=run(body,data);requireInput(new TextEncoder().encode(JSON.stringify(result)).length<=2097152,'result: exceeds output limit');return result;
}
