import {useEffect,useRef,useState} from 'react';
import {request} from '../api';
import {entryErrors,methodOf} from '../model';
import type {Draft,Errors} from '../model';
import {readableMoney,fixedUnit,terminalContribution} from '../presentation';
import {equityErrors} from '../equity';
import type {EquityDraft} from '../equity';
import {EquityReview} from '../EquityFields';
import {useWorkspace} from './useWorkspace';
import {Confirm} from './Confirm';
import type {Confirmation} from './Confirm';
import {ScenariosPanel} from './ScenariosPanel';
import {SensitivityPanel} from './SensitivityPanel';
import {reviewGrid,ratePercent} from './sensitivity';
import {profileGrid} from './preload';
import {PreloadReview} from './PreloadReview';
import {FullModel} from './FullModel';
import {ForecastChart} from './ForecastChart';
import {Sources} from './Sources';
import {MarketPanel} from './MarketPanel';
import {ExportData} from './ExportData';
import {EquityEditor} from './EquityEditor';
import {ModelEditor} from './ModelEditor';
import {TerminalComparison} from './TerminalComparison';
import {ValuationBreakdown} from './ValuationBreakdown';
import type {Label} from './scenarios';
import './canvas.css';
import './inline.css';
import './resultFirst.css';
import './compact.css';
import './chartInspection.css';
import type {ChartInspection} from './chartInspection';
import {CompactSidebar} from './CompactSidebar';
const companyNames:Record<string,string>={META:'Meta Platforms',GOOGL:'Alphabet',AAPL:'Apple'};
export function Workspace({load=request}:{load?:typeof request}){
 const w=useWorkspace(load),{catalog,state,session:c}=w;
 const [confirmation,setConfirmation]=useState<Confirmation|null>(null),[editor,setEditor]=useState<'model'|'bridge'|null>(null);
 const [view,setView]=useState<'dcf'|'scenarios'|'sensitivity'|'model'|'sources'>('dcf'),[focusPath,setFocusPath]=useState<string>(),[seed,setSeed]=useState<Draft>(),[seedPaths,setSeedPaths]=useState<string[]>([]);
 const [inspection,setInspection]=useState<{company:string;label:string;value:ChartInspection}|null>(null);
 const activeInspection=view==='dcf'&&!editor&&inspection?.company===state.selected&&inspection.label===c?.selectedCase?inspection.value:null;
 useEffect(()=>setInspection(null),[state.selected,c?.selectedCase,view]);
 const attempts=useRef(new Set<string>());
 const entry=catalog?.entries.find(e=>e.kind===state.selected),ticker=entry?.company??(state.selected==='demo'?'Synthetic':''),name=companyNames[ticker]??ticker;
 const current=c?.ev.phase==='current',equityCurrent=current&&c?.equity.phase==='current',result=(equityCurrent?c?.equity.result:c?.ev.result)??null;
 const estimateYear=c?.resultProfile?.economic.dates.information_review.slice(0,4);
 const currentYearEstimate=result?.stage_b.stage_a.years.find(y=>y.fiscal_year_label===`FY${estimateYear}`);
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
  if(view==='scenarios'&&!['current','failed','calculating'].includes(c.scenario.phase)&&!attempts.current.has('scenario'+key)&&['Bear','Base','Bull'].every(l=>!Object.keys(entryErrors(w.company!.cases[l]!.draft)).length)){
   attempts.current.add('scenario'+key);compare();return;
  }
  if(view==='sensitivity'&&suggestedSettings&&!['current','failed','calculating'].includes(c.grid.phase)&&!attempts.current.has('grid'+key)){
   attempts.current.add('grid'+key);calculateGrid();
  }
 },[state.selected,c?.selectedCase,c?.revision,c?.ev.phase,c?.scenario.phase,c?.grid.phase,w.busy,view,editor]);
 function select(kind:string){w.select(kind);setEditor(null);setConfirmation(null);}
 function openEditor(path?:string){setSeed(undefined);setSeedPaths([]);setFocusPath(path);setEditor('model');}
 function editCase(label:Label){w.selectCase(label);openEditor();}
 function reviewPair(){if(!c||!current||c.grid.phase!=='current'||!c.grid.inspected)return;const cell=c.grid.result?.cells[c.grid.inspected[0]]?.[c.grid.inspected[1]];if(cell?.status!=='VALID')return;const d=structuredClone(c.draft),path=methodOf(d)==='exit_multiple'?'exit_ev_ebit_multiple':'terminal_growth';d.rates.wacc=ratePercent(cell.wacc);d.rates[path]=cell.exit_ev_ebit_multiple??ratePercent(cell.terminal_growth!);setSeed(d);setSeedPaths(['wacc',path]);setFocusPath('wacc');setEditor('model');}
 function applyBridge(bridge:EquityDraft){if(c)for(const key of Object.keys(bridge)as (keyof EquityDraft)[])if(bridge[key]!==c.bridge[key])w.editBridge(key,bridge[key]);}
 const method=c?methodOf(c.draft):'perpetual_growth',missing=c?Object.entries(entryErrors(c.draft)):[],loading=c?.preload?.status==='loading'||c?.ev.phase==='calculating';
 const status=editor==='model'?'Editing draft · previous submitted result retained':loading?'Preparing the starting calculation…':c?.ev.phase==='failed'?'Calculation failed · entries preserved':current?'Current calculation · inputs remain unreviewed':result?'Previous calculation · stale':missing.length?'Required inputs remain unset':'Ready to calculate';
 const evValue=current&&result?readableMoney(result.stage_b.enterprise_value):result&&(result.stage_b.terminal_method??'perpetual_growth')===method?readableMoney(result.stage_b.enterprise_value):loading?'Calculating…':'Inputs required';
 return <div className="investor-prototype investor-workspace valuation-canvas cv-result-first cw-workspace"><a className="p-skip" href="#valuation-main">Skip to calculator</a>
 <div className="cw-company-bar" role="region" aria-label="Company selection"><div className="cv-company-tools"><label htmlFor="canvas-company">Company</label><select id="canvas-company" value={state.selected==='demo'?'':state.selected} disabled={!catalog} onChange={e=>select(e.target.value)}><option value="">Select a company</option>{catalog?.entries.map(e=><option value={e.kind} key={e.kind}>{e.company} · {companyNames[e.company]??e.company}</option>)}</select></div></div>
 <main id="valuation-main" className="cv-page"><header className="cv-company"><div><h1>{name||'Company valuation'} {ticker&&<small>{ticker}</small>} <span className="cw-model-badge">FCFF model</span></h1>{entry&&<p>FCFF valuation · {entry.identity.annual_end} fiscal-end anchor · later-filed information</p>}{c?.preload?.profile&&<small>Proposed starting estimates{c.draft.doc.forecast_years.length===10?' for years 1–5':''} · reviewed {c.preload.profile.economic.dates.information_review}.</small>}{currentYearEstimate&&<section className="cw-current-estimate" aria-label="Current-year model estimate"><h2>{currentYearEstimate.fiscal_year_label}E · Current-year estimate</h2><dl><div><dt>Revenue</dt><dd title={currentYearEstimate.revenue+' USD'}>{fixedUnit(String(currentYearEstimate.revenue),'1000000000',2)}B</dd></div><div><dt>FCFF</dt><dd title={currentYearEstimate.fcff+' USD'}>{fixedUnit(String(currentYearEstimate.fcff),'1000000000',2)}B</dd></div></dl><small>{c?.selectedCase} · {current?'Submitted model estimate':'Previous submitted estimate · stale'} · reported anchor FY{result?.submitted_inputs.anchor.annual_end.slice(0,4)}</small></section>}</div>{c&&<section className="cw-value cw-header-value" aria-label="Valuation summary" data-chart-inspection={activeInspection??undefined}><span>Enterprise value · {c.selectedCase}</span><strong className="cv-ev">{evValue}</strong><small>Operating business value · {method==='exit_multiple'?'Exit multiple':'Perpetual growth'}</small><p role="status">{status}</p><div className="cw-value-cases"><div className="cv-segments" role="group" aria-label="Selected scenario">{(['Bear','Base','Bull']as const).map(label=><button aria-pressed={c.selectedCase===label} key={label} onClick={()=>w.selectCase(label)}>{label}</button>)}</div>{w.busy&&<button className="cw-cancel-calculation" onClick={w.cancel}>Cancel calculation</button>}</div><button className="cw-equity-settings" onClick={()=>setEditor('bridge')}>Equity &amp; per-share settings <span>{eligibleEquity?'Declared':'Not set'} ›</span></button></section>}</header>
 {!catalog&&<p role="status">{w.catalogFailure?<>{w.catalogFailure} <button onClick={w.retryCatalog}>Retry loading companies</button></>:'Loading companies…'}</p>}
 {c?<>
 <div className="cw-layout"><CompactSidebar key={state.selected+c.selectedCase} inspection={activeInspection} inspect={value=>setInspection(value?{company:state.selected,label:c.selectedCase,value}:null)} draft={c.draft} result={result} stale={!current} edit={openEditor} sources={()=>setView('sources')}/><div className="cw-main">
 <nav className="cw-nav" aria-label="Explore this valuation">{([['dcf','DCF','dcf'],['scenarios','Scenarios','scenario-comparison'],['sensitivity','Sensitivity','sensitivity'],['model','Full Model','full-model'],['sources','Sources','sources-methodology']]as const).map(([key,label,id])=><a key={key} href={'#'+id} aria-current={view===key?'page':undefined} onClick={e=>{e.preventDefault();setView(key);}}>{label}</a>)}</nav>
 <section hidden={view!=='dcf'} id="dcf" className="cv-analysis-section cv-dcf-section" aria-labelledby="dcf-heading"><h2 id="dcf-heading" className="cw-sr-only">DCF · {c.selectedCase}</h2>
 {(Object.keys(issues).length>0||missing.length>0)&&!loading&&<details className="cv-issues" open={method==='exit_multiple'&&!c.draft.rates.exit_ev_ebit_multiple||undefined}><summary>{missing.length||Object.keys(issues).length} inputs require review</summary>{Object.entries({...Object.fromEntries(missing),...issues}).map(([p,m])=><p key={p}><button onClick={()=>p.startsWith('bridge.')?setEditor('bridge'):openEditor(p)}>{p}: {m}</button></p>)}<button onClick={()=>openEditor()}>Enter required assumptions</button></details>}
 {c.ev.failure&&<p className="cv-issues" role="status">{c.ev.failure} <button disabled={Boolean(w.busy)} onClick={()=>void w.calculate('ev')}>Retry enterprise value</button></p>}{c.preload?.failure&&<p role="status">{c.preload.failure} <button onClick={()=>void w.refreshPreload(true)}>Retry starting profile</button></p>}
 {result?<><ForecastChart cases={[{label:c.selectedCase,result}]} entry={entry} inspection={activeInspection} stale={!current}/></>:<p className="cv-compact-loading" role="status">{loading?`Loading source-bound inputs and calculating ${c.selectedCase}…`:'No forecast result. Open Edit all assumptions to complete the model.'}</p>}
 <div className="cv-chart-footer"><span>{c.draft.doc.anchor.annual_end} fiscal-end analytical model · later-filed information</span>{result&&<ExportData value={{workspace_case:c.selectedCase,input_revision:equityCurrent?c.equity.inputRevision:c.ev.inputRevision,status:current?'current':'stale',calculation:result,preload_profile:c.resultProfile??null,user_overrides:c.resultOverrides??[]}} name={result.case_name}/>}</div>
 {result&&<div className="cw-reconciliation" data-chart-inspection={activeInspection??undefined}><span>Explicit PV <b>{readableMoney(result.stage_b.pv_explicit_fcff)}</b></span><span>Terminal PV <b>{readableMoney(result.stage_b.pv_terminal_value)}</b></span><span>Terminal / EV <b>{terminalContribution(result.stage_b.pv_terminal_value,result.stage_b.enterprise_value).text}</b></span>{!current&&<small>Previous submitted result · out of date</small>}</div>}</section>
 <section id="full-model" hidden={view!=='model'} className="cv-analysis-section" aria-label={`Full Model · ${c.selectedCase}`}><h2>Full Model · {c.selectedCase}</h2>
 <FullModel draft={c.draft} result={result} stale={!current} revision={equityCurrent?c.equity.inputRevision:c.ev.inputRevision} entry={entry} change={w.editDraft} preload={c.resultProfile?{profile:c.resultProfile,status:'ready',failure:''}:undefined} overrides={c.resultOverrides??[]} label={c.selectedCase} expanded={view==='model'}/></section>
 <section hidden={view!=='scenarios'} id="scenario-comparison" className="cv-analysis-section" aria-labelledby="scenario-heading"><h2 id="scenario-heading">Scenario comparison</h2><ScenariosPanel company={w.company!} entry={entry} busy={w.busy} reset={w.resetOverrides} calculate={compare} cancel={w.cancel} confirm={setConfirmation} eligibleEquity={eligibleEquity} setMethod={w.setTerminalMethod} editCase={editCase}/></section>
 <section hidden={view!=='sensitivity'} id="sensitivity" className="cv-analysis-section" aria-labelledby="sensitivity-heading"><h2 id="sensitivity-heading">Sensitivity · {c.selectedCase}</h2><SensitivityPanel label={c.selectedCase} caseName={c.draft.doc.case_name} grid={c.grid} method={method} configuredDiagnostics={Boolean(c.preload?.profile)} sourceStatus={c.ev.phase} busy={w.busy} edit={w.editGrid} calculate={calculateGrid} cancel={w.cancel} inspect={w.inspectCell} apply={w.applyCell} reviewPair={reviewPair} confirm={setConfirmation} review={()=>openEditor('wacc')} generate={()=>suggestedSettings&&w.configureGrid(suggestedSettings)} suggestedSettings={suggestedSettings} eligibleEquity={eligibleEquity}/></section>
 <section hidden={view!=='sources'} id="sources-methodology" className="cv-analysis-section" aria-labelledby="sources-heading"><h2 id="sources-heading">Sources &amp; methodology</h2>{c.preload&&<PreloadReview label={c.selectedCase} state={c.preload} draft={c.draft} overrides={c.overrides??[]} refresh={()=>void w.refreshPreload()} adopt={w.adoptPreload}/>}{result&&<><ValuationBreakdown result={result} stale={!current}/><TerminalComparison result={result} stale={!current}/></>} <details className="cv-secondary"><summary>Optional equity / market comparison</summary><p>Actual eligibility, claims, classes and awards remain unresolved.</p><button onClick={()=>setEditor('bridge')}>Cash, debt and shares · optional</button><button disabled={!current||Boolean(w.busy)} onClick={()=>void w.calculate('equity')}>Calculate value per share</button>{c.equity.failure&&<p>{c.equity.failure}</p>}{c.equity.result?.stage_c&&<><p>{readableMoney(c.equity.result.stage_c.equity_value)} equity · {fixedUnit(c.equity.result.stage_c.value_per_share)} USD/share</p><EquityReview compact result={c.equity.result} stale={!equityCurrent}/></>}<MarketPanel result={result} stale={!current} compact/></details>
<Sources entry={entry} result={result} preload={c.preload}/></section>
 </div></div>
 {editor==='model'&&<ModelEditor key={state.selected+c.selectedCase} company={ticker} label={c.selectedCase} session={c} initial={seed} initialPaths={seedPaths} focusPath={focusPath} submit={w.updateValuation} close={()=>setEditor(null)}/>}
 {editor==='bridge'&&<EquityEditor key={state.selected+c.selectedCase} company={ticker} label={c.selectedCase} initial={c.bridge} anchorDate={c.draft.doc.anchor.annual_end} ev={c.ev.result} outcome={c.equity} operatingCurrent={Boolean(current)} busy={w.busy} save={applyBridge} calculate={async bridge=>{applyBridge(bridge);await w.calculate('equity');}} cancel={w.cancel} close={()=>setEditor(null)}/>}
 </>:catalog&&<section className="cv-start"><h2>Select a company</h2><p>Registered companies offer editable starting estimates with company-specific sources and assumptions.</p><details><summary>Separate software example</summary><button onClick={()=>select('demo')}>Load synthetic example</button></details></section>}
 <footer className="cv-footer">Unsaved work remains in this tab, including navigation/remounts; a full page reload clears it. Manual estimates are not independently reviewed. Cancellation may not immediately stop server work.</footer></main>{confirmation&&<Confirm value={confirmation} close={()=>setConfirmation(null)}/>}</div>;
}
