// @vitest-environment node
import {it,expect} from 'vitest';
import ExcelJS from 'exceljs';
import {createHash} from 'node:crypto';
import {captureModelSnapshot,modelFilename} from './modelSnapshot';
import {writeModelWorkbook,buildModelWorkbook} from './modelWorkbook';
import {createSession} from './useWorkspace';
import {resizeHorizon} from '../model';
import type {CaseDoc,Result} from '../model';
import fixture from '../../../examples/valuation/synthetic-base.json';

function setup(){
 const session=createSession(structuredClone(fixture) as CaseDoc);
 session.cases.Base.draft.rates['forecast_years[0].revenue_growth']='12.12345678901234567890123456789';
 session.cases.Base.draft.rates['forecast_years[1].operating_margin']='-3.5';
 session.cases.Base.draft.rates.wacc='0';session.bridge.assets='';session.bridge.financing='0';
 return captureModelSnapshot({ticker:'AAPL',company_name:'Apple',selected_company:'aapl-fy2025',selected_scenario:'Base',session,entry:null,analyst:{}},new Date('2026-11-07T16:00:00Z'));
}
function find(sheet:ExcelJS.Worksheet,label:string,column=1){let found:ExcelJS.Row|undefined;sheet.eachRow(r=>{if(!found&&r.getCell(column).value===label)found=r;});if(!found)throw Error('Missing row '+label);return found;}
function savedState(book:ExcelJS.Workbook){const s=book.getWorksheet('Model State')!;let json='';s.eachRow((r,n)=>{if(n>=8)json+=String(r.getCell(2).value??'');});return {json,state:JSON.parse(json),sha:find(s,'SHA-256').getCell(2).value};}
async function reopen(snapshot=setup()){
 const bytes=await writeModelWorkbook(snapshot),book=new ExcelJS.Workbook();expect([...new Uint8Array(bytes).slice(0,2)]).toEqual([80,75]);await book.xlsx.load(bytes as never);return book;
}
it('creates a genuine XLSX with readable assumptions, units and all saved scenarios',async()=>{
 const book=await reopen();expect(book.worksheets.map(s=>s.name)).toEqual(['Overview','Assumptions','Bridge & Analyst','Last Results','Sources','Model State']);
 const assumptions=book.getWorksheet('Assumptions')!;
 expect(find(assumptions,'Annual revenue growth').getCell(2).value).toBeCloseTo(.12123456789,10);
 expect(find(assumptions,'Operating profit margin').getCell(3).value).toBe(-.035);
 expect(find(assumptions,'WACC').getCell(2).value).toBe(0);expect(find(assumptions,'WACC').getCell(2).numFmt).toBe('0.00%');
 for(const label of ['Base','Bear','Bull'])expect(find(assumptions,label)).toBeTruthy();
 expect(find(book.getWorksheet('Bridge & Analyst')!,'Cash & investments').getCell(2).value).toBeNull();
 expect(find(book.getWorksheet('Bridge & Analyst')!,'Debt & financing').getCell(2).value).toBe(0);
});
it('round-trips the exact state and checksum without decimal or unicode loss',async()=>{
 const snapshot=setup();snapshot.session.cases.Base.draft.doc.preparation.notes='Saved notes 🙂 & < >\n'+ 'Long note 🧮 '.repeat(3500);
 const book=await reopen(snapshot),saved=savedState(book);
 expect(saved.state).toEqual(JSON.parse(JSON.stringify(snapshot)));expect(saved.sha).toBe(createHash('sha256').update(saved.json).digest('hex'));
 book.eachSheet(s=>s.eachRow(r=>r.eachCell(c=>{if(typeof c.value==='string')expect(c.value.length).toBeLessThanOrEqual(32767);}))); 
});
it('exports an incomplete ten-year open editor without modifying the saved five-year case',async()=>{
 const snapshot=setup(),draft=resizeHorizon(snapshot.session.cases.Base.draft,10);
 draft.rates['forecast_years[5].revenue_growth']='';draft.rates['forecast_years[6].operating_margin']='-';
 snapshot.pending_editor={kind:'model',draft,touched:['forecast_years[6].operating_margin'],resets:[],replacementInputs:{revenue_growth:'7.125'}};
 const before=JSON.stringify(snapshot),book=await reopen(snapshot),s=book.getWorksheet('Assumptions')!;
 expect(find(s,'Base · editor draft').getCell(11).value).toBe(draft.doc.forecast_years[9].fiscal_year_label);
 expect(find(s,'Annual revenue growth').getCell(7).value).toBeNull();expect(find(s,'Operating profit margin').getCell(8).value).toBe('-');
 expect(savedState(book).state.session.cases.Base.draft.doc.forecast_years).toHaveLength(5);expect(savedState(book).state.pending_editor.draft.doc.forecast_years).toHaveLength(10);
 expect(JSON.stringify(snapshot)).toBe(before);
});
it('preserves pending bridge declarations separately and never labels old results current',async()=>{
 const snapshot=setup();snapshot.pending_editor={kind:'bridge',draft:{...snapshot.session.bridge,assets:'123.456789',shares:'15',nonOverlap:false}};
 const book=await reopen(snapshot);expect(find(book.getWorksheet('Bridge & Analyst')!,'Cash & investments').getCell(2).value).toBe(123.456789);
 expect(find(book.getWorksheet('Last Results')!,'Enterprise value').getCell(4).value).toContain('editor draft not applied');
 expect(savedState(book).state.session.bridge.assets).toBe('');expect(savedState(book).state.pending_editor.draft.nonOverlap).toBe(false);
});
it('retains inactive terminal inputs, parked years, analyst drafts and previous calculation statuses',async()=>{
 const snapshot=setup();snapshot.session.cases.Base.draft.terminalMethod='exit_multiple';snapshot.session.cases.Base.draft.rates.exit_ev_ebit_multiple='15.5';snapshot.session.cases.Base.draft.rates.terminal_growth='2';
 snapshot.session.cases.Base.draft.parkedRates={'forecast_years[9].revenue_growth':'3.1234567890123456789'};
 snapshot.analyst.Base={form:{cost_of_equity:'9.875',additional_claims_usd:''},status:'stale',resultForm:{cost_of_equity:'8'},result:{fcff:{value_per_share_usd:'175.46'},fcfe:{value_per_share_usd:'161.00'}}};
 const book=await reopen(snapshot),s=book.getWorksheet('Assumptions')!;
 expect(find(s,'Exit EV / EBIT multiple').getCell(2).value).toBe(15.5);expect(find(s,'Terminal growth').getCell(3).value).toContain('Inactive');
 expect(find(book.getWorksheet('Last Results')!,'Analyst FCFE value per share').getCell(4).value).toBe('stale');
 expect(savedState(book).state.analyst.Base).toEqual(snapshot.analyst.Base);expect(savedState(book).state.session.cases.Base.draft.parkedRates).toEqual(snapshot.session.cases.Base.draft.parkedRates);
});
it('keeps formula-like text literal and never adds spreadsheet calculations or external links',async()=>{
 const snapshot=setup();snapshot.session.cases.Base.draft.doc.case_name='=HYPERLINK("https://invalid.example","click")';snapshot.session.bridge.classes='+SUM(1,2)';snapshot.session.cases.Base.draft.rates.wacc='=1+1';
 const book=await reopen(snapshot);expect(find(book.getWorksheet('Assumptions')!,'Case name').getCell(2).type).toBe(ExcelJS.ValueType.String);
 expect(find(book.getWorksheet('Assumptions')!,'WACC').getCell(2).value).toBe('=1+1');
 book.eachSheet(s=>s.eachRow(r=>r.eachCell(c=>{expect(c.type).not.toBe(ExcelJS.ValueType.Formula);expect(c.type).not.toBe(ExcelJS.ValueType.Hyperlink);}))); 
});
it('captures independently at click time and creates a safe filename',()=>{
 const source=setup(),captured=captureModelSnapshot({...source,ticker:'../AAPL',selected_scenario:'Base / custom'});
 source.session.cases.Base.draft.rates.wacc='25';expect(captured.session.cases.Base.draft.rates.wacc).toBe('0');expect(modelFilename(captured)).not.toContain('/');expect(modelFilename(captured)).toMatch(/\.xlsx$/);
});
