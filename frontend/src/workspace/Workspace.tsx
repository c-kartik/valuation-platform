import {useState} from 'react';
import {request} from '../api';
import {readableMoney} from '../presentation';
import {equityErrors} from '../equity';
import {useWorkspace} from './useWorkspace';
import {ForwardEditor} from './ForwardEditor';
import {BridgePanel} from './BridgePanel';
import {Confirm} from './Confirm';
import {ScenariosPanel} from './ScenariosPanel';
import {SensitivityPanel} from './SensitivityPanel';
import {smallGrid} from './sensitivity';
import {InvestorResult} from './InvestorResult';
import {Sources} from './Sources';
import type {Confirmation} from './Confirm';
export function Workspace({load=request}:{load?:typeof request}){
 const w=useWorkspace(load),{catalog,state,session:c}=w;
 const [view,setView]=useState<'valuation'|'scenarios'|'sensitivity'>('valuation'),[confirmation,setConfirmation]=useState<Confirmation|null>(null),[bridge,setBridge]=useState(false);
 const entry=catalog?.entries.find(e=>e.kind===state.selected),context=entry?.financial_context;
 const name=entry?.company??(state.selected==='demo'?'Synthetic demonstration':'Investor calculator');
 const current=c?.ev.phase==='current',equityCurrent=current&&c?.equity.phase==='current',result=equityCurrent?c.equity.result:c?.ev.result;
 const eligibleEquity=c?Object.keys(equityErrors(c.bridge,c.draft.doc.anchor.annual_end)).length===0:false;
 function navigate(next:typeof view){setView(next);requestAnimationFrame(()=>document.getElementById('investor-view-title')?.focus());}
 function select(kind:string){w.select(kind);setView('valuation');setBridge(false);setConfirmation(null);}
 function generate(){if(!c)return;try{const values=smallGrid(c.draft);for(const [k,v] of Object.entries(values))w.editGrid(k as keyof typeof values,v);}catch{}}
 function compare(){if(!c)return;if(c.scenarioEquity!==eligibleEquity)w.configureSet('scenarioEquity',eligibleEquity);void w.calculateScenarios();}
 return <div className="investor-prototype investor-workspace investor-review"><a className="p-skip" href="#w-main">Skip to calculator</a><nav className="p-topbar" aria-label="Investor calculator"><span className="p-brand">K<span>.</span> Chaturvedi</span><span>Investor calculator</span><span className="p-session">Unsaved · this browser tab only</span></nav><main className="p-shell" id="w-main">
 <header className="p-case-header"><div className="p-company"><span className="p-monogram">{entry?.company[0]??'V'}</span><div><span className="p-eyebrow">MANUAL FCFF VALUATION</span><h1>{name}</h1>{entry&&<><p>Calculation anchor: FY2025 revenue {readableMoney(entry.revenue)} · fiscal end {entry.identity.annual_end}</p>{context?<p className="p-freshness">Financials through {context.financials_through} · Filed {context.filed} · Checked {context.checked_at.replace('T',' ').slice(0,19)} UTC</p>:<p>Latest financial context unavailable; this retained anchor is not labeled current.</p>}</>}{context&&<p className="p-qualification">Newer filing available; valuation preparation incomplete. Calculation still uses the retained fiscal-end anchor.</p>}</div></div><div className="w-company-picker"><label htmlFor="w-company">Company</label><select id="w-company" value={state.selected==='demo'?'':state.selected} disabled={!catalog} onChange={e=>select(e.target.value)}><option value="">Select a company</option>{catalog?.entries.map(e=><option key={e.kind} value={e.kind}>{e.company}</option>)}</select></div></header>
 {!catalog&&<div className="p-notice" role="status">{w.catalogFailure?<><p>{w.catalogFailure}</p><button onClick={w.retryCatalog}>Retry loading companies</button></>:'Loading financial data…'}</div>}
 {c?<><div className="p-tabs ir-main-tabs" aria-label="Investor workflow">{(['valuation','scenarios','sensitivity'] as const).map(v=><button key={v} aria-current={view===v?'page':undefined} className={view===v?'w-active':''} onClick={()=>navigate(v)}>{v[0].toUpperCase()+v.slice(1)}</button>)}</div><h2 className="ir-sr" id="investor-view-title" tabIndex={-1}>{name} {view}</h2>
 {view==='valuation'?<><ForwardEditor label={c.selectedCase} key={state.selected+c.selectedCase} draft={c.draft} change={w.editDraft} outcome={c.ev} busy={w.busy} calculate={()=>void w.calculate('ev')} cancel={w.cancel} confirm={setConfirmation}/>
 {result&&<InvestorResult result={result} stale={!current} marketStale={Boolean(result.stage_c)&&!equityCurrent}/>}
 <section className="p-panel ir-optional-bridge"><h3>Optional equity & value per share</h3><p>EV values the operating business. Add dated eligible assets, financing, claims and shares for a separate, scope-qualified equity reference.</p><button onClick={()=>setBridge(v=>!v)} aria-expanded={bridge}>{bridge?'Hide cash, claims & shares':'Add cash, claims & shares'}</button>{bridge&&<BridgePanel key={state.selected} values={c.bridge} outcome={c.equity} anchorDate={c.draft.doc.anchor.annual_end} operatingCurrent={Boolean(current)} busy={w.busy} edit={w.editBridge} calculate={()=>void w.calculate('equity')} cancel={w.cancel}/>}</section></>:view==='scenarios'?<ScenariosPanel company={w.company!} busy={w.busy} editRate={w.editScenarioRate} reset={w.resetOverrides} calculate={compare} cancel={w.cancel} confirm={setConfirmation} eligibleEquity={eligibleEquity}/>:<SensitivityPanel label={c.selectedCase} caseName={c.draft.doc.case_name} grid={c.grid} sourceStatus={c.ev.phase} busy={w.busy} edit={w.editGrid} calculate={()=>void w.calculateSensitivity()} cancel={w.cancel} inspect={w.inspectCell} apply={w.applyCell} confirm={setConfirmation} review={()=>navigate('valuation')} generate={generate}/>}
 <Sources entry={entry} result={result}/>
 </>:catalog&&<section className="p-panel w-empty"><h2>Select a company to begin</h2><p>Review the financial basis, enter your own forecast, and calculate. Company assumptions start unset.</p><details><summary>Try a separate software example</summary><p>Synthetic economics on a USD100 synthetic company; not a company forecast or market quote.</p><button onClick={()=>select('demo')}>Load separate synthetic demonstration</button></details></section>}
 <footer className="p-footer"><p>Unsaved work stays in this tab. Reloading or closing it loses your inputs. Browser cancellation does not guarantee immediate server cancellation.</p></footer></main>{confirmation&&<Confirm value={confirmation} close={()=>setConfirmation(null)}/>}</div>;
}
