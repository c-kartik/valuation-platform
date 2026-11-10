import {methodOf,multipleDisplay} from '../model';
import type {Draft,TerminalMethod} from '../model';
/** Main-view method selection; all input and calculation state stays in Workspace. */
export function TerminalMethodControl({draft,busy,pending,change,edit}:{draft:Draft;busy:boolean;pending:boolean;change:(method:TerminalMethod)=>void;edit:()=>void}){
 const selected=methodOf(draft),multiple=draft.rates.exit_ev_ebit_multiple?.trim(),growth=draft.rates.terminal_growth?.trim();
 let exitValue='Not set';try{if(multiple)exitValue=multipleDisplay(multiple);}catch{exitValue='Check input';}
 return <section className="oc-terminal-method" aria-label="Terminal method"><div className="oc-terminal-choice"><span className="oc-eyebrow">Terminal method</span><div className="oc-terminal-buttons" role="group" aria-label="Choose terminal method">{(['perpetual_growth','exit_multiple'] as const).map(method=><button type="button" key={method} aria-pressed={selected===method} disabled={busy||pending} onClick={()=>{if(method!==selected)change(method);}}>{method==='perpetual_growth'?'Perpetual growth':'Exit multiple'}</button>)}</div></div><div className="oc-terminal-input"><span>{selected==='exit_multiple'?`Final-year EV / EBIT · ${exitValue}`:`Terminal growth · ${growth?growth+'%':'Not set'}`}</span>{selected==='exit_multiple'&&!multiple&&<button type="button" disabled={busy} onClick={edit}>Enter exit multiple</button>}</div>{pending&&<p role="status">Apply pending rate changes before switching methods.</p>}</section>;
}
