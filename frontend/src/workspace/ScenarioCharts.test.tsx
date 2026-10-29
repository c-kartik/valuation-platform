import {it,expect} from 'vitest';
import {render,screen,fireEvent,within} from '@testing-library/react';
import {ScenarioCharts} from './ScenarioCharts';
import {makeDraft} from '../model';
import type {CaseDoc,Result} from '../model';
import fixture from '../../../examples/valuation/synthetic-base.json';
function result(offset:number):Result{const doc=makeDraft(fixture as CaseDoc).doc;return {case_name:'Software fixture',input_basis:'SYNTHETIC_FIXTURE',submitted_inputs:doc,limitations:[],stage_b:{stage_a:{anchor:{revenue:'1000000000'},years:doc.forecast_years.map((y,i)=>({fiscal_year_label:y.fiscal_year_label,revenue:String((i+2+offset)*1000000000),fcff:String((i-2+offset)*1000000000)}))},years:[],terminal:{},timing:{analytical_t0:doc.anchor.annual_end,notice:'Fixture',information_cutoff:'UNKNOWN'},terminal_value:'0',pv_terminal_value:'0',pv_explicit_fcff:'0',enterprise_value:'0'}};}
it('renders two aligned line charts from returned points, with shared keyboard/tap/hover selection and exact data',()=>{
 render(<ScenarioCharts cases={['Bear','Base','Bull'].map((label,i)=>({label,result:result(i)}))}/>);
 expect(document.querySelectorAll('polyline')).toHaveLength(6);expect(screen.getAllByText(/independent .* scale/)).toHaveLength(2);
 const revenue=screen.getByRole('region',{name:'Revenue scenario line chart'}),fcff=screen.getByRole('region',{name:'FCFF scenario line chart'});
 const points=within(revenue).getAllByRole('button');fireEvent.focus(points[1]);fireEvent.keyDown(points[1],{key:'ArrowRight'});expect(screen.getByRole('status').textContent).toContain('Base: Revenue 4.00 · FCFF 0.00');expect(within(fcff).getAllByRole('button')[2].getAttribute('aria-pressed')).toBe('true');
 fireEvent.click(within(fcff).getAllByRole('button')[1]);expect(screen.getByRole('status').textContent).toContain('Bear: Revenue 2.00 · FCFF -2.00');expect(points[1].getAttribute('aria-pressed')).toBe('true');fireEvent.mouseEnter(points[3]);expect(within(fcff).getAllByRole('button')[3].getAttribute('aria-pressed')).toBe('true');
 fireEvent.click(points[0]);expect(screen.getByRole('status').textContent).toContain('historical FCFF unavailable');expect(screen.getAllByText('—')).toHaveLength(3);expect(document.querySelectorAll('polyline')[3].getAttribute('points')!.split(' ')).toHaveLength(5);expect(screen.getByText('Bear Synthetic period 2')).toBeTruthy();
});
it('keeps previous line values visible with an explicit stale notice',()=>{render(<ScenarioCharts stale cases={[{label:'Base',result:result(0)}]}/>);expect(screen.getByText(/Previous comparison · stale/)).toBeTruthy();expect(document.querySelectorAll('polyline')).toHaveLength(2);});
