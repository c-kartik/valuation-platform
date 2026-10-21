import {it,expect} from 'vitest';
import fixture from '../../examples/valuation/synthetic-base.json';
import {makeDraft,applyQuick,copyYearFive,quickValues,annualState,buildRequest} from './model';
import type {CaseDoc} from './model';
it('applies exact strings immutably and never changes terminal assumptions',()=>{
 const d=makeDraft(fixture as CaseDoc), before=structuredClone(d);
 const next=applyQuick(d,{revenue_growth:'-2.125'});expect(d).toEqual(before);expect(buildRequest(next).forecast_years[4].revenue_growth).toBe('-0.02125');expect(next.doc.terminal).toEqual(d.doc.terminal);expect(quickValues(next).revenue_growth).toBe('-2.125');
});
it('accepts equivalent decimal formatting without a false varying-year warning',()=>{
 const d=makeDraft(fixture as CaseDoc);d.rates['forecast_years[2].revenue_growth']='10.00';expect(annualState(d,'revenue_growth').varies).toBe(false);
});
it('rejects partial missing or invalid bulk values atomically',()=>{
 const d=makeDraft(fixture as CaseDoc),before=structuredClone(d);
 expect(()=>applyQuick(d,{revenue_growth:'12',operating_margin:''})).toThrow();expect(()=>applyQuick(d,{revenue_growth:'12',forecast_tax_rate:'25%'})).toThrow();expect(d).toEqual(before);
});
it('copies all five terminal ratios atomically and independently from WACC/g',()=>{
 const d=makeDraft(fixture as CaseDoc);const next=copyYearFive(d);expect(next.rates['terminal.operating_margin']).toBe('20');expect(d.rates['terminal.operating_margin']).toBe('30');expect(next.rates.wacc).toBe('25');expect(next.rates.terminal_growth).toBe('5');
 next.rates['forecast_years[4].operating_margin']='55';expect(next.rates['terminal.operating_margin']).toBe('20');
 d.rates['forecast_years[4].capex_percent_revenue']='';expect(()=>copyYearFive(d)).toThrow();expect(d.rates['terminal.operating_margin']).toBe('30');
});
