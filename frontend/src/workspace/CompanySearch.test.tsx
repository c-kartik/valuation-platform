import {it,expect,vi} from 'vitest';
import {render,screen,fireEvent} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {CompanySearch} from './CompanySearch';
const companies=[{kind:'meta',company:'META',name:'Meta Platforms'},{kind:'googl',company:'GOOGL',name:'Alphabet'},{kind:'aapl',company:'AAPL',name:'Apple'},{kind:'msft',company:'MSFT',name:'Microsoft'}];
function setup(disabled=false){const onSelect=vi.fn();render(<><CompanySearch companies={companies} selected="googl" disabled={disabled} onSelect={onSelect}/><button>Outside</button></>);return {input:screen.getByRole('combobox',{name:'Company'}),onSelect};}
const tickers=()=>screen.queryAllByRole('option').map(e=>e.querySelector('strong')?.textContent);
it('shows exactly three suggestions on focus without selecting or loading a company',()=>{
 const {input,onSelect}=setup();expect((input as HTMLInputElement).value).toBe('GOOGL · Alphabet');
 fireEvent.focus(input);expect(tickers()).toEqual(['META','GOOGL','AAPL']);expect(input.getAttribute('aria-expanded')).toBe('true');expect(onSelect).not.toHaveBeenCalled();
});
it('updates on every letter, matches names without case sensitivity, and restores suggestions when cleared',()=>{
 const {input,onSelect}=setup();fireEvent.focus(input);
 for(const [query,expected] of [['m',['META','MSFT']],['me',['META']],['met',['META']],['meta',['META']],['p',['META','GOOGL','AAPL']],[' aPp ',['AAPL']],['',['META','GOOGL','AAPL']]] as const){
  fireEvent.change(input,{target:{value:query}});expect(tickers()).toEqual(expected);
 }
 expect(onSelect).not.toHaveBeenCalled();
});
it('prioritizes an exact ticker ahead of other partial matches',()=>{
 const {input}=setup();fireEvent.change(input,{target:{value:'MSFT'}});expect(tickers()).toEqual(['MSFT']);
});
it('supports keyboard selection and restores the selected label on Escape without changing company',async()=>{
 const user=userEvent.setup(),{input,onSelect}=setup();await user.click(input);await user.keyboard('{ArrowDown}{Enter}');
 expect(onSelect).toHaveBeenCalledWith('googl');expect(screen.queryByRole('listbox')).toBeNull();
 await user.click(input);await user.type(input,'apple');expect(tickers()).toEqual(['AAPL']);await user.keyboard('{Escape}');
 expect((input as HTMLInputElement).value).toBe('GOOGL · Alphabet');expect(onSelect).toHaveBeenCalledTimes(1);
 await user.click(input);expect(tickers()).toHaveLength(3);
});
it('selects by pointer and closes on outside click or Tab without accidental selection',async()=>{
 const user=userEvent.setup(),{input,onSelect}=setup();await user.click(input);await user.click(screen.getByRole('option',{name:/AAPL/}));
 expect(onSelect).toHaveBeenCalledWith('aapl');expect(screen.queryByRole('listbox')).toBeNull();
 await user.click(input);await user.click(screen.getByRole('button',{name:'Outside'}));expect(screen.queryByRole('listbox')).toBeNull();
 await user.click(input);await user.tab();expect(screen.queryByRole('listbox')).toBeNull();expect(onSelect).toHaveBeenCalledTimes(1);
});
it('handles no matches and disabled loading without selecting unsupported tickers',async()=>{
 const user=userEvent.setup(),{input,onSelect}=setup();await user.click(input);await user.type(input,'unknown');
 expect(screen.getByRole('status').textContent).toContain('No prepared dataset available');expect(input.hasAttribute('aria-activedescendant')).toBe(false);
 await user.keyboard('{ArrowDown}{Enter}');expect(onSelect).not.toHaveBeenCalled();
});
it('keeps the search disabled until the catalog is ready',async()=>{
 const user=userEvent.setup(),{input}=setup(true);await user.click(input);expect(screen.queryByRole('listbox')).toBeNull();expect((input as HTMLInputElement).disabled).toBe(true);
});
