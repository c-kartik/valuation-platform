/** Editor percentage points only; never rewrite untouched financial operands. */
import Decimal from 'decimal.js';
import {percentageToFraction} from '../model';
const EditorDecimal=Decimal.clone({precision:160,rounding:Decimal.ROUND_HALF_EVEN});
export function editorPercent(value:string):string{
 try{return percentageToFraction(value)===null?value:new EditorDecimal(value.trim()).toFixed(2);}
 catch{return value;}
}
