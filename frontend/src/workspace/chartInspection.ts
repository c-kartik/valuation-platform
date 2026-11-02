/** Transient display state only. Never submitted as a valuation input. */
import Decimal from 'decimal.js';
import type {Result} from '../model';
import {percentage} from '../presentation';
export type ChartInspection='revenue'|'margin'|'cash'|'period'|'discount'|'terminal';
const D=Decimal.clone({precision:220,rounding:Decimal.ROUND_HALF_EVEN});
/** Read the matching submitted assumption, not an unsaved draft or a historical proxy. */
export function submittedMargins(result:Result){
 return result.stage_b.stage_a.years.map(year=>{
  const label=String(year.fiscal_year_label),value=result.submitted_inputs.forecast_years.find(y=>y.fiscal_year_label===label)?.operating_margin;
  try{if(value===null||value===undefined||value.length>1024)throw Error();const d=new D(value);if(!d.isFinite()||Math.abs(d.e)>1000)throw Error();return {label,value:d.toFixed()};}
  catch{return {label,value:null};}
 });
}

/** Bound direct chart labels while leaving full exact percentages in titles. */
export function marginCaption(value:string){const label=percentage(value);return label.length>12?new D(value).times(100).toExponential(3)+'%':label;}
