import {useId,useState} from 'react';
import Decimal from 'decimal.js';
import type {Result} from '../model';
import {fixedUnit} from '../presentation';
const D=Decimal.clone({precision:220,rounding:Decimal.ROUND_HALF_EVEN});
export function ForecastChart({cases}:{cases:{label:string;result:Result}[]}){
 const id=useId().replace(/:/g,''),[selected,setSelected]=useState('Base'),[metric,setMetric]=useState<'both'|'revenue'|'fcff'>('both'),[year,setYear]=useState(1);
 const chosen=cases.find(c=>c.label===selected)??cases.find(c=>c.label==='Base')??cases[0];if(!chosen)return null;
 const visible=selected==='Compare'?cases:[chosen];
 const rows=visible.map(c=>({label:c.label,rows:[{fiscal_year_label:String(c.result.submitted_inputs.anchor.annual_end.slice(0,4)),revenue:String(c.result.stage_b.stage_a.anchor.revenue),fcff:null},...c.result.stage_b.stage_a.years.map(y=>({fiscal_year_label:String(y.fiscal_year_label).replace('FY',''),revenue:String(y.revenue),fcff:String(y.fcff)}))]}));
 const values=rows.flatMap(c=>c.rows.flatMap(y=>[...(metric!=='fcff'?[y.revenue]:[]),...(metric!=='revenue'&&y.fcff!==null?[y.fcff]:[])])).map(v=>new D(v));
 const min=values.reduce((a,b)=>D.min(a,b),new D(0)),max=values.reduce((a,b)=>D.max(a,b),new D(0)),range=max.minus(min).isZero()?new D(1):max.minus(min);
 const y=(v:string)=>260-new D(v).minus(min).div(range).times(210).toNumber(),zero=y('0');
 function move(i:number){const n=Math.max(0,Math.min(5,i));setYear(n);document.getElementById(`${id}-year-${n}`)?.focus();}
 return <section className="ir-chart p-panel" aria-label="Interactive revenue and FCFF chart"><div className="p-view-title"><div><span className="p-eyebrow">OPERATING PATH</span><h3>Revenue & free cash flow to the firm</h3><p>USD billions · reported revenue followed by five forecast years</p></div></div>
 {cases.length>1&&<div className="p-tabs" aria-label="Chart case">{[...cases.map(c=>c.label),'Compare'].map(label=><button key={label} aria-pressed={selected===label} onClick={()=>setSelected(label)}>{label}</button>)}</div>}
 <div className="p-tabs" aria-label="Chart metric">{(['both','revenue','fcff'] as const).map(m=><button key={m} aria-pressed={metric===m} onClick={()=>setMetric(m)}>{m==='both'?'Revenue + FCFF':m==='revenue'?'Revenue only':'FCFF only'}</button>)}</div>
 <p className="ir-legend">Solid bars: Revenue · patterned bars: FCFF. Grey: reported history. {selected==='Compare'?'Bear / Base / Bull grouped within each year.':''}</p>{selected==='Compare'&&<ul className="ir-case-legend">{cases.map((c,i)=><li key={c.label}><span style={{background:['#597089','#b39a55','#47746b'][i]}} aria-hidden="true"/>{c.label} · pair {i+1} from left</li>)}</ul>}
 <div className="p-table-wrap" role="region" aria-label="Scrollable interactive forecast chart" tabIndex={0}><svg viewBox="0 0 820 330" className="ir-forecast-svg" aria-label="Revenue and FCFF by fiscal year; arrow keys select a year" role="group">
 <defs>{['#597089','#b39a55','#47746b'].map((color,i)=><pattern id={`${id}-pattern-${i}`} key={i} width="5" height="5" patternUnits="userSpaceOnUse"><rect width="5" height="5" fill={color}/><path d="M0 0L5 5" stroke="white" strokeWidth="1"/></pattern>)}</defs>
 {[0,1,2,3,4].map(i=>{const v=min.plus(range.times(i).div(4));const py=y(v.toFixed());return <g key={i}><line x1="80" x2="800" y1={py} y2={py} stroke="#dce1e8"/><text x="70" y={py+4} textAnchor="end">{fixedUnit(v.toFixed(),'1000000000',2)}</text></g>;})}
 <line x1="80" x2="800" y1={zero} y2={zero} stroke="#263b50" strokeWidth="1.5"/>
 <line x1="200" x2="200" y1="32" y2="280" stroke="#778594" strokeDasharray="5 4"/>
 {rows[0].rows.map((_,i)=><g key={i} id={`${id}-year-${i}`} role="button" tabIndex={0} aria-pressed={year===i} aria-label={`Select FY${rows[0].rows[i].fiscal_year_label}, ${i===0?'reported revenue; FCFF unavailable':'forecast revenue and FCFF'}`} onFocus={()=>setYear(i)} onMouseEnter={()=>setYear(i)} onClick={()=>setYear(i)} onKeyDown={e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();move(e.key==='Home'?0:e.key==='End'?5:i+(e.key==='ArrowRight'?1:-1));}else if(e.key==='Enter'||e.key===' '){e.preventDefault();setYear(i);}}}>
 <rect x={82+i*120} y="35" width="116" height="245" fill={year===i?'#b39a5518':'transparent'} stroke={year===i?'#a58a43':'transparent'} rx="4"/>
 {rows.map((c,k)=>{const r=c.rows[i],width=selected==='Compare'?12:28,x=106+i*120+k*32-(rows.length-1)*13;return <g key={c.label}>{metric!=='fcff'&&<rect x={x} y={Math.min(zero,y(r.revenue))} width={width} height={new D(r.revenue).isZero()?0:Math.max(.3,Math.abs(zero-y(r.revenue)))} fill={i===0?'#8d99a5':['#597089','#b39a55','#47746b'][k]}/>} {metric!=='revenue'&&r.fcff!==null&&<rect x={x+width+2} y={Math.min(zero,y(r.fcff))} width={width} height={new D(r.fcff).isZero()?0:Math.max(.3,Math.abs(zero-y(r.fcff)))} fill={`url(#${id}-pattern-${k})`}/>}<title>{c.label} FY{r.fiscal_year_label}: revenue {fixedUnit(r.revenue,'1000000000',2)} USD bn; FCFF {r.fcff===null?'unavailable':fixedUnit(r.fcff,'1000000000',2)+' USD bn'}</title></g>;})}
 <text x={140+i*120} y="302" textAnchor="middle">FY{rows[0].rows[i].fiscal_year_label}</text><text x={140+i*120} y="320" textAnchor="middle">{i===0?'Reported':'Forecast'}</text>
 </g>)}
 <text x="80" y="22">USD billions</text></svg></div>
 <div className="ir-year-readout" role="status" aria-live="polite"><b>FY{rows[0].rows[year].fiscal_year_label} · {year===0?'reported revenue':'forecast'}</b>{rows.map(c=><span key={c.label}>{c.label}: Revenue {fixedUnit(c.rows[year].revenue,'1000000000',2)}bn · FCFF {c.rows[year].fcff===null?'unavailable':fixedUnit(c.rows[year].fcff,'1000000000',2)+'bn'}</span>)}</div>
 <p>One scale; use FCFF only to inspect smaller cash flows. Negative FCFF is a cash outflow. Historical FCFF is unavailable.</p>
 <details><summary>View data table</summary><div className="p-table-wrap"><table><caption>Revenue and FCFF · USD billions; — means unavailable</caption><thead><tr><th>Case / year</th><th>Basis</th><th>Revenue</th><th>FCFF</th></tr></thead><tbody>{rows.flatMap(c=>c.rows.map((r,i)=><tr key={c.label+i}><th>{c.label} FY{r.fiscal_year_label}</th><td>{i===0?'Reported':'Forecast'}</td><td>{fixedUnit(r.revenue,'1000000000',2)}</td><td>{r.fcff===null?'—':fixedUnit(r.fcff,'1000000000',2)}</td></tr>))}</tbody></table></div></details>
 </section>;
}
