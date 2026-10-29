import {useEffect,useId,useRef,useState} from 'react';
import Decimal from 'decimal.js';
import type {Result} from '../model';
import {fixedUnit} from '../presentation';
import {financialAxis} from './chartAxis';
const D=Decimal.clone({precision:220,rounding:Decimal.ROUND_HALF_EVEN});
type Metric='both'|'revenue'|'fcff';
export function ForecastChart({cases,comparison=false}:{cases:{label:string;result:Result}[];comparison?:boolean}){
 const id=useId().replace(/:/g,''),host=useRef<HTMLDivElement>(null),[width,setWidth]=useState(700),[selected,setSelected]=useState(comparison?'Compare':'Base'),[metric,setMetric]=useState<Metric>(comparison?'fcff':'both'),[year,setYear]=useState(1);
 useEffect(()=>{if(typeof ResizeObserver==='undefined')return;const node=host.current!;const observer=new ResizeObserver(([entry])=>setWidth(Math.max(300,Math.round(entry.contentRect.width))));observer.observe(node);return()=>observer.disconnect();},[]);
 const compare=comparison||selected==='Compare',chosen=cases.find(c=>c.label===selected)??cases.find(c=>c.label==='Base')??cases[0];if(!chosen)return null;
 const visible=compare?cases:[chosen],shownMetric=compare&&metric==='both'?'fcff':metric;
 const rows=visible.map(c=>({label:c.label,rows:[{label:'FY'+c.result.submitted_inputs.anchor.annual_end.slice(0,4),revenue:String(c.result.stage_b.stage_a.anchor.revenue),fcff:null},...c.result.stage_b.stage_a.years.map(y=>({label:String(y.fiscal_year_label),revenue:String(y.revenue),fcff:String(y.fcff)}))]}));
 const values=rows.flatMap(c=>c.rows.flatMap(y=>[...(shownMetric!=='fcff'?[y.revenue]:[]),...(shownMetric!=='revenue'&&y.fcff!==null?[y.fcff]:[])])).map(v=>new D(v));
 const axis=financialAxis(values.map(v=>v.toFixed())),flat=values.every(v=>v.isZero()),left=Math.min(width*.45,Math.max(64,...axis.ticks.map(v=>axis.label(v).length*6.5+12))),step=(width-left-8)/6;
 const y=(v:string)=>226-axis.position(v)*174,zero=y('0'),colors=['#61758a','#ae8d40','#37746f'];
 function move(i:number){const n=Math.max(0,Math.min(5,i));setYear(n);document.getElementById(`${id}-year-${n}`)?.focus();}
 return <section className="cv-chart ir-chart" aria-label="Interactive revenue and FCFF chart"><div className="cv-chart-heading"><h2>{compare?'Compare operating paths':'Revenue & FCFF'}</h2><span>USD billions</span></div>{axis.scaleNote&&<p className="cv-axis-scale">{axis.scaleNote}</p>}
 <div className="cv-chart-tools">{cases.length>1&&!comparison&&<div className="cv-segments" aria-label="Chart case">{[...cases.map(c=>c.label),'Compare'].map(label=><button key={label} aria-pressed={selected===label} onClick={()=>{setSelected(label);if(label==='Compare')setMetric('fcff');}}>{label}</button>)}</div>}
 <div className="cv-segments" aria-label="Chart metric">{(compare?(['revenue','fcff']as Metric[]):(['both','revenue','fcff']as Metric[])).map(m=><button key={m} aria-pressed={shownMetric===m} onClick={()=>setMetric(m)}>{m==='both'?'Revenue + FCFF':m==='revenue'?'Revenue only':'FCFF only'}</button>)}</div></div>
 <div className="cv-chart-readout" role="status" aria-live="polite"><b>{rows[0].rows[year].label} · {year===0?'reported revenue':'forecast'}</b>{rows.map(c=><span key={c.label}>{cases.length>1?c.label+': ':''}Revenue {fixedUnit(c.rows[year].revenue,'1000000000',2)}bn <i>·</i> FCFF {c.rows[year].fcff===null?'unavailable':fixedUnit(c.rows[year].fcff,'1000000000',2)+'bn'}</span>)}</div>
 <div ref={host} className="cv-plot"><svg viewBox={`0 0 ${width} 282`} aria-label="Revenue and FCFF by fiscal year; arrow keys select a year" role="group">
 <defs><pattern id={`${id}-fcff`} width="7" height="7" patternUnits="userSpaceOnUse"><rect width="7" height="7" fill="#b59b61"/><path d="M0 0L7 7" stroke="#ffffff70" strokeWidth="1"/></pattern></defs>
 <rect x={left+step} y="32" width={step*5} height="204" fill="#f4f5f6"/><text x={left+4} y="20">History</text><text x={left+step+6} y="20">Forecast</text>
 {axis.ticks.map(v=>{const py=y(v);return <g key={v}><line x1={left} x2={width-8} y1={py} y2={py} stroke="#dfe4e9"/><text x={left-8} y={py+4} textAnchor="end">{axis.label(v)}</text></g>;})}
 <line x1={left} x2={width-8} y1={zero} y2={zero} stroke="#627184"/>
 <line x1={left+step} x2={left+step} y1="30" y2="236" stroke="#9da7b1" strokeDasharray="3 4"/>
 {rows[0].rows.map((_,i)=><g key={i} id={`${id}-year-${i}`} className="cv-year" role="button" tabIndex={0} aria-pressed={year===i} aria-label={`Select ${rows[0].rows[i].label}, ${i===0?'reported revenue; FCFF unavailable':'forecast revenue and FCFF'}`} onFocus={()=>setYear(i)} onMouseEnter={()=>setYear(i)} onClick={()=>setYear(i)} onKeyDown={e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();move(e.key==='Home'?0:e.key==='End'?5:i+(e.key==='ArrowRight'?1:-1));}else if(e.key==='Enter'||e.key===' '){e.preventDefault();setYear(i);}}}>
 <rect className="cv-year-highlight" x={left+i*step+2} y="34" width={step-4} height="202" fill={year===i?'#ac8a3412':'transparent'} rx="3"/><line className="cv-year-marker" x1={left+i*step+7} x2={left+(i+1)*step-7} y1="239" y2="239" stroke={year===i?'#a48130':'transparent'} strokeWidth="2"/>
 {rows.map((c,k)=>{const r=c.rows[i],bars=compare?rows.length:shownMetric==='both'?2:1,bw=Math.min(25,(step-14)/bars),x=left+i*step+(step-bw*bars)/2+k*bw;const bar=(value:string,at:number,fill:string)=><rect x={at} y={Math.min(zero,y(value))} width={Math.max(1,bw-3)} height={new D(value).isZero()?0:Math.max(.4,Math.abs(zero-y(value)))} fill={fill}/>;return <g key={c.label}>{shownMetric!=='fcff'&&bar(r.revenue,x,i===0?'#9aa5b0':compare?colors[k]:'#233f59')}{shownMetric!=='revenue'&&r.fcff!==null&&bar(r.fcff,x+(shownMetric==='both'?bw:0),compare?colors[k]:`url(#${id}-fcff)`)}<title>{c.label} {r.label}: revenue {fixedUnit(r.revenue,'1000000000',2)} USD bn; FCFF {r.fcff===null?'unavailable':fixedUnit(r.fcff,'1000000000',2)+' USD bn'}</title></g>;})}
 <text x={left+(i+.5)*step} y="258" textAnchor="middle">{rows[0].rows[i].label.replace(/^FY/,'')}</text>
 </g>)}</svg></div>
 <div className="cv-chart-legend">{compare?rows.map((c,i)=><span key={c.label}><i style={{background:colors[i]}}/>{c.label}</span>):<>{shownMetric!=='fcff'&&<span><i/>Revenue</span>}{shownMetric!=='revenue'&&<span><i className="cv-fcff-swatch"/>FCFF</span>}</>}<small>{flat?'All displayed cash flows are zero. ':''}One reported revenue anchor; historical FCFF unavailable.</small></div>
 <details className="cv-data-table"><summary>View data table</summary><div className="cv-table-scroll"><table><caption>Revenue and FCFF · USD billions; — means unavailable</caption><thead><tr><th>Case / year</th><th>Basis</th><th>Revenue</th><th>FCFF</th></tr></thead><tbody>{rows.flatMap(c=>c.rows.map((r,i)=><tr key={c.label+i}><th>{c.label} {r.label}</th><td>{i===0?'Reported':'Forecast'}</td><td>{fixedUnit(r.revenue,'1000000000',2)}</td><td>{r.fcff===null?'—':fixedUnit(r.fcff,'1000000000',2)}</td></tr>))}</tbody></table></div></details>
 </section>;
}
