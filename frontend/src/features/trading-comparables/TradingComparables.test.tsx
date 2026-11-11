import {act,fireEvent,render,screen,waitFor,within} from '@testing-library/react';
import {afterEach,describe,expect,it,vi} from 'vitest';
import raw from '../../../public/features/trading-comparables/GOOGL.json';
import TradingComparables from './TradingComparables';
import {TradingComparablesFeature,comparablesAvailable} from './index';
import {tradingComparables} from './config';
import {fetchComparables,validateComparables} from './client';
import {ChapterBand} from '../../workspace/ChapterBand';
import type {ComparablesPackage} from './types';
const data=()=>validateComparables(structuredClone(raw),'GOOGL');
afterEach(()=>vi.unstubAllGlobals());

it('shows actual direct cloud/advertising revenue, same-filing growth and explicit proxy boundaries',async()=>{
 render(<TradingComparables ticker="GOOGL" load={vi.fn().mockResolvedValue(data())}/>);
 const cloud=await screen.findByRole('article',{name:'Google Cloud comparison'});
 expect(cloud.textContent).toContain('$30.71B');expect(cloud.textContent).toContain('+102.6%');expect(cloud.textContent).toContain('Workspace');
 expect(screen.getByRole('article',{name:'AWS comparison'}).textContent).toContain('+39.3%');
 const azure=screen.getByRole('article',{name:'Azure comparison'});expect(azure.textContent).toContain('$33.16B');expect(azure.textContent).toContain('Not disclosed');
 expect(screen.getByRole('article',{name:'Meta Ads comparison'}).textContent).toContain('+25.9%');
 expect(screen.getByRole('article',{name:'Reddit Ads comparison'}).textContent).toContain('+54.2%');
 expect(screen.getByRole('article',{name:'Pinterest comparison'}).textContent).toContain('proxy');
 const table=screen.getByRole('table',{name:'Google advertising revenue and growth'});expect(table.textContent).toContain('+12.0%');expect(table.textContent).toContain('+1.4%');
});
it('keeps peer selection, sources and all three views inside its own container',async()=>{
 render(<TradingComparables ticker="GOOGL" load={vi.fn().mockResolvedValue(data())}/>);
 await screen.findByRole('table',{name:'Peer financial comparison'});
 fireEvent.click(screen.getByRole('button',{name:/Reddit RDDT/}));
 expect(screen.getByRole('region',{name:'Selected peer financial detail'}).textContent).toContain('Smaller, faster-growing');
 fireEvent.click(screen.getByRole('button',{name:'Business comparisons'}));
 expect(screen.getByRole('table',{name:'Reported services profitability'}).textContent).toContain('Meta Reality Labs');
 fireEvent.click(screen.getByRole('button',{name:'Valuation & inputs'}));
 expect(screen.getByRole('heading',{name:'Not selected'})).toBeTruthy();
 expect(screen.getByRole('table',{name:'Reported balance candidates'}).textContent).toContain('0.98');
 fireEvent.click(screen.getByRole('button',{name:'Peer financials'}));
 expect(screen.getByRole('button',{name:/Reddit RDDT/}).getAttribute('aria-pressed')).toBe('true');
});
it('handles data failure and explicit retry without an API or DCF action',async()=>{
 const load=vi.fn().mockRejectedValueOnce(new Error('offline')).mockResolvedValueOnce(data());
 render(<TradingComparables ticker="GOOGL" load={load}/>);
 fireEvent.click(await screen.findByRole('button',{name:'Retry comparables'}));
 await screen.findByRole('article',{name:'Google Cloud comparison'});expect(load).toHaveBeenCalledTimes(2);
});
it('aborts loading on disconnect and ignores a late source response',async()=>{
 let finish!:(d:ComparablesPackage)=>void;let signal:AbortSignal|undefined;
 const load=vi.fn((_ticker:string,s?:AbortSignal)=>{signal=s;return new Promise<ComparablesPackage>(resolve=>{finish=resolve;});});
 const view=render(<TradingComparables ticker="GOOGL" load={load}/>);view.unmount();
 expect(signal?.aborted).toBe(true);await act(async()=>finish(data()));expect(screen.queryByRole('heading',{name:'Trading comparables'})).toBeNull();
});
it('one disconnect flag removes feature mounting, data requests and valuation-band navigation',()=>{
 const fetch=vi.fn();vi.stubGlobal('fetch',fetch);tradingComparables.enabled=false;
 try {
  render(<><ChapterBand chapter="valuation" comparables={comparablesAvailable('GOOGL')}/><TradingComparablesFeature ticker="GOOGL"/></>);
  expect(screen.queryByRole('link',{name:'Trading comparables'})).toBeNull();
  expect(document.getElementById('company-trading-comparables')).toBeNull();expect(fetch).not.toHaveBeenCalled();
  expect(screen.getByRole('link',{name:'DCF'})).toBeTruthy();
 } finally {tradingComparables.enabled=true;}
});
it('unsupported company has no comparables mount or navigation',()=>{
 render(<><ChapterBand chapter="valuation" comparables={comparablesAvailable('AAPL')}/><TradingComparablesFeature ticker="AAPL"/></>);
 expect(document.getElementById('company-trading-comparables')).toBeNull();expect(screen.queryByRole('link',{name:'Trading comparables'})).toBeNull();
});
it('groups section 6 with section 5 in the valuation chapter',()=>{
 render(<ChapterBand chapter="valuation" comparables={comparablesAvailable('GOOGL')}/>);
 const nav=screen.getByRole('navigation',{name:'Valuation sections'});
 expect(within(nav).getByRole('link',{name:'Trading comparables'}).getAttribute('href')).toBe('#company-trading-comparables');expect(screen.getByText('05–06 / Valuation methods')).toBeTruthy();
});
describe('data boundary',()=>{
 it('rejects market figures instead of silently introducing a default',()=>{const d=structuredClone(raw);(d.market as Record<string,unknown>).exit_default=15;expect(()=>validateComparables(d,'GOOGL')).toThrow();});
 it('rejects a mismatched issuer and incorrect growth',()=>{expect(()=>validateComparables(raw,'META')).toThrow();const d=structuredClone(raw);d.growth.GOOGL_cloud.growth=.2;expect(()=>validateComparables(d,'GOOGL')).toThrow();});
 it('uses only the isolated static path and passes cancellation',async()=>{const signal=new AbortController().signal;const fetch=vi.fn().mockResolvedValue({ok:true,json:async()=>raw});vi.stubGlobal('fetch',fetch);await fetchComparables('GOOGL',signal);expect(fetch).toHaveBeenCalledWith('/features/trading-comparables/GOOGL.json',{signal});});
});
