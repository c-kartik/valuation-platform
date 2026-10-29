/** Display-only Decimal domains. Clean steps: 1, 2, 2.5, 5, 10 × powers of ten.
 * Domains include zero and every value, round outwards, and use one shared scale
 * per compared metric. Tick precision follows the exact step in the display unit.
 * Only normalized, bounded plot coordinates become JS numbers; inputs stay exact.
 */
import Decimal from 'decimal.js';
const D=Decimal.clone({precision:220,rounding:Decimal.ROUND_HALF_EVEN});
export function financialAxis(values:string[],unit='1000000000'){
 if(values.some(v=>v.length>1024))throw Error('Chart presentation budget exceeded');
 const numbers=values.map(v=>new D(v));if(numbers.some(v=>!v.isFinite()))throw Error('Finite chart values required');if(numbers.some(v=>Math.abs(v.e)>1000))throw Error('Chart presentation budget exceeded');
 const min=numbers.reduce((a,b)=>D.min(a,b),new D(0)),max=numbers.reduce((a,b)=>D.max(a,b),new D(0));
 const span=max.minus(min),raw=(span.isZero()?new D(unit):span).div(4),power=new D(10).pow(raw.e),normalized=raw.div(power);
 const step=new D(['1','2','2.5','5','10'].find(v=>normalized.lte(v))!).times(power);
 const lower=min.div(step).floor().times(step),upper=(span.isZero()?new D(unit):max).div(step).ceil().times(step),range=upper.minus(lower);
 let multiplier=new D(1),places=step.div(unit).decimalPlaces();
 const format=(v:string)=>{const [whole,fraction]=new D(v).div(unit).div(multiplier).toFixed(places).split('.');return whole.replace(/\B(?=(\d{3})+(?!\d))/g,',')+(fraction?'.'+fraction:'');};
 // Extreme scales get one explicit, wrapping decimal multiplier, never repeated
 // scientific labels, clipped digits or tiny values rounded to zero.
 if(Math.max(format(lower.toFixed()).length,format(upper.toFixed()).length)>14){multiplier=new D(10).pow(step.div(unit).e);places=step.div(unit).div(multiplier).decimalPlaces();}
 const label=(v:string)=>format(v),scaleNote=multiplier.eq(1)?'':`Axis tick labels × ${multiplier.toFixed()} in the stated unit.`;
 const ticks:string[]=[];for(let v=lower;v.lte(upper);v=v.plus(step)){if(ticks.length>12)throw Error('Chart tick budget exceeded');ticks.push(v.toFixed());}
 return {scaleNote,lower:lower.toFixed(),upper:upper.toFixed(),step:step.toFixed(),ticks,label,position:(v:string)=>new D(v).minus(lower).div(range).toNumber()};
}
