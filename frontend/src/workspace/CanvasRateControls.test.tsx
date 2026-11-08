import {it,expect,vi} from 'vitest';
import {render,screen,fireEvent,waitFor} from '@testing-library/react';
import {CanvasRateControls} from './CanvasRateControls';
import {makeDraft} from '../model';
import type {CaseDoc,Draft} from '../model';
import fixture from '../../../examples/valuation/synthetic-base.json';
it('stages a rate for workbook export and submits only the intended paths through the existing action on explicit apply',async()=>{
 const draft=makeDraft(fixture as CaseDoc),copy=structuredClone(draft),submit=vi.fn(async(_draft:Draft,_paths:string[])=>true),pending=vi.fn();render(<CanvasRateControls draft={draft} busy={false} submit={submit} onPending={pending} edit={()=>{}}/>);
 fireEvent.change(screen.getByRole('slider',{name:'Quick WACC'}),{target:{value:'20.25'}});expect(submit).not.toHaveBeenCalled();expect(pending.mock.calls.at(-1)![0]).toMatchObject({kind:'model',draft:{rates:{wacc:'20.25'}},touched:['wacc']});
 fireEvent.click(screen.getByRole('button',{name:'Apply rate changes'}));await waitFor(()=>expect(submit).toHaveBeenCalledTimes(1));expect(submit.mock.calls[0][0].rates.terminal_growth).toBe(draft.rates.terminal_growth);expect(submit.mock.calls[0][1]).toEqual(['wacc']);expect(draft).toEqual(copy);
});
it('uses the existing required-input validation before submitting and preserves an incomplete source draft',async()=>{
 const draft=makeDraft(fixture as CaseDoc);draft.rates.wacc='4';draft.rates.terminal_growth='3';draft.rates['forecast_years[0].operating_margin']='';const submit=vi.fn(async(_draft:Draft,_paths:string[])=>true);render(<CanvasRateControls draft={draft} busy={false} submit={submit} onPending={()=>{}} edit={()=>{}}/>);
 fireEvent.change(screen.getByRole('slider',{name:'Quick terminal growth'}),{target:{value:'5'}});fireEvent.click(screen.getByRole('button',{name:'Apply rate changes'}));await screen.findByRole('alert');expect(submit).not.toHaveBeenCalled();expect(draft.rates.terminal_growth).toBe('3');
});
it('blocks duplicate operations while busy and clears unapplied rates when the source changes',()=>{
 const draft=makeDraft(fixture as CaseDoc),submit=vi.fn(async(_draft:Draft,_paths:string[])=>true),pending=vi.fn(),view=render(<CanvasRateControls draft={draft} busy={false} submit={submit} onPending={pending} edit={()=>{}}/>);
 fireEvent.change(screen.getByRole('slider',{name:'Quick WACC'}),{target:{value:'20'}});const next=structuredClone(draft);next.rates.wacc='18';view.rerender(<CanvasRateControls draft={next} busy submit={submit} onPending={pending} edit={()=>{}}/>);expect(pending.mock.calls.at(-1)![0]).toBeNull();expect((screen.getByRole('slider',{name:'Quick WACC'}) as HTMLInputElement).value).toBe('18');expect((screen.getByRole('button',{name:'Apply rate changes'}) as HTMLButtonElement).disabled).toBe(true);
});
