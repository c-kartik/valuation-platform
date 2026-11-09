import {beforeEach,it,expect,vi} from 'vitest';
import {render,screen,fireEvent,waitFor} from '@testing-library/react';
import {PlatformApp,preparedCompanies} from './PlatformApp';
import type {Catalog} from '../model';
import type {request} from '../api';
vi.mock('./Workspace',()=>({Workspace:({initialCompany,onHome,onCompanyChange}:{initialCompany:string;onHome:()=>void;onCompanyChange:(s:string)=>void})=><div><h1>Workspace {initialCompany}</h1><button onClick={onHome}>All companies</button><button onClick={()=>onCompanyChange('META')}>Switch Meta</button></div>}));
const catalog={entries:['GOOGL','AAPL','META'].map(company=>({company,kind:company.toLowerCase(),template:{}}))} as Catalog;
const loader=(value=catalog)=>vi.fn(async()=>value) as unknown as typeof request;
beforeEach(()=>window.history.replaceState(null,'','/valuation/'));
it('loads only the catalog on landing and counts supported companies from the catalog',async()=>{
 const load=loader();render(<PlatformApp load={load}/>);
 expect(await screen.findByText('Explore 3 companies')).toBeTruthy();
 expect(screen.getByRole('combobox').getAttribute('placeholder')).toBe('Search 3 companies by name or ticker');
 expect(screen.getByRole('region',{name:'Suggested companies'}).querySelectorAll('a')).toHaveLength(3);
 expect(screen.queryByText(/Workspace/)).toBeNull();expect(load).toHaveBeenCalledTimes(1);
 expect(preparedCompanies({entries:[...catalog.entries,catalog.entries[0],{company:'BAD',kind:'bad'}]} as Catalog)).toHaveLength(3);
});
it('uses a dynamic count for a smaller catalog',async()=>{
 render(<PlatformApp load={loader({...catalog,entries:catalog.entries.slice(0,1)})}/>);
 expect(await screen.findByText('Explore 1 company')).toBeTruthy();expect(screen.getByRole('combobox').getAttribute('placeholder')).toContain('1 company');
});
it('opens the suggested company, maintains URL selection and supports returning to the landing page',async()=>{
 render(<PlatformApp load={loader()}/>);fireEvent.click(await screen.findByRole('link',{name:/AAPL Apple/}));
 expect(await screen.findByText('Workspace AAPL')).toBeTruthy();expect(window.location.search).toBe('?company=AAPL');
 fireEvent.click(screen.getByRole('button',{name:'Switch Meta'}));expect(await screen.findByText('Workspace META')).toBeTruthy();
 fireEvent.click(screen.getByRole('button',{name:'All companies'}));expect(await screen.findByText('Explore 3 companies')).toBeTruthy();expect(window.location.search).toBe('');
});
it('filters and selects through the keyboard without loading an unrelated company',async()=>{
 const load=loader();render(<PlatformApp load={load}/>);await screen.findByText('Explore 3 companies');const input=screen.getByRole('combobox');
 fireEvent.focus(input);expect(screen.getAllByRole('option')).toHaveLength(3);fireEvent.change(input,{target:{value:'ap'}});expect(screen.getAllByRole('option')).toHaveLength(1);
 fireEvent.keyDown(input,{key:'Enter'});expect(await screen.findByText('Workspace AAPL')).toBeTruthy();expect(load).toHaveBeenCalledTimes(1);
});
it('honors direct links and popstate while preserving unrelated query parameters',async()=>{
 window.history.replaceState(null,'','/valuation/?engine=browser&company=AAPL');render(<PlatformApp load={loader()}/>);
 expect(await screen.findByText('Workspace AAPL')).toBeTruthy();
 window.history.replaceState(null,'','/valuation/?engine=browser&company=META');fireEvent.popState(window);expect(await screen.findByText('Workspace META')).toBeTruthy();
 fireEvent.click(screen.getByRole('button',{name:'All companies'}));await screen.findByText('Explore 3 companies');expect(window.location.search).toBe('?engine=browser');
});
it('rejects an unsupported ticker and offers retry after catalog failure',async()=>{
 window.history.replaceState(null,'','/valuation/?company=UNKNOWN');let failed=true;
 const load=vi.fn(async()=>{if(failed)throw Error('offline');return catalog;}) as unknown as typeof request;render(<PlatformApp load={load}/>);
 const retry=await screen.findByRole('button',{name:'Retry company list'});failed=false;fireEvent.click(retry);
 await waitFor(()=>expect(screen.getByRole('status').textContent).toContain('UNKNOWN is not in the prepared company list'));
 expect(screen.queryByText(/Workspace/)).toBeNull();
});
