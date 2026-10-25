import {it,expect} from 'vitest';
import {render,screen,fireEvent,within,waitFor} from '@testing-library/react';
import {Prototype} from './Prototype';
import {fixtures,demoBridge,fresh,signature,variantFor,perShareFresh} from './model';
import {initialWorkspace,newAnalysis,editInputs,forkCase,impliedInputs,rateInputs,effectiveReverse,reverseKey,gridKey,reverseCurrent,gridCurrent} from './workspace';
const click=(name:string)=>fireEvent.click((screen.queryByRole('dialog')?within(screen.getByRole('dialog')):screen).getByRole('button',{name}));
const choose=(name:string,value:string)=>fireEvent.change(screen.getByLabelText(name,{exact:true}),{target:{value}});
function guided(){click('Start guided illustrative journey');click('Use guided context');click('Preview valuation');click('← Return to overview');}
function prepareState(){const s=initialWorkspace();s.bridge=demoBridge();s.cases.Base.shown!.bridgeSignature=signature(s.bridge);s.comparison={price:'25',date:'2025-12-31'};const a=s.analyses.Base;a.output={key:reverseKey('Base',s.cases.Base,effectiveReverse(a,s.comparison),s.bridge),record:fixtures.reverse[0]};a.gridShown=gridKey('Base',s.cases.Base,a.grid);return s;}
it('tracks only relevant reverse/grid dependencies and keeps forward EV separate from bridge eligibility',()=>{
 const s=prepareState();expect(reverseCurrent(s,'Base')).toBe(true);expect(gridCurrent(s,'Base')).toBe(true);
 const bridgeEdit={...s,bridge:{...s.bridge,shares:'101'}};expect(fresh(bridgeEdit.cases.Base)).toBe(true);expect(perShareFresh(bridgeEdit.cases.Base,bridgeEdit.bridge)).toBe(false);expect(reverseCurrent(bridgeEdit,'Base')).toBe(false);expect(gridCurrent(bridgeEdit,'Base')).toBe(true);
 s.analyses.Base.reverse={metric:'ev',target:'2500',date:'2025-12-31',lower:'-10',upper:'30',mode:'override'};s.analyses.Base.output!.key=reverseKey('Base',s.cases.Base,s.analyses.Base.reverse,s.bridge);
 expect(reverseCurrent({...s,bridge:{...s.bridge,claims:'99'},comparison:{price:'99',date:'2025-12-31'}},'Base')).toBe(true);
 const next=editInputs(s,'Base',{...s.cases.Base.inputs,wacc:'11'});expect(reverseCurrent(next,'Base')).toBe(false);expect(gridCurrent(next,'Base')).toBe(false);expect(fresh(next.cases.Base)).toBe(false);expect(next.cases.Base.revision).toBe(2);
});
it('distinguishes shared price targets from independent overrides without staling business value',()=>{
 const s=prepareState(),changed={...s,comparison:{price:'26',date:'2025-12-31'}};expect(reverseCurrent(changed,'Base')).toBe(false);expect(fresh(changed.cases.Base)).toBe(true);expect(gridCurrent(changed,'Base')).toBe(true);
 s.analyses.Base.reverse={...effectiveReverse(s.analyses.Base,s.comparison),mode:'override'};s.analyses.Base.output!.key=reverseKey('Base',s.cases.Base,s.analyses.Base.reverse,s.bridge);expect(reverseCurrent({...s,comparison:changed.comparison},'Base')).toBe(true);
 s.cases.Base.notes='Notes do not change economics';expect(reverseCurrent(s,'Base')).toBe(true);expect(gridCurrent(s,'Base')).toBe(true);
});
it('creates exact reverse-derived and rate-pair exploratory inputs without overwriting named cases',()=>{
 const s=prepareState();s.cases.Bear=structuredClone(s.cases.Base);s.analyses.Bear=newAnalysis();const before=structuredClone(s);const r=fixtures.reverse.find(r=>r.status==='SUCCESS')!;
 const derived=impliedInputs(s.cases.Base,r.growth!),next=forkCase(s,'Base',derived,'implied target');
 expect(next.selected).toBe('Exploratory 1');expect(next.cases.Base).toEqual(before.cases.Base);expect(next.cases.Bear).toEqual(before.cases.Bear);expect(next.cases['Exploratory 1'].inputs.annual.map(y=>y.growth)).toEqual(Array(5).fill(r.growth));
 expect(derived.annual.map(({growth,...rest})=>rest)).toEqual(s.cases.Base.inputs.annual.map(({growth,...rest})=>rest));expect(derived.terminal).toEqual(s.cases.Base.inputs.terminal);expect(derived.wacc).toBe(s.cases.Base.inputs.wacc);expect(derived.g).toBe(s.cases.Base.inputs.g);expect(variantFor(derived)).toBeTruthy();expect(next.cases['Exploratory 1'].shown).toBeUndefined();expect(next.cases['Exploratory 1'].relation).toEqual({source:'Base',revision:1,description:'implied target'});
 const forked=forkCase(next,'Exploratory 1',rateInputs(next.cases['Exploratory 1'],'9','2.5'),'rate pair');expect(forked.cases['Exploratory 2'].inputs).toEqual({...derived,wacc:'9',g:'2.5'});expect(forked.cases['Exploratory 1']).toEqual(next.cases['Exploratory 1']);expect(variantFor(forked.cases['Exploratory 2'].inputs)).toBeTruthy();
});
it('preserves independent case analyses, notes and siblings across revision changes',()=>{
 const s=prepareState();s.cases.Bear=structuredClone(s.cases.Base);s.analyses.Bear=newAnalysis();s.analyses.Bear.gridShown=gridKey('Bear',s.cases.Bear,s.analyses.Bear.grid);const before=structuredClone(s.cases.Base);
 const changed=editInputs(s,'Bear',{...s.cases.Bear.inputs,g:'3.5'});expect(changed.cases.Base).toEqual(before);expect(reverseCurrent(changed,'Base')).toBe(true);expect(gridCurrent(changed,'Base')).toBe(true);expect(gridCurrent(changed,'Bear')).toBe(false);
});
it('starts with an honest compact overview and routes missing price prerequisites to the bridge',()=>{
 render(<Prototype/>);expect(screen.getByRole('region',{name:'Base analytical overview'})).toBeTruthy();expect(screen.getAllByText('Not performed')).toHaveLength(2);expect(screen.queryByLabelText('Revenue growth (%)')).toBeNull();click('Explain this price');expect(screen.getByText(/Complete the shared equity\/share illustration/)).toBeTruthy();expect(screen.getByLabelText('Include an optional equity / share reference')).toBeTruthy();
});
it('completes the explicit linked fixture journey, retaining per-case work and overview return focus',async()=>{
 render(<Prototype/>);guided();click('Explain this price');expect(screen.getByLabelText('Price to explain (USD/share)').getAttribute('value')).toBe('25');expect(screen.getByText('shared comparison price')).toBeTruthy();click('Preview implied revenue growth');click('Create scenario from implied growth');
 const record=fixtures.reverse[0];expect(screen.getByRole('dialog').textContent).toContain(record.growth);click('Keep current inputs');expect(screen.queryByLabelText('Optional notes · Exploratory 1')).toBeNull();click('Create scenario from implied growth');click('Create exploratory case');
 expect(screen.getByLabelText('Revenue growth (%)').getAttribute('value')).toBe(record.growth);click('Preview valuation');click('← Return to overview');click('Compare scenarios');expect(screen.getByRole('heading',{name:'Implied path reference · Exploratory 1 · implied reference'})).toBeTruthy();click('Test sensitivity · Exploratory 1');click('Preview grid');click('Inspect WACC 9%, terminal growth 2.5%');expect(screen.getByText('Inspection has not changed Exploratory 1. Only these two assumptions would be replaced.')).toBeTruthy();
 click('Create exploratory case using this rate pair');click('Create exploratory case');expect(screen.getByLabelText('WACC (%)').getAttribute('value')).toBe('9');expect(screen.getByLabelText('Revenue growth (%)').getAttribute('value')).toBe(record.growth);click('Preview valuation');click('← Return to overview');expect(screen.getByRole('region',{name:'Exploratory 2 analytical overview'})).toBeTruthy();
 choose('Inspecting case','Exploratory 1');expect(screen.getByText('Prepared grid')).toBeTruthy();click('Test this case’s sensitivity');expect(screen.getByRole('heading',{name:'9% WACC / 2.5% growth'})).toBeTruthy();click('← Return to overview');await waitFor(()=>expect(document.activeElement).toBe(screen.getByRole('button',{name:'Test this case’s sensitivity'})));
 choose('Inspecting case','Base');expect(within(screen.getByRole('region',{name:'Your valuation'})).getByText('Prepared illustration')).toBeTruthy();click('Explain this price');expect(screen.getByText('annual revenue growth for five years')).toBeTruthy();
});
it('does not reattribute a stored reverse result when another case is selected',()=>{
 render(<Prototype/>);guided();click('Explain this price');click('Preview implied revenue growth');fireEvent.click(screen.getByRole('tab',{name:/Scenarios/}));click('Create Bear from Base');fireEvent.click(screen.getByRole('tab',{name:/Reverse DCF/}));expect(screen.queryByText('annual revenue growth for five years')).toBeNull();choose('Inspecting case','Base');expect(screen.getByText('annual revenue growth for five years')).toBeTruthy();
});
it('keeps independent reverse targets on shared-price edits and stales a shared target',()=>{
 render(<Prototype/>);guided();click('Explain this price');click('Preview implied revenue growth');choose('Comparison price (USD/share)','26');expect(screen.getByRole('heading',{name:'Reverse result is stale'})).toBeTruthy();click('Use $25 target');click('Preview implied revenue growth');choose('Comparison price (USD/share)','27');expect(screen.getByText('annual revenue growth for five years')).toBeTruthy();expect(screen.getByText('independent override')).toBeTruthy();
});
it('uses shared price for Explain this price while review restores an independent EV target',()=>{
 render(<Prototype/>);guided();click('Explain this price');click('Use USD2,500m EV target');click('Preview implied revenue growth');click('← Return to overview');choose('Comparison price (USD/share)','26');click('Review price expectations');expect(screen.getByLabelText('Enterprise-value target (USD millions)').getAttribute('value')).toBe('2500');expect(screen.getByText('annual revenue growth for five years')).toBeTruthy();click('← Return to overview');click('Explain this price');expect(screen.getByLabelText('Price to explain (USD/share)').getAttribute('value')).toBe('26');expect(screen.getByText('shared comparison price')).toBeTruthy();expect(screen.queryByText('annual revenue growth for five years')).toBeNull();
});
it('reports unsupported analysis attempts honestly in the overview and keeps an unperformed grid explicit',()=>{
 render(<Prototype/>);guided();click('Explain this price');choose('Price to explain (USD/share)','37');click('Preview implied revenue growth');click('← Return to overview');expect(screen.getByText('Not calculated · unsupported fixture')).toBeTruthy();expect(screen.getByText('Not performed')).toBeTruthy();click('Test this case’s sensitivity');choose('WACC start (%)','8');click('Preview grid');click('← Return to overview');expect(screen.getAllByText('Not calculated · unsupported fixture')).toHaveLength(2);
});
it('matches each exact reverse-derived forward reference to the prepared reverse solution',()=>{
 for(const r of fixtures.reverse.filter(r=>r.status==='SUCCESS')){
  const s=initialWorkspace();s.cases.Base.inputs=structuredClone(r.inputs);const variant=variantFor(impliedInputs(s.cases.Base,r.growth!))!;
  expect(variant).toBeTruthy();expect(variant.result).toEqual(r.result);
 }
});

it('clears a previous-case action notice when inspecting a sibling without changing either case',()=>{
 render(<Prototype/>);guided();click('Compare scenarios');click('Create Bear from Base');click('Preview valuation');expect(screen.getByText('Illustrative preview loaded for Bear.')).toBeTruthy();click('Inspect Base');expect(screen.queryByText('Illustrative preview loaded for Bear.')).toBeNull();expect(screen.getByLabelText('Revenue growth (%)').getAttribute('value')).toBe('10');click('Inspect Bear');expect(screen.getByLabelText('Revenue growth (%)').getAttribute('value')).toBe('10');
});
