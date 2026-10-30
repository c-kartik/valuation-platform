import {useState} from 'react';
import {annualPath,annualState,editQuick,replaceAnnual,percentageToFraction,multipleString} from '../model';
import type {AnnualKey,Draft,Errors} from '../model';
import {help,pathsFor} from './canvasModel';

export const inputId=(prefix:string,path:string)=>`${prefix}-${path}`;
export function RateInput({prefix,path,label,value,edit,error,unit='%'}:{prefix:string;path:string;label:string;value:string;edit:(v:string)=>void;error?:string;unit?:'%'|'×'}){
 const [syntax,setSyntax]=useState('');const issue=error||syntax,id=inputId(prefix,path);
 return <div className="cv-inline-field"><label htmlFor={id}>{label}</label><div className="cv-inline-number"><input id={id} value={value} inputMode="decimal" onChange={e=>{setSyntax('');edit(e.target.value);}} onBlur={()=>{try{if(unit==='×')multipleString(value);else percentageToFraction(value);setSyntax('');}catch(e){setSyntax((e as Error).message);}}} aria-invalid={Boolean(issue)} aria-describedby={issue?id+'-error':undefined}/><span aria-hidden="true">{unit}</span></div>{issue&&<small id={id+'-error'} className="cv-error">{issue}</small>}</div>;
}
export function AnnualRate({prefix,draft,driver,label,change,errors={},inherited=false,reference,showDetails=true,annualOnly=false}:{prefix:string;draft:Draft;driver:AnnualKey;label:string;change:(d:Draft,paths:string[])=>void;errors?:Errors;inherited?:boolean;reference?:string;showDetails?:boolean;annualOnly?:boolean}){
 const state=annualState(draft,driver),proposal=driver in draft.replacements;
 const paths=pathsFor(driver),annualError=paths.some(p=>Boolean(errors[p])),[byYear,setByYear]=useState(false),[replaceError,setReplaceError]=useState('');
 function editYear(path:string,value:string){const next=structuredClone(draft);next.rates[path]=value;delete next.replacements[driver];change(next,[path]);}
 function replace(){try{change(replaceAnnual(draft,driver),paths);setReplaceError('');}catch(e){setReplaceError((e as {fields?:Errors}).fields?.[`quick.${driver}`]??(e as Error).message);}}
 return <div className="cv-inline-driver">{!annualOnly&&<><RateInput prefix={prefix} path={'quick.'+driver} label={label} value={proposal?draft.replacements[driver]!:state.varies?'':state.value} edit={value=>{setReplaceError('');change(editQuick(draft,driver,value),state.varies||proposal?[]:paths);}} error={errors['quick.'+driver]||replaceError}/>
 {inherited&&<small className="cv-inherited">From Base</small>}{reference&&<small className="cv-reference">{reference}</small>}
 {state.varies&&<small className="cv-path-status">Varies by year · constant field is an unapplied replacement.</small>}
 {proposal&&<div className="cv-replace"><button onClick={replace}>Replace five {label.toLowerCase()} values</button>{proposal&&<button onClick={()=>{const next=structuredClone(draft);delete next.replacements[driver];change(next,[]);setReplaceError('');}}>Keep annual values</button>}<small>Only this annual driver changes. A pending replacement blocks calculation.</small></div>}
 </>}{showDetails&&<><details data-inline-prefix={prefix} data-input-path="forecast_years" data-input-driver={driver} open={byYear||annualError} onToggle={e=>setByYear(e.currentTarget.open)} className="cv-inline-years"><summary>By year · {label}</summary><div>{(byYear||annualError)&&draft.doc.forecast_years.map((y,i)=><RateInput key={i} prefix={prefix} path={annualPath(driver,i)} label={`${y.fiscal_year_label} ${label}`} value={draft.rates[annualPath(driver,i)]} edit={v=>editYear(annualPath(driver,i),v)} error={errors[annualPath(driver,i)]}/>)}</div></details>
 <details className="cv-inline-help"><summary>About {label.toLowerCase()}</summary><p>{help[driver]}</p></details></>}</div>;
}

/** Collapsed inline detail is mounted on demand; working values live in the case. */
export function InlineDisclosure({title,prefix,paths,children,className=''}:{title:string;prefix:string;paths:string[];children:import('react').ReactNode;className?:string}){
 const [open,setOpen]=useState(false);return <details className={className} data-inline-prefix={prefix} data-input-path={paths.join(',')} open={open} onToggle={e=>setOpen(e.currentTarget.open)}><summary>{title}</summary>{open&&children}</details>;
}
