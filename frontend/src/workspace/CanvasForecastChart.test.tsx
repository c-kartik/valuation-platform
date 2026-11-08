import {it,expect} from 'vitest';
import {render,screen,fireEvent} from '@testing-library/react';
import {CanvasForecastChart} from './CanvasForecastChart';
import {makeDraft} from '../model';
import type {CaseDoc,Entry,Result} from '../model';
import fixture from '../../../examples/valuation/synthetic-base.json';
function data(n=5){const doc=makeDraft(fixture as CaseDoc).doc;doc.forecast_years=Array.from({length:n},(_,i)=>({...doc.forecast_years[0],period_index:i+1,fiscal_year_label:'FY'+(2026+i)}));const result:Result={case_name:'Software fixture',input_basis:'SYNTHETIC_FIXTURE',submitted_inputs:doc,limitations:[],stage_b:{stage_a:{anchor:{revenue:'1000000000'},years:doc.forecast_years.map((y,i)=>({fiscal_year_label:y.fiscal_year_label,revenue:String((i+2)*1e9),fcff:String((i-2)*1e9)}))},years:[],terminal:{},timing:{analytical_t0:doc.anchor.annual_end,notice:'Fixture',information_cutoff:'UNKNOWN'},terminal_value:'0',pv_terminal_value:'0',pv_explicit_fcff:'0',enterprise_value:'0'}};const entry={identity:doc.anchor,historical_window:Array.from({length:5},(_,i)=>({fiscal_year_label:'FY'+(2021+i),revenue:{amount:String((i+6)*1e8),unit:'USD',precision:'-6',period_start:(2021+i)+'-01-01',period_end:(2021+i)+'-12-31',accession:'synthetic',concept:'synthetic',sources:[]},fcff:i===2?null:'100000000',fcff_basis:'REPORTED_CFO_CASH_PPE'}))} as unknown as Entry;return {result,entry};}
it('uses the retained history and returned forecast, keeps missing FCFF as a gap and never mutates either source',()=>{
 const {result,entry}=data(),copy=structuredClone({result,entry});render(<CanvasForecastChart result={result} entry={entry} label="Base"/>);
 expect(screen.getAllByRole('button',{name:/Select FY/})).toHaveLength(10);
 fireEvent.click(screen.getByRole('button',{name:'Select FY2023 history'}));expect(screen.getByLabelText('Selected year values').textContent).toContain('Unavailable');
 fireEvent.click(screen.getByRole('button',{name:'Select FY2026 forecast'}));expect(screen.getByLabelText('Selected year values').textContent).toContain('−$2.00B');
 expect(document.querySelector('[data-history-series=fcff]')!.getAttribute('d')!.match(/M/g)).toHaveLength(2);
 expect(document.querySelector('[data-forecast-series=fcff]')!.getAttribute('stroke-dasharray')).toBe('5 5');
 expect({result,entry}).toEqual(copy);
});
it('retains all fifteen years, keyboard selection and a five-year boundary while rendering only submitted margin data',()=>{
 const {result,entry}=data(10);result.submitted_inputs.forecast_years[0].operating_margin='0.321234';const {rerender}=render(<CanvasForecastChart result={result} entry={entry} label="Bull"/>);
 expect(screen.getAllByRole('button',{name:/Select FY/})).toHaveLength(15);expect(document.querySelector('[data-five-year-boundary]')).toBeTruthy();
 const paths=()=>[...document.querySelectorAll('[data-history-series],[data-forecast-series]')].map(p=>p.getAttribute('d'));
 const before=paths();rerender(<CanvasForecastChart result={result} entry={entry} inspection="margin" label="Bull"/>);expect(paths()).toEqual(before);expect(document.querySelector('[data-margin-value="0.321234"]')).toBeTruthy();
 const last=screen.getByRole('button',{name:'Select FY2035 forecast'});fireEvent.keyDown(last,{key:'Home'});expect(screen.getByLabelText('Selected year values').textContent).toContain('FY2021');
 fireEvent.change(screen.getByRole('combobox',{name:'Selected chart fiscal year'}),{target:{value:'FY2035'}});expect(screen.getByLabelText('Selected year values').textContent).toContain('FY2035');
});
it('fails back to the matching annual anchor rather than binding another company’s history',()=>{
 const {result,entry}=data();entry.identity={...entry.identity,cik:999};render(<CanvasForecastChart result={result} entry={entry} label="Base" stale/>);
 expect(screen.getAllByRole('button',{name:/Select FY/})).toHaveLength(6);fireEvent.click(screen.getByRole('button',{name:'Select FY2025 history'}));expect(screen.getByLabelText('Selected year values').textContent).toContain('Unavailable');expect(screen.getByLabelText('Selected year values').textContent).toContain('Previous result');
});
