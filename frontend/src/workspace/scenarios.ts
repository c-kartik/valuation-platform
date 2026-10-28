/** Complete investor scenario envelope; no financial calculations or implicit inheritance. */
import {buildRequest,entryErrors,InputErrors} from '../model';
import type {Draft,Errors,InvestorDoc,InvestorEquityDoc,Result} from '../model';
import {buildEquityRequest,equityErrors} from '../equity';
import type {EquityDraft} from '../equity';
export const labels=['Bear','Base','Bull'] as const;
export type Label=typeof labels[number];
export type ScenarioDoc={schema_version:'investor-scenario-set-v1';scenario_set_name:string;scenarios:{label:Label;analytical_date:string;information_cutoff:string;case:InvestorDoc|InvestorEquityDoc}[]};
export type ScenarioResult={schema_version:string;scenario_set_name:string;submitted_inputs:ScenarioDoc;scenarios:{label:Label;analytical_date:string;information_cutoff:string;result:Result}[];limitations:string[]};
export function requestFor(draft:Draft,base:Draft,bridge:EquityDraft,equity:boolean):InvestorDoc|InvestorEquityDoc{
 const doc=buildRequest(draft);
 if(!equity)return doc;
 // Complete shared bridge, including review metadata, built once from Base context.
 const sharedContext={...draft,doc:{...draft.doc,preparation:{...draft.doc.preparation,timestamp_utc:base.doc.preparation.timestamp_utc}}};
 const full=buildEquityRequest(sharedContext,bridge);
 return {...full,preparation:doc.preparation};
}
export function scenarioRequest(cases:Partial<Record<Label,{draft:Draft}>>,bridge:EquityDraft,cutoff:string,equity:boolean):ScenarioDoc{
 const errors:Errors={};
 for(const label of labels){const c=cases[label];if(!c)errors[label]='Create this case explicitly from Base.';else for(const [key,value]of Object.entries(entryErrors(c.draft)))errors[`${label}.${key}`]=value;}
 if(!cutoff)errors.information_cutoff='Enter a shared information-cutoff date; this declaration is not verified source availability.';
 if(equity)for(const [key,value]of Object.entries(equityErrors(bridge,cases.Base!.draft.doc.anchor.annual_end)))errors[`bridge.${key}`]=value;
 if(Object.keys(errors).length)throw new InputErrors(errors);
 const base=cases.Base!.draft;
 return {schema_version:'investor-scenario-set-v1',scenario_set_name:`${base.doc.case_name} · Bear/Base/Bull`,scenarios:labels.map(label=>({label,analytical_date:base.doc.anchor.annual_end,information_cutoff:cutoff,case:requestFor(cases[label]!.draft,base,bridge,equity)}))};
}

export function sameSnapshot(a:unknown,b:unknown):boolean{
 const canonical=(v:unknown):string=>JSON.stringify(v&&typeof v==='object'?Array.isArray(v)?v.map(x=>JSON.parse(canonical(x))):Object.fromEntries(Object.entries(v).sort(([a],[b])=>a.localeCompare(b)).map(([k,x])=>[k,JSON.parse(canonical(x))])):v);
 return canonical(a)===canonical(b);
}
