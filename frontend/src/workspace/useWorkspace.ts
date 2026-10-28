import {useEffect,useRef,useState} from 'react';
import {request,ApiError,Revisions,failureMessage} from '../api';
import {useExecutionGate} from '../execution';
import {executeCase,requireMatchingEquity} from '../caseExecution';
import {makeDraft,entryErrors,InputErrors,fieldErrors} from '../model';
import type {Catalog,CaseDoc,Draft,Errors,Result} from '../model';
import {emptyEquity,equityErrors,equityDiagnostics} from '../equity';
import type {EquityDraft} from '../equity';
import {percentageDiagnostic} from '../diagnostics';
import {labels,requestFor,scenarioRequest,sameSnapshot} from './scenarios';
import type {Label,ScenarioResult} from './scenarios';
import {newReverse,staleReverse,reverseRequest} from './reverse';
import type {ReverseState,ReverseResult} from './reverse';
import {newGrid,staleGrid,sensitivityRequest,ratePercent} from './sensitivity';
import type {GridState,GridSettings,SensitivityResult} from './sensitivity';
export type Phase='empty'|'incomplete'|'calculating'|'current'|'stale'|'failed';
export type Outcome={phase:Phase;result:Result|null;errors:Errors;failure:string};
export type CaseState={draft:Draft;revision:number;ev:Outcome;equity:Outcome;grid:GridState;reverse:ReverseState;origin?:{kind:string;sourceCase:string;createdAt:string;submitted:unknown}};
export type ScenarioOutcome={phase:Phase;result:ScenarioResult|null;errors:Errors;failure:string;equityCurrent:boolean;previousPhase?:Phase};
export type Session={cases:Record<string,CaseState>&{Base:CaseState};selectedCase:string;bridge:EquityDraft;bridgeRevision:number;comparison:{price:string;date:string};cutoff:string;scenarioEquity:boolean;scenario:ScenarioOutcome};
type State={selected:string;cases:Record<string,Session>};
const emptyOutcome=():Outcome=>({phase:'empty',result:null,errors:{},failure:''});
const invalidate=(o:Outcome):Outcome=>({...o,phase:o.result?'stale':'incomplete',errors:{},failure:''});
const invalidateSet=(o:ScenarioOutcome):ScenarioOutcome=>({...o,phase:o.result?'stale':'incomplete',errors:{},failure:'',equityCurrent:false});
const newCase=(draft:Draft):CaseState=>({draft,revision:1,ev:emptyOutcome(),equity:emptyOutcome(),grid:newGrid(),reverse:newReverse()});
export function createSession(template:CaseDoc):Session{return {cases:{Base:newCase(makeDraft(template))},selectedCase:'Base',bridge:emptyEquity(),bridgeRevision:1,comparison:{price:'',date:''},cutoff:'',scenarioEquity:false,scenario:{phase:'empty',result:null,errors:{},failure:'',equityCurrent:false}};}
export function useWorkspace(load:typeof request=request){
 const [catalog,setCatalog]=useState<Catalog|null>(null),[catalogFailure,setCatalogFailure]=useState(''),[attempt,setAttempt]=useState(0);
 const [state,setState]=useState<State>({selected:'',cases:{}}),live=useRef(state);live.current=state;
 const {gate,action}=useExecutionGate(),evRevision=useRef(new Revisions()),equityRevision=useRef(new Revisions()),setRevision=useRef(new Revisions()),gridRevision=useRef(new Revisions()),reverseRevision=useRef(new Revisions()),forkId=useRef(0);
 function update(fn:(s:State)=>State){const next=fn(live.current);live.current=next;setState(next);}
 function change(kind:string,fn:(s:Session)=>Session){update(old=>({...old,cases:{...old.cases,[kind]:fn(old.cases[kind])}}));}
 function changeCase(kind:string,label:string,fn:(c:CaseState)=>CaseState){change(kind,s=>({...s,cases:{...s.cases,[label]:fn(s.cases[label]!)}}));}
 useEffect(()=>{const abort=new AbortController();setCatalogFailure('');load<Catalog>('/api/v1/catalog',undefined,abort.signal).then(data=>{if(!abort.signal.aborted)setCatalog(data);}).catch(error=>{if(!abort.signal.aborted)setCatalogFailure(failureMessage(error));});return()=>abort.abort();},[load,attempt]);
 useEffect(()=>()=>{evRevision.current.edit();equityRevision.current.edit();setRevision.current.edit();gridRevision.current.edit();reverseRevision.current.edit();gate.cancel();},[]);
 function stop(){evRevision.current.edit();equityRevision.current.edit();setRevision.current.edit();gridRevision.current.edit();reverseRevision.current.edit();gate.cancel();
  const kind=live.current.selected;if(kind)change(kind,s=>({...s,cases:Object.fromEntries(Object.entries(s.cases).filter((entry):entry is [string,CaseState]=>Boolean(entry[1])).map(([label,c])=>[label,{...c,ev:c.ev.phase==='calculating'?invalidate(c.ev):c.ev,equity:c.equity.phase==='calculating'?invalidate(c.equity):c.equity,grid:c.grid.phase==='calculating'?staleGrid(c.grid):c.grid,reverse:c.reverse.phase==='calculating'?staleReverse(c.reverse):c.reverse}])) as Session['cases'],scenario:s.scenario.phase==='calculating'?invalidateSet(s.scenario):s.scenario}));
 }
 function select(kind:string){
  if(!catalog||kind===live.current.selected)return;
  const template=kind==='demo'?catalog.synthetic_demo:catalog.entries.find(e=>e.kind===kind)?.template;
  if(kind&&!template)return;stop();
  update(old=>({selected:kind,cases:template&&!old.cases[kind]?{...old.cases,[kind]:createSession(template)}:old.cases}));
 }
 function selectCase(label:string){const s=live.current.cases[live.current.selected];if(!s?.cases[label]||s.selectedCase===label)return;stop();change(live.current.selected,s=>({...s,selectedCase:label}));}
 function createCase(label:'Bear'|'Bull'){
  stop();const kind=live.current.selected;
  change(kind,s=>{const draft=structuredClone(s.cases.Base.draft);draft.doc.case_name+=` · ${label}`;draft.doc.preparation.timestamp_utc=new Date().toISOString();return {...s,selectedCase:label,cases:{...s.cases,[label]:newCase(draft)},scenario:invalidateSet(s.scenario)};});
 }
 function removeCase(label:'Bear'|'Bull'){stop();change(live.current.selected,s=>{const cases={...s.cases};delete cases[label];return {...s,cases,selectedCase:s.selectedCase===label?'Base':s.selectedCase,scenario:invalidateSet(s.scenario)};});}
 function editDraft(draft:Draft,financial=true){
  const kind=live.current.selected,s=live.current.cases[kind];if(!s)return;const label=s.selectedCase;
  if(financial){evRevision.current.edit();equityRevision.current.edit();setRevision.current.edit();gridRevision.current.edit();reverseRevision.current.edit();gate.cancel();}
  change(kind,s=>({...s,cases:{...s.cases,[label]:{...s.cases[label]!,draft,revision:s.cases[label]!.revision+(financial?1:0),ev:financial?invalidate(s.cases[label]!.ev):s.cases[label]!.ev,equity:financial?invalidate(s.cases[label]!.equity):s.cases[label]!.equity,grid:financial?staleGrid(s.cases[label]!.grid):s.cases[label]!.grid,reverse:financial?staleReverse(s.cases[label]!.reverse):s.cases[label]!.reverse}},scenario:financial&&labels.some(l=>l===label)?invalidateSet(s.scenario):s.scenario}));
 }
 function editBridge<K extends keyof EquityDraft>(key:K,value:EquityDraft[K]){
  const kind=live.current.selected;if(!kind)return;equityRevision.current.edit();gate.cancel('equity');
  if(live.current.cases[kind].cases[live.current.cases[kind].selectedCase]!.grid.equity){gridRevision.current.edit();gate.cancel('sensitivity');}
  if(live.current.cases[kind].cases[live.current.cases[kind].selectedCase]!.reverse.metric==='VALUE_PER_SHARE'){reverseRevision.current.edit();gate.cancel('reverse');}
  if(live.current.cases[kind].scenarioEquity){setRevision.current.edit();gate.cancel('scenarios');}
  change(kind,s=>({...s,bridge:{...s.bridge,[key]:value},bridgeRevision:s.bridgeRevision+1,cases:Object.fromEntries(Object.entries(s.cases).filter((entry):entry is [string,CaseState]=>Boolean(entry[1])).map(([label,c])=>[label,{...c,equity:invalidate(c.equity),reverse:c.reverse.metric==='VALUE_PER_SHARE'?staleReverse(c.reverse):c.reverse,grid:{...c.grid,equityCurrent:false,errors:{},failure:'',phase:c.grid.phase==='calculating'&&c.grid.equity?(c.grid.result?(c.grid.previousPhase==='current'?'current':'stale'):'incomplete'):c.grid.phase}}])) as Session['cases'],scenario:{...s.scenario,phase:s.scenario.phase==='calculating'&&s.scenarioEquity?(s.scenario.result?(s.scenario.previousPhase==='current'?'current':'stale'):'incomplete'):s.scenario.phase,equityCurrent:false,errors:{},failure:''}}));
 }
 function editComparison(key:'price'|'date',value:string){const kind=live.current.selected;if(kind)change(kind,c=>({...c,comparison:{...c.comparison,[key]:value}}));}
 function configureSet(key:'cutoff'|'scenarioEquity',value:string|boolean){setRevision.current.edit();gate.cancel('scenarios');change(live.current.selected,s=>({...s,[key]:value,scenario:invalidateSet(s.scenario)}));}
 async function calculate(scope:'ev'|'equity'){
  const kind=live.current.selected,s=live.current.cases[kind],label=s?.selectedCase,c=s?.cases[label];if(!c||gate.snapshot())return;
  if(scope==='equity'&&(c.ev.phase!=='current'||!c.ev.result))return;
  const revisions=scope==='ev'?evRevision.current:equityRevision.current,token=revisions.begin();
  const current=()=>revisions.current(token)&&live.current.selected===kind&&live.current.cases[kind].selectedCase===label;
  changeCase(kind,label,c=>({...c,[scope]:{...c[scope],phase:'calculating',errors:{},failure:''}}));
  try{
   const response=await executeCase<Result>({gate,action:scope,load,current,build:()=>{
    const local=entryErrors(c.draft);if(Object.keys(local).length)throw new InputErrors(local);
    if(scope==='equity'){const errors=equityErrors(s.bridge,c.draft.doc.anchor.annual_end);if(Object.keys(errors).length)throw new InputErrors(errors);}
    return requestFor(c.draft,s.cases.Base.draft,s.bridge,scope==='equity');
   },check:value=>{for(const [key,expected] of Object.entries(c.draft.doc.anchor))if(value.submitted_inputs.anchor[key as keyof typeof c.draft.doc.anchor]!==expected)throw new Error('Returned anchor did not match submitted case.');if(scope==='equity')requireMatchingEquity(value,c.ev.result!);}});
   if(!response||!current())return;
   changeCase(kind,label,c=>({...c,[scope]:{phase:'current',result:response,errors:{},failure:''}}));
  }catch(error){if(!current())return;const errors=error instanceof InputErrors?error.fields:error instanceof ApiError&&error.code==='invalid_case'?(scope==='ev'?fieldErrors(error.details.map(percentageDiagnostic)):equityDiagnostics(error.details,s.bridge)):{};
   changeCase(kind,label,c=>({...c,[scope]:{...c[scope],phase:Object.keys(errors).length?'incomplete':'failed',errors,failure:Object.keys(errors).length?'':failureMessage(error)}}));}
 }
 async function calculateScenarios(validationOnly=false){
  const kind=live.current.selected,s=live.current.cases[kind];if(!s||gate.snapshot())return;
  const snapshotPhase=s.scenario.phase;
  const token=setRevision.current.begin(),current=()=>setRevision.current.current(token)&&live.current.selected===kind;
  change(kind,s=>({...s,scenario:{...s.scenario,previousPhase:s.scenario.phase,phase:'calculating',errors:{},failure:''}}));
  try{
   let submitted:ReturnType<typeof scenarioRequest>;
   const response=await executeCase<ScenarioResult|{status:string}>({gate,action:'scenarios',operation:validationOnly?'validate':'run',load,current,build:()=>submitted=scenarioRequest(s.cases,s.bridge,s.cutoff,s.scenarioEquity),check:value=>{if(!validationOnly){const r=value as ScenarioResult;if(!sameSnapshot(r.submitted_inputs,submitted)||r.scenarios.some((e,i)=>e.label!==labels[i]||!sameSnapshot(e.result.submitted_inputs,submitted.scenarios[i].case)))throw new Error('Scenario response snapshot mismatch');}}});
   if(!response||!current())return;
   if(validationOnly){change(kind,s=>({...s,scenario:{...s.scenario,phase:s.scenario.result?snapshotPhase:'empty',failure:'Input checks passed. No scenario calculation or economic approval.'}}));return;}
   const result=response as ScenarioResult;
   change(kind,s=>{const cases={...s.cases};for(const e of result.scenarios){const old=cases[e.label]!;cases[e.label]={...old,ev:{phase:'current',result:e.result,errors:{},failure:''},equity:s.scenarioEquity?{phase:'current',result:e.result,errors:{},failure:''}:old.equity};}return {...s,cases,scenario:{phase:'current',result,errors:{},failure:'',equityCurrent:s.scenarioEquity}};});
  }catch(error){if(!current())return;let errors:Errors={};
   if(error instanceof InputErrors)errors=error.fields;
   else if(error instanceof ApiError&&error.code==='invalid_case')for(const raw of error.details){const match=/^scenarios\[(\d)\](?:\.case)?\.(.+?):\s*(.*)$/.exec(raw);if(match){const key=match[2],message=percentageDiagnostic(`${key}: ${match[3]}`).split(': ').slice(1).join(': ');errors[`${labels[Number(match[1])]}.${key}`]=message;}else errors[raw.split(':')[0]]=raw.split(': ').slice(1).join(': ');}
   change(kind,s=>({...s,scenario:{...s.scenario,phase:Object.keys(errors).length?'incomplete':'failed',errors,failure:Object.keys(errors).length?'':failureMessage(error)}}));
  }
 }
 function editGrid(key:keyof GridSettings|'cutoff'|'equity',value:string|boolean){
  gridRevision.current.edit();gate.cancel('sensitivity');const kind=live.current.selected,label=live.current.cases[kind].selectedCase;
  changeCase(kind,label,c=>({...c,grid:{...staleGrid(c.grid),...(key==='cutoff'||key==='equity'?{[key]:value}:{settings:{...c.grid.settings,[key]:value}})}}));
 }
 function inspectCell(row:number,column:number){const kind=live.current.selected,label=live.current.cases[kind].selectedCase;changeCase(kind,label,c=>({...c,grid:{...c.grid,inspected:[row,column]}}));}
 function applyCell(){
  const s=live.current.cases[live.current.selected],c=s.cases[s.selectedCase]!;if(gate.snapshot()||c.ev.phase!=='current'||c.grid.phase!=='current'||!c.grid.inspected)return;
  const [i,j]=c.grid.inspected,cell=c.grid.result?.cells[i]?.[j];if(cell?.status!=='VALID')return;
  const draft=structuredClone(c.draft);draft.rates.wacc=ratePercent(cell.wacc);draft.rates.terminal_growth=ratePercent(cell.terminal_growth);editDraft(draft);
 }
 async function calculateSensitivity(validationOnly=false){
  const kind=live.current.selected,s=live.current.cases[kind],label=s?.selectedCase,c=s?.cases[label];if(!c||gate.snapshot()||!validationOnly&&c.ev.phase!=='current')return;
  const token=gridRevision.current.begin(),current=()=>gridRevision.current.current(token)&&live.current.selected===kind&&live.current.cases[kind].selectedCase===label;
  changeCase(kind,label,c=>({...c,grid:{...c.grid,previousPhase:c.grid.phase,phase:'calculating',errors:{},failure:'',inspected:null}}));
  try{
   let submitted:ReturnType<typeof sensitivityRequest>;
   const response=await executeCase<SensitivityResult|{status:string}>({gate,action:'sensitivity',operation:validationOnly?'validate':'run',load,current,build:()=>submitted=sensitivityRequest(c.draft,s.cases.Base.draft,s.bridge,c.grid),check:value=>{if(!validationOnly){const r=value as SensitivityResult;if(!sameSnapshot(r.submitted_inputs,submitted)||!sameSnapshot(r.selected_case,submitted.source.case)||!sameSnapshot(r.reference_result.submitted_inputs,submitted.source.case)||!sameSnapshot(r.reference_result.stage_b,c.ev.result!.stage_b))throw new Error('Sensitivity response snapshot mismatch');}}});
   if(!response||!current())return;
   if(validationOnly){changeCase(kind,label,latest=>({...latest,grid:{...latest.grid,phase:c.grid.phase,failure:'Input checks passed. No sensitivity calculation or economic approval.'}}));return;}
   changeCase(kind,label,latest=>({...latest,grid:{...latest.grid,phase:'current',result:response as SensitivityResult,errors:{},failure:'',equityCurrent:c.grid.equity,inspected:null}}));
  }catch(error){if(!current())return;let errors:Errors={};
   if(error instanceof InputErrors)errors=error.fields;
   else if(error instanceof ApiError&&error.code==='invalid_case')for(const raw of error.details){const [path,...message]=raw.split(': ');const key=path.startsWith('sensitivity.source.information_cutoff')?'cutoff':path.startsWith('sensitivity.wacc_values')?'waccStart':path.startsWith('sensitivity.terminal_growth_values')?'growthStart':path;errors[key]=message.join(': ');}
   changeCase(kind,label,latest=>({...latest,grid:{...latest.grid,phase:Object.keys(errors).length?'incomplete':'failed',errors,failure:Object.keys(errors).length?'':failureMessage(error)}}));
  }
 }
 function editReverse(key:'metric'|'amount'|'lower'|'upper'|'cutoff'|'targetDate',value:string){
  reverseRevision.current.edit();gate.cancel('reverse');const kind=live.current.selected,label=live.current.cases[kind].selectedCase;
  changeCase(kind,label,c=>({...c,reverse:{...staleReverse(c.reverse),[key]:value}}));
 }
 async function calculateReverse(validationOnly=false){
  const kind=live.current.selected,s=live.current.cases[kind],label=s?.selectedCase,c=s?.cases[label];if(!c||gate.snapshot()||!validationOnly&&c.ev.phase!=='current')return;
  const token=reverseRevision.current.begin(),current=()=>reverseRevision.current.current(token)&&live.current.selected===kind&&live.current.cases[kind].selectedCase===label;
  changeCase(kind,label,c=>({...c,reverse:{...c.reverse,phase:'calculating',errors:{},failure:''}}));
  try{
   let submitted:ReturnType<typeof reverseRequest>;
   const response=await executeCase<ReverseResult|{status:string}>({gate,action:'reverse',operation:validationOnly?'validate':'run',load,current,build:()=>submitted=reverseRequest(c.draft,s.cases.Base.draft,s.bridge,c.reverse),check:value=>{if(!validationOnly){const r=value as ReverseResult;if(!sameSnapshot(r.submitted_inputs,submitted)||!sameSnapshot(r.selected_case,submitted.source.case)||!sameSnapshot(r.reference_result.submitted_inputs,submitted.source.case)||!sameSnapshot(r.reference_result.stage_b,c.ev.result!.stage_b))throw new Error('Reverse response snapshot mismatch');}}});
   if(!response||!current())return;
   changeCase(kind,label,latest=>({...latest,reverse:validationOnly?{...latest.reverse,phase:c.reverse.phase,failure:'Input checks passed. No certification, solve or economic approval.'}:{...latest.reverse,phase:'current',result:response as ReverseResult,errors:{},failure:''}}));
  }catch(error){if(!current())return;let errors:Errors={};if(error instanceof InputErrors)errors=error.fields;else if(error instanceof ApiError&&error.code==='invalid_case')for(const raw of error.details){const [path,...message]=raw.split(': ');const key=path.startsWith('reverse.target.amount')?'amount':path.startsWith('reverse.target.date')?'targetDate':path.startsWith('reverse.target.metric')?'metric':path.startsWith('reverse.growth_bounds.upper')?'upper':path.startsWith('reverse.growth_bounds')?'lower':path.startsWith('reverse.source.information_cutoff')?'cutoff':path;errors[key]=message.join(': ');}
   changeCase(kind,label,latest=>({...latest,reverse:{...latest.reverse,phase:Object.keys(errors).length?'incomplete':'failed',errors,failure:Object.keys(errors).length?'':failureMessage(error)}}));
  }
 }
 function createExploratory(tool:'reverse'|'sensitivity'){
  if(gate.snapshot())return;const kind=live.current.selected,s=live.current.cases[kind],c=s.cases[s.selectedCase]!;if(c.ev.phase!=='current')return;
  const draft=structuredClone(c.draft);let submitted:unknown;
  if(tool==='reverse'){const r=c.reverse;if(r.phase!=='current'||r.result?.status!=='SUCCESS'||!r.result.solution)return;const growth=ratePercent(r.result.solution.constant_annual_growth);for(let i=0;i<5;i++)draft.rates[`forecast_years[${i}].revenue_growth`]=growth;delete draft.replacements.revenue_growth;submitted=r.result;}
  else{const g=c.grid,cell=g.inspected&&g.result?.cells[g.inspected[0]]?.[g.inspected[1]];if(g.phase!=='current'||cell?.status!=='VALID')return;draft.rates.wacc=ratePercent(cell.wacc);draft.rates.terminal_growth=ratePercent(cell.terminal_growth);submitted={request:g.result!.submitted_inputs,cell};}
  const label=`Exploratory ${++forkId.current}`,createdAt=new Date().toISOString();draft.doc.case_name=`${draft.doc.case_name} · ${label} (${tool})`;draft.doc.preparation.timestamp_utc=createdAt;
  stop();change(kind,s=>({...s,selectedCase:label,cases:{...s.cases,[label]:{...newCase(draft),origin:{kind:tool,sourceCase:c.draft.doc.case_name,createdAt,submitted}}}}));
 }
 function reviewError(path:string){if(path.startsWith('bridge.')){const s=live.current.cases[live.current.selected];changeCase(live.current.selected,s.selectedCase,c=>({...c,equity:{...c.equity,errors:{[path.slice(7)]:s.scenario.errors[path]}}}));return false;}const label=labels.find(l=>path.startsWith(l+'.'));if(label&&live.current.cases[live.current.selected].cases[label]){selectCase(label);const field=path.slice(label.length+1);changeCase(live.current.selected,label,c=>({...c,ev:{...c.ev,errors:{[field]:live.current.cases[live.current.selected].scenario.errors[path]}}}));return true;}return false;}
 const company=state.cases[state.selected],selected=company?.cases[company.selectedCase];
 return {catalog,catalogFailure,retryCatalog:()=>setAttempt(n=>n+1),state,company,session:company&&selected?{...company,...selected}:undefined,select,selectCase,createCase,removeCase,editDraft,editBridge,editComparison,configureSet,calculate,calculateScenarios,editGrid,inspectCell,applyCell,calculateSensitivity,editReverse,calculateReverse,createExploratory,reviewError,cancel:()=>gate.cancel(),busy:action};
}
