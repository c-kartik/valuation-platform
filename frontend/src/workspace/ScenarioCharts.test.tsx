import {it,expect,vi} from 'vitest';
import {render,screen,fireEvent,within,act} from '@testing-library/react';
import Decimal from 'decimal.js';
import {ScenarioCharts} from './ScenarioCharts';
import {ForecastChart} from './ForecastChart';
import {endpointCagr,endpointGuide} from './OperatingCharts';
import {makeDraft} from '../model';
import type {CaseDoc,Result,Entry} from '../model';
import fixture from '../../../examples/valuation/synthetic-base.json';
function result(offset=0):Result{const doc=makeDraft(fixture as CaseDoc).doc;doc.forecast_years.forEach((y,i)=>y.fiscal_year_label='FY'+(2026+i));return {case_name:'Software fixture',input_basis:'SYNTHETIC_FIXTURE',submitted_inputs:doc,limitations:[],stage_b:{stage_a:{anchor:{revenue:'1000000000'},years:doc.forecast_years.map((y,i)=>({fiscal_year_label:y.fiscal_year_label,revenue:String((i+2+offset)*1000000000),fcff:String((i-2+offset)*1000000000)}))},years:[],terminal:{},timing:{analytical_t0:doc.anchor.annual_end,notice:'Fixture',information_cutoff:'UNKNOWN'},terminal_value:'0',pv_terminal_value:'0',pv_explicit_fcff:'0',enterprise_value:'0'}};}
function history():Entry{return {identity:fixture.anchor,historical_window:[['2023','700000000'],['2024','800000000'],['2025','1000000000']].map(([y,amount])=>({fiscal_year_label:'FY'+y,revenue:{amount,unit:'USD',precision:'-6',period_start:y+'-01-01',period_end:y+'-12-31',accession:'synthetic',concept:'synthetic',sources:[]},fcff:null}))} as unknown as Entry;}
it('renders two grouped bar plots in stable Bear/Base/Bull order with common history and synchronized full-year selection',()=>{
 render(<ScenarioCharts entry={history()} cases={['Bull','Base','Bear'].map((label,i)=>({label,result:result(2-i)}))}/>);expect(document.querySelector('polyline')).toBeNull();const revenue=screen.getByRole('region',{name:'Revenue scenario grouped bar chart'}),fcff=screen.getByRole('region',{name:'FCFF scenario grouped bar chart'});
 expect([...revenue.querySelectorAll('[data-bar-year="FY2026"]')].map(n=>n.getAttribute('data-scenario-bar'))).toEqual(['Bear','Base','Bull']);expect(document.querySelectorAll('[data-scenario-bar="Reported"]')).toHaveLength(3);expect(fcff.querySelectorAll('[data-scenario-bar="Reported"]')).toHaveLength(0);
 const years=within(revenue).getAllByRole('button');fireEvent.focus(years[3]);fireEvent.keyDown(years[3],{key:'ArrowRight'});expect(within(fcff).getAllByRole('button')[4].getAttribute('aria-pressed')).toBe('true');expect(screen.getByText('FY2027 · Forecast')).toBeTruthy();expect(screen.getAllByText(/vs Base:/)).toHaveLength(4);fireEvent.click(within(fcff).getAllByRole('button')[0]);expect(years[0].getAttribute('aria-pressed')).toBe('true');expect(revenue.querySelector('[data-base-trend]')?.getAttribute('data-start-year')).toBe('FY2023');expect(revenue.querySelector('[data-base-trend]')?.getAttribute('data-end-year')).toBe('FY2025');expect(fcff.querySelector('[data-base-trend]')).toBeNull();
 fireEvent.mouseMove(years[1]);expect(revenue.querySelector('[data-base-trend]')?.getAttribute('data-start-year')).toBe('FY2024');fireEvent.click(years[2]);expect(revenue.querySelector('[data-base-trend]')).toBeNull();expect(screen.getAllByText(/FY2025 baseline/).length).toBe(1);expect(screen.getAllByText(/FY2025 FCFF unavailable · no guide/)).toHaveLength(1);
});
it('uses adjacent metric bars, one zero-based signed axis, three observed years and a distinct fixed anchor',()=>{
 const r=result(),copy=structuredClone(r);render(<ForecastChart cases={[{label:'Base',result:r}]} entry={history()}/>);expect(document.querySelectorAll('svg')).toHaveLength(1);expect(document.querySelectorAll('[data-metric="revenue"]')).toHaveLength(8);expect(document.querySelectorAll('[data-metric="fcff"]')).toHaveLength(5);expect(document.querySelector('[data-fixed-anchor]')?.getAttribute('data-fixed-anchor')).toBe('FY2025');const first=document.querySelector('[data-metric="fcff"]')!;expect(Number(first.getAttribute('height'))).toBeGreaterThan(0);expect(screen.getByText('-2')).toBeTruthy();expect(r).toEqual(copy);
 const bars=[...document.querySelectorAll('[data-bar-year]')];expect(new Set(bars.map(n=>n.getAttribute('width'))).size).toBe(1);expect(bars.every(n=>n.getAttribute('rx')==='1.5'&&n.getAttribute('ry')==='1.5')).toBe(true);
 const chart=screen.getByRole('region',{name:'Combined Revenue and FCFF plot'}),readout=screen.getByLabelText('Selected year values');expect(chart.contains(readout)).toBe(false);expect(document.querySelector('.cv-chart-legend')).toBeNull();expect(document.querySelector('.cv-operating-readout')).toBeNull();expect(readout.textContent).toContain('FY2030 · Forecast');expect(readout.textContent).toContain('6.00B');expect(readout.textContent).not.toContain('USD');
 fireEvent.mouseMove(screen.getByRole('button',{name:'combined: select FY2026'}));expect(readout.textContent).toContain('-2.00B');fireEvent.click(screen.getByRole('button',{name:'combined: select FY2023'}));expect(readout.textContent).toContain('FY2023 · Reported');expect(readout.textContent).toContain('Unavailable');expect(readout.textContent).not.toContain('history');
});
it('computes endpoint comparisons with exact independent expectations and isolated Decimal context',()=>{
 const before=Decimal.precision;Decimal.set({precision:2});try{
 expect(endpointGuide('FY2025','1000000000','FY2027','1210000000')).toBe('FY2025 → FY2027: 10.00% endpoint CAGR · 2 fiscal-year intervals');expect(endpointGuide('FY2025','1000000000','FY2023','700000000')).toBe('FY2023 → FY2025: 19.52% endpoint CAGR · 2 fiscal-year intervals');expect(endpointGuide('FY2025','1000000000','FY2024','800000000')).toBe('FY2024 → FY2025: 25.00% endpoint CAGR · 1 fiscal-year interval');expect(endpointGuide('FY2025','1000000000','FY2025','1000000000')).toContain('baseline');expect(endpointGuide('FY2025',null,'FY2027','2000000000')).toBe('FY2025 FCFF unavailable · no guide');expect(endpointGuide('FY2025','-1000000000','FY2027','2000000000')).toContain('+3.00 USD bn');expect(endpointGuide('FY2025','0','FY2027','2000000000')).not.toContain('%');expect(Decimal.precision).toBe(2);
 }finally{Decimal.set({precision:before});}
});
it('keeps previous observations visible with their stale status and precise USD data',()=>{render(<ScenarioCharts stale cases={[{label:'Base',result:result()}]}/>);expect(screen.getByText(/Previous operating calculation · stale/)).toBeTruthy();expect(screen.getByText('Base FY2026')).toBeTruthy();expect(screen.getAllByText('-2000000000').length).toBeGreaterThan(0);});

it('does not attach historical observations from a different source identity',()=>{
 const entry=history();entry.identity={...entry.identity,accession:'different-source'};render(<ForecastChart entry={entry} cases={[{label:'Base',result:result()}]}/>);expect(document.querySelectorAll('[data-scenario-bar="Reported"]')).toHaveLength(1);expect(screen.queryByRole('button',{name:'combined: select FY2023'})).toBeNull();
});

it('uses solid navy/gold DCF bars and consistent slate/gold/teal scenario legends and readouts',()=>{
 const dcf=render(<ForecastChart entry={history()} cases={[{label:'Base',result:result()}]}/>);expect(document.querySelector('pattern')).toBeNull();expect([...document.querySelectorAll('[data-metric="fcff"]')].every(n=>n.getAttribute('fill')==='var(--cw-gold, #aa8534)')).toBe(true);expect(document.querySelector('[data-scenario-bar="Base"][data-metric="revenue"]')?.getAttribute('fill')).toBe('var(--cw-revenue, #23435a)');expect(document.querySelector('[data-scenario-bar="Reported"]')?.getAttribute('fill')).toBe('var(--cw-history, #9ba8b2)');dcf.unmount();render(<ScenarioCharts entry={history()} cases={['Bear','Base','Bull'].map(label=>({label,result:result()}))}/>);for(const [label,color]of [['Bear','var(--cw-bear, #657c91)'],['Base','var(--cw-gold, #aa8534)'],['Bull','var(--cw-bull, #39766b)']]){expect([...document.querySelectorAll(`[data-scenario-bar="${label}"]`)].every(n=>n.getAttribute('fill')===color)).toBe(true);expect(document.querySelector(`.cv-operating-readout th i[style*="${color}"]`)).toBeTruthy();expect(document.querySelector(`.cv-chart-legend i[style*="${color}"]`)).toBeTruthy();}expect(document.querySelector('[fill^="url("]')).toBeNull();
});

it('fits fifteen years to a narrow container and preserves geometry when another section hides the plot',()=>{
 let resize!:(entries:{contentRect:{width:number}}[])=>void;
 vi.stubGlobal('ResizeObserver',class{constructor(callback:typeof resize){resize=callback;}observe(){}disconnect(){}});
 try{
  const entry=history(),first=entry.historical_window![0];
  entry.historical_window!.unshift(...['2021','2022'].map(year=>({...first,fiscal_year_label:'FY'+year,revenue:{...first.revenue,period_start:year+'-01-01',period_end:year+'-12-31'}})));
  const r=result();r.stage_b.stage_a.years=Array.from({length:10},(_,i)=>({...r.stage_b.stage_a.years[i%5],fiscal_year_label:'FY'+(2026+i)}));
  render(<ForecastChart entry={entry} cases={[{label:'Base',result:r}]}/>);
  act(()=>resize([{contentRect:{width:330}}]));
  const svg=document.querySelector('svg')!;expect(svg.getAttribute('viewBox')).toBe('0 0 330 450');
  expect(within(screen.getByRole('group',{name:'combined by fiscal year; arrow keys select a year'})).getAllByRole('button')).toHaveLength(15);
  expect([...svg.querySelectorAll('[data-bar-year]')].every(n=>Number(n.getAttribute('width'))>0)).toBe(true);
  expect(svg.querySelector('[data-five-year-boundary]')).not.toBeNull();
  fireEvent.click(screen.getByRole('button',{name:'combined: select FY2035'}));expect(screen.getByText('FY2035 · Forecast')).toBeTruthy();
  act(()=>resize([{contentRect:{width:0}}]));expect(svg.getAttribute('viewBox')).toBe('0 0 330 450');
 }finally{vi.unstubAllGlobals();}
});


it('places DCF CAGR labels above the middle of the chronological endpoint guide and the selected-year readout below the plot',()=>{
 const r=result(),copy=structuredClone(r);render(<ForecastChart cases={[{label:'Base',result:r}]} entry={history()}/>);
 const chart=screen.getByRole('region',{name:'Combined Revenue and FCFF plot'}),svg=chart.querySelector('svg')!;
 expect(svg.getAttribute('data-chart-height')).toBe('520');
 expect(chart.querySelector('.cv-chart-heading')).toBeNull();expect(chart.querySelector('.cv-guide-labels')).toBeNull();
 const container=document.querySelector('.cv-operating-scroll')!;expect(container.nextElementSibling?.className).toBe('cw-chart-readout-footer');
 fireEvent.mouseMove(screen.getByRole('button',{name:'combined: select FY2023'}));
 let line=chart.querySelector('[data-base-trend="revenue"]')!,label=chart.querySelector('[data-cagr-metric="revenue"]')!;
 expect(line.getAttribute('data-start-year')).toBe('FY2023');expect(line.getAttribute('data-end-year')).toBe('FY2025');
 expect(label.getAttribute('data-cagr-from')).toBe('FY2023');expect(label.textContent).toContain('19.52% CAGR');
 const coords=label.getAttribute('transform')!.match(/translate\(([^ ]+) ([^)]+)\)/)!;
 expect(Number(coords[1])).toBeCloseTo((Number(line.getAttribute('x1'))+Number(line.getAttribute('x2')))/2);
 expect(Number(coords[2])).toBeLessThan((Number(line.getAttribute('y1'))+Number(line.getAttribute('y2')))/2);
 const rev=chart.querySelector('[data-bar-year="FY2026"][data-metric="revenue"]')!,cash=chart.querySelector('[data-bar-year="FY2026"][data-metric="fcff"]')!;
 const gap=Number(cash.getAttribute('x'))-Number(rev.getAttribute('x'))-Number(rev.getAttribute('width'));
 expect(gap).toBeGreaterThan(0);expect(gap/Number(rev.getAttribute('width'))).toBeLessThan(.08);
 fireEvent.click(screen.getByRole('button',{name:'combined: select FY2027'}));
 line=chart.querySelector('[data-base-trend="revenue"]')!;label=chart.querySelector('[data-cagr-metric="revenue"]')!;
 expect(line.getAttribute('data-start-year')).toBe('FY2025');expect(label.getAttribute('data-cagr-to')).toBe('FY2027');
 expect(label.textContent).toContain('73.21% CAGR');expect(chart.querySelector('[data-cagr-metric="fcff"]')).toBeNull();
 fireEvent.click(screen.getByRole('button',{name:'combined: select FY2025, fixed anchor'}));expect(chart.querySelector('[data-cagr-metric]')).toBeNull();expect(r).toEqual(copy);
});

it('uses earlier-year denominators without forcing declining history positive and avoids CAGR for nonpositive endpoints',()=>{
 expect(endpointCagr('FY2025','1210000000','FY2023','1000000000')).toEqual({from:'FY2023',to:'FY2025',intervals:2,percent:'10.00'});
 expect(endpointCagr('FY2025','1000000000','FY2023','1210000000')?.percent).toBe('-9.09');
 for(const [a,v]of [['0','1'],['-1','2'],['1','-2'],['1','0']])expect(endpointCagr('FY2025',a,'FY2023',v)).toBeNull();
 expect(endpointCagr('FY2025',null,'FY2023','1')).toBeNull();expect(endpointCagr('FY2025','1','FY2025','1')).toBeNull();
});


it('keeps extreme CAGR annotations compact while retaining the exact comparison in the title',()=>{
 const r=result();r.stage_b.stage_a.years.at(-1)!.revenue='1'+'0'.repeat(100);
 render(<ForecastChart cases={[{label:'Base',result:r}]} entry={history()}/>);
 const label=document.querySelector('[data-cagr-metric="revenue"]')!;
 expect(label.querySelector('text')!.textContent!.length).toBeLessThan(24);
 expect(label.querySelector('title')!.textContent!.length).toBeGreaterThan(24);
 expect(Number(label.querySelector('rect')!.getAttribute('width'))).toBeLessThan(180);
});
