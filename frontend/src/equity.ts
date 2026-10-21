/** Optional manual Stage C declarations. No bridge arithmetic is performed here. */
import {buildRequest,InputErrors} from './model';
import type {Draft,Errors,InvestorEquityDoc} from './model';
export const coverageOptions = {
 selected: 'Selected population only — no completeness claim',
 omitted: 'Selected population, plus explicit unbounded omissions',
} as const;
export const awards = {
 none: 'No existing awards in my stated population (unverified declaration)',
 omitted: 'Existing awards unresolved — omit provisionally',
 shares: 'Pre-anchor rights included in my adjusted shares; no duplicate service charge',
 claims: 'Pre-anchor rights included in other claims; no duplicate service charge',
} as const;
export type EquityDraft = {
 assets:string; financing:string; claims:string; shares:string; date:string;
 claimsTreatment:''|'amount'|'none'|'unassessed';
 assetsCoverage:''|'selected'|'omitted'; financingCoverage:''|'selected'|'omitted'; claimsCoverage:''|'selected'|'omitted';
 shareBasis:''|'issued'|'basic_equivalent'; classes:string;
 equivalence:''|'single_common_class'|'explicit_common_unit_equivalence';
 awards:''|keyof typeof awards; nonOverlap:boolean;
 overlapAssets:string; overlapFinancing:string; overlapClaims:string;
 alternativeAssets:string; alternativeFinancing:string; alternativeClaims:string;
};
export const emptyEquity = ():EquityDraft=>({assets:'',financing:'',claims:'',shares:'',date:'',claimsTreatment:'unassessed',assetsCoverage:'',financingCoverage:'',claimsCoverage:'',shareBasis:'',classes:'',equivalence:'',awards:'',nonOverlap:false,overlapAssets:'',overlapFinancing:'',overlapClaims:'',alternativeAssets:'',alternativeFinancing:'',alternativeClaims:''});
/** Exact textual shift to base USD/shares. Blank stays missing; never Number/float. */
export function millionsToUnits(raw:string):string|null {
 const text=raw.trim();if(!text)return null;
 const match=/^(-?)(\d*)(?:\.(\d*))?$/.exec(text);
 if(!match || (!match[2]&&!match[3]) || text.length>100)throw new Error('Enter a decimal amount in millions; no commas, currency symbols or exponents.');
 const [,sign,whole,fraction='']=match;const digits=whole+fraction,point=whole.length+6;
 const left=(digits.slice(0,point)+'0'.repeat(Math.max(0,point-digits.length))).replace(/^0+(?=\d)/,'')||'0';
 const right=digits.slice(point);return sign+left+(right?'.'+right:'');
}
export type EquityDoc=InvestorEquityDoc;
export function equityErrors(e:EquityDraft,anchorDate:string):Errors {
 const errors:Errors={};
 for(const key of ['assets','financing','shares',...(e.claimsTreatment==='amount'?['claims']:[])] as const){
  try {if(millionsToUnits(e[key as 'assets'])===null)errors[key]='Enter an explicit amount; blank is not zero.';}
  catch(error){errors[key]=(error as Error).message;}
 }
 if(!e.date)errors.date='Enter the share observation date.';
 else if(e.date!==anchorDate)errors.date=`Shares must match the fiscal-end analytical date ${anchorDate}.`;
 if(!['amount','none'].includes(e.claimsTreatment))errors.claimsTreatment='Assess other claims, enter an amount, or explicitly declare none identified within your scope.';
 for(const key of ['assetsCoverage','financingCoverage',...(e.claimsTreatment==='amount'?['claimsCoverage']:[])] as const)if(!e[key as 'assetsCoverage'])errors[key]='Choose a scoped coverage declaration; this is not verified completeness.';
 if(!e.shareBasis)errors.shareBasis='Choose issued or basic-equivalent shares.';
 if(!e.classes.trim())errors.classes='Name the included share class or classes.';
 if(!e.equivalence)errors.equivalence='Declare a single class or explicit economic equivalence.';
 if(!e.awards)errors.awards='Declare existing-award treatment; no automatic dilution or absence assumption.';
 if(e.awards==='shares'&&e.shareBasis!=='basic_equivalent')errors.shareBasis='Award-adjusted shares require the basic-equivalent basis.';
 if(e.awards==='claims'&&e.claimsTreatment!=='amount')errors.awards='An award claim requires an explicit other-claims amount.';
 if(!e.nonOverlap)errors.nonOverlap='Declare date, eligibility and non-overlap before calculating equity.';
 return errors;
}
export function buildEquityRequest(draft:Draft,e:EquityDraft):EquityDoc {
 const errors=equityErrors(e,draft.doc.anchor.annual_end);if(Object.keys(errors).length)throw new InputErrors(errors);
 const doc=buildRequest(draft), cik=doc.anchor.cik, date=doc.anchor.annual_end;
 const components:Record<string,unknown>[]=[], observations:Record<string,unknown>[]=[], coverage:Record<string,unknown>[]=[];
 const roles=[['assets','ELIGIBLE_ASSET','Eligible cash & investments','assetsCoverage','overlapAssets','alternativeAssets'],['financing','FINANCING_CLAIM','Debt & financing obligations','financingCoverage','overlapFinancing','alternativeFinancing'],['claims','OTHER_EQUITY_CLAIM','Other claims','claimsCoverage','overlapClaims','alternativeClaims']] as const;
 function omission(id:string,role:string,rationale:string){observations.push({observation_id:id,company_cik:cik,role,disposition:'OMISSION',population_id:id,value:null,as_of:null,unit:'USD',precision:null,origin:'unavailable',source_references:[],decision_references:[`manual:${id}`],rationale});}
 for(const [key,role,label,choice,overlap,alternative] of roles){
  const omissions:string[]=[], populations:string[]=[];
  if(key!=='claims'||e.claimsTreatment==='amount'){
   populations.push(`manual:${key}`);
   const refs=(raw:string)=>raw.split(',').map(s=>s.trim()).filter(Boolean);
   components.push({component_id:key,company_cik:cik,role,amount:millionsToUnits(e[key]),as_of:date,population_id:`manual:${key}`,origin:'manual_input',precision:'INF',source_references:[`unverified:user-entry:${key}`],decision_references:[`manual:${key}:selected`],rationale:`User-entered ${label}, as of ${date}; manual unverified aggregate, not a reported fact or approval.`,overlap_references:refs(e[overlap]),alternative_references:refs(e[alternative]),overlaps_forecast:false,unit:'USD',scale:1});
  }
  if(e[choice]==='omitted'||(key==='claims'&&e.claimsTreatment==='none')){
   const id=`omitted-${key}`;omissions.push(id);
   omission(id,role,key==='claims'&&e.claimsTreatment==='none'?'User declares none identified within the stated scope; unverified, not proof of absence. Unidentified claims remain unbounded, not zero.':`User explicitly omits additional ${label} populations; amount unknown and unbounded, not zero.`);
  }
  if(key==='claims'&&e.awards==='omitted'){omissions.push('omitted-awards');omission('omitted-awards',role,'Existing pre-anchor award rights are unresolved and explicitly omitted. Future service SBC stays in operating margins; omitted rights may be material and unbounded.');}
  const declaration=key==='claims'&&e.claimsTreatment==='none'?'None identified within my stated scope; unverified':coverageOptions[e[choice] as keyof typeof coverageOptions];
  coverage.push({role,population_ids:populations,omission_references:omissions,review:{author:'Anonymous investor (unverified declaration)',timestamp_utc:doc.preparation.timestamp_utc,rationale:`User-selected declaration: ${declaration}. Not an authenticated review or financial approval.`},decision_references:[`manual:coverage:${key}`]});
 }
 const classId=`${e.shareBasis}: ${e.classes.trim()}`;
 return {...doc,limitations:[...doc.limitations,'The optional equity bridge is a separate manual, unverified extension. EV-only template bridge exclusions describe historical/source scope; they do not select or approve these manual assets, claims or shares.'],schema_version:'investor-case-v2',calculation_scope:'EQUITY_PER_SHARE',bridge:{components,observations,coverage,shares:{company_cik:cik,shares:millionsToUnits(e.shares),observation_date:e.date,class_id:classId,equivalence_convention:e.equivalence,award_policy:'sbc_expensed_no_duplicate_service_charge_v1',award_policy_references:[`manual:awards:${e.awards}: ${awards[e.awards as keyof typeof awards]}`],source_references:['unverified:user-entry:shares'],decision_references:[`manual:shares:${e.shareBasis}`],precision:'INF',rationale:`User-selected ${e.shareBasis==='issued'?'issued':'basic-equivalent'} population: ${e.classes.trim()}. ${awards[e.awards as keyof typeof awards]}. SBC service cost remains in margins once; no automatic dilution or proceeds.`,unit:'shares',scale:1},input_basis:doc.input_basis,valuation_class_id:classId,unresolved_requirements:[],convention_version:'manual-equity-bridge-v1'}};
}
