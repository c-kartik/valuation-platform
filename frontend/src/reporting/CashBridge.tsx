import {useEffect,useRef,useState} from 'react';
import {money,billions} from './model';
export type BridgeObservation={id:string;values:Record<'net_income'|'sbc'|'cfo'|'cash_capex'|'fcf'|'other_operating',number>};
function useChartWidth(){
 const ref=useRef<HTMLDivElement>(null),[width,setWidth]=useState(760);
 useEffect(()=>{const node=ref.current;if(!node)return;const resize=()=>setWidth(Math.max(250,node.clientWidth||760));resize();if(typeof ResizeObserver==='undefined')return;const observer=new ResizeObserver(resize);observer.observe(node);return()=>observer.disconnect();},[]);
 return {ref,width};
}
function CashBridge({row}:{row:BridgeObservation}){
 const {ref,width}=useChartWidth(),v=row.values,height=285,left=46,right=12,top=30,bottom=50;
 const steps=[{label:'Net income',a:0,b:v.net_income,total:true},{label:'SBC',a:v.net_income,b:v.net_income+v.sbc},{label:'Other',a:v.net_income+v.sbc,b:v.cfo},{label:'CFO',a:0,b:v.cfo,total:true},{label:'Cash capex',a:v.cfo,b:v.fcf},{label:'FCF',a:0,b:v.fcf,total:true}];
 const hi=Math.max(...steps.flatMap(s=>[s.a,s.b]),0)*1.17||1,lo=Math.min(...steps.flatMap(s=>[s.a,s.b]),0)*1.2,range=hi-lo;
 const y=(n:number)=>top+(hi-n)/range*(height-top-bottom),step=(width-left-right)/6,bw=Math.min(64,step*.62);
 return <div ref={ref} className="qr-chart"><svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`${row.id} cash-flow bridge from net income through operating cash flow to free cash flow`}><text x={0} y={12}>USD B</text>
 {[0,1,2,3,4].map(i=>{const n=lo+range*i/4;return <g key={i}><line x1={left} x2={width-right} y1={y(n)} y2={y(n)} className="qr-grid"/><text x={left-7} y={y(n)+4} textAnchor="end">{(n/1e9).toFixed(0)}</text></g>;})}
 {steps.map((s,i)=>{const x=left+step*i+(step-bw)/2,delta=s.b-s.a,n=s.total?s.b:delta;return <g key={s.label}><rect x={x} y={Math.min(y(s.a),y(s.b))} width={bw} height={Math.max(1,Math.abs(y(s.a)-y(s.b)))} fill={s.total?'#21485a':delta<0?'#a48031':'#397965'}><title>{s.label}: {money(n)}</title></rect><text x={x+bw/2} y={Math.min(y(s.a),y(s.b))-8} textAnchor="middle" className="qr-bar-value">{n<0?'−':s.total?'':'+'}{billions(n)}</text><text x={x+bw/2} y={height-26} textAnchor="middle">{s.label.split(' ').map((word,j)=><tspan key={j} x={x+bw/2} dy={j?13:0}>{word}</tspan>)}</text>{i<5&&i!==2&&<line x1={x+bw} x2={left+step*(i+1)+(step-bw)/2} y1={y(s.b)} y2={y(s.b)} className="qr-grid"/>}</g>;})}
 </svg></div>;
}
export function CashBridgePanel({row,label,start,end}:{row:BridgeObservation;label:string;start:string;end:string}){
 return <section id="company-cash-bridge" className="qr-panel qr-bridge" aria-labelledby="cash-bridge-heading"><header className="qr-panel-heading"><div><span className="qr-eyebrow">03 / Cash generation</span><h2 id="cash-bridge-heading">From earnings to cash</h2><p>{label} · {start} — {end}</p></div><span className="qr-eyebrow">Net income → CFO → FCF</span></header><div className="oc-cash-bridge-layout"><CashBridge row={row}/><dl className="qr-reconciliation"><div><dt>Operating cash flow</dt><dd>{money(row.values.cfo)}</dd></div><div><dt>Cash capex</dt><dd>{money(row.values.cash_capex)}</dd></div><div><dt>Free cash flow</dt><dd>{money(row.values.fcf)}</dd></div></dl></div><p className="qr-disclosure">FCF = CFO − cash PP&amp;E purchases; separate from FCFF/FCFE. “Other” groups remaining noncash adjustments and operating asset/liability movements: CFO − net income − SBC. SBC add-back is an accounting reconciliation, not an assertion that compensation is free.</p></section>;
}
