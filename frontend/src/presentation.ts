/** Display-only arithmetic. Nothing here produces or edits a financial operand. */
import Decimal from 'decimal.js';
const DisplayDecimal = Decimal.clone({precision:220, rounding:Decimal.ROUND_HALF_EVEN});
// Match the CLI summary's precision-50 HALF_EVEN division and percentage display.
const RatioDecimal = DisplayDecimal.clone({precision:50});
export function terminalContribution(pv: string, ev: string): {text: string; note: string} {
  const value = new RatioDecimal(ev);
  if (value.isZero()) return {text:'Undefined', note:'EV is zero, so terminal PV / EV is undefined.'};
  const ratio = new RatioDecimal(pv).div(value);
  const notes: string[] = [];
  if (ratio.lt(0) || ratio.gt(1)) notes.push(`Contribution ${ratio.lt(0) ? 'is negative' : 'exceeds 100%'} before rounding; offsetting cash-flow PVs are preserved, not clamped.`);
  if (value.lt(0)) notes.push('EV is negative; this is an arithmetic ratio, not a positive value allocation.');
  return {text:ratio.times('100').toFixed(2)+'%', note:notes.join(' ') || 'Discounted terminal value / enterprise value. This measures terminal dependence, not economic approval.'};
}
export function chartPoints(values: string[], sharedMagnitude?:string): {x:number; y:number}[] | null {
  try {
    if (values.length !== 5 || values.some(v => v.length > 1024)) return null;
    const amounts = values.map(v => new DisplayDecimal(v));
    if (amounts.some(v => !v.isFinite() || Math.abs(v.e) > 1000)) return null;
    const max = amounts.reduce((a,b) => a.gte(b.abs()) ? a : b.abs(), new DisplayDecimal(sharedMagnitude??'0'));
    return amounts.map((v,i) => {
      // This bounded conversion is for SVG coordinates ONLY; raw amounts stay strings.
      const normalized = max.isZero() ? 0 : v.div(max).toNumber();
      return {x:30+i*60, y:100-normalized*80};
    });
  } catch {return null;}
}

/** Readable USD scale; exact inputs/results remain untouched in the trace. */
export function readableMoney(raw: string): string {
  const value = new DisplayDecimal(raw);
  const magnitude = value.abs();
  const [scale,suffix] = magnitude.gte('1000000000000') ? ['1000000000000','tn'] : magnitude.gte('1000000000') ? ['1000000000','bn'] : magnitude.gte('1000000') ? ['1000000','m'] : ['1',''];
  const scaled = value.div(scale);
  const rounded = !scaled.isZero() && scaled.abs().lt("0.005") ? scaled.toSignificantDigits(3).toFixed() : scaled.toFixed(2);
  const [whole,fraction] = rounded.split('.');
  return `${value.isNegative() && !value.isZero() ? '−' : ''}$${whole.replace('-','').replace(/\B(?=(\d{3})+(?!\d))/g,',')}${fraction === undefined ? '' : '.'+fraction}${suffix}`;
}
/** Display wording only: original qualifications remain in submitted/full traces. */
export function readableLimitation(line: string): string {
  return line
    .replace('Actual-input review, operating/tax/investment/venture scope and execution remain pending; see docs/phase2-meta-base-input-review.md.', 'Operating, tax, investment and venture assumptions still require review before an investment case can be established.')
    .replace('No bridge/share intake;', 'Cash/debt/share adjustments are excluded;')
    .replace('Revenue-only retained historical binding;', 'Historical data establishes revenue only;');
}

/** Exact share-unit display; a positive denominator must never round to zero. */
export function shareMillions(raw:string):string {
  const [whole,fraction]=new DisplayDecimal(raw).div('1000000').toFixed().split('.');
  return whole.replace(/\B(?=(\d{3})+(?!\d))/g,',')+(fraction===undefined?'':'.'+fraction);
}

/** Conditional display comparison; dates must equal the selected fiscal-end basis. */
export function comparisonDifference(value:string,price:string,date:string,analyticalDate:string):string|null {
 try{const p=new RatioDecimal(price);if(!price.trim()||!p.isFinite()||!p.gt(0)||date!==analyticalDate)return null;return new RatioDecimal(value).div(p).minus(1).times(100).toFixed(1);}catch{return null;}
}

/** Ordinary fractional percentages; preserve small nonzero observations. */
export function percentage(raw:string|null|undefined,points=false):string{
 if(raw===null||raw===undefined)return 'Undefined';
 const x=new DisplayDecimal(raw).times(points?'1':'100');
 const text=!x.isZero()&&x.abs().lt('0.005')?x.toSignificantDigits(3).toFixed():x.toFixed(2);
 return text+(points?' pp':'%');
}
export function exactDifference(value:string,base:string):string|null{const d=new RatioDecimal(base);return d.isZero()?null:new RatioDecimal(value).div(d).minus(1).toFixed();}

/** Fixed-unit tables/charts retain tiny nonzero values and bound long labels. */
export function fixedUnit(raw:string|null|undefined,scale='1',places=2):string{
 if(raw===null||raw===undefined)return 'Undefined';const x=new DisplayDecimal(raw).div(scale);
 if(x.abs().gte('1000000000'))return x.toExponential(places);
 if(!x.isZero()&&x.abs().lt(new DisplayDecimal(10).pow(-places).div(2)))return x.toSignificantDigits(3).toFixed();
 return displayFixed(x.toFixed(places));
}
function displayFixed(text:string){const [a,b]=text.split('.');return a.replace(/\B(?=(\d{3})+(?!\d))/g,',')+(b===undefined?'':'.'+b);}
