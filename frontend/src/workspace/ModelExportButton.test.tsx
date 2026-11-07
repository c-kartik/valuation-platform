import {it,expect,vi,afterEach} from 'vitest';
import {render,screen,fireEvent,waitFor} from '@testing-library/react';
import {ModelExportButton} from './ModelExportButton';
import {writeModelWorkbook} from './modelWorkbook';
import {captureModelSnapshot} from './modelSnapshot';
import {createSession} from './useWorkspace';
import fixture from '../../../examples/valuation/synthetic-base.json';
import type {CaseDoc} from '../model';
vi.mock('./modelWorkbook',()=>({writeModelWorkbook:vi.fn()}));
afterEach(()=>{vi.restoreAllMocks();vi.mocked(writeModelWorkbook).mockReset();});
function setup(){
 const session=createSession(fixture as CaseDoc);
 const snapshot=vi.fn(()=>captureModelSnapshot({ticker:'AAPL',company_name:'Apple',selected_company:'aapl',selected_scenario:'Base',session,entry:null,analyst:{}}));
 const click=vi.spyOn(HTMLAnchorElement.prototype,'click').mockImplementation(()=>{});
 const urls=vi.spyOn(URL,'createObjectURL').mockReturnValue('blob:model-export-test');
 render(<ModelExportButton snapshot={snapshot}/>);return {session,snapshot,click,urls};
}
it('captures immediately, downloads XLSX and keeps later model edits out of the saved copy',async()=>{
 let finish!:(bytes:ArrayBuffer)=>void;vi.mocked(writeModelWorkbook).mockImplementation(()=>new Promise(resolve=>{finish=resolve;}));
 const {session,snapshot,click,urls}=setup();fireEvent.click(screen.getByRole('button',{name:'Download Excel'}));
 expect(snapshot).toHaveBeenCalledTimes(1);session.cases.Base.draft.rates.wacc='33';
 await waitFor(()=>expect(writeModelWorkbook).toHaveBeenCalledTimes(1));expect(vi.mocked(writeModelWorkbook).mock.calls[0][0].session.cases.Base.draft.rates.wacc).not.toBe('33');
 fireEvent.click(screen.getByRole('button',{name:'Preparing Excel…'}));expect(snapshot).toHaveBeenCalledTimes(1);
 finish(new ArrayBuffer(8));await waitFor(()=>expect(click).toHaveBeenCalledTimes(1));
 expect((urls.mock.calls[0][0] as Blob).type).toBe('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
 const anchor=click.mock.instances[0] as HTMLAnchorElement;expect(anchor.download).toMatch(/^AAPL-Base-assumptions-.*\.xlsx$/);expect(anchor.href).toBe('blob:model-export-test');
});
it('shows a retryable failure and never mutates inputs when Excel generation fails',async()=>{
 vi.mocked(writeModelWorkbook).mockRejectedValueOnce(Error('internal details')).mockResolvedValue(new ArrayBuffer(4));
 const {session,click}=setup(),before=JSON.stringify(session);fireEvent.click(screen.getByRole('button',{name:'Download Excel'}));
 expect((await screen.findByRole('alert')).textContent).toContain('Please try again');expect(screen.queryByText('internal details')).toBeNull();expect(click).not.toHaveBeenCalled();expect(JSON.stringify(session)).toBe(before);
 fireEvent.click(screen.getByRole('button',{name:'Download Excel'}));await waitFor(()=>expect(click).toHaveBeenCalledTimes(1));
});
