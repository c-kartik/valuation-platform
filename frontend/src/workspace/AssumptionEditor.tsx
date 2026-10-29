import {useEffect,useRef,useState} from 'react';
import {annual,annualPath,annualState,terminal,copyYearFive,percentageToFraction,InputErrors} from '../model';
import type {AnnualKey,Draft,Entry,Errors,HistoricalReference,Result} from '../model';
import {EquityFields} from '../EquityFields';
import {millionsToUnits} from '../equity';
import type {EquityDraft} from '../equity';
import {percentage,readableMoney} from '../presentation';
import {editorSections,help,sectionFor} from './canvasModel';
import type {EditorSection} from './canvasModel';

export function AssumptionEditor({company,label,initial,bridge,section,entry,result,stale,errors:serverErrors,apply,close}:{company:string;label:string;initial:Draft;bridge:EquityDraft;section:EditorSection;entry?:Entry;result:Result|null;stale:boolean;errors:Errors;apply:(draft:Draft,bridge:EquityDraft,touched:string[])=>void;close:()=>void}){
 const [draft,setDraft]=useState(()=>structuredClone(initial)),[equity,setEquity]=useState(()=>structuredClone(bridge));
 const [active,setActive]=useState(section),[modes,setModes]=useState<Partial<Record<AnnualKey,'constant'|'annual'>>>({}),[touched,setTouched]=useState<string[]>([]),[errors,setErrors]=useState<Errors>({}),[notice,setNotice]=useState('');
 const [advanced,setAdvanced]=useState(true),[componentsOpen,setComponentsOpen]=useState(()=>Object.keys(serverErrors).some(p=>/^bridge\.(overlap|alternative|components)/.test(p))),[notesOpen,setNotesOpen]=useState(false);
 const dialog=useRef<HTMLDialogElement>(null),opener=useRef(document.activeElement as HTMLElement|null);
 useEffect(()=>{
  const d=dialog.current!,body=document.body,scroll=window.scrollY;
  const previous={position:body.style.position,top:body.style.top,width:body.style.width};
  // Keep the background at its current position and prevent page scrolling
  // behind the full-height sheet, including touch scroll on narrow screens.
  Object.assign(body.style,{position:'fixed',top:`-${scroll}px`,width:'100%'});
  d.showModal();d.querySelector<HTMLButtonElement>('[data-editor-section][aria-pressed="true"]')?.focus();
  return()=>{d.close();Object.assign(body.style,previous);window.scrollTo(0,scroll);if(opener.current?.isConnected)opener.current.focus({preventScroll:true});};
 },[]);
 function rate(path:string,value:string){setDraft(old=>{const d=structuredClone(old);d.rates[path]=value;const key=/^forecast_years\[\d+\]\.(.+)$/.exec(path)?.[1];if(key)delete d.replacements[key as AnnualKey];return d;});setTouched(old=>[...new Set([...old,path])]);setErrors({});}
 function uniform(key:AnnualKey,value:string){const paths=Array.from({length:5},(_,i)=>annualPath(key,i));setDraft(old=>{const d=structuredClone(old);paths.forEach(p=>{d.rates[p]=value;});delete d.replacements[key];return d;});setTouched(old=>[...new Set([...old,...paths])]);setErrors({});}
 function error(path:string){
  const key=path.startsWith('quick.')?path.slice(6):null;
  const find=(values:Errors)=>values[path]??(key?Object.entries(values).find(([p])=>p.endsWith('.'+key))?.[1]:undefined);
  const edited=key?touched.some(p=>p.endsWith('.'+key)):touched.includes(path);
  return find(errors)??(!edited?find(serverErrors):'');
 }
 function field(path:string,name:string,value=draft.rates[path],change=(v:string)=>rate(path,v)){
  const issue=error(path);return <div className="cv-field" key={path}><label htmlFor={`edit-${path}`}>{name}</label><div><input id={`edit-${path}`} value={value} inputMode="decimal" onChange={e=>change(e.target.value)} aria-invalid={Boolean(issue)} aria-describedby={issue?`edit-${path}-error`:undefined}/><span>%</span></div>{issue&&<small id={`edit-${path}-error`} className="cv-error">{issue}</small>}</div>;
 }
 function reference(r:HistoricalReference){return <aside className="cv-history" key={r.metric}><b>{r.label}</b><strong>{r.value===null?'Unavailable':percentage(r.value)}</strong><details><summary>Reference basis</summary><p>{r.formula}. {r.limitation}</p>{r.operands.map((o,i)=><p key={i}>{o.field==='ebit'?'Operating income':'Revenue'}: {readableMoney(o.amount)} · {o.period_start} → {o.period_end} · source precision {o.precision}. {o.sources.map((s,j)=><a href={s} key={s} target="_blank" rel="noreferrer">SEC source {j+1} </a>)}</p>)}</details><p>Context only; your forecast stays separate.</p></aside>;}
 function annualEditor(key:AnnualKey){
  const name=annual.find(([k])=>k===key)![1],state=annualState(draft,key),mode=modes[key]??(state.varies?'annual':'constant');
  return <fieldset className="cv-driver" key={key}><legend>{name}</legend><p>{help[key]}</p>{entry?.historical_references?.filter(r=>r.metric===key).map(reference)}
   <div className="cv-mode" aria-label={`${name} entry mode`}><button type="button" aria-pressed={mode==='constant'} onClick={()=>setModes(m=>({...m,[key]:'constant'}))}>Constant</button><button type="button" aria-pressed={mode==='annual'} onClick={()=>setModes(m=>({...m,[key]:'annual'}))}>By year</button></div>
   {mode==='constant'?<>{field(`quick.${key}`,`${name} (%)`,state.varies?'':state.value,v=>uniform(key,v))}{state.varies&&<small>Existing values vary. Entering a constant replaces this row's five annual values when you Apply.</small>}</>:<div className="cv-annual-inputs">{draft.doc.forecast_years.map((year,i)=>field(annualPath(key,i),`${year.fiscal_year_label} ${name} (%)`))}</div>}
  </fieldset>;
 }
 function copy(){try{setDraft(copyYearFive(draft));setTouched(old=>[...new Set([...old,...terminal.map(([k])=>`terminal.${k}`)])]);setNotice('Copied five year-five ratios once. Future annual edits will not change them.');}catch(e){if(e instanceof InputErrors){setErrors(e.fields);setActive(sectionFor(Object.keys(e.fields)[0]));setNotice('Year-five operating ratios are incomplete. Nothing was copied.');}}}
 function submit(){const issues:Errors={};for(const [path,value]of Object.entries(draft.rates))if(value.trim())try{percentageToFraction(value);}catch(e){issues[path]=(e as Error).message;}
  for(const key of ['assets','financing','claims','shares'] as const)if(equity[key].trim())try{millionsToUnits(equity[key]);}catch(e){issues['bridge.'+key]=(e as Error).message;}
  if(!draft.doc.case_name.trim())issues.case_name='Enter a case name.';if((draft.doc.preparation.notes?.length??0)>2048)issues['preparation.notes']='Keep notes within 2,048 characters.';
  if(Object.keys(issues).length){setErrors(issues);setActive(sectionFor(Object.keys(issues)[0]));if(issues.case_name||issues['preparation.notes'])setNotesOpen(true);return;}
  apply(draft,equity,touched);close();
 }
 const bridgeErrors=Object.fromEntries(Object.entries({...serverErrors,...errors}).filter(([p])=>p.startsWith('bridge.')).map(([p,m])=>[p.slice(7),m]));
 return <dialog ref={dialog} className="cv-editor" aria-label={`Edit ${company} ${label} assumptions`} onCancel={e=>{e.preventDefault();close();}}>
 <header><div><span className="cv-eyebrow">{company} · {label} case</span><h2>Edit assumptions</h2></div><button type="button" onClick={close} aria-label="Close editor without applying">×</button></header>
 <div className="cv-editor-context">{result?<><b>Last calculated EV {readableMoney(result.stage_b.enterprise_value)}</b><span>{stale?'Stale · previous calculation':'Before editor changes'}</span></>:<b>Not calculated</b>}<small>No live preview. Apply edits, then Calculate.</small></div>
 <nav aria-label="Assumption sections">{editorSections.map(s=><button data-editor-section type="button" key={s} aria-pressed={active===s} onClick={()=>setActive(s)}>{s}</button>)}</nav>
 <div className="cv-editor-body"><h3>{active}</h3><p className="cv-draft-notice">{label==='Base'?'Manual Base inputs.':'Untouched inputs follow Base; applied edits become explicit overrides.'} Drafts stay here when you switch sections. 10 means 10%.</p>
 {active==='Growth'&&annualEditor('revenue_growth')}{active==='Operating margin'&&annualEditor('operating_margin')}{active==='Cash-flow assumptions'&&annual.slice(2).map(([key])=>annualEditor(key))}
 {active==='Discount rate'&&<><p>One constant WACC discounts FCFF for all five years and the terminal value. It must exceed long-term growth.</p>{field('wacc','WACC (%)')}</>}
 {active==='Long-term assumptions'&&<><p>Perpetual-growth FCFF after year five. These five ratios are independent of the annual forecast and require sustainable operating/reinvestment assumptions.</p>{field('terminal_growth','Terminal growth (%)')}<button type="button" className="cv-copy" onClick={copy}>Use year-five assumptions</button><small>Copies only the five operating ratios once; WACC and growth stay unchanged.</small>{notice&&<p role="status">{notice}</p>}{terminal.map(([key,name])=>field(`terminal.${key}`,`${name} (%)`))}<details open={notesOpen} onToggle={e=>setNotesOpen(e.currentTarget.open)}><summary>Case name & personal notes</summary><label htmlFor="edit-case-name">Case name</label><input id="edit-case-name" value={draft.doc.case_name} onChange={e=>setDraft(d=>({...d,doc:{...d.doc,case_name:e.target.value}}))}/><label htmlFor="edit-notes">Optional personal notes</label><textarea id="edit-notes" value={draft.doc.preparation.notes??''} onChange={e=>setDraft(d=>({...d,doc:{...d.doc,preparation:{...d.doc.preparation,notes:e.target.value}}}))}/><p>Notes are not evidence or approval. Creation time is not a valuation date or information cutoff.</p></details></>}
 {active==='Cash, debt and shares'&&<><p>Optional manual bridge. Required coverage, classes, awards and dated shares must be reviewed before calculating value per share; incomplete drafts may be applied.</p><EquityFields values={equity} errors={bridgeErrors} edit={(key,value)=>setEquity(e=>({...e,[key]:value}))} anchorDate={draft.doc.anchor.annual_end} advanced={advanced} setAdvanced={setAdvanced} componentsOpen={componentsOpen} setComponentsOpen={setComponentsOpen}/></>}
 {Object.keys(errors).length>0&&<p className="cv-error" role="alert">Correct the highlighted entries. Blank required inputs remain visibly incomplete.</p>}
 </div><footer><button type="button" onClick={close}>Cancel</button><button type="button" className="cv-primary" onClick={submit}>Apply edits</button></footer>
 </dialog>;
}
