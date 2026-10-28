import {display} from './model';
import type {Result,Errors} from './model';
import {awards,coverageOptions} from './equity';
import type {EquityDraft} from './equity';
import {readableMoney,shareMillions} from './presentation';
export const equityFieldLabels:Record<string,string>={assets:'Eligible assets',financing:'Financing',claims:'Other claims',shares:'Valuation shares',date:'Share date',claimsTreatment:'Other-claims assessment',assetsCoverage:'Eligible-asset coverage',financingCoverage:'Financing coverage',claimsCoverage:'Other-claims coverage',shareBasis:'Share population',classes:'Included classes',equivalence:'Class treatment',awards:'Existing awards',nonOverlap:'Date, eligibility & non-overlap',issues:'Bridge declarations',components:'Component references',overlapAssets:'Assets overlap references',alternativeAssets:'Assets alternative references',overlapFinancing:'Financing overlap references',alternativeFinancing:'Financing alternative references',overlapClaims:'Claims overlap references',alternativeClaims:'Claims alternative references'};
export const equityAdvancedFields=['assetsCoverage','financingCoverage','claimsCoverage','shareBasis','classes','equivalence','awards','nonOverlap'];

export function EquityFields({values,errors,edit,anchorDate,advanced,setAdvanced,componentsOpen,setComponentsOpen}:{values:EquityDraft;errors:Errors;edit:<K extends keyof EquityDraft>(key:K,value:EquityDraft[K])=>void;anchorDate:string;advanced:boolean;setAdvanced:(value:boolean)=>void;componentsOpen:boolean;setComponentsOpen:(value:boolean)=>void}){
 function field(key:'assets'|'financing'|'claims'|'shares'|'date'|'classes',label:string){
  return <div className="field"><label htmlFor={`equity.${key}`}>{label}</label><input id={`equity.${key}`} type={key==='date'?'date':'text'} value={values[key]} onChange={e=>edit(key,e.target.value)} aria-invalid={Boolean(errors[key])} aria-describedby={errors[key]?`equity.${key}-error`:undefined}/>{errors[key]&&<span className="field-error" id={`equity.${key}-error`}>{errors[key]}</span>}</div>;
 }
 function choice<K extends 'claimsTreatment'|'assetsCoverage'|'financingCoverage'|'claimsCoverage'|'shareBasis'|'equivalence'|'awards'>(key:K,label:string,options:Record<string,string>){
  return <div className="field"><label htmlFor={`equity.${key}`}>{label}</label><select id={`equity.${key}`} value={values[key]} onChange={e=>edit(key,e.target.value as EquityDraft[K])} aria-invalid={Boolean(errors[key])} aria-describedby={errors[key]?`equity.${key}-error`:undefined}><option value="">Choose…</option>{Object.entries(options).map(([value,text])=><option key={value} value={value}>{text}</option>)}</select>{errors[key]&&<span className="field-error" id={`equity.${key}-error`}>{errors[key]}</span>}</div>;
 }
 return <>
   <p className="hint">Amounts: <b>USD millions</b>. Shares: <b>millions of shares</b>. Blank is not zero. All amounts must represent {anchorDate}.</p>
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
    <label className="check-row"><input id="equity.nonOverlap" type="checkbox" checked={values.nonOverlap} onChange={e=>edit('nonOverlap',e.target.checked)} aria-invalid={Boolean(errors.nonOverlap)} aria-describedby={errors.nonOverlap?'equity.nonOverlap-error':undefined}/>I declare these amounts are dated {anchorDate}, assets exclude operating reserves/value, and selected populations do not duplicate each other or forecast settlements; finance leases count once.</label>
    {errors.nonOverlap&&<p className="field-error" id="equity.nonOverlap-error">{errors.nonOverlap}</p>}
   </details>
   <details open={componentsOpen} onToggle={e=>setComponentsOpen(e.currentTarget.open)}><summary id="equity.components">Component details &amp; overlap references</summary>
    <p className="hint">Three manual aggregate components: assets (+), financing (−), claims (− when entered). No reported balances are supplied. Optional comma-separated component references declare overlap or alternative measurements; selected overlapping operands reject. Detailed multi-component cases remain available through the existing CLI/API.</p>
    {(['Assets','Financing','Claims'] as const).map((name,i)=><div key={name}><b>{['assets','financing','claims'][i]}</b>{(['overlap','alternative'] as const).map(kind=>{const key=`${kind}${name}` as keyof EquityDraft;return <div className="field" key={key}><label htmlFor={`equity.${key}`}>{name} {kind} references</label><input id={`equity.${key}`} value={String(values[key])} onChange={e=>edit(key,e.target.value)} aria-invalid={Boolean(errors[key])} aria-describedby={errors[key]?`equity.${key}-error`:undefined}/>{errors[key]&&<span className="field-error" id={`equity.${key}-error`}>{errors[key]}</span>}</div>;})}</div>)}
   </details>
 </>;
}

export function EquityReview({result,stale}:{result:Result;stale:boolean}){
 const c=result.stage_c;if(!c)return null;const provisional=c.inputs.observations.filter(o=>o.disposition==='OMISSION');
 return <div aria-label="Equity reconciliation">
   {stale&&<p className="errors" role="status"><b>STALE EQUITY RESULT — recalculate after edits.</b></p>}
   <h2>{provisional.length?'Provisional equity reference':'Manual equity reference'}</h2>
   <p className="hint">Unverified selected populations; not fully diluted fair value or complete claims certification.</p>
   {provisional.length>0&&<div className="notice"><b>Explicit omissions — total value is not bounded</b><ul>{provisional.map(o=><li key={o.observation_id}>{o.rationale}</li>)}</ul></div>}
   <dl className="reconciliation">{[['Enterprise value',c.stage_b.enterprise_value],['+ Eligible assets',c.eligible_assets],['− Financing obligations',c.financing_claims],['− Other claims',c.other_equity_claims],['= Equity value',c.equity_value]].map(([label,value])=><div key={label}><dt>{label} (USD)</dt><dd>{readableMoney(value)}</dd></div>)}
    <div><dt>÷ Valuation shares (millions)</dt><dd>{shareMillions(c.valuation_shares)}</dd></div>
    <div><dt>= Value {c.inputs.shares.class_id.startsWith('issued:')?'per issued share':'per basic-equivalent share'} (USD/share)</dt><dd>{display(c.value_per_share,'1',2)}</dd></div>
   </dl>
   <p className="hint">{c.inputs.shares.class_id} · {c.inputs.shares.observation_date}. {c.inputs.shares.rationale}</p>
   <details><summary>Equity provenance &amp; exact values</summary><ul>{c.contributions.map(line=><li key={line.component.component_id}>{line.component.component_id}: {line.signed_contribution} USD (unrounded)</li>)}</ul><pre>{JSON.stringify(result,null,2)}</pre></details>
  </div>;
}
