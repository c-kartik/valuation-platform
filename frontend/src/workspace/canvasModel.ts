import {annual,terminal,annualPath,annualState,percentageToFraction,samePercentage,displayPath} from '../model';
import type {AnnualKey,Draft} from '../model';
import {percentage} from '../presentation';
import type {CaseState} from './useWorkspace';

export const editorSections=['Growth','Operating margin','Cash-flow assumptions','Discount rate','Long-term assumptions','Cash, debt and shares'] as const;
export type EditorSection=typeof editorSections[number];
export const shortLabels:Record<AnnualKey,string>={revenue_growth:'Revenue growth',operating_margin:'Operating margin',forecast_tax_rate:'Operating tax rate',d_and_a_percent_revenue:'D&A / revenue',capex_percent_revenue:'Operating investment / revenue',change_in_operating_nwc_percent_revenue:'Working-capital cash needs / revenue'};
export const help:Record<AnnualKey,string>={
 revenue_growth:'Annual growth compounds from the reported revenue anchor. Historical growth is context, not a forecast.',
 operating_margin:'EBIT / revenue. Includes SBC, operating-lease service costs and expense-aligned depreciation once.',
 forecast_tax_rate:'Tax on positive operating profit. Operating losses receive no immediate tax benefit.',
 d_and_a_percent_revenue:'Expense-aligned D&A / full forecast revenue. Include finance-asset depreciation once; historical CFO proxies may be incomplete.',
 capex_percent_revenue:'Cash PP&E plus non-overlapping new finance-leased operating assets / revenue. Exclude finance principal and duplicate capital-creditor settlements.',
 change_in_operating_nwc_percent_revenue:'Cash requirement / full forecast revenue, not revenue growth. Positive uses cash; negative releases cash. Historical CFO movements are not automatic forecast inputs.',
};
export function sectionFor(path:string):EditorSection{
 if(path.startsWith('bridge.'))return 'Cash, debt and shares';
 if(path==='wacc')return 'Discount rate';
 if(path.startsWith('terminal')||path==='case_name'||path.startsWith('preparation.'))return 'Long-term assumptions';
 if(path.includes('revenue_growth'))return 'Growth';
 if(path.includes('operating_margin'))return 'Operating margin';
 return 'Cash-flow assumptions';
}
export function rateText(value:string):string{
 try{return percentageToFraction(value)===null?'Not entered':percentage(percentageToFraction(value));}catch{return 'Check input';}
}
export function annualSummary(draft:Draft,key:AnnualKey):string{
 const state=annualState(draft,key);
 if(state.missing===5)return 'Not entered';
 if(state.missing)return `${5-state.missing}/5 entered`;
 return state.varies?'Varies by year':rateText(state.value);
}
export function pathsFor(key:AnnualKey){return Array.from({length:5},(_,i)=>annualPath(key,i));}
export function inherited(label:string,c:CaseState,paths:string[]){return label!=='Base'&&paths.every(p=>!(c.overrides??[]).includes(p));}
export function scenarioDescription(label:string,c:CaseState,base:CaseState):string{
 if(label==='Base')return 'Your central working case';
 const differences=annual.filter(([key])=>pathsFor(key).some(p=>!samePercentage(c.draft.rates[p],base.draft.rates[p]))).map(([key])=>shortLabels[key]);
 if(['wacc','terminal_growth','exit_ev_ebit_multiple',...Object.keys(c.draft.rates).filter(p=>p.startsWith('terminal.'))].some(p=>!samePercentage(c.draft.rates[p],base.draft.rates[p])))differences.push('Valuation / long term');
 return differences.length?`${differences.join(', ')} differ from Base`:(c.overrides??[]).length?'Matches Base; some inputs fixed':'Matches Base · inherits changes';
}

export function inputName(draft:Draft,path:string):string{
 const p=displayPath(draft,path),key=p.startsWith('quick.')?p.slice(6):/^forecast_years\[(\d+)\]\.(.+)$/.exec(p)?.[2];
 if(key&&key in shortLabels){const index=/^forecast_years\[(\d+)\]/.exec(p)?.[1];return (index===undefined?'':(draft.doc.forecast_years[Number(index)]?.fiscal_year_label??'Annual')+' ')+shortLabels[key as AnnualKey];}
 if(p.startsWith('terminal.'))return terminal.find(([key])=>p==='terminal.'+key)?.[1]??'Terminal input';
 return p==='exit_ev_ebit_multiple'?'Year-five EV/EBIT':p==='wacc'?'WACC':p==='terminal_growth'?'Terminal growth':p==='case_name'?'Case name':p==='preparation.notes'?'Personal notes':p.startsWith('bridge.')?'Cash, debt and shares':'Case input';
}
