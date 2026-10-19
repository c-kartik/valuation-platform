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
export function chartPoints(values: string[]): {x:number; y:number}[] | null {
  try {
    if (values.length !== 5 || values.some(v => v.length > 1024)) return null;
    const amounts = values.map(v => new DisplayDecimal(v));
    if (amounts.some(v => !v.isFinite() || Math.abs(v.e) > 1000)) return null;
    const max = amounts.reduce((a,b) => a.gte(b.abs()) ? a : b.abs(), new DisplayDecimal('0'));
    return amounts.map((v,i) => {
      // This bounded conversion is for SVG coordinates ONLY; raw amounts stay strings.
      const normalized = max.isZero() ? 0 : v.div(max).toNumber();
      return {x:30+i*60, y:100-normalized*80};
    });
  } catch {return null;}
}
