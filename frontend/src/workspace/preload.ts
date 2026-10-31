/** Proposed-input adaptation only; no valuation math. */
import Decimal from 'decimal.js';
import {fractionToPercentage} from '../model';
import type {Draft,CaseDoc} from '../model';
const D=Decimal.clone({precision:80,rounding:Decimal.ROUND_HALF_EVEN});
export type EstimateField={value:string|null;status:string;classification:string[];basis:string;unit:string;rule:string;operands:Record<string,unknown>;sources:string[];periods:{start:string|null;end:string;published_at:string|null;available_at?:string}[];context_sources?:string[];context_role?:string;configuration_selected_at?:string;limitation:string};
export type PreloadProfile={schema_version:'preload-profile-v1';economic_hash:string;generated_at:string;economic:{issuer:{ticker:string;issuer:string;listing_class:string};anchor:CaseDoc['anchor'];anchor_revenue:string;dates:{model_origin:string;information_review:string;timing:string};fields:Record<string,EstimateField>;scenarios:Record<string,Record<string,string|null>>;policy:{version:string};configuration:Record<string,string|string[]|null>;configuration_provenance:Record<string,string>;sources:{id:string;title:string;url:string;published_at:string|null;retrieved_at:string;sha256:string;rights:string;observation_date:string|null}[];observations:unknown[];diagnostics:string[];optional_bridge:{status:string;reason:string}}};
export type PreloadState={profile?:PreloadProfile;candidate?:PreloadProfile;status:'loading'|'ready'|'failed';failure:string};
export function checkProfile(p:PreloadProfile,anchor:CaseDoc['anchor']):PreloadProfile{
 if(p?.schema_version!=='preload-profile-v1'||!p.economic_hash?.match(/^[a-f0-9]{64}$/)||p.economic?.anchor_revenue!=='402836000000'||Object.keys(anchor).some(k=>anchor[k as keyof typeof anchor]!==p.economic.anchor[k as keyof typeof anchor])||Object.keys(p.economic.fields).length!==38)throw Error('Starting estimate profile does not match this anchor.');
 for(const field of Object.values(p.economic.fields))if(field.value!==null&&!/^-?\d+(?:\.\d+)?$/.test(field.value))throw Error('Invalid exact estimate value.');
 return p;
}
export function generatedRates(profile:PreloadProfile,label:string){
 const values=profile.economic.scenarios[label]??profile.economic.scenarios.Base;
 return Object.fromEntries(Object.entries(values).map(([path,value])=>[path,profile.economic.fields[path]?.status==='STALE'?'':path==='exit_ev_ebit_multiple'?value??'':fractionToPercentage(value)]));
}
export function generatedDraft(draft:Draft,profile:PreloadProfile,label:string):Draft{
 const next=structuredClone(draft);next.rates=generatedRates(profile,label);next.replacements={};
 next.doc.case_name=`${profile.economic.issuer.ticker} starting estimate · ${label}`;
 next.doc.preparation.notes=`Starting-estimate provenance: proposed ${profile.economic.policy.version}; profile ${profile.economic_hash}; information reviewed ${profile.economic.dates.information_review}; fiscal-end ${profile.economic.dates.model_origin} using later information. Explicit configuration is AI-assisted analyst judgment, not user-supplied approved forecasts.`;
 next.doc.limitations=next.doc.limitations.filter(s=>!s.startsWith('Fiscal-end analytical')&&!s.startsWith('Revenue-only retained'));
 next.doc.limitations.push(profile.economic.dates.timing,...profile.economic.diagnostics);
 return next;
}
export function inheritedRate(profile:PreloadProfile|undefined,label:string,path:string,baseValue:string){
 if(!profile||!baseValue.trim()||label==='Base')return baseValue;
 const key=path.startsWith('forecast_years')&&path.endsWith('.revenue_growth')?'growth':path.startsWith('forecast_years')&&path.endsWith('.operating_margin')?'margin':path==='wacc'?'wacc':null;
 const offset=key?profile.economic.configuration[`${label.toLowerCase()}_${key}_offset`]:null;
 if(typeof offset!=='string')return baseValue;
 try{return new D(baseValue).plus(new D(offset).times(100)).toFixed();}catch{return baseValue;}
}
export function estimateRefreshRows(previous:PreloadProfile,candidate:PreloadProfile,active:Draft,overrides:string[],label='Base'){
 return Object.keys(candidate.economic.fields).map(path=>({path,previous:previous.economic.scenarios[label]?.[path]??null,candidate:candidate.economic.scenarios[label]?.[path]??null,active:active.rates[path]??'',overridden:overrides.includes(path)}));
}
export function applyEstimates(draft:Draft,profile:PreloadProfile,label:string,overrides:string[]):Draft{
 const next=generatedDraft(draft,profile,label);
 for(const path of overrides)next.rates[path]=draft.rates[path];
 // Preserve unapplied replacement proposals; refresh must not flatten annual intent.
 next.replacements=structuredClone(draft.replacements);next.terminalMethod=draft.terminalMethod;
 const personal=(draft.doc.preparation.notes??'').replace(/^Starting-estimate provenance:[^\n]*(?:\n)?/,'').replace(/^Proposed [^\n]*not user-supplied approved forecasts\./,'').trim();
 if(personal)next.doc.preparation.notes+='\n'+personal;
 return next;
}
/** Diagnostic input generation only; unlike legacy preview, never narrows/clamps offsets. */
export function profileGrid(draft:Draft,profile:PreloadProfile):import('./sensitivity').GridSettings{
 const config=profile.economic.configuration,exit=draft.terminalMethod==='exit_multiple';
 const w=new D(draft.rates.wacc),t=new D(exit?draft.rates.exit_ev_ebit_multiple:draft.rates.terminal_growth);
 const ws=new D(String(config.sensitivity_wacc_offset)).times(100),ts=new D(String(config[exit?'sensitivity_multiple_offset':'sensitivity_growth_offset'])).times(exit?1:100);
 if(!w.isFinite()||!t.isFinite()||!ws.gt(0)||!ts.gt(0))throw Error('Available active operands and configured offsets required.');
 return {waccStart:w.minus(ws).toFixed(),waccEnd:w.plus(ws).toFixed(),waccStep:ws.div(2).toFixed(),growthStart:t.minus(ts).toFixed(),growthEnd:t.plus(ts).toFixed(),growthStep:ts.div(2).toFixed()};
}
