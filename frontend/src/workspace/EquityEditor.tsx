import {useEffect,useRef,useState} from 'react';
import {EquityFields,equityAdvancedFields,equityFieldLabels} from '../EquityFields';
import {equityErrors,millionsToUnits} from '../equity';
import type {EquityDraft} from '../equity';
import type {Errors,Result} from '../model';
import {display} from '../model';
import {readableMoney,shareMillions} from '../presentation';
import type {Outcome} from './useWorkspace';
import './equityEditor.css';

/** Display server-returned amounts only; no browser-side valuation preview. */
function Breakdown({ev,outcome,dirty,operatingCurrent}:{ev:Result|null;outcome:Outcome;dirty:boolean;operatingCurrent:boolean}){
 const c=outcome.result?.stage_c,stale=dirty||outcome.phase!=='current'||!operatingCurrent;
 return <section id="equity-editor-breakdown" tabIndex={-1} className="cw-equity-breakdown" aria-label="Enterprise value to value per share"><h3>From business value to one share</h3>
 <p>{c?(stale?'Previous calculation · recalculate before use':'Submitted calculation · manual inputs'):'Enter the inputs, then calculate to see the breakdown.'}</p>
 <dl>{[['Enterprise value',c?c.stage_b.enterprise_value:ev?.stage_b.enterprise_value],['+ Cash & investments',c?.eligible_assets],['− Debt',c?.financing_claims],['− Other claims',c?.other_equity_claims],['= Equity value',c?.equity_value]].map(([label,value])=><div key={label}><dt>{label}</dt><dd>{value===undefined?'—':readableMoney(value)}</dd></div>)}
 <div><dt>÷ Shares (millions)</dt><dd>{c?shareMillions(c.valuation_shares):'—'}</dd></div>
 <div className="cw-equity-total"><dt>= Value per share (USD)</dt><dd>{c?display(c.value_per_share,'1',2):'—'}</dd></div></dl>
 {c&&<><p>Selected share population; not fully diluted fair value or complete claims coverage.</p>{c.inputs.observations.some(o=>o.disposition==='OMISSION')&&<p className="cw-equity-warning">Provisional result: some claims or populations are omitted and their effect is unbounded.</p>}<details><summary>Calculation basis &amp; exact values</summary><p>{c.inputs.shares.class_id} · {c.inputs.shares.observation_date}. {c.inputs.shares.rationale}</p><ul>{c.inputs.observations.filter(o=>o.disposition==='OMISSION').map(o=><li key={o.observation_id}>{o.rationale}</li>)}</ul><p>Enterprise value: {c.stage_b.enterprise_value} USD<br/>Equity value: {c.equity_value} USD<br/>Shares: {c.valuation_shares}<br/>Value per share: {c.value_per_share} USD/share</p><ul>{c.contributions.map(line=><li key={line.component.component_id}>{line.component.component_id}: {line.signed_contribution} USD</li>)}</ul></details></>}
 </section>;
}
export function EquityEditor({company,label,initial,anchorDate,ev,outcome,operatingCurrent,busy,save,calculate,cancel,close}:{company:string;label:string;initial:EquityDraft;anchorDate:string;ev:Result|null;outcome:Outcome;operatingCurrent:boolean;busy:string|null;save:(draft:EquityDraft)=>void;calculate:(draft:EquityDraft)=>Promise<void>;cancel:()=>void;close:()=>void}){
 const [draft,setDraft]=useState(()=>structuredClone(initial)),[errors,setErrors]=useState<Errors>({});
 const [advanced,setAdvanced]=useState(false),[componentsOpen,setComponentsOpen]=useState(false),[running,setRunning]=useState(false);
 const dialog=useRef<HTMLDialogElement>(null),opener=useRef(document.activeElement as HTMLElement|null),mounted=useRef(true);
 const previousPhase=useRef(outcome.phase);
 const dirty=JSON.stringify(draft)!==JSON.stringify(initial);
 useEffect(()=>{
  if(outcome.phase==='current'&&previousPhase.current!=='current'){
   setAdvanced(false);requestAnimationFrame(()=>document.getElementById('equity-editor-breakdown')?.focus());
  }
  previousPhase.current=outcome.phase;
 },[outcome.phase]);
 function focus(key:string){
  if(key==='date'||equityAdvancedFields.includes(key)||key==='components'||/^(overlap|alternative)/.test(key))setAdvanced(true);
  if(key==='components'||/^(overlap|alternative)/.test(key))setComponentsOpen(true);
  requestAnimationFrame(()=>{const target=document.getElementById(`equity.${key}`)??document.getElementById('equity-editor-issues');target?.focus();});
 }
 useEffect(()=>{
  mounted.current=true;const d=dialog.current!,body=document.body,scroll=window.scrollY,previous={position:body.style.position,top:body.style.top,width:body.style.width};
  Object.assign(body.style,{position:'fixed',top:`-${scroll}px`,width:'100%'});d.showModal();document.getElementById('equity.assets')?.focus();
  return()=>{mounted.current=false;d.close();Object.assign(body.style,previous);window.scrollTo(0,scroll);if(opener.current?.isConnected)opener.current.focus({preventScroll:true});};
 },[]);
 useEffect(()=>{setErrors(outcome.errors);const first=Object.keys(outcome.errors)[0];if(first)focus(first);},[outcome.errors]);
 function edit<K extends keyof EquityDraft>(key:K,value:EquityDraft[K]){setDraft(d=>({...d,[key]:value}));setErrors({});}
 function saveDraft(){
  const issues:Errors={};for(const key of ['assets','financing','shares',...(draft.claimsTreatment==='amount'?['claims']as const:[])]as const)try{millionsToUnits(draft[key]);}catch(error){issues[key]=(error as Error).message;}
  if(Object.keys(issues).length){setErrors(issues);focus(Object.keys(issues)[0]);return;}save(draft);close();
 }
 async function run(){
  const issues=equityErrors(draft,anchorDate);if(Object.keys(issues).length){setErrors(issues);focus(Object.keys(issues)[0]);return;}
  setErrors({});setRunning(true);try{await calculate(draft);}finally{if(mounted.current)setRunning(false);}
 }
 function dismiss(){if(running||busy==='equity')cancel();close();}
 const pending=running||Boolean(busy);
 return <dialog ref={dialog} className="cv-editor cv-bridge-editor cw-equity-editor" aria-label={`Edit ${company} ${label} cash, debt and shares`} onCancel={e=>{e.preventDefault();dismiss();}}>
 <header><div><span className="cv-eyebrow">{company} · {label} case</span><h2>Cash, debt &amp; shares</h2></div><button type="button" onClick={dismiss} aria-label="Close editor without applying">×</button></header>
 <div className="cv-editor-context"><b>Enterprise value {ev?readableMoney(ev.stage_b.enterprise_value):'not calculated'}{ev&&!operatingCurrent?' · Previous calculation':''}</b><small>Amounts in USD millions · shares in millions · as of {anchorDate}</small></div>
 <div className="cv-editor-body"><p className="cw-equity-intro">Turn the value of the business into the value of one share. These are your manual entries; blank is not zero.</p>
 <fieldset disabled={pending} className="cw-equity-fields"><legend className="cw-sr-only">Cash, debt and share inputs</legend><EquityFields simple values={draft} errors={errors} edit={edit} anchorDate={anchorDate} advanced={advanced} setAdvanced={setAdvanced} componentsOpen={componentsOpen} setComponentsOpen={setComponentsOpen}/></fieldset>
 {Object.keys(errors).length>0&&<div id="equity-editor-issues" tabIndex={-1} className="cw-equity-issues" role="region" aria-label="Equity input issues"><h3>Complete the required details</h3>{Object.entries(errors).map(([key,message])=><button key={key} onClick={()=>focus(key)}>{equityFieldLabels[key]??'Bridge input'}: {message}</button>)}</div>}
 {!operatingCurrent&&<p className="cw-equity-warning">Update the operating assumptions to calculate a current enterprise value first.</p>}
 {outcome.failure&&<p className="cw-equity-warning" role="status">{outcome.failure} Your entries are retained. Use Calculate to retry.</p>}
 {pending&&<p role="status">{busy==='equity'||running?'Calculating value per share…':'Another calculation is in progress…'}</p>}
 <Breakdown ev={ev} outcome={outcome} dirty={dirty} operatingCurrent={operatingCurrent}/>
 <p className="cw-equity-save-note">Save inputs keeps an incomplete draft. Calculate saves the inputs and updates the breakdown after checking the required details.</p>
 </div><footer><button type="button" onClick={dismiss}>{running?'Cancel calculation':'Cancel'}</button><button type="button" disabled={pending} onClick={saveDraft}>Save inputs</button><button type="button" className="cv-primary" disabled={pending||!operatingCurrent} onClick={()=>void run()}>Calculate value per share</button></footer>
 </dialog>;
}
