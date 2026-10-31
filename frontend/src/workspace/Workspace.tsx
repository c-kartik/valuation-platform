import {useEffect,useRef,useState} from 'react';
import type {CSSProperties} from 'react';
import {request} from '../api';
import {entryErrors,methodOf} from '../model';
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
import {reviewGrid} from './sensitivity';
import {profileGrid} from './preload';
import {PreloadReview} from './PreloadReview';
import {FullModel} from './FullModel';
import {ForecastChart} from './ForecastChart';
import {Sources} from './Sources';
import {MarketPanel} from './MarketPanel';
import {ExportData} from './ExportData';
import {AssumptionEditor} from './AssumptionEditor';
import {ModelEditor} from './ModelEditor';
import {ActiveAssumptions,MethodSelector} from './ActiveAssumptions';
import {TerminalComparison} from './TerminalComparison';
import {ValuationBreakdown} from './ValuationBreakdown';
import type {Label} from './scenarios';
import './canvas.css';
import './inline.css';
import './resultFirst.css';
const companyNames:Record<string,string>={META:'Meta Platforms',GOOGL:'Alphabet',AAPL:'Apple'};
function useVisible(key:string){
 const ref=useRef<HTMLElement>(null),[visible,setVisible]=useState(false);
 useEffect(()=>{setVisible(false);if(!ref.current||typeof IntersectionObserver==='undefined')return;const observer=new IntersectionObserver(([e])=>setVisible(e.isIntersecting),{threshold:0});observer.observe(ref.current);return()=>observer.disconnect();},[key]);
 return {ref,visible};
}
export function Workspace({load=request}:{load?:typeof request}){
 const w=useWorkspace(load),{catalog,state,session:c}=w;
 const [confirmation,setConfirmation]=useState<Confirmation|null>(null),[editor,setEditor]=useState<'model'|'bridge'|null>(null);
 const contextRef=useRef<HTMLDivElement>(null),[contextHeight,setContextHeight]=useState<number|null>(null);
 useEffect(()=>{if(!contextRef.current||typeof ResizeObserver==='undefined')return;const observer=new ResizeObserver(()=>setContextHeight(Math.ceil(contextRef.current!.getBoundingClientRect().height)));observer.observe(contextRef.current);return()=>observer.disconnect();},[Boolean(c)]);
 const scenarios=useVisible(state.selected),sensitivity=useVisible(state.selected),attempts=useRef(new Set<string>());
 const entry=catalog?.entries.find(e=>e.kind===state.selected),ticker=entry?.company??(state.selected==='demo'?'Synthetic':''),name=companyNames[ticker]??ticker;
 const current=c?.ev.phase==='current',equityCurrent=current&&c?.equity.phase==='current',result=(equityCurrent?c?.equity.result:c?.ev.result)??null;
 const eligibleEquity=c?Object.keys(equityErrors(c.bridge,c.draft.doc.anchor.annual_end)).length===0:false;
 const issues:Errors={...c?.ev.errors,...Object.fromEntries(Object.entries(c?.equity.errors??{}).map(([k,v])=>['bridge.'+k,v]))};
 const suggestedSettings=(()=>{try{return c?.preload?.profile?profileGrid(c.draft,c.preload.profile):c?reviewGrid(c.draft):undefined;}catch{return undefined;}})();
 function calculateGrid(){if(!c)return;if((c.grid.generated||Object.values(c.grid.settings).every(v=>!v.trim()))&&suggestedSettings)w.configureGrid(suggestedSettings);void w.calculateSensitivity();}
 function compare(){if(!c)return;if(c.scenarioEquity!==eligibleEquity)w.configureSet('scenarioEquity',eligibleEquity);void w.calculateScenarios();}
 // Auto work is section-driven and revision-bound, never keystroke-driven. Failure
 // phases and one attempted binding prevent retry storms; explicit retry remains.
 useEffect(()=>{
  if(!c||!current||w.busy||editor)return;
  const key=JSON.stringify([state.selected,c.selectedCase,c.revision,c.preload?.profile?.economic_hash,methodOf(c.draft)]);
  if(scenarios.visible&&!['current','failed','calculating'].includes(c.scenario.phase)&&!attempts.current.has('scenario'+key)&&['Bear','Base','Bull'].every(l=>!Object.keys(entryErrors(w.company!.cases[l]!.draft)).length)){
   attempts.current.add('scenario'+key);compare();return;
  }
  if(sensitivity.visible&&suggestedSettings&&!['current','failed','calculating'].includes(c.grid.phase)&&!attempts.current.has('grid'+key)){
   attempts.current.add('grid'+key);calculateGrid();
  }
 },[state.selected,c?.selectedCase,c?.revision,c?.ev.phase,c?.scenario.phase,c?.grid.phase,w.busy,scenarios.visible,sensitivity.visible,editor]);
 function select(kind:string){w.select(kind);setEditor(null);setConfirmation(null);}
 function editCase(label:Label){w.selectCase(label);setEditor('model');}
 function applyBridge(_draft:Draft,bridge:EquityDraft){if(c)for(const key of Object.keys(bridge)as (keyof EquityDraft)[])if(bridge[key]!==c.bridge[key])w.editBridge(key,bridge[key]);}
 const method=c?methodOf(c.draft):'perpetual_growth',missing=c?Object.entries(entryErrors(c.draft)):[],loading=c?.preload?.status==='loading'||c?.ev.phase==='calculating';
 const status=editor==='model'?'Editing draft · previous submitted result retained':loading?'Preparing the starting calculation…':c?.ev.phase==='failed'?'Calculation failed · entries preserved':current?'Current calculation · inputs remain unreviewed':result?'Previous calculation · stale':missing.length?'Required inputs remain unset':'Ready to calculate';
 return <div className="investor-prototype investor-workspace valuation-canvas cv-result-first" style={contextHeight===null?undefined:{'--cv-context-height':`${contextHeight}px`}as CSSProperties}><a className="p-skip" href="#valuation-main">Skip to calculator</a><nav className="cv-topbar" aria-label="Investor calculator"><span>K<span>.</span> Chaturvedi <i>/</i> Valuation</span><small>Unsaved · this tab only</small></nav>
 <main id="valuation-main" className="cv-page"><header className="cv-company"><div><span className="cv-eyebrow">FCFF · FIVE-YEAR DCF</span><h1>{name||'Company valuation'} {ticker&&<small>{ticker}</small>}</h1>{entry&&<p>Fiscal-end origin {entry.identity.annual_end} · reported revenue {readableMoney(entry.revenue)} · later-filed information</p>}{c?.preload?.profile&&<small>Proposed editable estimates · information reviewed {c.preload.profile.economic.dates.information_review}; hindsight at this model origin.</small>}</div><div className="cv-company-tools"><label htmlFor="canvas-company">Company</label><select id="canvas-company" value={state.selected==='demo'?'':state.selected} disabled={!catalog} onChange={e=>select(e.target.value)}><option value="">Select a company</option>{catalog?.entries.map(e=><option value={e.kind} key={e.kind}>{e.company} · {companyNames[e.company]??e.company}</option>)}</select></div></header>
 {!catalog&&<p role="status">{w.catalogFailure?<>{w.catalogFailure} <button onClick={w.retryCatalog}>Retry loading companies</button></>:'Loading companies…'}</p>}
 {c?<>
 <section className={'cv-result '+(!current&&result?'cv-result-stale':'')} aria-label="Valuation summary"><div><span className="cv-eyebrow">{c.selectedCase} · {method==='exit_multiple'?'exit multiple':'perpetual growth'} · enterprise value</span><strong className="cv-ev">{current&&result?readableMoney(result.stage_b.enterprise_value):loading?'Calculating…':result&&result.stage_b.terminal_method===method?readableMoney(result.stage_b.enterprise_value):'Inputs required'}</strong>{!current&&result&&<small>Previous result{result.stage_b.terminal_method!==method?' uses a different terminal method; EV withheld here':' · stale'}</small>}<p>Operating business value, before cash, claims and shares.</p></div><div className="cv-result-context"><p role="status">{status}</p>{current&&result&&<dl><div><dt>Explicit forecast PV</dt><dd>{readableMoney(result.stage_b.pv_explicit_fcff)}</dd></div><div><dt>Terminal PV</dt><dd>{readableMoney(result.stage_b.pv_terminal_value)}</dd></div></dl>}<MethodSelector id="dcf-terminal-method" method={method} change={w.setTerminalMethod}/><button className="cv-primary" onClick={()=>setEditor('model')}>Edit assumptions</button></div></section>
 <div ref={contextRef} className="cv-context-strip"><div className="cv-segments" role="group" aria-label="Selected scenario">{(['Bear','Base','Bull']as const).map(label=><button aria-pressed={c.selectedCase===label} key={label} onClick={()=>w.selectCase(label)}>{label}</button>)}</div><p><b>{ticker} · {c.selectedCase}</b><small>{status}</small></p>{w.busy&&<button onClick={w.cancel}>Cancel calculation</button>}</div>
 <nav className="cv-section-nav" aria-label="Explore this valuation"><a href="#dcf">DCF</a><a href="#scenario-comparison">Scenario comparison</a><a href="#sensitivity">Sensitivity</a><a href="#sources-methodology">Sources &amp; methodology</a></nav>
 <section id="dcf" className="cv-analysis-section cv-dcf-section" aria-labelledby="dcf-heading"><h2 id="dcf-heading">DCF · {c.selectedCase}</h2>
 {(Object.keys(issues).length>0||missing.length>0)&&!loading&&<details className="cv-issues" open={method==='exit_multiple'&&!c.draft.rates.exit_ev_ebit_multiple||undefined}><summary>{missing.length||Object.keys(issues).length} inputs require review</summary>{Object.entries({...Object.fromEntries(missing),...issues}).map(([p,m])=><p key={p}><button onClick={()=>setEditor(p.startsWith('bridge.')?'bridge':'model')}>{p}: {m}</button></p>)}<button onClick={()=>setEditor('model')}>Enter required assumptions</button></details>}
 {c.ev.failure&&<p className="cv-issues" role="status">{c.ev.failure} <button disabled={Boolean(w.busy)} onClick={()=>void w.calculate('ev')}>Retry enterprise value</button></p>}{c.preload?.failure&&<p role="status">{c.preload.failure} <button onClick={()=>void w.refreshPreload(true)}>Retry starting profile</button></p>}
 {result?<><p className="cv-chart-caption">{c.selectedCase} · {current?'Calculated operating forecast':`Previous submitted operating path · ${result.stage_b.terminal_method??'perpetual_growth'} valuation is stale`}</p><ForecastChart cases={[{label:c.selectedCase,result}]} entry={entry}/></>:<p className="cv-compact-loading" role="status">{loading?'Loading source-bound inputs and calculating Base…':'No forecast result. Open Edit assumptions to complete the model.'}</p>}
 <ActiveAssumptions draft={c.draft} label={c.selectedCase} overrides={c.overrides} generated={Boolean(c.preload?.profile)}/>
 <div className="cv-chart-footer"><span>{c.draft.doc.anchor.annual_end} fiscal-end analytical model · later-filed information</span>{result&&<ExportData value={{workspace_case:c.selectedCase,input_revision:equityCurrent?c.equity.inputRevision:c.ev.inputRevision,status:current?'current':'stale',calculation:result,preload_profile:c.resultProfile??null,user_overrides:c.resultOverrides??[]}} name={result.case_name}/>}</div>
 {result&&<><ValuationBreakdown result={result} stale={!current}/><TerminalComparison result={result} stale={!current}/></>}
 <details className="cv-secondary"><summary>Optional equity / market comparison</summary><p>Actual eligibility, claims, classes and awards remain unresolved.</p><button onClick={()=>setEditor('bridge')}>Cash, debt and shares · optional</button><button disabled={!current||Boolean(w.busy)} onClick={()=>void w.calculate('equity')}>Calculate value per share</button>{c.equity.failure&&<p>{c.equity.failure}</p>}{c.equity.result?.stage_c&&<><p>{readableMoney(c.equity.result.stage_c.equity_value)} equity · {fixedUnit(c.equity.result.stage_c.value_per_share)} USD/share</p><EquityReview compact result={c.equity.result} stale={!equityCurrent}/></>}<MarketPanel result={result} stale={!current} compact/></details>
 <FullModel draft={c.draft} result={result} stale={!current} revision={equityCurrent?c.equity.inputRevision:c.ev.inputRevision} entry={entry} change={w.editDraft} preload={c.resultProfile?{profile:c.resultProfile,status:'ready',failure:''}:undefined} overrides={c.resultOverrides??[]}/></section>
 <section ref={scenarios.ref} id="scenario-comparison" className="cv-analysis-section" aria-labelledby="scenario-heading"><h2 id="scenario-heading">Scenario comparison</h2><ScenariosPanel company={w.company!} entry={entry} busy={w.busy} reset={w.resetOverrides} calculate={compare} cancel={w.cancel} confirm={setConfirmation} eligibleEquity={eligibleEquity} setMethod={w.setTerminalMethod} editCase={editCase}/></section>
 <section ref={sensitivity.ref} id="sensitivity" className="cv-analysis-section" aria-labelledby="sensitivity-heading"><h2 id="sensitivity-heading">Sensitivity · {c.selectedCase}</h2><SensitivityPanel label={c.selectedCase} caseName={c.draft.doc.case_name} grid={c.grid} method={method} configuredDiagnostics={Boolean(c.preload?.profile)} sourceStatus={c.ev.phase} busy={w.busy} edit={w.editGrid} calculate={calculateGrid} cancel={w.cancel} inspect={w.inspectCell} apply={w.applyCell} confirm={setConfirmation} review={()=>setEditor('model')} generate={()=>suggestedSettings&&w.configureGrid(suggestedSettings)} suggestedSettings={suggestedSettings} eligibleEquity={eligibleEquity}/></section>
 <section id="sources-methodology" className="cv-analysis-section" aria-labelledby="sources-heading"><h2 id="sources-heading">Sources &amp; methodology</h2>{c.preload&&<PreloadReview label={c.selectedCase} state={c.preload} draft={c.draft} overrides={c.overrides??[]} refresh={()=>void w.refreshPreload()} adopt={w.adoptPreload}/>}<Sources entry={entry} result={result} preload={c.preload}/></section>
 {editor==='model'&&<ModelEditor key={state.selected+c.selectedCase} company={ticker} label={c.selectedCase} session={c} submit={w.updateValuation} close={()=>setEditor(null)}/>}
 {editor==='bridge'&&<AssumptionEditor key={state.selected+c.selectedCase} company={ticker} label={c.selectedCase} initial={c.draft} bridge={c.bridge} section="Cash, debt and shares" entry={entry} result={result} stale={!current} errors={issues} bridgeOnly apply={applyBridge} close={()=>setEditor(null)}/>}
 </>:catalog&&<section className="cv-start"><h2>Select a company</h2><p>GOOGL offers proposed editable starting estimates. Other companies remain unset.</p><details><summary>Separate software example</summary><button onClick={()=>select('demo')}>Load synthetic example</button></details></section>}
 <footer className="cv-footer">Unsaved work remains in this tab, including navigation/remounts; a full page reload clears it. Manual estimates are not independently reviewed. Cancellation may not immediately stop server work.</footer></main>{confirmation&&<Confirm value={confirmation} close={()=>setConfirmation(null)}/>}</div>;
}
