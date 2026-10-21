import {describe,it,expect} from 'vitest';
import Decimal from 'decimal.js';
import fixture from '../../examples/valuation/synthetic-base.json';
import {percentageToFraction, fractionToPercentage, makeDraft, buildRequest, money, display, fieldErrors, InputErrors, entryErrors} from './model';
import type {CaseDoc} from './model';
import {Revisions, request, ApiError} from './api';

describe('exact input and presentation boundary', () => {
  it.each([['10','0.10'],['-2.5','-0.025'],['0','0.00'],['.125','0.00125'],['00010.000','0.10000'],['99.999999999999999999','0.99999999999999999999'],['','UNSET']])('converts %s without binary arithmetic', (value, expected) => {
    expect(percentageToFraction(value) ?? 'UNSET').toBe(expected);
  });
  it.each(['10%','NaN','Infinity','1e2','1,000','0x10','--2','.'])('rejects %s', value => expect(() => percentageToFraction(value)).toThrow());
  it('preserves fixture financial inputs and originals during metadata conversion without terminal copying', () => {
    const before = JSON.stringify(fixture); const draft = makeDraft(fixture as CaseDoc);
    expect(buildRequest(draft).forecast_years).toEqual(fixture.forecast_years);
    expect(buildRequest(draft)).not.toHaveProperty('analyst');
    expect(buildRequest(draft)).not.toHaveProperty('scope');
    draft.rates['forecast_years[4].operating_margin']='99';
    expect(buildRequest(draft).terminal.operating_margin).toBe('0.30');
    expect(JSON.stringify(fixture)).toBe(before);
    expect(buildRequest(draft)).not.toHaveProperty('bridge');
    expect(buildRequest(draft)).not.toHaveProperty('calculation_scope');
    expect(buildRequest(draft)).not.toHaveProperty('information_cutoff');
  });
  it('keeps 37 unset fields without analyst declarations for an unset template', () => {
    const empty = structuredClone(fixture) as CaseDoc;
    empty.forecast_years.forEach(y => Object.keys(y).filter(k => !['period_index','fiscal_year_label'].includes(k)).forEach(k => {(y as unknown as Record<string,unknown>)[k]=null;}));
    empty.wacc=null;empty.terminal_growth=null;
    Object.keys(empty.terminal).forEach(k => {(empty.terminal as Record<string,unknown>)[k]=null;});
    const draft = makeDraft(empty);
    expect(Object.values(draft.rates)).toHaveLength(37);
    expect(Object.values(draft.rates).every(v=>v==='')).toBe(true);
    expect(draft.doc.preparation.notes).toBeNull();expect(draft.doc.preparation.provenance).toBe('ANONYMOUS_INVESTOR');
    expect(buildRequest(draft).terminal.operating_margin).toBeNull();
  });
  it('retains field paths on conversion errors and maps API paths', () => {
    const draft=makeDraft(fixture as CaseDoc);draft.rates.wacc='10%';
    try {buildRequest(draft); throw Error('expected error');} catch(e) {expect(e).toBeInstanceOf(InputErrors);expect((e as InputErrors).fields.wacc).toMatch(/decimal percentage/);}
    expect(fieldErrors(['forecast_years[2].forecast_tax_rate: bad tax','case.scope: required'])).toEqual({'forecast_years[2].forecast_tax_rate':'bad tax',scope:'required'});
  });
  it('uses isolated display rounding with zero, negatives and undefined values', () => {
    Decimal.set({precision:2,rounding:Decimal.ROUND_DOWN});
    expect(money('1234567890.123456789')).toBe('1,234.57');
    expect(money('0')).toBe('0.00');expect(money('-1000000')).toBe('-1.00');
    expect(display(null)).toBe('Undefined');expect(display('-1.23455','1',4)).toBe('-1.2346');
    expect(Decimal.precision).toBe(2); expect(fractionToPercentage('-0.025')).toBe('-2.5');
  });
});

describe('HTTP and revision behavior', () => {
  it('rejects late replies after edits, company switches and newer requests', () => {
    const r=new Revisions();const first=r.begin();r.edit();expect(r.current(first)).toBe(false);
    const second=r.begin();const third=r.begin();expect(r.current(second)).toBe(false);expect(r.current(third)).toBe(true);
    r.edit();expect(r.current(third)).toBe(false);
  });
  it.each([[413,'request_too_large'],[503,'busy'],[504,'deadline_exceeded'],[500,'internal_error']])('preserves API error %s', async(status,code)=> {
    const original=globalThis.fetch;
    globalThis.fetch=async()=>new Response(JSON.stringify({error:{code,message:'Correct or retry',details:['wacc: fix']}}),{status});
    try {await expect(request('/api/v1/cases/run',fixture)).rejects.toMatchObject({code,details:['wacc: fix']});}finally{globalThis.fetch=original;}
  });
  it('reports network errors without losing input and uses no browser credentials', async()=> {
    const original=globalThis.fetch;let sent:RequestInit|undefined;
    globalThis.fetch=async(_,init)=>{sent=init;throw Error('offline');};
    try {await expect(request('/api/v1/cases/run',fixture)).rejects.toBeInstanceOf(ApiError);expect(sent?.credentials).toBe('omit');expect(JSON.parse(sent?.body as string)).toEqual(fixture);}finally{globalThis.fetch=original;}
  });
});

it('bounds a stalled local request with a client deadline',async()=>{
  const original=globalThis.fetch;
  const {vi}=await import('vitest');vi.useFakeTimers();
  globalThis.fetch=async(_,init)=>new Promise((_,reject)=>init?.signal?.addEventListener('abort',()=>reject(new Error('aborted'))));
  try {
    const pending=request('/api/v1/cases/run',fixture);
    const check=expect(pending).rejects.toMatchObject({code:'request_cancelled'});
    await vi.advanceTimersByTimeAsync(50001);await check;
  }finally{vi.useRealTimers();globalThis.fetch=original;}
});

it('generates stable anonymous details, filters only template instructions and preserves notes verbatim',()=>{
 const template=structuredClone(fixture) as CaseDoc;
 template.limitations=['All 37 numerical assumptions and analyst identity/date/rationale are unset; no defaults or historical calibration.','Enduring historical unknown'];
 const d=makeDraft(template,'2026-10-21T10:00:00.000Z');
 expect(d.doc.case_name).toBe('Synthetic demonstration · Investor calculation');
 expect(buildRequest(d).preparation).toEqual({provenance:'ANONYMOUS_INVESTOR',timestamp_utc:'2026-10-21T10:00:00.000Z',notes:null});
 expect(buildRequest(d).limitations).toEqual(['Enduring historical unknown']);
 d.doc.preparation.notes='  ';expect(buildRequest(d).preparation.notes).toBeNull();expect(d.doc.preparation.notes).toBe('  ');
 d.doc.preparation.notes='  My words.\nNot source evidence.  ';
 expect(buildRequest(d).preparation.notes).toBe('  My words.\nNot source evidence.  ');
 expect(buildRequest(d)).toEqual(buildRequest(d));
 expect(template.limitations).toHaveLength(2);
 d.doc.preparation.notes=' '.repeat(2049);expect(entryErrors(d)).not.toHaveProperty('preparation.notes');expect(buildRequest(d).preparation.notes).toBeNull();
 d.doc.preparation.notes='😀'.repeat(2048);expect(entryErrors(d)).not.toHaveProperty('preparation.notes');
 d.doc.preparation.notes+='x';expect(entryErrors(d)).toHaveProperty('preparation.notes');
});
