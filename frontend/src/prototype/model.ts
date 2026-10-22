import Decimal from 'decimal.js';
import raw from './fixtures.json';
export const D=Decimal.clone({precision:40,rounding:Decimal.ROUND_HALF_EVEN});
export const keys=['growth','margin','tax','da','investment','wc'] as const;
export type Key=typeof keys[number];
export type Rates=Record<Key,string>;
export type Inputs={annual:Rates[];terminal:Omit<Rates,'growth'>;wacc:string;g:string};
export type Year=Record<'revenue'|'ebit'|'tax'|'nopat'|'d_and_a'|'investment'|'working_capital_cash_requirement'|'fcff'|'pv_fcff'|'discount_factor',string>;
export type Illustration={years:Year[];ev:string;equity:string;perShare:string;explicitPV:string;terminalPV:string;terminalValue:string;terminalFCFF:string;terminalContribution:string};
export type Variant={profile:string;inputs:Inputs;result:Illustration};
export type ReverseRecord={profile:string;inputs:Inputs;metric:string;target:string;lower:string;upper:string;status:string;reason:string;growth:string|null;result:Illustration|null};
export const fixtures=raw as unknown as {profiles:Record<string,Inputs>;variants:Variant[];reverse:ReverseRecord[]};
export type Label='Base'|'Bear'|'Bull';
export const labels:Label[]=['Bear','Base','Bull'];
export type Case={inputs:Inputs;notes:string;shown?:{signature:string;variant:Variant;bridgeSignature:string}};
export type Bridge={enabled:boolean;assets:string;financing:string;claims:string;shares:string;date:string;basis:string;awards:string;coverage:boolean};
export const emptyBridge=():Bridge=>({enabled:false,assets:'',financing:'',claims:'',shares:'',date:'',basis:'',awards:'',coverage:false});
export const demoBridge=():Bridge=>({enabled:true,assets:'150',financing:'200',claims:'25',shares:'100',date:'2025-12-31',basis:'issued',awards:'omitted',coverage:true});
export const signature=(x:unknown)=>JSON.stringify(x);
export const enteredCount=(x:Inputs)=>[...x.annual.flatMap(y=>keys.map(k=>y[k])),...Object.values(x.terminal),x.wacc,x.g].filter(v=>v.trim()!=='').length;
export const fresh=(c:Case)=>c.shown?.signature===signature(c.inputs);
export const newCase=():Case=>({inputs:structuredClone(fixtures.profiles.steady),notes:''});
export function createScenario(cases:Partial<Record<Label,Case>>,label:Label){
 if(label==='Base'||cases[label])return cases;
 const base=cases.Base!;
 return {...cases,[label]:structuredClone(base)}; // No optimistic/pessimistic changes.
}
const canonical=(value:string)=>{try{return value.trim()===''?'UNSET':new D(value).toString();}catch{return 'INVALID';}};
const normalized=(x:Inputs,operatingOnly=false)=>signature([x.annual.map(y=>keys.map(k=>canonical(y[k]))),keys.filter(k=>k!=='growth').map(k=>canonical(x.terminal[k])),...(operatingOnly?[]:[canonical(x.wacc),canonical(x.g)])]);
export const sameInputs=(a:Inputs,b:Inputs)=>normalized(a)===normalized(b);
export const variantFor=(x:Inputs)=>fixtures.variants.find(v=>normalized(v.inputs)===normalized(x));
export const profileFor=(x:Inputs)=>Object.keys(fixtures.profiles).find(k=>normalized(fixtures.profiles[k],true)===normalized(x,true));
export function inputErrors(x:Inputs){
 const errors:Record<string,string>={};
 const check=(v:string,path:string,label:string,min?:number,max?:number)=>{
  if(!/^-?(?:\d+(?:\.\d*)?|\.\d+)$/.test(v.trim()))errors[path]=`Enter ${label} as a number; 10 means 10%.`;
  else if((min!==undefined&&new D(v).lt(min))||(max!==undefined&&new D(v).gt(max)))errors[path]=`${label} must be ${max!==undefined?`between ${min}% and ${max}%`:`at least ${min}%`}.`;
 };
 x.annual.forEach((y,i)=>keys.forEach(k=>check(y[k],`annual.${i}.${k}`,`FY${2026+i} ${names[k]}`,k==='growth'?-100:k==='tax'?0:undefined,k==='tax'?100:undefined)));
 Object.entries(x.terminal).forEach(([k,v])=>check(v,`terminal.${k}`,`Long-term ${names[k as Key]}`,k==='tax'?0:undefined,k==='tax'?100:undefined));
 check(x.wacc,'wacc','WACC',0);check(x.g,'g','Terminal growth',-100);
 if(!errors.wacc&&new D(x.wacc).lte(0))errors.wacc='WACC must be greater than 0%.';
 if(!errors.g&&new D(x.g).lte(-100))errors.g='Terminal growth must be greater than −100%.';
 if(!errors.g&&!errors.wacc&&new D(x.g).gte(x.wacc))errors.g='Terminal growth must be below WACC.';
 return errors;
}
export const names:Record<Key,string>={growth:'Revenue growth',margin:'Operating margin',tax:'Operating tax',da:'Expense D&A / revenue',investment:'Investment / revenue',wc:'Working-capital cash / revenue'};
export function bridgeErrors(b:Bridge){
 if(!b.enabled)return {};
 const errors:Record<string,string>={};
 for(const k of ['assets','financing','claims','shares'] as const){try{if(!b[k].trim()||!new D(b[k]).isFinite()||new D(b[k]).lt(0)||(k==='shares'&&new D(b[k]).isZero()))throw Error();}catch{errors[k]=k==='shares'?'Enter a positive share count.':'Enter a nonnegative amount; blank is not zero.';}}
 if(b.date!=='2025-12-31')errors.date='Use the analytical date, 2025-12-31.';
 if(!b.basis)errors.basis='Declare a share population.';
 if(!b.awards)errors.awards='Declare how existing awards are treated.';
 if(!b.coverage)errors.coverage='Review the scope and non-overlap declaration.';
 return errors;
}
export const bridgeMatches=(b:Bridge)=>signature(b)===signature(demoBridge());
export const perShareFresh=(c:Case,b:Bridge)=>fresh(c)&&bridgeMatches(b)&&c.shown?.bridgeSignature===signature(b);
export const num=(v:string|undefined,digits=1)=>v===undefined?'—':new D(v).toDecimalPlaces(digits).toNumber().toLocaleString('en-US',{minimumFractionDigits:digits,maximumFractionDigits:digits});
export const dollars=(v:string)=>'$'+num(v,2);
export const billions=(v:string)=>'$'+num(new D(v).div(1000).toString(),2)+'bn';
// Display-only comparison; never a valuation or solver.
export function priceDifference(value:string,price:string,date:string){
 try{if(date!=='2025-12-31'||!new D(price).isFinite()||!new D(price).gt(0))return null;return new D(value).div(price).minus(1).times(100).toFixed(1);}catch{return null;}
}
export const grids={standard:{w:['9','10','11'],g:['2.5','3','3.5'],settings:['9','11','1','2.5','3.5','0.5']},invalid:{w:['2','3','4'],g:['2','3','4'],settings:['2','4','1','2','4','1']}};
export const supportedGrid=(values:string[])=>Object.values(grids).find(g=>g.settings.every((v,i)=>canonical(v)===canonical(values[i])));
