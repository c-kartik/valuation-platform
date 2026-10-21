import {it,expect} from 'vitest';
import {execFileSync} from 'node:child_process';
import {resolve} from 'node:path';
import fixture from '../../examples/valuation/synthetic-base.json';
import {makeDraft,editQuick,replaceAnnual,copyYearFive,annualState,buildRequest,entryErrors,terminalDifferences,annual} from './model';
import type {CaseDoc} from './model';
it('updates exact uniform raw strings immutably, including partial edits, without changing terminal inputs',()=>{
 const d=makeDraft(fixture as CaseDoc),before=structuredClone(d);const next=editQuick(d,'revenue_growth','-2.125');
 expect(d).toEqual(before);expect(buildRequest(next).forecast_years[4].revenue_growth).toBe('-0.02125');expect(next.doc.terminal).toEqual(d.doc.terminal);
 const partial=editQuick(next,'revenue_growth','-');expect(partial.rates['forecast_years[4].revenue_growth']).toBe('-');expect(()=>buildRequest(partial)).toThrow();
 const empty=editQuick(next,'revenue_growth','');expect(entryErrors(empty)).toHaveProperty('forecast_years[0].revenue_growth');expect(buildRequest(empty).forecast_years[0].revenue_growth).toBeNull();
});
it('recognizes equivalent decimals and keeps a varying-row replacement explicit and blocking',()=>{
 const d=makeDraft(fixture as CaseDoc);d.rates['forecast_years[2].revenue_growth']='10.00';expect(annualState(d,'revenue_growth').varies).toBe(false);
 d.rates['forecast_years[2].revenue_growth']='18';const next=editQuick(d,'revenue_growth','11.125');expect(()=>buildRequest(next)).toThrow();expect(next.rates['forecast_years[2].revenue_growth']).toBe('18');
 const confirmed=replaceAnnual(next,'revenue_growth');expect(buildRequest(confirmed).forecast_years.every(y=>y.revenue_growth==='0.11125')).toBe(true);expect(confirmed.rates['forecast_years[2].operating_margin']).toBe('20');
});
it('copies final-year operating ratios once, atomically and independently of discount/growth',()=>{
 const d=makeDraft(fixture as CaseDoc),next=copyYearFive(d);expect(next.rates['terminal.operating_margin']).toBe('20');expect(d.rates['terminal.operating_margin']).toBe('30');expect(next.rates.wacc).toBe('25');expect(next.rates.terminal_growth).toBe('5');expect(terminalDifferences(next)).toEqual([]);
 next.rates['forecast_years[4].operating_margin']='55';expect(next.rates['terminal.operating_margin']).toBe('20');expect(terminalDifferences(next)).toContain('Long-term operating profit margin');
 d.rates['forecast_years[4].capex_percent_revenue']='';expect(()=>copyYearFive(d)).toThrow();expect(d.rates['terminal.operating_margin']).toBe('30');
});
it('matches complete Python financial result components for equivalent old and direct-entry requests',()=>{
 let draft=makeDraft(fixture as CaseDoc);
 for(const [key] of annual)draft=editQuick(draft,key,draft.rates[`forecast_years[0].${key}`]);
 const direct=buildRequest(draft);expect(direct.forecast_years).toEqual(fixture.forecast_years);
 const program=`import json,sys\nfrom pathlib import Path\nfrom valuation_platform.valuation.case_inputs import read_case,run_case\nold,new=json.load(sys.stdin)\na=run_case(read_case(json.dumps(old)),Path('.'))\nb=run_case(read_case(json.dumps(new)),Path('.'))\nassert a['stage_b']==b['stage_b']\nassert a['submitted_inputs']!=b['submitted_inputs']\nfrom decimal import Decimal\nassert Decimal(b['stage_b']['enterprise_value'])==Decimal('77.5770603520')\nprint('Financial components match')`;
 const root=resolve('..');const out=execFileSync(resolve(root,'.venv/bin/python'),['-c',program],{cwd:root,input:JSON.stringify([fixture,direct]),encoding:'utf8',env:{...process.env,PYTHONPATH:'src',PYTHONDONTWRITEBYTECODE:'1'}});
 expect(out.trim()).toBe('Financial components match');
});
