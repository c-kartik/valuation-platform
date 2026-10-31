import {it,expect} from 'vitest';
import {makeDraft,resizeHorizon,annual,annualPath,buildRequest,entryErrors} from '../model';
import fixture from '../../../examples/valuation/synthetic-base.json';
import type {CaseDoc} from '../model';
it('extends without generating financial assumptions and parks extra-year entries when shortened',()=>{
 const five=makeDraft(fixture as CaseDoc),ten=resizeHorizon(five,10);
 expect(ten.doc.forecast_years).toHaveLength(10);expect(ten.doc.forecast_years.slice(0,5)).toEqual(five.doc.forecast_years);
 expect(ten.rates['forecast_years[5].revenue_growth']).toBe('');expect(entryErrors(ten)).toHaveProperty('forecast_years[9].operating_margin');
 ten.rates['forecast_years[8].revenue_growth']='6.12345678';const shortened=resizeHorizon(ten,5);
 expect(shortened.rates).not.toHaveProperty('forecast_years[8].revenue_growth');expect(resizeHorizon(shortened,10).rates['forecast_years[8].revenue_growth']).toBe('6.12345678');
 expect(five.doc.forecast_years).toHaveLength(5);
});
it('builds explicit v4 ten-year requests and leaves five-year request versions unchanged',()=>{
 const five=makeDraft(fixture as CaseDoc);five.terminalMethod='perpetual_growth';const ten=resizeHorizon(five,10);
 for(let i=5;i<10;i++)for(const [key]of annual)ten.rates[annualPath(key,i)]=five.rates[annualPath(key,4)];
 const doc=buildRequest(ten);expect(doc.schema_version).toBe('investor-case-v4');expect('forecast_horizon' in doc&&doc.forecast_horizon).toBe(10);expect(doc.forecast_years).toHaveLength(10);
 expect(buildRequest(five).schema_version).toBe('investor-case-v3');
 ten.terminalMethod='exit_multiple';ten.rates.exit_ev_ebit_multiple='12';expect(buildRequest(ten).conventions.discounting).toBe('fiscal-end-terminal-ev-ebit-v2');
});
it('refreshes only supported preload fields and leaves manual extra-year inputs intact',async()=>{
 const {applyEstimates}=await import('./preload');
 const five=makeDraft(fixture as CaseDoc),ten=resizeHorizon(five,10);ten.rates['forecast_years[9].revenue_growth']='4.123456789';
 const profile={economic_hash:'a'.repeat(64),economic:{issuer:{ticker:'TEST'},policy:{version:'test'},dates:{information_review:'2026-10-31',model_origin:'2025-12-31',timing:'test'},fields:{},scenarios:{Base:{'forecast_years[0].revenue_growth':'0.15'}},diagnostics:[]}}as unknown as import('./preload').PreloadProfile;
 const refreshed=applyEstimates(ten,profile,'Base',[]);
 expect(refreshed.doc.forecast_years).toHaveLength(10);expect(refreshed.rates['forecast_years[0].revenue_growth']).toBe('15');expect(refreshed.rates['forecast_years[9].revenue_growth']).toBe('4.123456789');
});
