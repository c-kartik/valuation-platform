import {it,expect,vi,afterEach} from 'vitest';
import {render,screen,fireEvent,within} from '@testing-library/react';
import {Prototype} from './Prototype';
import {fixtures,newCase,createScenario,variantFor,fresh,signature,emptyBridge,demoBridge,bridgeMatches,inputErrors,D,priceDifference,supportedGrid} from './model';
afterEach(()=>vi.unstubAllGlobals());
const click=(name:string)=>{const dialog=screen.queryByRole('dialog');fireEvent.click((dialog?within(dialog):screen).getByRole('button',{name}));};
const tab=(name:string)=>fireEvent.click(screen.getByRole('tab',{name:new RegExp(name)}));
const set=(name:string,value:string)=>fireEvent.change(screen.getByLabelText(name,{exact:true}),{target:{value}});
function addBridge(){fireEvent.click(screen.getByLabelText('Include an optional equity / share reference'));click('Use illustrative bridge');click('Load synthetic bridge');click('Preview valuation');}
function load(profile:string){fireEvent.click(screen.getByText('Explore a prepared illustration'));set('Illustration',profile);click('Load illustration');click('Load illustration');}
it('copies Base independently without generating Bear/Bull economics or changing existing cases',()=>{
 const base=newCase();base.notes='My thesis';const cases=createScenario({Base:base},'Bear');expect(cases.Bear).toEqual(base);expect(cases.Bear).not.toBe(base);
 cases.Bear!.inputs.annual[0].growth='99';expect(base.inputs.annual[0].growth).toBe('10');expect(createScenario(cases,'Bear')).toBe(cases);
});
it('only matches complete prepared states; unsupported edits are not calculations',()=>{
 const c=newCase();const v=variantFor(c.inputs)!;c.shown={signature:signature(c.inputs),variant:v,bridgeSignature:signature(emptyBridge())};expect(fresh(c)).toBe(true);
 c.inputs.annual[1].growth='12';expect(fresh(c)).toBe(false);expect(variantFor(c.inputs)).toBeUndefined();
 expect(inputErrors({...c.inputs,wacc:'3',g:'4'}).g).toMatch(/below WACC/);expect(inputErrors({...c.inputs,wacc:''}).wacc).toMatch(/number/);
 expect(bridgeMatches(demoBridge())).toBe(true);expect(bridgeMatches({...demoBridge(),shares:'101'})).toBe(false);
});
it('keeps all offline fixture reconciliations coherent without running an engine in the browser',()=>{
 const Precise=D.clone({precision:90});const near=(a:DecimalLike,b:DecimalLike)=>expect(new Precise(a).minus(b).abs().lt('1e-38')).toBe(true);
 for(const v of fixtures.variants){const r=v.result;near(r.ev,new Precise(r.explicitPV).plus(r.terminalPV));near(r.equity,new Precise(r.ev).plus(150).minus(200).minus(25));near(r.perShare,new Precise(r.equity).div(100));
  for(const y of r.years)near(y.fcff,new Precise(y.nopat).plus(y.d_and_a).minus(y.investment).minus(y.working_capital_cash_requirement));
 }
 expect(fixtures.reverse.some(r=>r.status==='SUCCESS')).toBe(true);expect(fixtures.reverse.some(r=>r.status==='UNREACHABLE_TARGET')).toBe(true);expect(fixtures.reverse.some(r=>r.status==='UNIQUENESS_NOT_CERTIFIED')).toBe(true);
});
type DecimalLike=string|InstanceType<typeof D>;
it('limits the grids and date-consistent presentation comparison',()=>{
 expect(supportedGrid(['9','11','1','2.5','3.5','0.5'])).toBeTruthy();expect(supportedGrid(['8','11','1','2.5','3.5','0.5'])).toBeUndefined();
 expect(priceDifference('30','25','2025-12-31')).toBe('20.0');expect(priceDifference('30','25','2026-01-01')).toBeNull();expect(priceDifference('30','0','2025-12-31')).toBeNull();expect(priceDifference('30','Infinity','2025-12-31')).toBeNull();
});
it('starts with a persistent synthetic designation, sends no network calls and stores nothing',()=>{
 const fetch=vi.fn();vi.stubGlobal('fetch',fetch);const local=vi.spyOn(Storage.prototype,'setItem');render(<Prototype/>);
 expect(screen.getByText('Interactive prototype — illustrative data')).toBeTruthy();expect(screen.getByRole('heading',{name:'Northstar Instruments'})).toBeTruthy();expect(fetch).not.toHaveBeenCalled();expect(local).not.toHaveBeenCalled();local.mockRestore();
});
it('marks unsupported edited outputs stale, preserves notes between tabs and never presents a new fixture calculation',()=>{
 render(<Prototype/>);set('Optional notes · Base','Keep my work');set('Revenue growth (%)','12');click('Preview valuation');
 expect(screen.getByText(/Not calculated: these edited assumptions/)).toBeTruthy();expect(screen.getByText(/Not calculated for current inputs/)).toBeTruthy();expect(screen.getByText(/Earlier illustration · STALE/)).toBeTruthy();
 tab('Reverse DCF');tab('Valuation');expect((screen.getByLabelText('Revenue growth (%)') as HTMLInputElement).value).toBe('12');expect((screen.getByLabelText('Optional notes · Base') as HTMLTextAreaElement).value).toBe('Keep my work');
});
it('shows associated validation errors without selecting a fixture result',()=>{
 render(<Prototype/>);set('Operating tax (%)','150');click('Preview valuation');expect(screen.getByRole('region',{name:'Input issues'})).toBeTruthy();expect(screen.getByLabelText('Operating tax (%)').getAttribute('aria-invalid')).toBe('true');
});
it('copies terminal ratios only with confirmation and keeps later annual edits independent',()=>{
 render(<Prototype/>);fireEvent.click(screen.getByText('Edit terminal operating assumptions'));click('Copy FY2030 operating ratios');click('Keep current inputs');expect((screen.getByLabelText('Long-term Operating margin (%)') as HTMLInputElement).value).toBe('25');
 click('Copy FY2030 operating ratios');click('Copy five ratios');expect((screen.getByLabelText('Long-term Operating margin (%)') as HTMLInputElement).value).toBe('24');set('Operating margin (%)','26');expect((screen.getByLabelText('Long-term Operating margin (%)') as HTMLInputElement).value).toBe('24');
});
it('offers only an issued-share qualified result after explicitly loading and previewing the shared bridge',()=>{
 render(<Prototype/>);expect(screen.queryByText('Equity reconciliation')).toBeNull();addBridge();expect(screen.getByRole('heading',{name:'Equity reconciliation'})).toBeTruthy();expect(screen.getByText(/Not fully diluted fair value/)).toBeTruthy();
 set('Valuation shares','101');expect(screen.queryByRole('heading',{name:'Equity reconciliation'})).toBeNull();expect(screen.getByText(/Per-share reference unavailable/)).toBeTruthy();
});
it('reuses the selected forward case for reverse success, outside-bounds and unsupported target states',()=>{
 render(<Prototype/>);addBridge();tab('Reverse DCF');click('Use $25 target');click('Preview implied revenue growth');expect(screen.getByText('annual revenue growth for five years')).toBeTruthy();
 click('Use out-of-bounds target');expect(screen.getByRole('heading',{name:'Reverse result is stale'})).toBeTruthy();click('Preview implied revenue growth');expect(screen.getByRole('heading',{name:'Target outside the search interval'})).toBeTruthy();expect(screen.queryByText('annual revenue growth for five years')).toBeNull();
 set('Price to explain (USD/share)','37');click('Preview implied revenue growth');expect(screen.getByText(/this combination has no prepared illustration/)).toBeTruthy();
});
it('exposes an uncertified result only after explicitly replacing and previewing the heavy-investment case',()=>{
 render(<Prototype/>);addBridge();tab('Reverse DCF');click('Load uncertified illustration');click('Load uncertified illustration');tab('Valuation');click('Preview valuation');tab('Reverse DCF');click('Preview implied revenue growth');expect(screen.getByRole('heading',{name:'Uniqueness not certified'})).toBeTruthy();expect(screen.queryByText('annual revenue growth for five years')).toBeNull();
});
it('creates scenarios as exact Base copies; only explicit scenario edits change their economics',()=>{
 render(<Prototype/>);set('Optional notes · Base','Base notes');tab('Scenarios');click('Create Bear from Base');expect((screen.getByLabelText('Revenue growth (%)') as HTMLInputElement).value).toBe('10');set('Revenue growth (%)','6');click('Create Bull from Base');expect((screen.getByLabelText('Revenue growth (%)') as HTMLInputElement).value).toBe('10');set('Inspecting case','Bear');expect((screen.getByLabelText('Revenue growth (%)') as HTMLInputElement).value).toBe('6');set('Inspecting case','Base');expect((screen.getByLabelText('Optional notes · Base') as HTMLTextAreaElement).value).toBe('Base notes');
});
it('inspects a sensitivity cell without applying, then requires confirmation and stales only the selected case',()=>{
 render(<Prototype/>);tab('Scenarios');click('Create Bear from Base');tab('Sensitivity');click('Preview grid');click('Inspect WACC 9%, terminal growth 2.5%');
 expect(screen.getByText('Inspection has not changed Bear. Only these two assumptions would be replaced.')).toBeTruthy();click('Apply to case');click('Keep current inputs');expect(screen.getByRole('combobox',{name:'Completed scenario'})).toBeTruthy();click('Apply to case');click('Apply to case');tab('Valuation');expect((screen.getByLabelText('WACC (%)') as HTMLInputElement).value).toBe('9');expect((screen.getByLabelText('Terminal growth (%)') as HTMLInputElement).value).toBe('2.5');expect(screen.getByText(/Not calculated for current inputs/)).toBeTruthy();set('Inspecting case','Base');expect((screen.getByLabelText('WACC (%)') as HTMLInputElement).value).toBe('10');
});
it('explains invalid cells and provides no apply action; unsupported grid edits cannot show fresh results',()=>{
 render(<Prototype/>);tab('Sensitivity');click('Invalid-pair illustration');click('Preview grid');click('Inspect WACC 2%, terminal growth 2%, invalid: growth must be below WACC');expect(screen.getByText(/Invalid pair: terminal growth/)).toBeTruthy();expect(screen.queryByRole('button',{name:'Apply to case'})).toBeNull();set('WACC start (%)','8');click('Preview grid');expect(screen.getByText(/these ranges or operating inputs are outside/)).toBeTruthy();
});
it('supports arrow-key tab navigation, focus return and reset confirmation',()=>{
 render(<Prototype/>);const valuation=screen.getByRole('tab',{name:/Valuation/});valuation.focus();fireEvent.keyDown(valuation,{key:'ArrowRight'});expect(screen.getByRole('tab',{name:/Reverse DCF/}).getAttribute('aria-selected')).toBe('true');expect(document.activeElement).toBe(screen.getByRole('tab',{name:/Reverse DCF/}));
 const opener=screen.getByRole('button',{name:'Sources & methodology ↗'});click('Sources & methodology ↗');expect(screen.getByRole('dialog',{name:'Sources & methodology'})).toBeTruthy();click('Close');expect(document.activeElement).toBe(opener);click('Reset session');expect(within(screen.getByRole('dialog')).getByRole('button',{name:'Keep current inputs'})).toBeTruthy();click('Keep current inputs');
});
it('replaces varied annual rates only after a complete constant-entry confirmation',()=>{
 render(<Prototype/>);fireEvent.click(screen.getByText(/Edit annual assumptions/));set('FY2027 Revenue growth (%)','12');click('Varies · replace five revenue growth rates');set('Revenue growth constant rate (%)','15');click('Keep current inputs');expect((screen.getByLabelText('FY2027 Revenue growth (%)') as HTMLInputElement).value).toBe('12');
 click('Varies · replace five revenue growth rates');set('Revenue growth constant rate (%)','13');click('Replace five entries');expect((screen.getByLabelText('Revenue growth (%)') as HTMLInputElement).value).toBe('13');expect((screen.getByLabelText('FY2030 Revenue growth (%)') as HTMLInputElement).value).toBe('13');
});
