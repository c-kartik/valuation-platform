import {useEffect,useState} from 'react';
import {annual,terminal,copyYearFive,reviewErrors,InputErrors,displayPath} from '../model';
import type {Draft,Entry,Errors} from '../model';
import type {CaseState} from './useWorkspace';
import {percentage} from '../presentation';
import {AnnualRate,RateInput,inputId,InlineDisclosure} from './InlineRates';
import {inherited,pathsFor,shortLabels} from './canvasModel';
export function focusInline(prefix:string,draft:Draft,path:string){
 const target=displayPath(draft,path),id=inputId(prefix,target);let attempts=0;
 const reveal=()=>{for(const details of document.querySelectorAll<HTMLDetailsElement>('details[data-inline-prefix]')){if(prefix.startsWith(details.dataset.inlinePrefix!)&&details.dataset.inputPath!.split(',').some(p=>target.startsWith(p))&&(!details.dataset.inputDriver||target.endsWith('.'+details.dataset.inputDriver)))details.open=true;}
 const input=document.getElementById(id);if(input){let node=input.parentElement;while(node){if(node instanceof HTMLDetailsElement)node.open=true;node=node.parentElement;}input.focus();}else if(++attempts<8)requestAnimationFrame(reveal);};requestAnimationFrame(reveal);
}
export function AssumptionSummary({label,caseState:c,entry,change,editBridge,errors:raw={}}:{label:string;caseState:CaseState;entry?:Entry;change:(d:Draft,financial?:boolean,paths?:string[])=>void;editBridge:()=>void;errors?:Errors}){
 const prefix='dcf',draft=c.draft,[localErrors,setLocalErrors]=useState<Errors>({}),errors=reviewErrors(draft,{...raw,...localErrors});
 useEffect(()=>{const path=Object.keys(raw).find(p=>!p.startsWith('bridge.'));if(path)focusInline(prefix,draft,path);},[raw]);
 function commit(d:Draft,paths:string[]=[]){setLocalErrors({});change(d,true,paths);}
 function rate(path:string,value:string){const d=structuredClone(draft);d.rates[path]=value;commit(d,[path]);}
 function history(metric:string){const r=entry?.historical_references?.find(r=>r.metric===metric);return r?.value?`${r.label}: ${percentage(r.value)} · context only`:undefined;}
 function copy(){try{commit(copyYearFive(draft),terminal.map(([k])=>`terminal.${k}`));}catch(e){if(e instanceof InputErrors){setLocalErrors(e.fields);focusInline(prefix,draft,Object.keys(e.fields)[0]);}}}
 return <section className="cv-assumptions cv-direct-assumptions" aria-label="Forward assumptions"><div className="cv-section-title"><h2>Assumptions</h2><span>{Object.values(draft.rates).filter(v=>v.trim()).length}/37 entered</span></div><p className="cv-input-convention">Percentages · 10 means 10%. Five forecast years.</p>
 {annual.map(([key])=><AnnualRate key={key} prefix={prefix} draft={draft} driver={key} label={shortLabels[key]} change={(d,paths)=>commit(d,paths)} errors={errors} inherited={inherited(label,c,pathsFor(key))} reference={history(key)} showDetails={false}/>)}
 <h3>Valuation</h3><RateInput prefix={prefix} path="wacc" label="WACC" value={draft.rates.wacc} edit={v=>rate('wacc',v)} error={errors.wacc}/><RateInput prefix={prefix} path="terminal_growth" label="Terminal growth" value={draft.rates.terminal_growth} edit={v=>rate('terminal_growth',v)} error={errors.terminal_growth}/>
 <InlineDisclosure className="cv-all-annual" title="Annual paths & input meanings" prefix={prefix} paths={['forecast_years']}>{annual.map(([key])=><AnnualRate key={key} prefix={prefix} draft={draft} driver={key} label={shortLabels[key]} change={(d,paths)=>commit(d,paths)} errors={errors} annualOnly/>)}</InlineDisclosure>
 <InlineDisclosure className="cv-terminal-inputs" title="Five independent terminal operating ratios" prefix={prefix} paths={['terminal.']}><p>After year five. Annual edits never change these values.</p>{terminal.map(([key,name])=><RateInput key={key} prefix={prefix} path={`terminal.${key}`} label={name} value={draft.rates[`terminal.${key}`]} edit={v=>rate(`terminal.${key}`,v)} error={errors[`terminal.${key}`]}/>)}<button onClick={copy}>Copy year-five ratios once</button><small>Copies only five operating ratios; WACC and growth stay unchanged.</small></InlineDisclosure>
 <InlineDisclosure className="cv-case-notes" title="Case name & personal notes" prefix={prefix} paths={['case_name','preparation.']}><label htmlFor="dcf-case_name">Case name</label><input id="dcf-case_name" value={draft.doc.case_name} onChange={e=>{const d=structuredClone(draft);d.doc.case_name=e.target.value;change(d,false);}}/>{errors.case_name&&<small className="cv-error">{errors.case_name}</small>}<label htmlFor="dcf-preparation.notes">Optional personal notes</label><textarea id="dcf-preparation.notes" value={draft.doc.preparation.notes??''} onChange={e=>{const d=structuredClone(draft);d.doc.preparation.notes=e.target.value;change(d,false);}}/>{errors['preparation.notes']&&<small className="cv-error">{errors['preparation.notes']}</small>}<small>Notes do not establish evidence review or an information cutoff.</small></InlineDisclosure>
 <button className="cv-bridge-button" onClick={editBridge}>Cash, debt and shares · optional</button></section>;
}
