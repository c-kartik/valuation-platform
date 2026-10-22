import {useEffect,useRef,useState} from 'react';
import {request,ApiError,failureMessage} from './api';
import {useExecutionGate} from './execution';
import type {ExecutionGate} from './execution';
import {InputErrors,display} from './model';
import type {Draft,Result,Errors} from './model';
import {awards,coverageOptions,emptyEquity,equityErrors,buildEquityRequest,equityDiagnostics} from './equity';
import type {EquityDraft} from './equity';
import {readableMoney,shareMillions} from './presentation';

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
 const fieldLabels:Record<string,string>={assets:'Eligible assets',financing:'Financing',claims:'Other claims',shares:'Valuation shares',date:'Share date',claimsTreatment:'Other-claims assessment',assetsCoverage:'Eligible-asset coverage',financingCoverage:'Financing coverage',claimsCoverage:'Other-claims coverage',shareBasis:'Share population',classes:'Included classes',equivalence:'Class treatment',awards:'Existing awards',nonOverlap:'Date, eligibility & non-overlap',issues:'Bridge declarations',components:'Component references',overlapAssets:'Assets overlap references',alternativeAssets:'Assets alternative references',overlapFinancing:'Financing overlap references',alternativeFinancing:'Financing alternative references',overlapClaims:'Claims overlap references',alternativeClaims:'Claims alternative references'};
 const advancedFields=['assetsCoverage','financingCoverage','claimsCoverage','shareBasis','classes','equivalence','awards','nonOverlap'];
 function focusError(key:string){
  setOpen(true);if(advancedFields.includes(key))setAdvanced(true);
  if(key==='components'||/^(overlap|alternative)/.test(key))setComponentsOpen(true);
  requestAnimationFrame(()=>{const target=document.getElementById(`equity.${key}`)??document.getElementById('equity.issues');target?.focus();});
 }
 async function calculate(){
  if(gate.snapshot())return;
  setSubmitted(true);setFailure('');setServerErrors({});
  const local=equityErrors(values,draft.doc.anchor.annual_end);
  if(Object.keys(local).length){focusError(Object.keys(local)[0]);return;}
  if(operatingStale)return;
  const lease=gate.start('equity');if(!lease)return;
  const token=++sequence.current,selectedEV=evResult;
  setStale(true);
  try{
   const body=buildEquityRequest(draft,values);
   const response=await lease.wait(load<Result>('/api/v1/cases/run',body,lease.signal));
   if(lease.signal.aborted||token!==sequence.current||current.current.evResult!==selectedEV||current.current.operatingStale)return;
   if(!response.stage_c||JSON.stringify(response.stage_b)!==JSON.stringify(selectedEV.stage_b))throw new Error('The equity response did not match the current enterprise-value calculation. Recalculate EV and retry.');
   setEquity(response);setStale(false);
  }catch(error){
   if(token!==sequence.current)return;
   if(error instanceof InputErrors){setServerErrors(error.fields);focusError(Object.keys(error.fields)[0]);}
   else if(error instanceof ApiError&&error.code==='invalid_case'){
    const mapped=equityDiagnostics(error.details,values);
    setServerErrors(mapped);focusError(Object.keys(mapped)[0]);
   }else setFailure(failureMessage(error));
  }finally{lease.finish();}
 }
 function field(key:'assets'|'financing'|'claims'|'shares'|'date'|'classes',label:string){
  return <div className="field"><label htmlFor={`equity.${key}`}>{label}</label><input id={`equity.${key}`} type={key==='date'?'date':'text'} value={values[key]} onChange={e=>edit(key,e.target.value)} aria-invalid={Boolean(errors[key])} aria-describedby={errors[key]?`equity.${key}-error`:undefined}/>{errors[key]&&<span className="field-error" id={`equity.${key}-error`}>{errors[key]}</span>}</div>;
 }
 function choice<K extends 'claimsTreatment'|'assetsCoverage'|'financingCoverage'|'claimsCoverage'|'shareBasis'|'equivalence'|'awards'>(key:K,label:string,options:Record<string,string>){
  return <div className="field"><label htmlFor={`equity.${key}`}>{label}</label><select id={`equity.${key}`} value={values[key]} onChange={e=>edit(key,e.target.value as EquityDraft[K])} aria-invalid={Boolean(errors[key])} aria-describedby={errors[key]?`equity.${key}-error`:undefined}><option value="">Choose…</option>{Object.entries(options).map(([value,text])=><option key={value} value={value}>{text}</option>)}</select>{errors[key]&&<span className="field-error" id={`equity.${key}-error`}>{errors[key]}</span>}</div>;
 }
 const c=equity?.stage_c,provisional=c?.inputs.observations.filter(o=>o.disposition==='OMISSION')??[];
 return <section className="equity-step" aria-label="Optional equity and shares">
  <details open={open} onToggle={e=>setOpen(e.currentTarget.open)}><summary>Add cash, debt &amp; shares</summary>
   <p className="hint">Optional second step. Manual, unverified inputs; closing keeps edits in this session only. EV remains available without them.</p>
   <p className="hint">Amounts: <b>USD millions</b>. Shares: <b>millions of shares</b>. Blank is not zero. All amounts must represent {draft.doc.anchor.annual_end}.</p>
   <div className="rate-grid">{field('assets','Eligible cash & investments (USD millions)')}{field('financing','Debt & financing obligations (USD millions)')}</div>
   <p className="hint">Exclude operating cash reserves and assets already in operating value. Include relevant finance leases once. Positive adjustments belong in eligible assets; financing and other claims are deduction magnitudes.</p>
   {choice('claimsTreatment','Other claims / adjustments',{amount:'Enter an amount',none:'None identified within my stated scope',unassessed:'Not assessed'})}
   {values.claimsTreatment==='amount'&&field('claims','Other claims (USD millions)')}
   <div className="rate-grid">{field('shares','Shares outstanding (millions of shares)')}{field('date','Share observation date')}</div>
   <p className="hint">Use a dated share population. Diluted weighted-average EPS shares are not automatically suitable. Coverage, class and award declarations are required below.</p>
   <details open={advanced} onToggle={e=>setAdvanced(e.currentTarget.open)}><summary>Coverage, classes &amp; awards</summary>
    <p className="hint">Each choice is your declaration, not an authenticated review. “Selected population” does not establish complete claims coverage. Disclosed omissions may be unbounded.</p>
    {choice('assetsCoverage','Eligible-asset coverage',coverageOptions)}{choice('financingCoverage','Financing coverage',coverageOptions)}
    {values.claimsTreatment==='amount'&&choice('claimsCoverage','Other-claims coverage',coverageOptions)}
    {choice('shareBasis','Share population',{issued:'Issued shares — no automatic dilution',basic_equivalent:'Basic-equivalent shares — explicitly adjusted population'})}
    {field('classes','Included share class(es)')}
    {choice('equivalence','Class treatment',{single_common_class:'Single common class only',explicit_common_unit_equivalence:'Explicit one-for-one common economic equivalence; no control premium'})}
    <p className="hint">Equivalence across classes is your assumption, including for META and Alphabet; the calculator cannot establish class rights.</p>
    {choice('awards','Existing awards',awards)}
    <p className="hint">SBC remains expensed in operating margins. Adjust only non-overlapping pre-anchor rights; no automatic RSU addition, proceeds or second employee-service charge.</p>
    <label className="check-row"><input id="equity.nonOverlap" type="checkbox" checked={values.nonOverlap} onChange={e=>edit('nonOverlap',e.target.checked)} aria-invalid={Boolean(errors.nonOverlap)} aria-describedby={errors.nonOverlap?'equity.nonOverlap-error':undefined}/>I declare these amounts are dated {draft.doc.anchor.annual_end}, assets exclude operating reserves/value, and selected populations do not duplicate each other or forecast settlements; finance leases count once.</label>
    {errors.nonOverlap&&<p className="field-error" id="equity.nonOverlap-error">{errors.nonOverlap}</p>}
   </details>
   <details open={componentsOpen} onToggle={e=>setComponentsOpen(e.currentTarget.open)}><summary id="equity.components">Component details &amp; overlap references</summary>
    <p className="hint">Three manual aggregate components: assets (+), financing (−), claims (− when entered). No reported balances are supplied. Optional comma-separated component references declare overlap or alternative measurements; selected overlapping operands reject. Detailed multi-component cases remain available through the existing CLI/API.</p>
    {(['Assets','Financing','Claims'] as const).map((name,i)=><div key={name}><b>{['assets','financing','claims'][i]}</b>{(['overlap','alternative'] as const).map(kind=>{const key=`${kind}${name}` as keyof EquityDraft;return <div className="field" key={key}><label htmlFor={`equity.${key}`}>{name} {kind} references</label><input id={`equity.${key}`} value={String(values[key])} onChange={e=>edit(key,e.target.value)} aria-invalid={Boolean(errors[key])} aria-describedby={errors[key]?`equity.${key}-error`:undefined}/>{errors[key]&&<span className="field-error" id={`equity.${key}-error`}>{errors[key]}</span>}</div>;})}</div>)}
   </details>
   {operatingStale&&<p className="errors" role="status">Operating inputs changed. Recalculate enterprise value before calculating value per share.</p>}
   <button disabled={Boolean(action)||operatingStale} onClick={()=>void calculate()}>Calculate value per share</button>
   {busy&&<p role="status">Calculating the submitted operating case and bridge…</p>}
   {Object.keys(errors).length>0&&<div className="errors" id="equity.issues" tabIndex={-1} role="region" aria-label="Equity input issues"><h3>Equity result needs input review; EV is retained</h3><ul>{Object.entries(errors).map(([key,message])=><li key={key}><button className="text-button" onClick={()=>focusError(key)}>{fieldLabels[key]??key}: {message}</button></li>)}</ul></div>}
   {failure&&<div className="errors" role="status" aria-live="polite">{failure}<button disabled={Boolean(action)||operatingStale} onClick={()=>void calculate()}>Retry value per share</button></div>}
  </details>
  {c&&<div aria-label="Equity reconciliation">
   {(stale||operatingStale)&&<p className="errors" role="status"><b>STALE EQUITY RESULT — recalculate after edits.</b></p>}
   <h2>{provisional.length?'Provisional equity reference':'Manual equity reference'}</h2>
   <p className="hint">Unverified selected populations; not fully diluted fair value or complete claims certification.</p>
   {provisional.length>0&&<div className="notice"><b>Explicit omissions — total value is not bounded</b><ul>{provisional.map(o=><li key={o.observation_id}>{o.rationale}</li>)}</ul></div>}
   <dl className="reconciliation">{[['Enterprise value',c.stage_b.enterprise_value],['+ Eligible assets',c.eligible_assets],['− Financing obligations',c.financing_claims],['− Other claims',c.other_equity_claims],['= Equity value',c.equity_value]].map(([label,value])=><div key={label}><dt>{label} (USD)</dt><dd>{readableMoney(value)}</dd></div>)}
    <div><dt>÷ Valuation shares (millions)</dt><dd>{shareMillions(c.valuation_shares)}</dd></div>
    <div><dt>= Value {c.inputs.shares.class_id.startsWith('issued:')?'per issued share':'per basic-equivalent share'} (USD/share)</dt><dd>{display(c.value_per_share,'1',2)}</dd></div>
   </dl>
   <p className="hint">{c.inputs.shares.class_id} · {c.inputs.shares.observation_date}. {c.inputs.shares.rationale}</p>
   <details><summary>Equity provenance &amp; exact values</summary><ul>{c.contributions.map(line=><li key={line.component.component_id}>{line.component.component_id}: {line.signed_contribution} USD (unrounded)</li>)}</ul><pre>{JSON.stringify(equity,null,2)}</pre></details>
  </div>}
 </section>;
}
