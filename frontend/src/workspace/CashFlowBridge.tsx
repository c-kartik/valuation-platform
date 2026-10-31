import {useState} from 'react';
import type {Result} from '../model';
import {cashFlowConversion,readableMoney} from '../presentation';

/** Explanation of returned annual operands; pending drafts never run a JS forecast. */
export function CashFlowBridge({result,stale=false}:{result?:Result|null;stale?:boolean}){
 const years=result?.stage_b.stage_a.years??[],[selected,setSelected]=useState('');
 const year=years.find(y=>String(y.fiscal_year_label)===selected)??years.at(-1);
 if(!year)return <p className="cw-cash-flow-empty">Complete the assumptions and update valuation to see the profit-to-cash calculation. Conversion is a summary, not an additional input.</p>;
 const conversion=cashFlowConversion(String(year.fcff),String(year.ebit));
 const rows=[
  ['','Operating profit','ebit','Starting profit after operating expenses.'],
  ['−','Operating taxes','tax','Taxes attributable to operating profit.'],
  ['+','Depreciation & amortization','d_and_a','Noncash expenses added back once.'],
  ['−','Capital investment','investment','Cash PP&E and new financed operating assets.'],
  ['−','Additional working-capital cash','working_capital_cash_requirement','Cash tied up in daily operations; negative releases cash.'],
  ['=','FCFF','fcff','Cash available to lenders and shareholders.'],
 ];
 return <section className="cw-cash-flow-bridge" aria-label="Submitted profit-to-cash calculation"><div className="cw-cash-flow-heading"><div className="cw-cash-flow-year"><label htmlFor="model-editor-cash_flow_conversion">Calculation year</label><select id="model-editor-cash_flow_conversion" value={String(year.fiscal_year_label)} onChange={e=>setSelected(e.target.value)}>{years.map(y=><option key={String(y.fiscal_year_label)} value={String(y.fiscal_year_label)}>{String(y.fiscal_year_label)}</option>)}</select></div><div><span>Cash flow conversion</span><strong title={conversion.note}>{conversion.text}</strong><small>FCFF / operating profit</small></div></div><p>{stale?'Previous submitted calculation · stale.':'Last submitted calculation.'} Pending edits below are not included.</p><table><caption className="cw-sr-only">{String(year.fiscal_year_label)} profit-to-FCFF bridge · USD</caption><thead><tr><th>Calculation</th><th>Amount</th><th>Meaning</th></tr></thead><tbody>{rows.map(([sign,label,key,meaning])=><tr key={key}><th aria-label={(sign==='−'?'Subtract ':sign==='+'?'Add ':sign==='='?'Equals ':'')+label}><span aria-hidden="true">{sign}</span>{label}</th><td title={String(year[key])+' USD'}>{readableMoney(String(year[key]))}</td><td>{meaning}</td></tr>)}</tbody></table>{conversion.text==='Unavailable'&&<p>{conversion.note}</p>}</section>;
}
