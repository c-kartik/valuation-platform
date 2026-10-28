import {useEffect,useRef,useState} from 'react';
import {request,ApiError,Revisions,failureMessage} from '../api';
import {useExecutionGate} from '../execution';
import {executeCase,requireMatchingEquity} from '../caseExecution';
import {makeDraft,buildRequest,entryErrors,InputErrors,fieldErrors} from '../model';
import type {Catalog,CaseDoc,Draft,Errors,Result} from '../model';
import {emptyEquity,equityErrors,buildEquityRequest,equityDiagnostics} from '../equity';
import type {EquityDraft} from '../equity';
import {percentageDiagnostic} from '../diagnostics';
export type Phase='empty'|'incomplete'|'calculating'|'current'|'stale'|'failed';
export type Outcome={phase:Phase;result:Result|null;errors:Errors;failure:string};
export type Session={draft:Draft;bridge:EquityDraft;revision:number;bridgeRevision:number;ev:Outcome;equity:Outcome;comparison:{price:string;date:string}};
type State={selected:string;cases:Record<string,Session>};
const emptyOutcome=():Outcome=>({phase:'empty',result:null,errors:{},failure:''});
const invalidate=(o:Outcome):Outcome=>({...o,phase:o.result?'stale':'incomplete',errors:{},failure:''});
export function createSession(template:CaseDoc):Session{return {draft:makeDraft(template),bridge:emptyEquity(),revision:1,bridgeRevision:1,ev:emptyOutcome(),equity:emptyOutcome(),comparison:{price:'',date:''}};}
export function useWorkspace(load:typeof request=request){
 const [catalog,setCatalog]=useState<Catalog|null>(null),[catalogFailure,setCatalogFailure]=useState(''),[attempt,setAttempt]=useState(0);
 const [state,setState]=useState<State>({selected:'',cases:{}}),live=useRef(state);live.current=state;
 const {gate,action}=useExecutionGate(),evRevision=useRef(new Revisions()),equityRevision=useRef(new Revisions());
 function update(fn:(s:State)=>State){const next=fn(live.current);live.current=next;setState(next);}
 function changeCase(kind:string,fn:(s:Session)=>Session){update(old=>({...old,cases:{...old.cases,[kind]:fn(old.cases[kind])}}));}
 useEffect(()=>{const abort=new AbortController();setCatalogFailure('');load<Catalog>('/api/v1/catalog',undefined,abort.signal).then(data=>{if(!abort.signal.aborted)setCatalog(data);}).catch(error=>{if(!abort.signal.aborted)setCatalogFailure(failureMessage(error));});return()=>abort.abort();},[load,attempt]);
 useEffect(()=>()=>{evRevision.current.edit();equityRevision.current.edit();gate.cancel();},[]);
 function select(kind:string){
  if(!catalog||kind===live.current.selected)return;
  const template=kind==='demo'?catalog.synthetic_demo:catalog.entries.find(e=>e.kind===kind)?.template;
  if(kind&&!template)return;
  evRevision.current.edit();equityRevision.current.edit();gate.cancel();
  update(old=>{const cases={...old.cases};if(cases[old.selected]){const c=cases[old.selected];cases[old.selected]={...c,ev:c.ev.phase==='calculating'?invalidate(c.ev):c.ev,equity:c.equity.phase==='calculating'?invalidate(c.equity):c.equity};}if(template&&!cases[kind])cases[kind]=createSession(template);return {selected:kind,cases};});
 }
 function editDraft(draft:Draft,financial=true){
  const kind=live.current.selected;if(!kind)return;
  if(financial){evRevision.current.edit();equityRevision.current.edit();gate.cancel();}
  changeCase(kind,c=>({...c,draft,revision:c.revision+(financial?1:0),ev:financial?invalidate(c.ev):c.ev,equity:financial?invalidate(c.equity):c.equity}));
 }
 function editBridge<K extends keyof EquityDraft>(key:K,value:EquityDraft[K]){
  const kind=live.current.selected;if(!kind)return;equityRevision.current.edit();gate.cancel('equity');
  changeCase(kind,c=>({...c,bridge:{...c.bridge,[key]:value},bridgeRevision:c.bridgeRevision+1,equity:invalidate(c.equity)}));
 }
 function editComparison(key:'price'|'date',value:string){const kind=live.current.selected;if(kind)changeCase(kind,c=>({...c,comparison:{...c.comparison,[key]:value}}));}
 async function calculate(scope:'ev'|'equity'){
  const kind=live.current.selected,c=live.current.cases[kind];if(!c||gate.snapshot())return;
  if(scope==='equity'&&(c.ev.phase!=='current'||!c.ev.result))return;
  const revisions=scope==='ev'?evRevision.current:equityRevision.current,token=revisions.begin();
  const current=()=>revisions.current(token)&&live.current.selected===kind;
  changeCase(kind,s=>({...s,[scope]:{...s[scope],phase:'calculating',errors:{},failure:''}}));
  try{
   const response=await executeCase<Result>({gate,action:scope,load,current,build:()=>{
    const local=entryErrors(c.draft);if(Object.keys(local).length)throw new InputErrors(local);
    if(scope==='equity'){const errors=equityErrors(c.bridge,c.draft.doc.anchor.annual_end);if(Object.keys(errors).length)throw new InputErrors(errors);return buildEquityRequest(c.draft,c.bridge);}
    return buildRequest(c.draft);
   },check:value=>{
    for(const [key,expected] of Object.entries(c.draft.doc.anchor))if(value.submitted_inputs.anchor[key as keyof typeof c.draft.doc.anchor]!==expected)throw new Error('Returned anchor did not match submitted case.');
    if(scope==='equity')requireMatchingEquity(value,c.ev.result!);
   }});
   if(!response||!current())return;
   changeCase(kind,s=>({...s,[scope]:{phase:'current',result:response,errors:{},failure:''}}));
  }catch(error){
   if(!current())return;
   const errors=error instanceof InputErrors?error.fields:error instanceof ApiError&&error.code==='invalid_case'?(scope==='ev'?fieldErrors(error.details.map(percentageDiagnostic)):equityDiagnostics(error.details,c.bridge)):{};
   changeCase(kind,s=>({...s,[scope]:{...s[scope],phase:Object.keys(errors).length?'incomplete':'failed',errors,failure:Object.keys(errors).length?'':failureMessage(error)}}));
  }
 }
 return {catalog,catalogFailure,retryCatalog:()=>setAttempt(n=>n+1),state,session:state.cases[state.selected],select,editDraft,editBridge,editComparison,calculate,cancel:()=>gate.cancel(),busy:action};
}
