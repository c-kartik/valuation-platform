import {useState} from 'react';
import {request} from '../api';
import {samePercentage} from '../model';
import type {Draft,Errors} from '../model';
import {readableMoney,fixedUnit} from '../presentation';
import {equityErrors} from '../equity';
import type {EquityDraft} from '../equity';
import {EquityReview} from '../EquityFields';
import {useWorkspace} from './useWorkspace';
import {Confirm} from './Confirm';
import type {Confirmation} from './Confirm';
import {ScenariosPanel} from './ScenariosPanel';
import {SensitivityPanel} from './SensitivityPanel';
import {smallGrid} from './sensitivity';
import {ForecastChart} from './ForecastChart';
import {Sources} from './Sources';
import {MarketPanel} from './MarketPanel';
import {ExportData} from './ExportData';
import {AssumptionSummary} from './AssumptionSummary';
import {AssumptionEditor} from './AssumptionEditor';
import {ValuationBreakdown} from './ValuationBreakdown';
import {scenarioDescription,sectionFor} from './canvasModel';
import type {EditorSection} from './canvasModel';
import type {Label} from './scenarios';
import './canvas.css';
const companyNames:Record<string,string>={META:'Meta Platforms',GOOGL:'Alphabet',AAPL:'Apple'};
const toolNames:Record<string,string>={ev:'enterprise value',equity:'equity and value per share',scenarios:'scenario comparison',sensitivity:'sensitivity',reverse:'reverse DCF'};
type Exploration='Scenario comparison'|'Sensitivity'|'Valuation breakdown'|'Sources & methodology';
export function Workspace({load=request}:{load?:typeof request}){
 const w=useWorkspace(load),{catalog,state,session:c}=w;
 const [exploration,setExploration]=useState<Exploration|null>(null),[confirmation,setConfirmation]=useState<Confirmation|null>(null),[editor,setEditor]=useState<EditorSection|null>(null);
 const entry=catalog?.entries.find(e=>e.kind===state.selected),context=entry?.financial_context;
 const ticker=entry?.company??(state.selected==='demo'?'Software example':''),name=companyNames[ticker]??ticker;
 const current=c?.ev.phase==='current',equityCurrent=current&&c?.equity.phase==='current',result=(equityCurrent?c?.equity.result:c?.ev.result)??null;
 const bridgeEntered=Boolean(c&&(c.bridge.assets||c.bridge.financing||c.bridge.shares||c.bridge.classes));
 const eligibleEquity=c?Object.keys(equityErrors(c.bridge,c.draft.doc.anchor.annual_end)).length===0:false;
 const issues:Errors={...c?.ev.errors,...Object.fromEntries(Object.entries(c?.equity.errors??{}).map(([k,v])=>['bridge.'+k,v]))};
 const issueGroups=[...new Set(Object.keys(issues).map(sectionFor))];
 function select(kind:string){w.select(kind);setEditor(null);setConfirmation(null);setExploration(null);}
 function edit(section:EditorSection,label?:Label){if(label)w.selectCase(label);setEditor(section);}
 function apply(draft:Draft,bridge:EquityDraft,touched:string[]){
  if(!c)return;const financial=Object.keys(draft.rates).some(p=>!samePercentage(draft.rates[p],c.draft.rates[p]))||touched.length>0;
  w.editDraft(draft,financial,touched);
  for(const key of Object.keys(bridge)as (keyof EquityDraft)[])if(bridge[key]!==c.bridge[key])w.editBridge(key,bridge[key]);
 }
 function generate(){if(!c)return;try{for(const [key,value]of Object.entries(smallGrid(c.draft)))w.editGrid(key as keyof ReturnType<typeof smallGrid>,value);}catch{/* Existing selected-case validation remains authoritative. */}}
 function compare(){if(!c)return;if(c.scenarioEquity!==eligibleEquity)w.configureSet('scenarioEquity',eligibleEquity);void w.calculateScenarios();}
 const status=w.busy?`Calculating ${toolNames[w.busy]}…`:Object.keys(c?.ev.errors??{}).length?'Review the indicated forecast inputs':c?.ev.phase==='stale'?'Previous result is stale · calculate after edits':c?.ev.phase==='failed'?'Calculation failed · entries preserved':current?'Calculation current · manual inputs unreviewed':c&&Object.values(c.draft.rates).every(v=>v.trim())?'Ready to calculate · inputs remain unreviewed':'Enter assumptions to calculate';
 return <div className="investor-prototype investor-workspace valuation-canvas"><a className="p-skip" href="#valuation-main">Skip to calculator</a><nav className="cv-topbar" aria-label="Investor calculator"><span>K<span>.</span> Chaturvedi <i>/</i> Valuation</span><small>Unsaved · this tab only</small></nav>
 <main id="valuation-main" className="cv-page"><header className="cv-company"><div><span className="cv-eyebrow">FCFF · FIVE-YEAR DCF</span><h1>{name||'Company valuation'} {ticker&&<small>{entry?.company??'Synthetic'}</small>}</h1>{entry&&<p>Calculation uses <b>FY2025 revenue {readableMoney(entry.revenue)}</b> · fiscal-end origin {entry.identity.annual_end}</p>}</div><div className="cv-company-tools"><label htmlFor="canvas-company">Company</label><select id="canvas-company" value={state.selected==='demo'?'':state.selected} disabled={!catalog} onChange={e=>select(e.target.value)}><option value="">Select a company</option>{catalog?.entries.map(e=><option value={e.kind} key={e.kind}>{e.company} · {companyNames[e.company]??e.company}</option>)}</select>{entry&&<details className="cv-data-details"><summary>{context?'Newer context · not used':'Data details'}</summary><p>Data used: FY2025 revenue anchor ending {entry.identity.annual_end}; later-filed information, not a current-date valuation. Information cutoff is unknown.</p>{context&&<p>Latest observed context: {context.form} through {context.financials_through}, filed {context.filed}, accepted {context.accepted_at??'unknown'}, checked {context.checked_at}. New valuation preparation remains incomplete. <a href={context.filing_url} target="_blank" rel="noreferrer">SEC filing</a></p>}</details>}</div></header>
 {!catalog&&<p role="status">{w.catalogFailure?<>{w.catalogFailure} <button onClick={w.retryCatalog}>Retry loading companies</button></>:'Loading companies…'}</p>}
 {c?<>
 <section className={'cv-result '+(!current&&result?'cv-result-stale':'')} aria-label="Valuation summary"><div><span className="cv-eyebrow">{c.selectedCase} · enterprise value</span><strong className="cv-ev">{result?readableMoney(result.stage_b.enterprise_value):'Not calculated'}</strong>{result&&!current&&<span className="cv-stale">Previous calculation · not current</span>}<p>Operating business value, before cash, claims and shares.</p></div><div className="cv-result-context"><p className={!current&&result?'cv-stale':'cv-status'} role="status">{status}</p>{result?<dl><div><dt>Five-year PV</dt><dd>{readableMoney(result.stage_b.pv_explicit_fcff)}</dd></div><div><dt>Terminal PV</dt><dd>{readableMoney(result.stage_b.pv_terminal_value)}</dd></div></dl>:<p>All 37 annual and long-term inputs remain explicit. No forecast is generated for you.</p>}{c.equity.result?.stage_c&&<p className={equityCurrent?'':'cv-stale'}>{equityCurrent?'Selected equity':'Previous equity · stale'}: {readableMoney(c.equity.result.stage_c.equity_value)} · {fixedUnit(c.equity.result.stage_c.value_per_share)} USD/share. Not fully diluted fair value.</p>}
 <MarketPanel result={result} stale={!current||Boolean(result?.stage_c)&&!equityCurrent} compact/>
 </div></section>
 <div className="cv-context-strip"><div className="cv-segments" role="group" aria-label="Selected scenario">{(['Bear','Base','Bull']as const).map(label=><button aria-pressed={c.selectedCase===label} key={label} onClick={()=>w.selectCase(label)}>{label}</button>)}</div><p><b>{ticker}</b> · {c.selectedCase} · {result?'EV '+readableMoney(result.stage_b.enterprise_value):'Not calculated'}{!current&&result?' · stale':''}<small>{w.busy?`Calculating ${toolNames[w.busy]}…`:scenarioDescription(c.selectedCase,c,w.company!.cases.Base)}</small></p><div className="cv-calculate"><button className="cv-primary" disabled={Boolean(w.busy)} onClick={()=>void w.calculate('ev')}>Calculate enterprise value</button>{w.busy?<button onClick={w.cancel}>Cancel calculation</button>:<button onClick={()=>void w.calculate('equity')} disabled={!current}>Calculate value per share</button>}</div></div>
 {(issueGroups.length>0||c.ev.failure||c.equity.failure)&&<div className="cv-issues" role="region" aria-label="Input issues">{issueGroups.length>0&&<><b>Review required inputs</b><div>{issueGroups.map(group=><button key={group} onClick={()=>edit(group)}>{group}</button>)}</div></>}{c.ev.failure&&<p>{c.ev.failure} <button onClick={()=>void w.calculate('ev')} disabled={Boolean(w.busy)}>Retry enterprise value</button></p>}{c.equity.failure&&<p>{c.equity.failure} <button onClick={()=>void w.calculate('equity')} disabled={Boolean(w.busy)||!current}>Retry value per share</button></p>}</div>}
 <div className="cv-model"><AssumptionSummary label={c.selectedCase} caseState={c} entry={entry} edit={edit} bridgeEntered={bridgeEntered}/><div className="cv-chart-column">{result?<><p className="cv-chart-caption">{c.selectedCase} · {!current?'Previous calculation — stale':'Calculated forecast'}</p><ForecastChart cases={[{label:c.selectedCase,result}]}/></>:<section className="cv-chart cv-empty-chart" aria-label="Financial chart"><div className="cv-chart-heading"><h2>Revenue & FCFF</h2><span>USD billions</span></div><p>{c.selectedCase} · forecast not calculated</p><div className="cv-empty-plot"><div><span>{entry?readableMoney(entry.revenue):'$100.00'}</span><i/><b>FY2025</b><small>Reported revenue{state.selected==='demo'?' · synthetic fixture':''}</small></div><p>Your five-year financial path appears here after calculation.<br/>Historical FCFF is unavailable.</p></div><p>Edit the assumptions alongside this chart. Apply keeps your working inputs; Calculate runs the model.</p></section>}
 <div className="cv-chart-footer"><span>{c.draft.doc.anchor.annual_end} fiscal-end model · later-filed information</span>{result&&<ExportData value={result} name={result.case_name}/>}</div>
 </div></div>
 <nav className="cv-explore-tabs" aria-label="Explore this valuation">{(['Scenario comparison','Sensitivity','Valuation breakdown','Sources & methodology']as Exploration[]).map(view=><button aria-expanded={exploration===view} key={view} onClick={()=>setExploration(exploration===view?null:view)}>{view}</button>)}</nav>
 {exploration&&<div className="cv-exploration" aria-label={`${c.selectedCase} exploration`}>
 {exploration==='Scenario comparison'&&<ScenariosPanel company={w.company!} busy={w.busy} editRate={w.editScenarioRate} reset={w.resetOverrides} calculate={compare} cancel={w.cancel} confirm={setConfirmation} eligibleEquity={eligibleEquity} editFocused={edit}/>}
 {exploration==='Sensitivity'&&<SensitivityPanel label={c.selectedCase} caseName={c.draft.doc.case_name} grid={c.grid} sourceStatus={c.ev.phase} busy={w.busy} edit={w.editGrid} calculate={()=>void w.calculateSensitivity()} cancel={w.cancel} inspect={w.inspectCell} apply={w.applyCell} confirm={setConfirmation} review={()=>edit('Discount rate')} generate={generate}/>}
 {exploration==='Valuation breakdown'&&(result?<><ValuationBreakdown result={result} stale={!current}/>{c.equity.result&&<details className="cv-equity-details"><summary>Equity bridge & dated shares</summary><EquityReview compact result={c.equity.result} stale={!equityCurrent}/></details>}</>:<p>Calculate the selected case to inspect its valuation composition.</p>)}
 {exploration==='Sources & methodology'&&<Sources entry={entry} result={result}/>}</div>}
 {c.selectedCase!=='Base'&&(c.overrides??[]).length>0&&<button className="cv-reset" onClick={()=>setConfirmation({title:`Reset ${c.selectedCase} to Base?`,body:'Discard this scenario’s overrides and restore inherited Base inputs. Its calculation will be cleared.',accept:'Reset to Base',action:()=>w.resetOverrides(c.selectedCase as 'Bear'|'Bull')})}>Reset {c.selectedCase} to Base</button>}
 {editor&&<AssumptionEditor key={state.selected+c.selectedCase} company={ticker} label={c.selectedCase} initial={c.draft} bridge={c.bridge} section={editor} entry={entry} result={result} stale={!current} errors={issues} apply={apply} close={()=>setEditor(null)}/>}
 </>:catalog&&<section className="cv-start"><h2>Select a company</h2><p>Start with its reported revenue anchor. Your forecast assumptions will be unset.</p><details><summary>Separate software example</summary><p>USD100 synthetic fixture; no company forecast or market reference.</p><button onClick={()=>select('demo')}>Load synthetic example</button></details></section>}
 <footer className="cv-footer">Unsaved work stays in this tab; reloading clears it. Manual inputs are not independently reviewed. Browser cancellation may not immediately stop server work.</footer></main>{confirmation&&<Confirm value={confirmation} close={()=>setConfirmation(null)}/>}</div>;
}
