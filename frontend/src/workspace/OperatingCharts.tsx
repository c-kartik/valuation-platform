/** Returned observations only. Endpoint guides and axes are display arithmetic. */
import {useEffect,useId,useRef,useState} from 'react';
import Decimal from 'decimal.js';
import type {Entry,Result} from '../model';
import {fixedUnit,percentage} from '../presentation';
import {submittedMargins,marginCaption} from './chartInspection';
import type {ChartInspection} from './chartInspection';
import {financialAxis} from './chartAxis';
const D=Decimal.clone({precision:220,rounding:Decimal.ROUND_HALF_EVEN});
type Point={label:string;revenue:string;fcff:string|null;historical:boolean};
export function chartRows(result:Result,entry?:Entry):Point[]{
 const anchor=result.submitted_inputs.anchor,year='FY'+anchor.annual_end.slice(0,4);
 const compatible=entry&&Object.entries(anchor).every(([key,value])=>entry.identity[key as keyof typeof anchor]===value);
 const history=compatible?entry.historical_window?.filter(h=>h.revenue.unit==='USD'&&h.revenue.period_end<=anchor.annual_end):undefined;
 const observed=history?.length&&history.at(-1)!.revenue.amount===String(result.stage_b.stage_a.anchor.revenue)?history.map(h=>({label:h.fiscal_year_label,revenue:h.revenue.amount,fcff:h.fcff,historical:true})):[{label:year,revenue:String(result.stage_b.stage_a.anchor.revenue),fcff:null,historical:true}];
 return [...observed,...result.stage_b.stage_a.years.map(y=>({label:String(y.fiscal_year_label),revenue:String(y.revenue),fcff:String(y.fcff),historical:false}))];
}
/** A historical selection starts its comparison; forecast selections start at the anchor. */
export function endpointCagr(anchorLabel:string,anchor:string|null,label:string,value:string|null){
 if(anchor===null||value===null)return null;
 const intervals=Number(label.replace('FY',''))-Number(anchorLabel.replace('FY',''));
 const a=new D(anchor),v=new D(value);
 if(!Number.isInteger(intervals)||intervals===0||!a.gt(0)||!v.gt(0))return null;
 const earlier=intervals<0;
 return {from:earlier?label:anchorLabel,to:earlier?anchorLabel:label,intervals:Math.abs(intervals),
  percent:(earlier?a.div(v):v.div(a)).pow(new D(1).div(Math.abs(intervals))).minus(1).times(100).toFixed(2)};
}
export function endpointGuide(anchorLabel:string,anchor:string|null,label:string,value:string|null){
 if(anchor===null)return `${anchorLabel} FCFF unavailable · no guide`;
 if(label===anchorLabel)return `${anchorLabel} baseline · ${fixedUnit(anchor,'1000000000')} USD bn`;
 if(value===null)return `${label} unavailable · no guide`;
 const a=new D(anchor),v=new D(value),delta=v.minus(a),signed=(x:Decimal,places=2)=>(x.gt(0)?'+':'')+x.toFixed(places);
 const difference=`${signed(delta.div('1000000000'))} USD bn vs ${anchorLabel}`;
 const cagr=endpointCagr(anchorLabel,anchor,label,value);
 if(cagr)return `${cagr.from} → ${cagr.to}: ${cagr.percent}% endpoint CAGR · ${cagr.intervals} fiscal-year ${cagr.intervals===1?'interval':'intervals'}`;
 return `${label}: ${difference} · CAGR unsuitable for zero/negative endpoints`;
}
const palette=['var(--cw-bear, #657c91)','var(--cw-gold, #aa8534)','var(--cw-bull, #39766b)'];
export function OperatingCharts({cases,entry,scenario=false,stale=false,inspection=null}:{cases:{label:string;result:Result}[];entry?:Entry;scenario?:boolean;stale?:boolean;inspection?:ChartInspection|null}){
 const id=useId().replace(/:/g,''),host=useRef<HTMLDivElement>(null),[availableWidth,setWidth]=useState(960),[selected,setSelected]=useState<string|null>(null);
 useEffect(()=>{if(!host.current||typeof ResizeObserver==='undefined')return;const observer=new ResizeObserver(([e])=>{if(e.contentRect.width>0)setWidth(Math.max(1,Math.floor(e.contentRect.width)));});observer.observe(host.current);return()=>observer.disconnect();},[]);
 const ordered=scenario?['Bear','Base','Bull'].flatMap(label=>cases.filter(c=>c.label===label)):cases.slice(0,1);
 if(!ordered.length)return null;
 const rows=ordered.map(c=>({...c,points:chartRows(c.result,entry)})),base=rows.find(c=>c.label==='Base')??rows[0],points=base.points;
 const anchorLabel='FY'+base.result.submitted_inputs.anchor.annual_end.slice(0,4),anchor=points.findIndex(p=>p.label===anchorLabel),firstForecast=points.findIndex(p=>!p.historical),at=Math.max(0,selected?points.findIndex(p=>p.label===selected):points.length-1),point=points[at];
 const metrics=['revenue','fcff'] as const,axes=(scenario?metrics.map(metric=>financialAxis(rows.flatMap(r=>r.points.flatMap(p=>p[metric]===null?[]:[p[metric]!])))):[financialAxis(points.flatMap(p=>[p.revenue,...p.fcff===null?[]:[p.fcff]]))]);
 const focus=scenario?null:inspection,margins=submittedMargins(base.result),marginValues=margins.flatMap(p=>p.value===null?[]:[p.value]);
 const marginAxis=financialAxis(marginValues,'0.01'),hasMargin=marginValues.length>0;
 const marginByYear=new Map(margins.map(p=>[p.label,p.value])),showMargin=focus==='margin'&&hasMargin;
 const width=availableWidth,right=scenario?14:Math.max(80,...marginAxis.ticks.map(v=>marginAxis.label(v).length*7+24)),plotRight=width-right;
 const exit=(base.result.stage_b.terminal_method??('terminal_valuation'in base.result.submitted_inputs?base.result.submitted_inputs.terminal_valuation.method:'perpetual_growth'))==='exit_multiple';
 const descriptions:Record<ChartInspection,string>={revenue:'Forecast revenue highlighted',margin:hasMargin?`Operating margin · ${margins.length} submitted forecast years`:'Operating margin unavailable in the submitted result',cash:'Forecast FCFF highlighted',period:`${points[firstForecast]?.label}–${points.at(-1)?.label} · ${points.length-firstForecast} forecast years`,discount:'Discounts cash flows; operating paths unchanged',terminal:exit?'Final-year operating profit sets the exit value':'Final-year FCFF feeds terminal value'};
 const left=Math.max(68,...axes.flatMap(a=>a.ticks.map(v=>a.label(v).length*7+12))),step=(width-left-right)/points.length,x=(i:number)=>left+(i+.5)*step;
 const money=(v:string|null)=>v===null?'Unavailable':fixedUnit(v,'1000000000',2)+' USD bn';
 function choose(i:number,metric:string,focus=false){const n=Math.max(0,Math.min(points.length-1,i));setSelected(points[n].label);if(focus)document.getElementById(`${id}-${metric}-${n}`)?.focus();}
 function plot(metric:'combined'|'revenue'|'fcff',index:number){
  const a=axes[index],height=metric==='combined'?(width<500?450:520):302,bottom=height-(step<30?52:42),top=34,y=(v:string)=>bottom-a.position(v)*(bottom-top),zero=y('0'),marginY=(value:string)=>bottom-marginAxis.position(value)*(bottom-top);
  const guideMetrics=metric==='combined'?metrics:[metric];
  const bar=(value:string|null,cx:number,bw:number,fill:string,label:string,m:string,i:number)=>value===null?null:<rect key={label+m+i} data-bar-year={points[i].label} data-scenario-bar={points[i].historical?'Reported':label} data-metric={m} data-value={value} x={cx-bw/2} y={Math.min(zero,y(value))} width={bw} height={Math.abs(zero-y(value))} fill={fill} opacity={!focus?1:points[i].historical?.25:focus==='period'?1:focus==='revenue'&&m==='revenue'||focus==='cash'&&m==='fcff'||focus==='terminal'&&i===points.length-1&&(exit||m==='fcff')?1:.22} rx="1"><title>{label} {points[i].label} {m}: {value} USD</title></rect>;
  return <section className={"cv-bar-metric "+(metric==='combined'?'cv-combined-metric':'')} key={metric} aria-label={metric==='combined'?'Combined Revenue and FCFF plot':`${metric==='revenue'?'Revenue':'FCFF'} scenario grouped bar chart`}>{metric!=='combined'&&<div className="cv-chart-heading"><h3>{metric==='revenue'?'Revenue':'FCFF'}</h3><span>Independent USD billions axis</span></div>}{a.scaleNote&&<p>{a.scaleNote}</p>}
  {metric!=='combined'&&<div className="cv-guide-labels">{guideMetrics.map(m=><p key={m} data-guide-label={m}>{m==='revenue'?'Revenue: ':'FCFF: '}{endpointGuide(anchorLabel,points[anchor]?.[m]??null,point.label,point[m])}</p>)}</div>}
  <svg data-chart-height={height} data-plot-right={plotRight} viewBox={`0 0 ${width} ${height}`} role="group" aria-label={`${metric} by fiscal year; arrow keys select a year`}>
   <title>{metric==='combined'?'Revenue and FCFF · shared USD billions axis':`${metric==='revenue'?'Revenue':'FCFF'} · USD billions`}</title>

   <rect x={left+firstForecast*step} y={top} width={step*(points.length-firstForecast)} height={bottom-top} fill={focus==='period'?'#aa853414':'#f1f3f5'}/>
   <text x={left+8} y="20">{firstForecast*step<110?'History':'Reported history'}</text><text x={left+firstForecast*step+8} y="20">Forecast</text>
   {a.ticks.map(v=><g key={v}><line x1={left} x2={plotRight} y1={y(v)} y2={y(v)} stroke="#dce3e8"/><text x={left-10} y={y(v)+4} textAnchor="end">{a.label(v)}</text></g>)}
   <line x1={left} x2={plotRight} y1={zero} y2={zero} stroke="#627184" strokeWidth="1.5"/>
   <line data-period-boundary x1={left+firstForecast*step} x2={left+firstForecast*step} y1={top} y2={bottom} stroke="#9da7b1" strokeDasharray="3 4"/>
   {points.length-firstForecast===10&&<line data-five-year-boundary aria-label="End of first five forecast years" x1={left+(firstForecast+5)*step} x2={left+(firstForecast+5)*step} y1={top} y2={bottom} stroke="#9da7b1" strokeDasharray="2 5"/>}
   <line data-fixed-anchor={anchorLabel} x1={x(anchor)} x2={x(anchor)} y1={top} y2={bottom} stroke="#b18d38" strokeDasharray="2 6"/>
   {points.map((p,i)=><g key={p.label}>{p.historical?bar(p[metric==='fcff'?'fcff':'revenue'],x(i),step*(scenario?.28:.42),'var(--cw-history, #9ba8b2)','Reported',metric==='fcff'?'fcff':'revenue',i):scenario?rows.map((r,k)=>bar(r.points[i][metric as 'revenue'|'fcff'],x(i)+(k-1)*step*.145,step*.12,palette[k],r.label,metric,i)):<>{bar(p.revenue,x(i)-step*.145,step*.27,'var(--cw-revenue, #23435a)',base.label,'revenue',i)}{bar(p.fcff,x(i)+step*.145,step*.27,'var(--cw-gold, #aa8534)',base.label,'fcff',i)}</>}</g>)}
   {guideMetrics.map(m=>{
    const anchorValue=points[anchor]?.[m],selectedValue=point[m];if(anchorValue===null||anchorValue===undefined||selectedValue===null||at===anchor)return null;
    const from=at<anchor?at:anchor,to=at<anchor?anchor:at,start=points[from][m]!,end=points[to][m]!;
    const offset=(i:number)=>metric==='combined'&&!points[i].historical?(m==='revenue'?-step*.145:step*.145):0;
    const x1=x(from)+offset(from),x2=x(to)+offset(to),y1=y(start),y2=y(end),color=m==='revenue'?'#385d7b':'#397d75';
    const cagr=endpointCagr(anchorLabel,anchorValue,point.label,selectedValue);
    const caption=cagr?`${cagr.percent.length>9?new D(cagr.percent).toExponential(3):cagr.percent}% CAGR`:null;
    const labelWidth=caption?caption.length*6.4+16:0,labelX=Math.max(left+labelWidth/2+2,Math.min(plotRight-2-labelWidth/2,(x1+x2)/2));
    const lineY=y1+(y2-y1)*(labelX-x1)/(x2-x1),labelY=Math.max(12,lineY-12);
    return <g key={m} pointerEvents="none" opacity={!focus||focus==='period'||focus==='revenue'&&m==='revenue'||focus==='cash'&&m==='fcff'?1:.13}><line data-base-trend={m} data-start-year={points[from].label} data-end-year={points[to].label} x1={x1} x2={x2} y1={y1} y2={y2} stroke={color} strokeWidth="1.8" strokeDasharray="5 4"/><circle cx={x1} cy={y1} r="4" fill="white" stroke="#aa8637"/><circle cx={x2} cy={y2} r="3.5" fill="white" stroke={color}/>
    {metric==='combined'&&caption&&<g className="cv-floating-cagr" data-cagr-metric={m} data-cagr-from={cagr!.from} data-cagr-to={cagr!.to} data-line-y={lineY} transform={`translate(${labelX} ${labelY})`}><title>{m==='revenue'?'Revenue':'FCFF'}: {endpointGuide(anchorLabel,anchorValue,point.label,selectedValue)}</title><rect x={-labelWidth/2} y="-19" width={labelWidth} height="24" rx="4" fill="white" stroke="#dce3e8"/><text textAnchor="middle" y="-3" style={{fill:color}}>{caption}</text></g>}
    </g>;
   })}
   {showMargin&&<g className="cw-margin-overlay" aria-label="Submitted operating margin · right percentage axis" pointerEvents="none">
    <line data-margin-axis x1={plotRight} x2={plotRight} y1={top} y2={bottom} stroke="var(--cw-bull, #39766b)" opacity=".4"/>
    <text x={plotRight+8} y="20">Margin (%)</text>
    {marginAxis.ticks.map(v=><text key={v} x={plotRight+8} y={marginY(v)+4}>{marginAxis.label(v)}%</text>)}
    {marginAxis.scaleNote&&<text x={plotRight} y="6" textAnchor="end"><title>{marginAxis.scaleNote}</title>Axis multiplier: {new D(marginAxis.scaleNote.match(/× (.+) in/)![1]).toExponential(2)}</text>}
    <path data-margin-line d={points.map((p,i)=>{const value=marginByYear.get(p.label);return value===null||value===undefined?'':`${i>0&&marginByYear.get(points[i-1].label)!=null?'L':'M'}${x(i)} ${marginY(value)}`;}).join(' ')} fill="none" stroke="var(--cw-bull, #39766b)" strokeWidth="2.5"/>
    {points.map((p,i)=>{const value=marginByYear.get(p.label);if(value===null||value===undefined)return null;return <g key={p.label}><circle data-margin-year={p.label} data-margin-value={value} cx={x(i)} cy={marginY(value)} r="4" fill="white" stroke="var(--cw-bull, #39766b)" strokeWidth="2"><title>{p.label}: operating margin {percentage(value)} · submitted assumption</title></circle>{(step>=58||i===points.length-1)&&<text className="cw-margin-point-label" x={x(i)} y={Math.max(top+13,marginY(value)-12)} textAnchor={step<58?(i===firstForecast?'start':'end'):'middle'}>{marginCaption(value)}</text>}</g>;})}
   </g>}
   {focus==='period'&&<path data-inspected-period d={`M${left+firstForecast*step+4} ${top-7} v5 H${plotRight-4} v-5`} fill="none" stroke="var(--cw-gold, #aa8534)" strokeWidth="2" pointerEvents="none"/>}
   {focus==='terminal'&&<g pointerEvents="none"><line data-terminal-inspection x1={plotRight} x2={plotRight} y1={top} y2={bottom} stroke="var(--cw-gold, #aa8534)" strokeWidth="2" strokeDasharray="3 4"/><text x={plotRight-6} y={top+16} textAnchor="end">Terminal value →</text></g>}
   {points.map((p,i)=><g key={p.label} id={`${id}-${metric}-${i}`} className="cv-year" role="button" tabIndex={0} aria-pressed={at===i} aria-label={`${metric}: select ${p.label}${i===anchor?', fixed anchor':''}`} onFocus={()=>choose(i,metric)} onMouseMove={()=>choose(i,metric)} onClick={()=>choose(i,metric)} onKeyDown={e=>{if(['ArrowLeft','ArrowRight','Home','End','Enter',' '].includes(e.key)){e.preventDefault();choose(e.key==='Home'?0:e.key==='End'?points.length-1:i+(e.key==='ArrowRight'?1:e.key==='ArrowLeft'?-1:0),metric,true);}}}>
    <rect className="cv-year-highlight" x={left+i*step} y={top} width={step} height={bottom-top+30} fill={at===i?'#aa863714':'transparent'}/><line x1={x(i)-18} x2={x(i)+18} y1={bottom+4} y2={bottom+4} stroke={at===i?'#aa8637':'transparent'} strokeWidth="2"/>
    <text x={x(i)} y={bottom+(step<30?12:22)} transform={step<30?`rotate(-60 ${x(i)} ${bottom+12})`:undefined} textAnchor={step<30?'end':'middle'} fontSize={step<45?9:11}>{step<45?p.label.replace('FY',''):p.label}</text>{i===anchor&&step>=50&&<text className="cv-anchor-label" x={x(i)} y={bottom+37} textAnchor="middle">Fixed anchor</text>}
   </g>)}
  </svg></section>;
 }
 const legend=<div className="cv-chart-legend">{scenario?rows.map((r,k)=><span key={r.label}><i style={{background:palette[k]}}/>{r.label}</span>):<><span><i style={{background:'var(--cw-revenue, #23435a)'}}/>Revenue</span><span><i style={{background:'var(--cw-gold, #aa8534)'}}/>FCFF</span></>}<span><i style={{background:'var(--cw-history, #9ba8b2)'}}/>Reported</span>{!scenario&&<span className="cw-margin-legend" aria-hidden={!showMargin} style={{visibility:showMargin?'visible':'hidden'}}><i/>Operating margin · right axis</span>}<small>USD billions · CAGR compares the selected year with {anchorLabel}</small></div>;
 return <section className="cv-operating-charts" data-chart-inspection={focus??undefined} aria-label={scenario?'Scenario revenue and FCFF paths':'Interactive revenue and FCFF chart'}>
  {stale&&<p className="cv-stale">Previous operating calculation · stale; values retain their submitted inputs.</p>}
  {scenario&&legend}
  <div className={"cv-operating-readout "+(scenario?"cv-scenario-readout":"")} aria-live="polite"><b>{point.label} · {point.historical?'reported history':'forecast'} · USD billions</b><div className="cv-table-scroll"><table><thead><tr><th>Basis</th><th>{!scenario&&<i className="cw-swatch" style={{background:'var(--cw-revenue, #23435a)'}}/>}Revenue</th><th>{!scenario&&<i className="cw-swatch" style={{background:'var(--cw-gold, #aa8534)'}}/>}FCFF</th></tr></thead><tbody>{(point.historical?[base]:rows).map(r=><tr key={r.label}><th>{(scenario||point.historical)&&<i className="cw-swatch" style={{background:point.historical?'var(--cw-history, #9ba8b2)':scenario?palette[rows.indexOf(r)]:'var(--cw-revenue, #23435a)'}}/>}{point.historical?'Reported':r.label}</th>{metrics.map(m=><td key={m} title={r.points[at][m]===null?'Unavailable':r.points[at][m]+' USD'}><strong>{money(r.points[at][m])}</strong>{scenario&&!point.historical&&r.label!=='Base'&&<small>vs Base: {money(new D(r.points[at][m]!).minus(base.points[at][m]!).toFixed())}</small>}</td>)}</tr>)}</tbody></table></div></div>
  {!scenario&&<div className="cw-chart-inspection" aria-hidden={!focus}><span>{focus?descriptions[focus]:''}{focus&&stale?' · Previous result':''}</span>{showMargin&&<strong>{point.label} · {marginByYear.get(point.label)!=null?marginCaption(marginByYear.get(point.label)!):'Unavailable'}</strong>}</div>}
  <div ref={host} className="cv-operating-scroll" role="region" aria-label="Financial charts, all years visible"><div className="cv-operating-stage">{scenario?<>{plot('revenue',0)}{plot('fcff',1)}</>:plot('combined',0)}</div></div>
  {!scenario&&legend}
  <p className="cv-pan-note">Hover, tap or focus a year column for exact values. Arrow keys move between years.</p><p className="cv-history-gap">Historical FCFF unavailable — filing components are not yet reconciled to this model. Missing values are not zero.</p>
  <details><summary>Exact chart observations & sources</summary><div className="cv-table-scroll"><table><caption>Unrounded returned/retained amounts · USD</caption><thead><tr><th>Basis / year</th><th>Revenue</th><th>FCFF</th></tr></thead><tbody>{rows.flatMap((r,k)=>r.points.filter(p=>!p.historical||k===0).map(p=><tr key={r.label+p.label}><th>{p.historical?'Reported':r.label} {p.label}</th><td>{p.revenue}</td><td>{p.fcff??'Unavailable'}</td></tr>))}</tbody></table></div>{entry?.historical_window?.map(h=><p key={h.fiscal_year_label}>{h.fiscal_year_label}: {h.revenue.period_start} → {h.revenue.period_end}; precision {h.revenue.precision}; {h.revenue.concept}; {h.revenue.accession}. {h.revenue.sources.map(s=><a href={s} key={s} target="_blank" rel="noreferrer">SEC source </a>)}</p>)}</details>
 </section>;
}
