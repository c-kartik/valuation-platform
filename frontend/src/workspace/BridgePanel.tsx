import {useEffect,useState} from 'react';
import {EquityFields,EquityReview,equityAdvancedFields,equityFieldLabels} from '../EquityFields';
import type {EquityDraft} from '../equity';
import type {Outcome} from './useWorkspace';
export function BridgePanel({values,outcome,anchorDate,operatingCurrent,busy,edit,calculate,cancel}:{values:EquityDraft;outcome:Outcome;anchorDate:string;operatingCurrent:boolean;busy:string|null;edit:<K extends keyof EquityDraft>(key:K,value:EquityDraft[K])=>void;calculate:()=>void;cancel:()=>void}){
 const [advanced,setAdvanced]=useState(false),[componentsOpen,setComponentsOpen]=useState(false);
 function focus(key:string){if(equityAdvancedFields.includes(key))setAdvanced(true);if(key==='components'||/^(overlap|alternative)/.test(key))setComponentsOpen(true);requestAnimationFrame(()=>{(document.getElementById(`equity.${key}`)??document.getElementById('w-equity-issues'))?.focus();});}
 useEffect(()=>{const first=Object.keys(outcome.errors)[0];if(first)focus(first);},[outcome.errors]);
 return <section className="p-panel w-bridge" aria-label="Optional equity and shares"><span className="p-eyebrow">OPTIONAL SECOND STEP · MANUAL DECLARATIONS</span><h2>Cash, claims & shares</h2><p>These are your entries, not reported balances or verified approvals. Missing bridge inputs block this step while retaining usable EV.</p><EquityFields values={values} errors={outcome.errors} edit={edit} anchorDate={anchorDate} advanced={advanced} setAdvanced={setAdvanced} componentsOpen={componentsOpen} setComponentsOpen={setComponentsOpen}/>
 {!operatingCurrent&&<p className="p-qualification">Calculate a current enterprise value before requesting equity/value per share.</p>}
 <button className="p-primary p-run" disabled={Boolean(busy)||!operatingCurrent} onClick={calculate}>Calculate value per share <span aria-hidden="true">→</span></button>{busy&&<><p role="status">Calculating {busy==='equity'?'equity and value per share':'enterprise value'}…</p><button onClick={cancel}>Cancel calculation</button></>}
 {Object.keys(outcome.errors).length>0&&<div id="w-equity-issues" tabIndex={-1} className="p-error-summary" role="region" aria-label="Equity input issues"><h3>Review bridge inputs · EV is retained</h3><ul>{Object.entries(outcome.errors).map(([key,message])=><li key={key}><button onClick={()=>focus(key)}>{equityFieldLabels[key]??key}: {message}</button></li>)}</ul></div>}
 {outcome.failure&&<div className="p-notice" role="status"><p>{outcome.failure}</p><button disabled={Boolean(busy)||!operatingCurrent} onClick={calculate}>Retry value per share</button></div>}
 {outcome.result&&<EquityReview result={outcome.result} stale={outcome.phase!=='current'||!operatingCurrent}/>}
 </section>;
}
