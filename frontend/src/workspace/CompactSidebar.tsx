import {useRef} from 'react';
import type {ChartInspection} from './chartInspection';
import {annualState,methodOf} from '../model';
import type {Draft,Result} from '../model';
import {cashFlowConversion} from '../presentation';
import {inputPercent} from './ActiveAssumptions';
export function CompactSidebar({draft,result,stale=false,edit,sources,inspect,inspection=null}:{draft:Draft;result?:Result|null;stale?:boolean;edit:(path?:string)=>void;sources:()=>void;inspect?:(value:ChartInspection|null)=>void;inspection?:ChartInspection|null}){
 const pointer=useRef<ChartInspection|null>(null),focused=useRef<ChartInspection|null>(null);
 function preview(key:ChartInspection){return {'data-chart-inspection':key,'data-active':inspection===key||undefined,
  onMouseEnter:()=>{pointer.current=key;inspect?.(key);},onMouseLeave:()=>{pointer.current=null;inspect?.(focused.current);},
  onFocus:()=>{focused.current=key;inspect?.(key);},onBlur:()=>{focused.current=null;inspect?.(pointer.current);}};}
 function path(key:Parameters<typeof annualState>[1]){const row=annualState(draft,key);return row.varies?`${inputPercent(draft.rates[`forecast_years[0].${key}`])} → ${inputPercent(draft.rates[`forecast_years[${draft.doc.forecast_years.length-1}].${key}`])}`:row.value.trim()?inputPercent(row.value):'Unset';}
 function row(name:string,value:string,key:ChartInspection,focus?:string){return <button className="cw-summary-row" {...preview(key)} onClick={()=>edit(focus)}><span>{name}</span><strong>{value}<i aria-hidden="true"> ›</i></strong></button>;}
 const exit=methodOf(draft)==='exit_multiple',years=draft.doc.forecast_years,last=result?.stage_b.stage_a.years.at(-1),conversion=last?cashFlowConversion(String(last.fcff),String(last.ebit)):undefined;
 return <aside className="cw-sidebar" aria-label="Active model summary"><section><h2>Business assumptions</h2><div className="cw-summary-list">{row('Revenue growth',path('revenue_growth'),'revenue','forecast_years[0].revenue_growth')}{row('Operating margin',path('operating_margin'),'margin','forecast_years[0].operating_margin')}<button className="cw-summary-row" {...preview('cash')} title={conversion?.note??'Calculate the model to see FCFF / operating profit.'} onClick={()=>edit('cash_flow_conversion')}><span>Cash flow conversion</span><strong>{conversion?.text??'Not calculated'}<small>{last?`${last.fiscal_year_label}${stale?' · Previous result':''}`:'FCFF / operating profit'}</small><i aria-hidden="true"> ›</i></strong></button><button className="cw-summary-row" {...preview('period')} onClick={()=>edit('forecast_horizon')}><span>Forecast period</span><strong>{years.length} years<small>{years[0].fiscal_year_label}–{years.at(-1)!.fiscal_year_label}</small><i aria-hidden="true"> ›</i></strong></button></div></section>
 <section><h2>Valuation settings</h2><div className="cw-summary-list">{row('Discount rate',draft.rates.wacc.trim()?inputPercent(draft.rates.wacc):'Unset','discount','wacc')}{row('Terminal value',exit?`Exit ${draft.rates.exit_ev_ebit_multiple?draft.rates.exit_ev_ebit_multiple+'×':'unset'}`:`Growth ${draft.rates.terminal_growth.trim()?inputPercent(draft.rates.terminal_growth):'unset'}`,'terminal',exit?'exit_ev_ebit_multiple':'terminal_growth')}</div></section>
 <section className="cw-sidebar-actions" aria-label="Model actions"><button className="cv-primary cw-edit-all" onClick={()=>edit()}>Edit all assumptions</button><button className="cw-source-link" onClick={sources}>Sources & methodology</button></section></aside>;
}
