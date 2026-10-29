import {it,expect,vi} from 'vitest';
import {renderHook,act,waitFor,render,screen,fireEvent,within} from '@testing-library/react';
import {useWorkspace} from './useWorkspace';
import {makeDraft} from '../model';
import type {CaseDoc,Catalog,Result,InvestorDoc} from '../model';
import {request} from '../api';
import {smallGrid,axes} from './sensitivity';
import {percentage,readableMoney,fixedUnit} from '../presentation';
import {ForecastChart} from './ForecastChart';
import {MarketPanel} from './MarketPanel';
import {InvestorResult} from './InvestorResult';
import {ValuationBreakdown} from './ValuationBreakdown';
import fixture from '../../../examples/valuation/synthetic-base.json';
const demo=fixture as CaseDoc;
const catalog:Catalog={schema_version:'fixture',entries:[{kind:demo.anchor.kind,company:'Fixture',identity:demo.anchor,revenue:'100',unit:'USD',precision:'INF',source_links:[],limitations:[],template:demo}],synthetic_demo:demo,timing_notice:'fixture',input_definitions:{}};
it('inherits Base changes, preserves overrides and independent terminal ratios, resets explicitly and stales results',async()=>{
 const load=vi.fn(async()=>structuredClone(catalog)) as unknown as typeof request;
 const h=renderHook(()=>useWorkspace(load));await waitFor(()=>expect(h.result.current.catalog).not.toBeNull());act(()=>h.result.current.select(demo.anchor.kind));
 expect(h.result.current.company!.cases.Bear!.draft.rates).toEqual(h.result.current.company!.cases.Base.draft.rates);
 act(()=>h.result.current.editScenarioRate('Bear',['forecast_years[0].revenue_growth'],'9.123456789123456789'));
 act(()=>h.result.current.editScenarioRate('Base',['forecast_years[0].revenue_growth','forecast_years[1].revenue_growth'],'12'));
 const s=h.result.current.company!;expect(s.cases.Bear!.draft.rates['forecast_years[0].revenue_growth']).toBe('9.123456789123456789');expect(s.cases.Bear!.draft.rates['forecast_years[1].revenue_growth']).toBe('12');expect(s.cases.Bull!.draft.rates['forecast_years[0].revenue_growth']).toBe('12');expect(s.cases.Base.draft.rates['terminal.operating_margin']).toBe('30');
 act(()=>h.result.current.editScenarioRate('Bull',['terminal.operating_margin'],'41'));
 act(()=>h.result.current.editScenarioRate('Base',['terminal.operating_margin'],'35'));
 expect(h.result.current.company!.cases.Bull!.draft.rates['terminal.operating_margin']).toBe('41');expect(h.result.current.company!.cases.Bear!.draft.rates['terminal.operating_margin']).toBe('35');
 act(()=>h.result.current.resetOverrides('Bear'));expect(h.result.current.company!.cases.Bear!.overrides).toEqual([]);expect(h.result.current.company!.cases.Bear!.draft.rates).toEqual(h.result.current.company!.cases.Base.draft.rates);expect(load).toHaveBeenCalledTimes(1);
 act(()=>h.result.current.selectCase('Bull'));
 act(()=>h.result.current.editDraft(structuredClone(h.result.current.session!.draft),true,['forecast_years[0].revenue_growth']));
 act(()=>h.result.current.selectCase('Base'));act(()=>h.result.current.editScenarioRate('Base',['forecast_years[0].revenue_growth'],'14'));
 expect(h.result.current.company!.cases.Bull!.draft.rates['forecast_years[0].revenue_growth']).toBe('12');
});
it('generates only explicit editable diagnostic axes, centered on user values, without changing the draft',()=>{
 const d=makeDraft(demo);d.rates.wacc='9.125';d.rates.terminal_growth='2.75';const before=structuredClone(d);const a=axes(smallGrid(d));expect(a.wacc_values).toEqual(['0.08125','0.09125','0.10125']);expect(a.terminal_growth_values).toEqual(['0.0225','0.0275','0.0325']);expect(d).toEqual(before);
 d.rates.wacc='0.1';d.rates.terminal_growth='-99.9';expect(axes(smallGrid(d)).wacc_values).toHaveLength(3);
});
it('formats trillions, ordinary percentages, signed percentage points and small nonzero values without input rounding',()=>{
 expect(readableMoney('1675800000000')).toBe('$1.68tn');expect(readableMoney('-1675800000000')).toBe('−$1.68tn');expect(percentage('0.123456')).toBe('12.35%');expect(percentage('-0.123456',true)).toBe('-0.12 pp');expect(percentage(null)).toBe('Undefined');expect(percentage('0.0000001')).toBe('0.00001%');expect(fixedUnit('-1000000','1000000000')).toBe('-0.001');expect(readableMoney('0.00000001')).toBe('$0.00000001');
});
function forward():Result{
 const doc=makeDraft(demo).doc;return {case_name:'Fixture',input_basis:'SYNTHETIC_FIXTURE',submitted_inputs:doc,limitations:[],stage_b:{stage_a:{anchor:{revenue:'100'},years:doc.forecast_years.map((y,i)=>({fiscal_year_label:y.fiscal_year_label,revenue:String(110+i*10),fcff:i===0?'-2':i===1?'0':'3'}))},years:[],terminal:{fcff:'1'},timing:{analytical_t0:doc.anchor.annual_end,notice:'Fixture',information_cutoff:'UNKNOWN'},terminal_value:'0',pv_terminal_value:'0',pv_explicit_fcff:'1',enterprise_value:'1'}};
}
it('offers paired bars, keyboard/tap year readouts, metric toggles, comparison and an accessible table without historical FCFF',()=>{
 const a=forward(),b=structuredClone(a);b.stage_b.stage_a.years[0].fcff='-0.0001';render(<ForecastChart cases={[{label:'Bear',result:a},{label:'Base',result:b},{label:'Bull',result:a}]}/>);
 const year=screen.getAllByRole('button',{name:/Select .*reported revenue|Select .*forecast revenue/})[1];fireEvent.focus(year);fireEvent.keyDown(year,{key:'ArrowRight'});expect(document.activeElement).toBe(screen.getAllByRole('button',{name:/Select .*reported revenue|Select .*forecast revenue/})[2]);fireEvent.click(screen.getAllByRole('button',{name:/Select .*reported revenue|Select .*forecast revenue/})[0]);expect(screen.getByRole('status').textContent).toContain('FCFF unavailable');fireEvent.click(screen.getByRole('button',{name:'FCFF only'}));fireEvent.click(screen.getByRole('button',{name:'Compare'}));expect(screen.getByRole('heading',{name:'Compare operating paths'})).toBeTruthy();expect(screen.queryByRole('button',{name:'Revenue + FCFF'})).toBeNull();expect(screen.getByText('View data table')).toBeTruthy();expect(screen.getAllByText('—').length).toBe(3);expect(document.querySelector('polyline')).toBeNull();
});
it('renders dated market reconciliation and percentage-point labels without solver internals or failure substitutes',()=>{
 const a=forward();a.investor_review={status:'SCOPE_QUALIFIED',reasons:[],model_ev:'1',forecast_cagr:'0.1',market_cap:'8',market_implied_ev:'19',ev_relative_difference:'-0.5',market_implied_growth:null,growth_gap_percentage_points:null,equity_difference:'-0.2',per_share_difference:'-0.2',reverse:{status:'UNREACHABLE_TARGET'},market:{price:'2',session_date:'2025-12-31',timezone:'America/New_York',delay:'Fixture only',fallback:'Prior session',share_class:'Class A',adjustment:'UNADJUSTED',source_url:'https://api.massive.com/fixture'},limitations:[]};
 a.stage_c={stage_b:{enterprise_value:'1'},eligible_assets:'12',financing_claims:'20',other_equity_claims:'3',equity_value:'-10',valuation_shares:'4',value_per_share:'-2.5',inputs:{observations:[],shares:{class_id:'Common',observation_date:'2025-12-31',rationale:'Fixture only'}},contributions:[]};
 render(<MarketPanel result={a} stale={false}/>);expect(screen.getByText(/\$2.00 USD\/share/)).toBeTruthy();expect(screen.getByText('− Selected eligible non-operating assets')).toBeTruthy();expect(screen.getByText('+ Financing claims')).toBeTruthy();expect(screen.getByText('$19.00')).toBeTruthy();expect(screen.getByText('-50.00%')).toBeTruthy();expect(screen.getAllByText('Undefined')).toHaveLength(2);expect(screen.getByText(/No implied growth: unreachable target/)).toBeTruthy();expect(screen.getByText(/Dated denominator: 4 shares/)).toBeTruthy();expect(screen.queryByText(/certificate|Bernstein/i)).toBeNull();
});
it('withholds a stale bridge-based market comparison while preserving the independently current operating EV',()=>{
 const a=forward();render(<InvestorResult result={a} stale={false} marketStale/>);
 expect(screen.getByText('Comparison stale — recalculate the changed case.')).toBeTruthy();expect(screen.queryByText('Stale result — inputs changed; calculate again.')).toBeNull();expect(screen.getAllByText('$1.00')).toHaveLength(2);
});
it('uses a composition bar only for positive allocations and preserves zero, negative and over-100% contributions',()=>{
 const a=forward();a.stage_b.years=Array.from({length:5},()=>({discount_factor:'1',pv_fcff:'8'}));Object.assign(a.stage_b,{enterprise_value:'100',pv_explicit_fcff:'40',pv_terminal_value:'60'});
 const view=render(<ValuationBreakdown result={a} stale={false}/>);expect(screen.getByRole('img').getAttribute('aria-label')).toContain('terminal PV $60.00');expect(screen.getByText('60.00%')).toBeTruthy();
 const b=structuredClone(a);Object.assign(b.stage_b,{pv_explicit_fcff:'-20',pv_terminal_value:'120'});view.rerender(<ValuationBreakdown result={b} stale/>);expect(screen.queryByRole('img')).toBeNull();expect(screen.getByText('120.00%')).toBeTruthy();expect(screen.getByText('Previous calculation · stale')).toBeTruthy();
 Object.assign(b.stage_b,{pv_explicit_fcff:'-120',enterprise_value:'0'});view.rerender(<ValuationBreakdown result={b} stale={false}/>);expect(screen.queryByRole('img')).toBeNull();expect(screen.getByText('Undefined')).toBeTruthy();
 Object.assign(b.stage_b,{pv_explicit_fcff:'-140',enterprise_value:'-20',pv_terminal_value:'120'});view.rerender(<ValuationBreakdown result={b} stale={false}/>);expect(screen.queryByRole('img')).toBeNull();expect(screen.getByText('-600.00%')).toBeTruthy();
});
