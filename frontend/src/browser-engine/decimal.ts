import Decimal from 'decimal.js';

// Isolated constructors: unrelated UI/global Decimal settings cannot change money.
export const D = Decimal.clone({precision: 50, rounding: Decimal.ROUND_HALF_EVEN, toExpNeg: -7, toExpPos: 50, maxE: 999999, minE: -999999});
export const SolverDecimal = D.clone({precision: 80});
export type Money = Decimal;
export type Doc = Record<string, any>;
export const clone = <T>(value:T):T => JSON.parse(JSON.stringify(value));
export const sum = (values:Decimal.Value[]) => values.reduce<Decimal>((a,b)=>a.plus(b),new D(0));
export const numericPolicy = {precision:50,rounding:'ROUND_HALF_EVEN',unit:'USD',intermediate_quantization:false};
export class InputError extends Error {
  code = 'invalid_case';
  constructor(public details:string[]){super('Review the indicated inputs.');}
}
export function requireInput(condition:unknown, message:string):asserts condition {if(!condition)throw new InputError([message]);}
export function number(value:unknown,path:string,min?:Decimal.Value,max?:Decimal.Value):Decimal {
  requireInput(typeof value==='string' && value.length<=128 && /^-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?$/.test(value),path+': supply a finite decimal string');
  const n=new D(value);
  requireInput(n.isFinite() && Math.abs(n.e)<=100,path+': decimal exponent outside allowed range');
  requireInput(min===undefined||n.gte(min),path+': below permitted minimum');
  requireInput(max===undefined||n.lte(max),path+': above permitted maximum');return n;
}
export function financingNumber(value:unknown,path:string,min?:Decimal.Value,max?:Decimal.Value):Decimal {
 requireInput(typeof value==='string'&&value.length<=128&&/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(value.trim()),path+': finite decimal string required');
 const n=new D(value.trim());requireInput(n.isFinite()&&Math.abs(n.e)<=100&&(min===undefined||n.gte(min))&&(max===undefined||n.lte(max)),path+': outside allowed range');return n;
}
export function keys(value:any,expected:string[],path:string){requireInput(value!==null&&typeof value==='object'&&!Array.isArray(value),path+': object required');requireInput(Object.keys(value).sort().join('|')===[...expected].sort().join('|'),path+': exact fields required: '+expected.join(', '));}
export function text(value:any,path:string){requireInput(typeof value==='string'&&value.trim().length>0,path+': nonempty text required');}
export function day(value:any,path:string){requireInput(typeof value==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(value)&&!Number.isNaN(Date.parse(value))&&new Date(value).toISOString().slice(0,10)===value,path+': YYYY-MM-DD required');}
export function refs(value:any,path:string,required=false){requireInput(Array.isArray(value)&&(!required||value.length>0),path+': explicit references required');value.forEach((v:any)=>text(v,path));requireInput(new Set(value).size===value.length,path+': repeated reference');}
export const same=(a:any,b:any):boolean=>{
 if(a===b)return true;if(!a||!b||typeof a!=='object'||typeof b!=='object')return false;
 const ak=Object.keys(a).sort(),bk=Object.keys(b).sort();return ak.join('|')===bk.join('|')&&ak.every(k=>same(a[k],b[k]));
};
