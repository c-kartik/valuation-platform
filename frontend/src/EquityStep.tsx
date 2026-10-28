import {useEffect,useRef,useState} from 'react';
import {request,ApiError,failureMessage} from './api';
import {useExecutionGate} from './execution';
import {executeCase,requireMatchingEquity} from './caseExecution';
import type {ExecutionGate} from './execution';
import {InputErrors} from './model';
import type {Draft,Result,Errors} from './model';
import {emptyEquity,equityErrors,buildEquityRequest,equityDiagnostics} from './equity';
import type {EquityDraft} from './equity';
import {EquityFields,EquityReview,equityAdvancedFields,equityFieldLabels} from './EquityFields';

type Props={draft:Draft;evResult:Result;operatingStale:boolean;load?:typeof request;executionGate?:ExecutionGate};
export function EquityStep({draft,evResult,operatingStale,load=request,executionGate}:Props){
 const [open,setOpen]=useState(false),[advanced,setAdvanced]=useState(false),[componentsOpen,setComponentsOpen]=useState(false);
 const [values,setValues]=useState(emptyEquity),[submitted,setSubmitted]=useState(false),[serverErrors,setServerErrors]=useState<Errors>({});
 const [equity,setEquity]=useState<Result|null>(null),[stale,setStale]=useState(false),[failure,setFailure]=useState('');
 const {gate,action}=useExecutionGate(executionGate);
 const busy=action==='equity';
 const sequence=useRef(0),current=useRef({evResult,operatingStale});current.current={evResult,operatingStale};
 useEffect(()=>{sequence.current++;gate.cancel('equity');setStale(true);},[evResult,operatingStale]);
 useEffect(()=>()=>{sequence.current++;gate.cancel('equity');},[]);
 function edit<K extends keyof EquityDraft>(key:K,value:EquityDraft[K]){
  sequence.current++;gate.cancel('equity');setStale(true);setFailure('');setServerErrors({});setValues(old=>({...old,[key]:value}));
 }
 const errors=submitted?{...serverErrors,...equityErrors(values,draft.doc.anchor.annual_end)}:{};
 function focusError(key:string){
  setOpen(true);if(equityAdvancedFields.includes(key))setAdvanced(true);
  if(key==='components'||/^(overlap|alternative)/.test(key))setComponentsOpen(true);
  requestAnimationFrame(()=>{const target=document.getElementById(`equity.${key}`)??document.getElementById('equity.issues');target?.focus();});
 }
 async function calculate(){
  if(gate.snapshot())return;
  setSubmitted(true);setFailure('');setServerErrors({});
  const local=equityErrors(values,draft.doc.anchor.annual_end);
  if(Object.keys(local).length){focusError(Object.keys(local)[0]);return;}
  if(operatingStale)return;
  const token=++sequence.current,selectedEV=evResult;
  setStale(true);
  try{
   const response=await executeCase<Result>({gate,action:'equity',load,build:()=>buildEquityRequest(draft,values),current:()=>token===sequence.current&&current.current.evResult===selectedEV&&!current.current.operatingStale,check:value=>requireMatchingEquity(value,selectedEV)});
   if(!response)return;
   setEquity(response);setStale(false);
  }catch(error){
   if(token!==sequence.current)return;
   if(error instanceof InputErrors){setServerErrors(error.fields);focusError(Object.keys(error.fields)[0]);}
   else if(error instanceof ApiError&&error.code==='invalid_case'){
    const mapped=equityDiagnostics(error.details,values);
    setServerErrors(mapped);focusError(Object.keys(mapped)[0]);
   }else setFailure(failureMessage(error));
  }
 }
 return <section className="equity-step" aria-label="Optional equity and shares">
  <details open={open} onToggle={e=>setOpen(e.currentTarget.open)}><summary>Add cash, debt &amp; shares</summary>
   <p className="hint">Optional second step. Manual, unverified inputs; closing keeps edits in this session only. EV remains available without them.</p>
   <EquityFields values={values} errors={errors} edit={edit} anchorDate={draft.doc.anchor.annual_end} advanced={advanced} setAdvanced={setAdvanced} componentsOpen={componentsOpen} setComponentsOpen={setComponentsOpen}/>
   {operatingStale&&<p className="errors" role="status">Operating inputs changed. Recalculate enterprise value before calculating value per share.</p>}
   <button disabled={Boolean(action)||operatingStale} onClick={()=>void calculate()}>Calculate value per share</button>
   {busy&&<p role="status">Calculating the submitted operating case and bridge…</p>}
   {Object.keys(errors).length>0&&<div className="errors" id="equity.issues" tabIndex={-1} role="region" aria-label="Equity input issues"><h3>Equity result needs input review; EV is retained</h3><ul>{Object.entries(errors).map(([key,message])=><li key={key}><button className="text-button" onClick={()=>focusError(key)}>{equityFieldLabels[key]??key}: {message}</button></li>)}</ul></div>}
   {failure&&<div className="errors" role="status" aria-live="polite">{failure}<button disabled={Boolean(action)||operatingStale} onClick={()=>void calculate()}>Retry value per share</button></div>}
  </details>
  {equity?.stage_c&&<EquityReview result={equity} stale={stale||operatingStale}/>}
 </section>;
}
