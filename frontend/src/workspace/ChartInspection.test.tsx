import {it,expect,vi} from 'vitest';
import {render,screen,fireEvent,act} from '@testing-library/react';
import Decimal from 'decimal.js';
import {ForecastChart} from './ForecastChart';
import {ScenarioCharts} from './ScenarioCharts';
import {submittedMargins,marginCaption} from './chartInspection';
import type {ChartInspection} from './chartInspection';
import type {CaseDoc,Result} from '../model';
import fixture from '../../../examples/valuation/synthetic-base.json';
function result(count=5):Result{
 const doc=structuredClone(fixture) as CaseDoc;
 doc.forecast_years=Array.from({length:count},(_,i)=>({...doc.forecast_years[i%5],period_index:i+1,fiscal_year_label:`FY${2026+i}`,operating_margin:(.32-i*.01).toFixed(2)}));
 return {case_name:'Software test',submitted_inputs:doc,input_basis:'SYNTHETIC_FIXTURE',limitations:[],stage_b:{stage_a:{anchor:{revenue:'1000000000'},years:doc.forecast_years.map((y,i)=>({fiscal_year_label:y.fiscal_year_label,revenue:String(2000000000+i*100000000),ebit:'400000000',fcff:String((i-2)*100000000)}))},years:[],terminal:{},timing:{analytical_t0:doc.anchor.annual_end,notice:'Test',information_cutoff:'UNKNOWN'},enterprise_value:'1',terminal_value:'1',pv_terminal_value:'1',pv_explicit_fcff:'0'}};
}
function geometry(){return JSON.stringify({box:document.querySelector('svg')!.getAttribute('viewBox'),right:document.querySelector('svg')!.getAttribute('data-plot-right'),bars:[...document.querySelectorAll('[data-bar-year]')].map(n=>['x','y','width','height'].map(a=>n.getAttribute(a))),years:[...document.querySelectorAll('.cv-year-highlight')].map(n=>['x','y','width','height'].map(a=>n.getAttribute(a)))});}
it('keeps every bar, year target and plot boundary fixed across all six inspection states and reset at narrow and wide widths',()=>{
 let resize!:(entries:{contentRect:{width:number}}[])=>void;
 vi.stubGlobal('ResizeObserver',class{constructor(callback:typeof resize){resize=callback;}observe(){}disconnect(){}});
 try{for(const width of [328,960]){
  const r=result(10),copy=structuredClone(r),cases=[{label:'Base',result:r}],view=render(<ForecastChart cases={cases}/>);act(()=>resize([{contentRect:{width}}]));const original=geometry();
  expect(Number(document.querySelector('svg')!.getAttribute('data-plot-right'))).toBeLessThan(width-60);
  for(const inspection of ['revenue','margin','cash','period','discount','terminal',null] as (ChartInspection|null)[]){
   view.rerender(<ForecastChart cases={cases} inspection={inspection}/>);expect(geometry()).toBe(original);
   expect(Boolean(document.querySelector('[data-margin-axis]'))).toBe(inspection==='margin');
   expect(document.querySelectorAll('[data-margin-year]')).toHaveLength(inspection==='margin'?10:0);
   expect(document.querySelector('[data-five-year-boundary]')).toBeTruthy();
  }
  expect(r).toEqual(copy);view.unmount();
 }}finally{vi.unstubAllGlobals();}
});
it('shows exact submitted annual margin assumptions, keeps signed FCFF, and changes only display emphasis',()=>{
 const r=result(),cases=[{label:'Base',result:r}],view=render(<ForecastChart cases={cases} inspection="margin"/>);
 expect([...document.querySelectorAll('[data-margin-year]')].map(n=>n.getAttribute('data-margin-value'))).toEqual(['0.32','0.31','0.3','0.29','0.28']);
 expect(document.querySelectorAll('[data-margin-year]')).toHaveLength(5);expect(document.querySelectorAll('[data-scenario-bar="Reported"][data-metric="fcff"]')).toHaveLength(0);
 expect(document.querySelector('[data-metric="fcff"]')?.getAttribute('data-value')).toBe('-200000000');
 fireEvent.click(screen.getByRole('button',{name:'combined: select FY2026'}));expect(screen.getByText('FY2026 · 32.00%')).toBeTruthy();
 view.rerender(<ForecastChart cases={cases} inspection="revenue"/>);expect(document.querySelector('[data-bar-year="FY2026"][data-metric="revenue"]')?.getAttribute('opacity')).toBe('1');expect(document.querySelector('[data-bar-year="FY2026"][data-metric="fcff"]')?.getAttribute('opacity')).toBe('0.22');
 view.rerender(<ForecastChart cases={cases} inspection="cash"/>);expect(document.querySelector('[data-bar-year="FY2026"][data-metric="fcff"]')?.getAttribute('opacity')).toBe('1');
 view.rerender(<ForecastChart cases={cases} inspection="discount"/>);expect(screen.getByText('Discounts cash flows; operating paths unchanged')).toBeTruthy();
 view.rerender(<ForecastChart cases={cases} inspection="period"/>);expect(document.querySelector('[data-inspected-period]')).toBeTruthy();
 view.rerender(<ForecastChart cases={cases} inspection="terminal"/>);expect(document.querySelector('[data-terminal-inspection]')).toBeTruthy();expect(document.querySelector('[data-bar-year="FY2030"][data-metric="fcff"]')?.getAttribute('opacity')).toBe('1');
 r.stage_b.terminal_method='exit_multiple';view.rerender(<ForecastChart cases={cases} inspection="terminal"/>);expect(screen.getByText('Final-year operating profit sets the exit value')).toBeTruthy();
});
it('uses previous submitted margins while stale, separates missing values and retains signed/out-of-range percentage domains',()=>{
 const r=result();r.submitted_inputs.forecast_years[0].operating_margin='-0.1';r.submitted_inputs.forecast_years[1].operating_margin=null;r.submitted_inputs.forecast_years[2].operating_margin='1.2';
 const view=render(<ForecastChart cases={[{label:'Base',result:r}]} stale inspection="margin"/>);
 expect(screen.getByText(/Operating margin.*Previous result/)).toBeTruthy();expect(document.querySelectorAll('[data-margin-year]')).toHaveLength(4);
 expect(document.querySelector('[data-margin-line]')?.getAttribute('d')?.match(/M/g)).toHaveLength(2);
 const axis=[...document.querySelector('.cw-margin-overlay')!.querySelectorAll('text')].map(n=>n.textContent);expect(axis).toContain('-50%');expect(axis).toContain('150%');
 r.submitted_inputs.forecast_years.forEach(y=>y.operating_margin=null);view.rerender(<ForecastChart cases={[{label:'Base',result:r}]} inspection="margin"/>);expect(document.querySelector('[data-margin-axis]')).toBeNull();expect(screen.getByText('Operating margin unavailable in the submitted result')).toBeTruthy();
});
it('isolates Decimal context and rejects absent, non-finite or mismatched submitted margins without inventing values',()=>{
 const precision=Decimal.precision;try{Decimal.set({precision:2});const r=result();r.submitted_inputs.forecast_years[0].operating_margin='0.3180510993602295084';r.submitted_inputs.forecast_years[1].operating_margin='NaN';r.submitted_inputs.forecast_years[2].fiscal_year_label='mismatched';expect(submittedMargins(r).slice(0,3).map(p=>p.value)).toEqual(['0.3180510993602295084',null,null]);expect(Decimal.precision).toBe(2);}finally{Decimal.set({precision});}
});
it('retains the scenario layout without the DCF margin axis',()=>{render(<ScenarioCharts cases={[{label:'Base',result:result()}]}/>);expect(document.querySelector('[data-margin-axis]')).toBeNull();expect(document.querySelectorAll('svg')).toHaveLength(2);expect(document.querySelector('.cw-chart-inspection')).toBeNull();});

it('keeps tiny and extreme margin labels bounded without losing the exact stored assumption',()=>{
 expect(marginCaption('0.3180510993602295084')).toBe('31.81%');
 for(const value of ['1e100','-1e100','1e-100'])expect(marginCaption(value).length).toBeLessThan(18);
 const r=result();r.submitted_inputs.forecast_years[0].operating_margin='1e100';render(<ForecastChart cases={[{label:'Base',result:r}]} inspection="margin"/>);
 expect(document.querySelector('[data-margin-year="FY2026"]')?.getAttribute('data-margin-value')).toBe('1'+'0'.repeat(100));
 expect(document.querySelector('.cw-margin-overlay title')?.textContent).toContain('Axis tick labels');
});
