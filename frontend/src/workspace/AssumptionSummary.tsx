import {annual,terminal} from '../model';
import type {Entry} from '../model';
import type {CaseState} from './useWorkspace';
import type {EditorSection} from './canvasModel';
import {annualSummary,inherited,pathsFor,rateText,shortLabels} from './canvasModel';
import {percentage} from '../presentation';
export function AssumptionSummary({label,caseState:c,entry,edit,bridgeEntered}:{label:string;caseState:CaseState;entry?:Entry;edit:(section:EditorSection)=>void;bridgeEntered:boolean}){
 function row(name:string,value:string,section:EditorSection,paths:string[],reference?:string){
  const follows=paths.length>0&&inherited(label,c,paths),missing=value==='Not entered'||value.includes('/5 entered')&&!value.startsWith('5/5');
  return <button className="cv-assumption" onClick={()=>edit(section)} aria-label={`Edit ${name}`} key={name}><span><b>{name}</b>{reference&&<small>{reference}</small>}{follows&&<small className="cv-inherited">From Base</small>}</span><span className={missing?'cv-missing':''}>{value}<i aria-hidden="true">›</i></span></button>;
 }
 function history(metric:string){const r=entry?.historical_references?.find(r=>r.metric===metric);return r?.value?`${r.label}: ${percentage(r.value)}`:'Historical reference unavailable';}
 const cash=annual.slice(2),longPaths=['terminal_growth',...terminal.map(([key])=>`terminal.${key}`)],longCount=longPaths.filter(p=>c.draft.rates[p].trim()).length;
 return <section className="cv-assumptions" aria-label="Assumption summary"><div className="cv-section-title"><h2>Assumptions</h2><span>{Object.values(c.draft.rates).filter(v=>v.trim()).length}/37 entered</span></div>
 <h3>Business forecast</h3>{row('Revenue growth',annualSummary(c.draft,'revenue_growth'),'Growth',pathsFor('revenue_growth'),history('revenue_growth'))}{row('Operating margin',annualSummary(c.draft,'operating_margin'),'Operating margin',pathsFor('operating_margin'),history('operating_margin'))}<div className="cv-fixed-row"><span>Forecast period</span><b>Five years · fixed</b></div>
 <h3>Cash flow <small>Tax rate · others / revenue</small></h3>{cash.map(([key])=>row(shortLabels[key],annualSummary(c.draft,key),'Cash-flow assumptions',pathsFor(key)))}
 <h3>Valuation</h3>{row('Discount rate / WACC',rateText(c.draft.rates.wacc),'Discount rate',['wacc'])}{row('Long-term growth',rateText(c.draft.rates.terminal_growth),'Long-term assumptions',['terminal_growth'])}{row('Long-term operating ratios',longCount===6?'5/5 entered':`${Math.max(0,longCount-(c.draft.rates.terminal_growth.trim()?1:0))}/5 entered`,'Long-term assumptions',longPaths.slice(1))}
 {row('Cash, debt and shares',bridgeEntered?'Review entries':'Optional','Cash, debt and shares',[])}
 </section>;
}
