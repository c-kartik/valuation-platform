import {it,expect,vi} from 'vitest';
import {render,screen,fireEvent,waitFor} from '@testing-library/react';
import {EquityStep} from './EquityStep';
import {ApiError,request} from './api';
import {makeDraft} from './model';
import type {CaseDoc,Result} from './model';
import fixture from '../../examples/valuation/synthetic-base.json';
const draft=()=>makeDraft(fixture as CaseDoc);
const ev=()=>({stage_b:{enterprise_value:'77.5770603520'}} as Result);
function reply(b:Result):Result{return {...b,stage_c:{stage_b:{enterprise_value:'77.5770603520'},eligible_assets:'12',financing_claims:'20',other_equity_claims:'3',equity_value:'66.5770603520',valuation_shares:'4',value_per_share:'16.6442650880',inputs:{shares:{class_id:'issued: Synthetic common',observation_date:'2025-12-31',rationale:'Synthetic manual population; no automatic dilution'},observations:[{observation_id:'unknown',disposition:'OMISSION',rationale:'Unbounded unidentified claims, not zero'}]},contributions:[{component:{component_id:'assets'},signed_contribution:'12'},{component:{component_id:'financing'},signed_contribution:'-20'},{component:{component_id:'claims'},signed_contribution:'-3'}]}};}
const set=(name:string,value:string)=>fireEvent.change(screen.getByLabelText(name),{target:{value}});
const run=()=>fireEvent.click(screen.getByRole('button',{name:'Calculate value per share'}));
function fill(){
 fireEvent.click(screen.getByText('Add cash, debt & shares'));
 set('Eligible cash & investments (USD millions)','0.000012');set('Debt & financing obligations (USD millions)','0.000020');set('Other claims / adjustments','amount');set('Other claims (USD millions)','0.000003');set('Shares outstanding (millions of shares)','0.000004');set('Share observation date','2025-12-31');
 fireEvent.click(screen.getByText('Coverage, classes & awards'));
 set('Eligible-asset coverage','selected');set('Financing coverage','selected');set('Other-claims coverage','selected');set('Share population','issued');set('Included share class(es)','Synthetic common');set('Class treatment','single_common_class');set('Existing awards','none');fireEvent.click(screen.getByLabelText(/I declare these amounts/));
}
it('keeps bridge advanced sections initially collapsed, all numbers blank and does not request anything',()=>{
 const load=vi.fn();render(<EquityStep draft={draft()} evResult={ev()} operatingStale={false} load={load as typeof request}/>);
 for(const name of ['Add cash, debt & shares','Coverage, classes & awards','Component details & overlap references'])expect(screen.getByText(name).closest('details')?.open).toBe(false);
 expect((screen.getByLabelText('Eligible cash & investments (USD millions)') as HTMLInputElement).value).toBe('');expect(load).not.toHaveBeenCalled();
});
it('blocks unassessed claims/declarations, focuses a useful error and preserves EV-only scope',async()=>{
 const load=vi.fn(),d=draft();render(<EquityStep draft={d} evResult={ev()} operatingStale={false} load={load as typeof request}/>);
 fireEvent.click(screen.getByText('Add cash, debt & shares'));run();await screen.findByRole('region',{name:'Equity input issues'});expect(load).not.toHaveBeenCalled();expect(d.doc.schema_version).toBe('investor-case-v1');
 await waitFor(()=>expect(document.activeElement).toBe(screen.getByLabelText('Eligible cash & investments (USD millions)')));
});
it('sends anonymous manual Stage C only on explicit action and shows signed server reconciliation and omissions',async()=>{
 const b=ev(),load=vi.fn(async()=>reply(b));render(<EquityStep draft={draft()} evResult={b} operatingStale={false} load={load as unknown as typeof request}/>);fill();expect(load).not.toHaveBeenCalled();run();
 await screen.findByRole('heading',{name:'Provisional equity reference'});expect(load.mock.calls[0]).toMatchObject(['/api/v1/cases/run',{schema_version:'investor-case-v2',calculation_scope:'EQUITY_PER_SHARE',preparation:{provenance:'ANONYMOUS_INVESTOR',notes:null}},expect.anything()]);
 expect(screen.getByText('− Financing obligations (USD)')).toBeTruthy();expect(screen.getByText('$66.58')).toBeTruthy();expect(screen.getByText('16.64')).toBeTruthy();expect(screen.getByText(/per issued share/)).toBeTruthy();expect(screen.getByText('Unbounded unidentified claims, not zero')).toBeTruthy();
 expect(screen.queryByText(/STALE EQUITY/)).toBeNull();
});
it('retains raw bridge edits across closing, marks only equity stale and invalidates it on a new EV',async()=>{
 const b=ev(),load=vi.fn(async()=>reply(b));const {rerender}=render(<EquityStep draft={draft()} evResult={b} operatingStale={false} load={load as unknown as typeof request}/>);fill();run();await screen.findByText('16.64');
 set('Eligible cash & investments (USD millions)','0.000013');expect(screen.getByText(/STALE EQUITY/)).toBeTruthy();expect(screen.queryByText(/Operating inputs changed/)).toBeNull();
 fireEvent.click(screen.getByText('Add cash, debt & shares'));fireEvent.click(screen.getByText('Add cash, debt & shares'));expect((screen.getByLabelText('Eligible cash & investments (USD millions)') as HTMLInputElement).value).toBe('0.000013');expect(load).toHaveBeenCalledTimes(1);
 run();await waitFor(()=>expect(screen.queryByText(/STALE EQUITY/)).toBeNull());
 rerender(<EquityStep draft={draft()} evResult={ev()} operatingStale={false} load={load as unknown as typeof request}/>);await screen.findByText(/STALE EQUITY/);
 rerender(<EquityStep draft={draft()} evResult={b} operatingStale={true} load={load as unknown as typeof request}/>);expect((screen.getByRole('button',{name:'Calculate value per share'}) as HTMLButtonElement).disabled).toBe(true);expect(screen.getByText(/Operating inputs changed/)).toBeTruthy();
});
it('rejects an old pending equity reply after bridge or operating edits',async()=>{
 const b=ev();let resolve!:(r:Result)=>void;const load=vi.fn(()=>new Promise<Result>(r=>{resolve=r;}));const {rerender}=render(<EquityStep draft={draft()} evResult={b} operatingStale={false} load={load as unknown as typeof request}/>);fill();run();
 set('Shares outstanding (millions of shares)','0.000008');resolve(reply(b));await waitFor(()=>expect(screen.queryByText('16.64')).toBeNull());
 run();rerender(<EquityStep draft={draft()} evResult={b} operatingStale={true} load={load as unknown as typeof request}/>);resolve(reply(b));await waitFor(()=>expect(screen.queryByText('16.64')).toBeNull());
});
it('recovers from service failure and maps invalid shares to field focus without clearing inputs',async()=>{
 const b=ev();let mode='service';const load=vi.fn(async()=>{if(mode==='service')throw new ApiError('busy','Service busy');if(mode==='domain')throw new ApiError('invalid_case','Invalid',['bridge.shares: Amount outside permitted sign domain']);return reply(b);});
 render(<EquityStep draft={draft()} evResult={b} operatingStale={false} load={load as unknown as typeof request}/>);fill();run();await screen.findByText('Another calculation is in progress. Your inputs are still here. Please retry shortly.');expect((screen.getByLabelText('Shares outstanding (millions of shares)') as HTMLInputElement).value).toBe('0.000004');
 mode='domain';run();await screen.findByRole('region',{name:'Equity input issues'});await waitFor(()=>expect(document.activeElement).toBe(screen.getByLabelText('Shares outstanding (millions of shares)')));expect(screen.queryByText('16.64')).toBeNull();mode='ok';run();await screen.findByText('16.64');
});
it('preserves negative equity/per-share display without treating it as fully diluted value',async()=>{
 const b=ev(),negative=reply(b);negative.stage_c!.equity_value='-20';negative.stage_c!.value_per_share='-5';const load=vi.fn(async()=>negative);
 render(<EquityStep draft={draft()} evResult={b} operatingStale={false} load={load as unknown as typeof request}/>);fill();run();await screen.findByText('−$20.00');expect(screen.getByText('-5.00')).toBeTruthy();expect(screen.getByText(/not fully diluted fair value/)).toBeTruthy();
});
it('expands advanced declarations for focused missing class errors and blocks incompatible awards',async()=>{
 const load=vi.fn();render(<EquityStep draft={draft()} evResult={ev()} operatingStale={false} load={load as typeof request}/>);fill();set('Class treatment','');fireEvent.click(screen.getByText('Coverage, classes & awards'));run();
 await waitFor(()=>expect(document.activeElement).toBe(screen.getByLabelText('Class treatment')));expect(screen.getByText('Coverage, classes & awards').closest('details')?.open).toBe(true);expect(load).not.toHaveBeenCalled();
 set('Class treatment','single_common_class');set('Existing awards','shares');run();await waitFor(()=>expect(document.activeElement).toBe(screen.getByLabelText('Share population')));expect(load).not.toHaveBeenCalled();
});

it('does not display a valid positive fractional share denominator as zero millions',async()=>{
 const b=ev(),fractional=reply(b);fractional.stage_c!.valuation_shares='0.1';fractional.stage_c!.value_per_share='665.770603520';
 render(<EquityStep draft={draft()} evResult={b} operatingStale={false} load={vi.fn(async()=>fractional) as unknown as typeof request}/>);fill();run();await screen.findByText('665.77');
 expect(screen.getByText('0.0000001')).toBeTruthy();expect(screen.queryByText('0.000000')).toBeNull();
});
it('opens a collapsed reference editor and associates an engine overlap error with its declaration',async()=>{
 const load=vi.fn(async()=>{throw new ApiError('invalid_case','Invalid',['bridge: Declared numeric population/forecast overlap']);});
 render(<EquityStep draft={draft()} evResult={ev()} operatingStale={false} load={load as unknown as typeof request}/>);fill();
 fireEvent.click(screen.getByText('Component details & overlap references'));set('Assets overlap references','financing');fireEvent.click(screen.getByText('Component details & overlap references'));run();
 await waitFor(()=>expect(document.activeElement).toBe(screen.getByLabelText('Assets overlap references')));expect(screen.getByText('Component details & overlap references').closest('details')?.open).toBe(true);
 expect(screen.getByLabelText('Assets overlap references').getAttribute('aria-invalid')).toBe('true');expect(screen.getByLabelText('Assets overlap references').getAttribute('aria-describedby')).toBe('equity.overlapAssets-error');
});
