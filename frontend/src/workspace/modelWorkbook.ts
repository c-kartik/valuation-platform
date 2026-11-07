import ExcelJS from 'exceljs';
import {annual,terminal,methodOf} from '../model';
import type {Draft} from '../model';
import type {ModelSnapshot} from './modelSnapshot';

const navy='17384B',muted='596B7A',blue='1455A3',line='DCE4EA';
const money='#,##0.00;[Red](#,##0.00);0.00';
type Sheet=ExcelJS.Worksheet;
const pretty=(s:string)=>s.replace(/([a-z])([A-Z])/g,'$1 $2').replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase());
const decimal=(s:unknown)=>typeof s==='string'&&/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(s.trim())&&Number.isFinite(Number(s));
/** Only presentation cells use Excel's numeric precision. Exact text is retained in Model State. */
function amount(s:unknown):ExcelJS.CellValue{return s===null||s===undefined||s===''?null:decimal(s)?Number(s):typeof s==='string'?s:String(s);}
function rate(s:string|undefined):ExcelJS.CellValue{return !s?.trim()?null:decimal(s)?Number(s)/100:s;}
function sheet(w:ExcelJS.Workbook,name:string,widths:number[]=[43,33,33,33]):Sheet{
 const s=w.addWorksheet(name,{views:[{showGridLines:false}],properties:{defaultRowHeight:19}});
 s.columns=widths.map(width=>({width}));
 s.pageSetup={orientation:'landscape',paperSize:9,fitToPage:true,fitToWidth:1,fitToHeight:0};
 return s;
}
function row(s:Sheet,values:ExcelJS.CellValue[],format?:string){
 const r=s.addRow(values.map(v=>v===''?null:typeof v==='string'&&v.length>32700?v.slice(0,32650)+'… [Full text in Model State]':v));r.eachCell(c=>{c.font={name:'Arial',size:10,color:{argb:navy}};c.alignment={vertical:'middle',wrapText:true};if(typeof c.value==='number')c.numFmt=format??money;});
 r.height=Math.max(19,...values.map((v,i)=>Math.min(140,Math.ceil(String(v??'').length/Math.max(10,s.getColumn(i+1).width??20))*15)));
 return r;
}
function title(s:Sheet,text:string){s.addRow([]);const r=row(s,[text]);r.font={name:'Arial',size:15,bold:true,color:{argb:navy}};r.height=26;s.mergeCells(r.number,1,r.number,Math.min(s.columns.length,4));}
function band(s:Sheet,values:string[]){const r=row(s,values);r.height=27;r.eachCell(c=>{c.fill={type:'pattern',pattern:'solid',fgColor:{argb:navy}};c.font={name:'Arial',size:10,bold:true,color:{argb:'FFFFFF'}};});return r;}
function note(s:Sheet,text:string){const r=row(s,[text]);s.mergeCells(r.number,1,r.number,s.columns.length);r.height=Math.max(30,Math.ceil(text.length/105)*15);r.font={name:'Arial',size:10,color:{argb:muted}};return r;}
function input(r:ExcelJS.Row,lastColumn=Infinity){r.eachCell((c,i)=>{if(i>1&&i<=lastColumn)c.font={name:'Arial',size:10,color:{argb:blue}};});}
function wideText(s:Sheet,label:string,text:string){
 const r=row(s,[label,text]);s.mergeCells(r.number,2,r.number,s.columns.length);
 const width=s.columns.slice(1).reduce((sum,c)=>sum+(c.width??15),0);
 r.height=Math.max(23,Math.min(400,Math.ceil(text.length/Math.max(30,width))*16));input(r,2);
}
function effectiveDraft(snapshot:ModelSnapshot,label:string):Draft{
 return label===snapshot.selected_scenario&&snapshot.pending_editor?.kind==='model'?snapshot.pending_editor.draft:snapshot.session.cases[label].draft;
}
function stateLabel(snapshot:ModelSnapshot,label:string,phase:string){return label===snapshot.selected_scenario&&snapshot.pending_editor?'Previous calculation — editor draft not applied':phase;}
function chunks(text:string){
 const result:string[]=[];let part='';
 for(const char of text){if(part.length+char.length>12000){result.push(part);part='';}part+=char;}
 if(part)result.push(part);return result;
}
export async function buildModelWorkbook(snapshot:ModelSnapshot){
 const w=new ExcelJS.Workbook();w.creator='K. Chaturvedi · Valuation Platform';w.created=new Date(snapshot.exported_at);
 w.title=`${snapshot.ticker} model assumptions`;w.subject='Value snapshot and exact model state; no Excel valuation formulas';
 const labels=[snapshot.selected_scenario,...Object.keys(snapshot.session.cases).filter(l=>l!==snapshot.selected_scenario)];
 const selected=snapshot.session.cases[snapshot.selected_scenario],draft=effectiveDraft(snapshot,snapshot.selected_scenario);
 const overview=sheet(w,'Overview',[36,53,28,28]);title(overview,`${snapshot.ticker} · Model snapshot`);
 for(const pair of [
  ['Company',`${snapshot.company_name} (${snapshot.ticker})`],['Selected scenario',snapshot.selected_scenario],['Exported at (UTC)',snapshot.exported_at],
  ['Financial anchor',draft.doc.anchor.annual_end],['Forecast years',draft.doc.forecast_years.length],['Terminal method',pretty(methodOf(draft))],
  ['Export scope','Selected company; all saved scenarios and the open editor draft, if any.'],
  ['Editor state',snapshot.pending_editor?`Open ${snapshot.pending_editor.kind} draft included; not yet applied`:'No open editor draft'],
  ['Last operating calculation',stateLabel(snapshot,snapshot.selected_scenario,selected.ev.phase)],
  ['Last equity calculation',stateLabel(snapshot,snapshot.selected_scenario,selected.equity.phase)],
 ] as [string,string|number][]){const r=row(overview,pair);if(typeof pair[1]==='number')r.getCell(2).numFmt='0';r.height=pair[0]==='Export scope'?34:23;}
 row(overview,['Reported anchor revenue',amount(snapshot.entry?.revenue),'USD']);
 overview.addRow([]);band(overview,['How to use this file']);
 note(overview,'This is a saved snapshot, not a recalculating Excel valuation model. Changing workbook cells does not recalculate results. Loading a workbook back into the website is not implemented yet.');
 note(overview,'Assumptions contains the current inputs, including incomplete or invalid draft entries. Blank cells mean not entered, never zero. Last Results contains previously calculated values and their status, not a new valuation.');
 note(overview,'Excel numeric cells have approximately 15 significant digits. Model State retains original decimal strings, notes, sources and complete saved state without rounding. It is the exact copy for a future loading feature.');
 note(overview,'Historical inputs, analyst estimates and fiscal-end valuation results are dated. These are not current stock prices. Company-specific qualifications remain in the saved sources and state.');

 const maxYears=Math.max(...labels.map(label=>effectiveDraft(snapshot,label).doc.forecast_years.length));
 const assumptions=sheet(w,'Assumptions',[43,...Array(maxYears).fill(17)]);title(assumptions,`${snapshot.ticker} · Forecast assumptions`);
 note(assumptions,'Blue values are saved inputs. Percentages display as percentages (10% is stored as 0.10). Missing years remain blank. Other-method inputs are retained and explicitly marked inactive.');
 assumptions.views=[{state:'frozen',xSplit:1,ySplit:4,showGridLines:false}];
 for(const label of labels){
  const d=effectiveDraft(snapshot,label),active=methodOf(d),pending=label===snapshot.selected_scenario&&snapshot.pending_editor?.kind==='model';
  const header=band(assumptions,[`${label}${pending?' · editor draft':''}`,...d.doc.forecast_years.map(y=>y.fiscal_year_label)]);
  if(label===labels[0])assumptions.views=[{state:'frozen',xSplit:1,ySplit:header.number,showGridLines:false}];
  for(const [key,name] of annual)input(row(assumptions,[name,...d.doc.forecast_years.map((_,i)=>rate(d.rates[`forecast_years[${i}].${key}`]))],'0.00%;[Red](0.00%);0.00%'));
  wideText(assumptions,'Case name',d.doc.case_name);wideText(assumptions,'Personal notes',d.doc.preparation.notes??'');
  band(assumptions,['Valuation & terminal inputs','Value','Use']);
  input(row(assumptions,['WACC',rate(d.rates.wacc),'Active'],'0.00%'),2);
  input(row(assumptions,['Terminal growth',rate(d.rates.terminal_growth),active==='perpetual_growth'?'Active':'Inactive comparison input'],'0.00%'),2);
  input(row(assumptions,['Exit EV / EBIT multiple',amount(d.rates.exit_ev_ebit_multiple),active==='exit_multiple'?'Active':'Inactive comparison input'],'0.00"×"'),2);
  for(const [key,name] of terminal)input(row(assumptions,[name,rate(d.rates['terminal.'+key]),active==='perpetual_growth'?'Active':'Inactive comparison input'],'0.00%'),2);
  if(Object.keys(d.replacements).length){band(assumptions,['Unapplied constant replacements','Value']);for(const [key,value] of Object.entries(d.replacements))input(row(assumptions,[pretty(key),rate(value)],'0.00%'));}
  if(pending&&snapshot.pending_editor?.kind==='model'&&Object.keys(snapshot.pending_editor.replacementInputs).length){band(assumptions,['Replacement form entries · not applied','Value']);for(const [key,value] of Object.entries(snapshot.pending_editor.replacementInputs))input(row(assumptions,[pretty(key),rate(value)],'0.00%'));}
  assumptions.addRow([]);
 }

 const bridge=sheet(w,'Bridge & Analyst',[45,31,31,55]);title(bridge,`${snapshot.ticker} · Equity and FCFE inputs`);
 note(bridge,'Manual bridge inputs are separate from the company analyst assumptions below. They are not automatically combined. Invalid/partial entries are preserved as text. Amount inputs use USD millions; share inputs use millions of shares.');
 const equity=snapshot.pending_editor?.kind==='bridge'?snapshot.pending_editor.draft:snapshot.session.bridge;
 band(bridge,[`Manual bridge${snapshot.pending_editor?.kind==='bridge'?' · editor draft':''}`,'Value','Unit']);
 const bridgeNames:Record<string,string>={assets:'Cash & investments',financing:'Debt & financing',claims:'Other claims',shares:'Valuation shares',date:'Share observation date',nonOverlap:'Date, eligibility & non-overlap declared'};
 for(const [key,value] of Object.entries(equity)){
  const unit=['assets','financing','claims'].includes(key)?'USD millions':key==='shares'?'Million shares':key.startsWith('overlap')||key.startsWith('alternative')?'Saved declaration':'';
  const r=row(bridge,[bridgeNames[key]??pretty(key),typeof value==='boolean'?(value?'Yes':'No'):unit&&unit!=='Saved declaration'?amount(value):value,unit]);input(r,2);
 }
 for(const [label,analyst] of Object.entries(snapshot.analyst)){
  bridge.addRow([]);band(bridge,[`${label} · analyst assumptions`,'Value','Unit']);row(bridge,['Calculation status',snapshot.pending_editor?'Previous calculation — editor draft not applied':analyst.status]);
  for(const [key,value] of Object.entries(analyst.form))input(row(bridge,[pretty(key.replace(/_usd$/,'')),key.endsWith('_usd')?amount(value):rate(value),key.endsWith('_usd')?'USD millions':'Percent'],key.endsWith('_usd')?money:'0.00%'),2);
  const last=analyst.result as {bridge?:Record<string,string>}|null;
  if(last?.bridge){band(bridge,[`${label} · last calculated analyst bridge`,'Value','Unit']);for(const [key,value] of Object.entries(last.bridge))row(bridge,[pretty(key.replace(/_usd$/,'')),amount(value),key==='valuation_shares'?'Shares':'USD']);}
 }

 const results=sheet(w,'Last Results',[37,24,24,24,24]);title(results,`${snapshot.ticker} · Last calculated values`);
 note(results,'Values only; no Excel formulas. Result status and original submitted inputs are preserved. A stale, pending or different draft must not be interpreted as the inputs that produced these values. Monetary values below use USD, not USD millions.');
 for(const label of labels){
  const c=snapshot.session.cases[label],r=c.ev.result,eq=c.equity.result;
  band(results,[label,'Value','Unit','Status']);
  for(const [name,value,phase,unit] of [
   ['Enterprise value',r?.stage_b.enterprise_value,c.ev.phase,'USD'],['Explicit FCFF present value',r?.stage_b.pv_explicit_fcff,c.ev.phase,'USD'],['Terminal present value',r?.stage_b.pv_terminal_value,c.ev.phase,'USD'],
   ['Manual equity value',eq?.stage_c?.equity_value,c.equity.phase,'USD'],['Manual value per share',eq?.stage_c?.value_per_share,c.equity.phase,'USD / share'],
  ])row(results,[String(name),amount(value),String(unit),stateLabel(snapshot,label,String(phase))]);
  const analyst=snapshot.analyst[label],data=analyst?.result as {fcff?:{value_per_share_usd?:string};fcfe?:{value_per_share_usd?:string}}|null;
  if(analyst)for(const [name,value] of [['Analyst FCFF value per share',data?.fcff?.value_per_share_usd],['Analyst FCFE value per share',data?.fcfe?.value_per_share_usd]])row(results,[name??'',amount(value),'USD / share',snapshot.pending_editor?'Previous calculation — editor draft not applied':analyst.status]);
  if(r){band(results,['Last calculated forecast','Revenue (USD)','EBIT (USD)','NOPAT (USD)','FCFF (USD)']);for(const y of r.stage_b.stage_a.years)row(results,[String(y.fiscal_year_label),amount(y.revenue),amount(y.ebit),amount(y.nopat),amount(y.fcff)]);}
  results.addRow([]);
 }

 const sources=sheet(w,'Sources',[37,60,60]);title(sources,`${snapshot.ticker} · Sources & qualifications`);
 row(sources,['Anchor filing',snapshot.entry?.identity.accession??draft.doc.anchor.accession]);
 row(sources,['Information review date',snapshot.session.preload?.profile?.economic.dates.information_review??'Not established']);
 const urls=new Set(snapshot.entry?.source_links??[]);
 for(const analyst of Object.values(snapshot.analyst)){const data=analyst.result as {source_urls?:string[]}|null;data?.source_urls?.forEach(url=>urls.add(url));}
 for(const url of urls)row(sources,['Source URL',url]).height=34;
 const limitations=new Set([...(snapshot.entry?.limitations??[]),...draft.doc.limitations,...Object.values(draft.doc.conventions)]);
 for(const analyst of Object.values(snapshot.analyst)){const data=analyst.result as {qualifications?:string[]}|null;data?.qualifications?.forEach(q=>limitations.add(q));}
 for(const text of limitations)note(sources,text);

 const state=sheet(w,'Model State',[16,120]);title(state,'Exact saved model state');
 note(state,'Machine-readable snapshot for a future loading feature. Keep this sheet unchanged. Website import is not available yet. Visible sheet edits do not update this exact copy.');
 const json=JSON.stringify(snapshot),parts=chunks(json),hash=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(json));
 const sha256=Array.from(new Uint8Array(hash),n=>n.toString(16).padStart(2,'0')).join('');
 row(state,['Schema',snapshot.schema_version]);row(state,['SHA-256',sha256]);row(state,['Chunk count',parts.length],'0');band(state,['Order','JSON text']);
 for(const [i,part] of parts.entries()){const r=row(state,[i+1,part]);r.getCell(2).numFmt='@';r.getCell(2).alignment={wrapText:false};r.height=19;}
 state.views=[{state:'frozen',ySplit:7,showGridLines:false}];
 for(const s of w.worksheets){s.eachRow(r=>r.eachCell(c=>{c.border={bottom:{style:'hair',color:{argb:line}}};}));}
 return w;
}
export async function writeModelWorkbook(snapshot:ModelSnapshot):Promise<ArrayBuffer>{
 const w=await buildModelWorkbook(snapshot),bytes=await w.xlsx.writeBuffer();
 // Copy to an ordinary ArrayBuffer for browsers' Blob typing and Safari downloads.
 return new Uint8Array(bytes).slice().buffer;
}
