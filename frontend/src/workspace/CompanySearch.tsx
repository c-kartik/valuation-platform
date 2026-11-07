import {useEffect,useId,useRef,useState} from 'react';
import './CompanySearch.css';

export type SearchCompany={kind:string;company:string;name:string};
export function CompanySearch({companies,selected,disabled=false,onSelect}:{companies:SearchCompany[];selected:string;disabled?:boolean;onSelect:(kind:string)=>void}){
 const id=useId(),root=useRef<HTMLDivElement>(null);
 const [open,setOpen]=useState(false),[query,setQuery]=useState(''),[active,setActive]=useState(0);
 const term=query.trim().toLowerCase();
 const rank=(c:SearchCompany)=>c.company.toLowerCase()===term?0:c.company.toLowerCase().startsWith(term)?1:c.name.toLowerCase().startsWith(term)?2:3;
 const matches=term?companies.filter(c=>`${c.company} ${c.name}`.toLowerCase().includes(term)).sort((a,b)=>rank(a)-rank(b)):companies.slice(0,3);
 const index=Math.min(active,Math.max(0,matches.length-1));
 function close(){setOpen(false);setQuery('');setActive(0);}
 function show(){setQuery('');setActive(0);setOpen(true);}
 function choose(c:SearchCompany){close();onSelect(c.kind);}
 useEffect(()=>{
  if(!open)return;
  function outside(e:PointerEvent){if(!root.current?.contains(e.target as Node))close();}
  document.addEventListener('pointerdown',outside);
  return()=>document.removeEventListener('pointerdown',outside);
 },[open]);
 return <div className="company-search" ref={root} onBlur={e=>{if(!e.currentTarget.contains(e.relatedTarget as Node|null))close();}}>
  <label htmlFor={id}>Company</label>
  <input id={id} type="text" role="combobox" aria-autocomplete="list" aria-expanded={open} aria-controls={open?`${id}-list`:undefined} aria-activedescendant={open&&matches.length?`${id}-option-${index}`:undefined}
   autoComplete="off" spellCheck={false} disabled={disabled} placeholder="Search" value={open?query:''}
   onFocus={show} onClick={()=>{if(!open)show();}} onChange={e=>{setQuery(e.target.value);setActive(0);setOpen(true);}}
   onKeyDown={e=>{
    if(e.key==='Escape'){e.preventDefault();close();}
    else if(e.key==='ArrowDown'||e.key==='ArrowUp'){
     e.preventDefault();
     if(!open){show();setActive(e.key==='ArrowUp'?Math.max(0,Math.min(companies.length,3)-1):0);}
     else if(matches.length)setActive((index+(e.key==='ArrowDown'?1:-1)+matches.length)%matches.length);
    }else if(e.key==='Enter'&&open){e.preventDefault();if(matches[index])choose(matches[index]);}
    else if(e.key==='Tab')close();
   }}/>
  {open&&<div className="company-search-panel">
   <p className="company-search-heading">{term?'Matching companies':'Suggested tickers'}</p>
   <div id={`${id}-list`} role="listbox" aria-label="Company suggestions">
    {matches.map((c,i)=><button type="button" role="option" aria-selected={i===index} id={`${id}-option-${i}`} key={c.kind} tabIndex={-1}
     onMouseDown={e=>e.preventDefault()} onMouseEnter={()=>setActive(i)} onClick={()=>choose(c)}>
     <strong>{c.company}</strong><span>{c.name}</span>{c.kind===selected&&<small>Current</small>}
    </button>)}
   </div>
   <p className="company-search-status" role="status">{matches.length?`${matches.length} ${matches.length===1?'company':'companies'} available`:'No prepared dataset available. Try another ticker or company name.'}</p>
  </div>}
 </div>;
}
