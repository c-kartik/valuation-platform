import {it,expect,vi} from 'vitest';
import {render,screen} from '@testing-library/react';
import {BridgePanel} from './BridgePanel';
import {emptyEquity} from '../equity';
it.each([['ev','enterprise value'],['equity','equity and value per share'],['scenarios','scenario comparison'],['sensitivity','sensitivity grid'],['reverse','reverse DCF']])('identifies the actual shared in-flight %s action after navigation', (busy,label)=>{
 render(<BridgePanel values={emptyEquity()} outcome={{phase:'empty',result:null,errors:{},failure:''}} anchorDate="2025-12-31" operatingCurrent={true} busy={busy} edit={vi.fn()} calculate={vi.fn()} cancel={vi.fn()}/>);
 expect(screen.getByRole('status').textContent).toBe(`Calculating ${label}…`);
 expect((screen.getByRole('button',{name:'Calculate value per share'}) as HTMLButtonElement).disabled).toBe(true);
});
