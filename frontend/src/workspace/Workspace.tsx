import {useEffect,useRef,useState} from 'react';
import type {CSSProperties} from 'react';
import {request} from '../api';
import {samePercentage,displayPath} from '../model';
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
import {AssumptionSummary,focusInline} from './AssumptionSummary';
import {AssumptionEditor} from './AssumptionEditor';
import {ValuationBreakdown} from './ValuationBreakdown';
import {scenarioDescription,inputName} from './canvasModel';
import type {EditorSection} from './canvasModel';
import type {Label} from './scenarios';
import './canvas.css';
import './inline.css';
const companyNames:Record<string,string>={META:'Meta Platforms',GOOGL:'Alphabet',AAPL:'Apple'};
const toolNames:Record<string,string>={ev:'enterprise value',equity:'equity and value per share',scenarios:'scenario comparison',sensitivity:'sensitivity',reverse:'reverse DCF'};
export function Workspace({load=request}:{load?:typeof request}){
 const w=useWorkspace(load),{catalog,state,session:c}=w;
 const [confirmation,setConfirmation]=useState<Confirmation|null>(null),[editor,setEditor]=useState<EditorSection|null>(null);
 const contextRef=useRef<HTMLDivElement>(null),[contextHeight,setContextHeight]=useState<number|null>(null);
 useEffect(()=>{if(!contextRef.current||typeof ResizeObserver==='undefined')return;const node=contextRef.current,observer=new ResizeObserver(()=>setContextHeight(Math.ceil(node.getBoundingClientRect().height)));observer.observe(node);return()=>observer.disconnect();},[Boolean(c)]);
 const entry=catalog?.entries.find(e=>e.kind===state.selected),context=entry?.financial_context;
 const ticker=entry?.company??(state.selected==='demo'?'Software example':''),name=companyNames[ticker]??ticker;
 const current=c?.ev.phase==='current',equityCurrent=current&&c?.equity.phase==='current',result=(equityCurrent?c?.equity.result:c?.ev.result)??null;
 const eligibleEquity=c?Object.keys(equityErrors(c.bridge,c.draft.doc.anchor.annual_end)).length===0:false;
 const issues:Errors={...c?.ev.errors,...Object.fromEntries(Object.entries(c?.equity.errors??{}).map(([k,v])=>['bridge.'+k,v]))};
 const issueEntries=Object.entries(Object.fromEntries(Object.entries(issues).map(([p,m])=>[c?displayPath(c.draft,p):p,m])));
 const suggestedSettings=(()=>{try{return c?smallGrid(c.draft):undefined;}catch{return undefined;}})();
 function focusIssue(path:string){if(path.startsWith('bridge.'))edit('Cash, debt and shares');else if(c)focusInline('dcf',c.draft,path);}
 function calculateGrid(){if(!c)return;if(Object.values(c.grid.settings).every(v=>!v.trim())&&suggestedSettings)for(const [key,value]of Object.entries(suggestedSettings))w.editGrid(key as keyof typeof suggestedSettings,value);void w.calculateSensitivity();}
 function select(kind:string){w.select(kind);setEditor(null);setConfirmation(null);}
 function edit(section:EditorSection,label?:Label){if(label)w.selectCase(label);setEditor(section);}
 function apply(draft:Draft,bridge:EquityDraft,touched:string[]){
  if(!c)return;const financial=Object.keys(draft.rates).some(p=>!samePercentage(draft.rates[p],c.draft.rates[p]))||touched.length>0;
  w.editDraft(draft,financial,touched);
  for(const key of Object.keys(bridge)as (keyof EquityDraft)[])if(bridge[key]!==c.bridge[key])w.editBridge(key,bridge[key]);
 }
 function generate(){if(!c)return;try{for(const [key,value]of Object.entries(smallGrid(c.draft)))w.editGrid(key as keyof ReturnType<typeof smallGrid>,value);}catch{/* Existing selected-case validation remains authoritative. */}}
 function compare(){if(!c)return;if(c.scenarioEquity!==eligibleEquity)w.configureSet('scenarioEquity',eligibleEquity);void w.calculateScenarios();}
 const status=w.busy?`Calculating ${toolNames[w.busy]}…`:Object.keys(c?.ev.errors??{}).length?'Review the indicated forecast inputs':c?.ev.phase==='stale'?'Previous result is stale · calculate after edits':c?.ev.phase==='failed'?'Calculation failed · entries preserved':current?'Calculation current · manual inputs unreviewed':c&&Object.values(c.draft.rates).every(v=>v.trim())?'Ready to calculate · inputs remain unreviewed':'Enter assumptions to calculate';
 return <div className="investor-prototype investor-workspace valuation-canvas" style={contextHeight===null?undefined:{'--cv-context-height':`${contextHeight}px`}as CSSProperties}><a className="p-skip" href="#valuation-main">Skip to calculator</a><nav className="cv-topbar" aria-label="Investor calculator"><span>K<span>.</span> Chaturvedi <i>/</i> Valuation</span><small>Unsaved · this tab only</small></nav>
 <main id="valuation-main" className="cv-page"><header className="cv-company"><div><span className="cv-eyebrow">FCFF · FIVE-YEAR DCF</span><h1>{name||'Company valuation'} {ticker&&<small>{entry?.company??'Synthetic'}</small>}</h1>{entry&&<p>Calculation uses <b>FY2025 revenue {readableMoney(entry.revenue)}</b> · fiscal-end origin {entry.identity.annual_end}</p>}</div><div className="cv-company-tools"><label htmlFor="canvas-company">Company</label><select id="canvas-company" value={state.selected==='demo'?'':state.selected} disabled={!catalog} onChange={e=>select(e.target.value)}><option value="">Select a company</option>{catalog?.entries.map(e=><option value={e.kind} key={e.kind}>{e.company} · {companyNames[e.company]??e.company}</option>)}</select>{entry&&<details className="cv-data-details"><summary>{context?'Newer context · not used':'Data details'}</summary><p>Data used: FY2025 revenue anchor ending {entry.identity.annual_end}; later-filed information, not a current-date valuation. Information cutoff is unknown.</p>{context&&<p>Latest observed context: {context.form} through {context.financials_through}, filed {context.filed}, accepted {context.accepted_at??'unknown'}, checked {context.checked_at}. New valuation preparation remains incomplete. <a href={context.filing_url} target="_blank" rel="noreferrer">SEC filing</a></p>}</details>}</div></header>
 {!catalog&&<p role="status">{w.catalogFailure?<>{w.catalogFailure} <button onClick={w.retryCatalog}>Retry loading companies</button></>:'Loading companies…'}</p>}
 {c?<>
 <section className={'cv-result '+(!current&&result?'cv-result-stale':'')} aria-label="Valuation summary"><div><span className="cv-eyebrow">{c.selectedCase} · enterprise value</span><strong className="cv-ev">{result?readableMoney(result.stage_b.enterprise_value):'Not calculated'}</strong>{result&&!current&&<span className="cv-stale">Previous calculation · not current</span>}<p>Operating business value, before cash, claims and shares.</p></div><div className="cv-result-context"><p className={!current&&result?'cv-stale':'cv-status'} role="status">{status}</p>{result?<dl><div><dt>Five-year PV</dt><dd>{readableMoney(result.stage_b.pv_explicit_fcff)}</dd></div><div><dt>Terminal PV</dt><dd>{readableMoney(result.stage_b.pv_terminal_value)}</dd></div></dl>:<p>All 37 annual and long-term inputs remain explicit. No forecast is generated for you.</p>}{c.equity.result?.stage_c&&<p className={equityCurrent?'':'cv-stale'}>{equityCurrent?'Selected equity':'Previous equity · stale'}: {readableMoney(c.equity.result.stage_c.equity_value)} · {fixedUnit(c.equity.result.stage_c.value_per_share)} USD/share. Not fully diluted fair value.</p>}
 <MarketPanel result={result} stale={!current||Boolean(result?.stage_c)&&!equityCurrent} compact/>
 </div></section>
 <div ref={contextRef} className="cv-context-strip"><div className="cv-segments" role="group" aria-label="Selected scenario">{(['Bear','Base','Bull']as const).map(label=><button aria-pressed={c.selectedCase===label} key={label} onClick={()=>w.selectCase(label)}>{label}</button>)}</div><p><b>{ticker}</b> · {c.selectedCase} · {result?'EV '+readableMoney(result.stage_b.enterprise_value):'Not calculated'}{!current&&result?' · stale':''}<small>{w.busy?`Calculating ${toolNames[w.busy]}…`:scenarioDescription(c.selectedCase,c,w.company!.cases.Base)}</small></p><div className="cv-calculate"><button className="cv-primary" disabled={Boolean(w.busy)} onClick={()=>void w.calculate('ev')}>Calculate enterprise value</button>{w.busy?<button onClick={w.cancel}>Cancel calculation</button>:<button onClick={()=>void w.calculate('equity')} disabled={!current}>Calculate value per share</button>}</div></div>
 <nav className="cv-section-nav" aria-label="Explore this valuation"><a href="#dcf">DCF</a><a href="#scenario-comparison">Scenario comparison</a><a href="#sensitivity">Sensitivity</a><a href="#sources-methodology">Sources &amp; methodology</a></nav>
 <section id="dcf" className="cv-analysis-section cv-dcf-section" aria-labelledby="dcf-heading"><h2 id="dcf-heading">DCF · {c.selectedCase}</h2>
 {(issueEntries.length>0||c.ev.failure||c.equity.failure)&&<div className="cv-issues" role="region" aria-label="Input issues">{issueEntries.length>0&&<><b>Review required inputs</b><div>{issueEntries.map(([path,message])=><button key={path} onClick={()=>focusIssue(path)}>{inputName(c.draft,path)}: {message}</button>)}</div></>}{c.ev.failure&&<p>{c.ev.failure} <button onClick={()=>void w.calculate('ev')} disabled={Boolean(w.busy)}>Retry enterprise value</button></p>}{c.equity.failure&&<p>{c.equity.failure} <button onClick={()=>void w.calculate('equity')} disabled={Boolean(w.busy)||!current}>Retry value per share</button></p>}</div>}
 <div className="cv-model"><AssumptionSummary key={state.selected+c.selectedCase} label={c.selectedCase} caseState={c} entry={entry} change={w.editDraft} editBridge={()=>edit('Cash, debt and shares')} errors={c.ev.errors}/><div className="cv-chart-column">{result?<><p className="cv-chart-caption">{c.selectedCase} · {!current?'Previous calculation — stale':'Calculated forecast'}</p><ForecastChart cases={[{label:c.selectedCase,result}]}/></>:<section className="cv-chart cv-empty-chart" aria-label="Financial chart"><div className="cv-chart-heading"><h2>Revenue & FCFF</h2><span>USD billions</span></div><p>{c.selectedCase} · forecast not calculated</p><div className="cv-empty-plot"><div><span>{entry?readableMoney(entry.revenue):'$100.00'}</span><i/><b>FY2025</b><small>Reported revenue{state.selected==='demo'?' · synthetic fixture':''}</small></div><p>Your five-year financial path appears here after calculation.<br/>Historical FCFF is unavailable.</p></div><p>Edit the assumptions alongside this chart. Type directly; Calculate runs the model.</p></section>}
 <div className="cv-chart-footer"><span>{c.draft.doc.anchor.annual_end} fiscal-end model · later-filed information</span>{result&&<ExportData value={result} name={result.case_name}/>}</div>
 {result?<ValuationBreakdown result={result} stale={!current}/>:<p className="cv-composition-empty">Valuation composition appears after calculating this case.</p>}{c.equity.result&&<details className="cv-equity-details"><summary>Equity bridge & dated shares</summary><EquityReview compact result={c.equity.result} stale={!equityCurrent}/></details>}
 </div></div></section>
 <section id="scenario-comparison" className="cv-analysis-section" aria-labelledby="scenario-heading"><h2 id="scenario-heading">Scenario comparison</h2><ScenariosPanel company={w.company!} busy={w.busy} changeDraft={(label,draft,paths)=>w.editDraft(draft,true,paths,label)} reset={w.resetOverrides} calculate={compare} cancel={w.cancel} confirm={setConfirmation} eligibleEquity={eligibleEquity}/></section>
 <section id="sensitivity" className="cv-analysis-section" aria-labelledby="sensitivity-heading"><h2 id="sensitivity-heading">Sensitivity · {c.selectedCase}</h2><SensitivityPanel label={c.selectedCase} caseName={c.draft.doc.case_name} grid={c.grid} sourceStatus={c.ev.phase} busy={w.busy} edit={w.editGrid} calculate={calculateGrid} cancel={w.cancel} inspect={w.inspectCell} apply={w.applyCell} confirm={setConfirmation} review={()=>focusIssue('wacc')} generate={generate} suggestedSettings={suggestedSettings} eligibleEquity={eligibleEquity}/></section>
 <section id="sources-methodology" className="cv-analysis-section" aria-labelledby="sources-heading"><h2 id="sources-heading">Sources &amp; methodology</h2><Sources entry={entry} result={result}/></section>
 {c.selectedCase!=='Base'&&(c.overrides??[]).length>0&&<button className="cv-reset" onClick={()=>setConfirmation({title:`Reset ${c.selectedCase} to Base?`,body:'Discard this scenario’s overrides and restore inherited Base inputs. Its calculation will be cleared.',accept:'Reset to Base',action:()=>w.resetOverrides(c.selectedCase as 'Bear'|'Bull')})}>Reset {c.selectedCase} to Base</button>}
 {editor&&<AssumptionEditor key={state.selected+c.selectedCase} company={ticker} label={c.selectedCase} initial={c.draft} bridge={c.bridge} section={editor} entry={entry} result={result} stale={!current} errors={issues} bridgeOnly apply={apply} close={()=>setEditor(null)}/>}
 </>:catalog&&<section className="cv-start"><h2>Select a company</h2><p>Start with its reported revenue anchor. Your forecast assumptions will be unset.</p><details><summary>Separate software example</summary><p>USD100 synthetic fixture; no company forecast or market reference.</p><button onClick={()=>select('demo')}>Load synthetic example</button></details></section>}
 <footer className="cv-footer">Unsaved work stays in this tab; reloading clears it. Manual inputs are not independently reviewed. Browser cancellation may not immediately stop server work.</footer></main>{confirmation&&<Confirm value={confirmation} close={()=>setConfirmation(null)}/>}</div>;
}
