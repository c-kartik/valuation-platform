/** Narrow investor envelope; existing Python solver owns certification and arithmetic. */
import {entryErrors,InputErrors,percentageToFraction} from '../model';
import type {Draft,Errors,InvestorDoc,InvestorEquityDoc,Result} from '../model';
import {equityErrors,millionsToUnits} from '../equity';
import type {EquityDraft} from '../equity';
import {requestFor} from './scenarios';
export type ReverseDoc={schema_version:'investor-reverse-dcf-request-v1';reverse_dcf_name:string;source:{kind:'single_case';case:InvestorDoc|InvestorEquityDoc;analytical_date:string;information_cutoff:string};target:{metric:'ENTERPRISE_VALUE'|'VALUE_PER_SHARE';amount:string;unit:'USD'|'USD/share';date:string};growth_bounds:{lower:string;upper:string}};
export type ReverseResult={schema_version:string;submitted_inputs:ReverseDoc;selected_case:InvestorDoc|InvestorEquityDoc;selection:{analytical_date:string;information_cutoff:string};reference_result:Result;held_fixed:string;limitations:string[];status:'SUCCESS'|'UNREACHABLE_TARGET'|'FLAT_RESPONSE'|'UNIQUENESS_NOT_CERTIFIED'|'ITERATION_LIMIT'|'NUMERICAL_VERIFICATION_FAILED';reason:string;monotonicity:{direction:string;reason:string};numerical_policy:Record<string,unknown>;iterations:number;evaluations:number;final_bracket:{lower_growth:string;upper_growth:string;width:string}|null;solution:{constant_annual_growth:string;achieved_metric:string;signed_residual:string;absolute_residual:string;residual_tolerance:string;exact_endpoint:boolean;forward_result:Result}|null};
export type ReverseState={metric:'ENTERPRISE_VALUE'|'VALUE_PER_SHARE';amount:string;lower:string;upper:string;cutoff:string;targetDate:string;phase:'empty'|'incomplete'|'calculating'|'current'|'stale'|'failed';result:ReverseResult|null;errors:Errors;failure:string};
export const newReverse=():ReverseState=>({metric:'ENTERPRISE_VALUE',amount:'',lower:'',upper:'',cutoff:'',targetDate:'',phase:'empty',result:null,errors:{},failure:''});
export const staleReverse=(r:ReverseState):ReverseState=>({...r,phase:r.result?'stale':'incomplete',errors:{},failure:''});
export function reverseRequest(draft:Draft,base:Draft,bridge:EquityDraft,r:ReverseState):ReverseDoc{
 const errors=entryErrors(draft);for(const k of ['cutoff','targetDate'] as const)if(!r[k])errors[k]='Enter an explicit date; it is not a live quote or authenticated information availability.';
 if(r.metric==='VALUE_PER_SHARE')for(const[k,v]of Object.entries(equityErrors(bridge,draft.doc.anchor.annual_end)))errors['bridge.'+k]=v;
 let amount:string|null=null,lower:string|null=null,upper:string|null=null;
 try{amount=r.metric==='ENTERPRISE_VALUE'?millionsToUnits(r.amount):r.amount.trim();if(!amount||! /^-?(?:0|[1-9]\d*)(?:\.\d+)?$/.test(amount))errors.amount='Enter a decimal target in the labeled units; no commas, exponent or currency sign.';}catch{errors.amount='Enter a decimal target in USD millions.';}
 for(const k of ['lower','upper'] as const)try{const v=percentageToFraction(r[k]);if(v===null)errors[k]='Required percentage: 10 means 10%.';if(k==='lower')lower=v;else upper=v;}catch(e){errors[k]=(e as Error).message;}
 if(Object.keys(errors).length)throw new InputErrors(errors);
 return {schema_version:'investor-reverse-dcf-request-v1',reverse_dcf_name:draft.doc.case_name+' · conditional implied growth',source:{kind:'single_case',case:requestFor(draft,base,bridge,r.metric==='VALUE_PER_SHARE'),analytical_date:draft.doc.anchor.annual_end,information_cutoff:r.cutoff},target:{metric:r.metric,amount:amount!,unit:r.metric==='ENTERPRISE_VALUE'?'USD':'USD/share',date:r.targetDate},growth_bounds:{lower:lower!,upper:upper!}};
}
export const reverseStatuses:Record<ReverseResult['status'],string>={SUCCESS:'Certified solution',UNREACHABLE_TARGET:'Target outside supplied bounds',FLAT_RESPONSE:'Flat response; no unique growth',UNIQUENESS_NOT_CERTIFIED:'Uniqueness not certified',ITERATION_LIMIT:'Iteration limit; no solution',NUMERICAL_VERIFICATION_FAILED:'Numerical verification failed'};
