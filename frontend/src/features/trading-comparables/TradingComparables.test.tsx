import {act,fireEvent,render,screen,waitFor,within} from '@testing-library/react';
import {afterEach,describe,expect,it,vi} from 'vitest';
import raw from '../../../public/features/trading-comparables/GOOGL.json';
import apple from '../../../public/features/trading-comparables/AAPL.json';
import meta from '../../../public/features/trading-comparables/META.json';
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
 render(<><ChapterBand chapter="valuation" comparables={comparablesAvailable('COST')}/><TradingComparablesFeature ticker="COST"/></>);
 expect(document.getElementById('company-trading-comparables')).toBeNull();expect(screen.queryByRole('link',{name:'Trading comparables'})).toBeNull();
});
it('Apple uses PC segments and services references with their actual dates and missing product profit',async()=>{
 render(<TradingComparables ticker="AAPL" load={vi.fn().mockResolvedValue(validateComparables(apple,'AAPL'))}/>);
 const mac=await screen.findByRole('article',{name:'Apple Mac comparison'});expect(mac.textContent).toContain('$10.79B');expect(mac.textContent).toContain('2026-09-26');expect(mac.textContent).toContain('Not disclosed');
 const dell=screen.getByRole('article',{name:'Dell Client Solutions comparison'});expect(dell.textContent).toContain('2026-07-31');expect(dell.textContent).toContain('$15.03B');
 expect(screen.getByRole('article',{name:'HP Personal Systems comparison'}).textContent).toContain('$11.77B');
 expect(screen.getByRole('article',{name:'Apple Services comparison'}).textContent).toContain('$31.57B');
 const peers=screen.getByRole('table',{name:'Peer financial comparison'});expect(peers.textContent).toContain('Dell');expect(peers.textContent).not.toContain('Reality Labs');
 fireEvent.click(screen.getByRole('button',{name:'Business comparisons'}));
 expect(screen.getByRole('table',{name:'Apple revenue mix reconciliation'}).textContent).toContain('114.48');
});
it('Meta compares social/advertising businesses and retains losses and proxy labels',async()=>{
 render(<TradingComparables ticker="META" load={vi.fn().mockResolvedValue(validateComparables(meta,'META'))}/>);
 expect((await screen.findByRole('article',{name:'Meta Ads comparison'})).textContent).toContain('$63.06B');
 expect(screen.getByRole('article',{name:'Snap Ads comparison'}).textContent).toContain('$1.37B');
 expect(screen.getByRole('article',{name:'Pinterest comparison'}).textContent).toContain('proxy');
 expect(screen.queryByRole('article',{name:'AWS comparison'})).toBeNull();
 const peers=screen.getByRole('table',{name:'Peer financial comparison'});expect(peers.textContent).toContain('-0.12');
 fireEvent.click(screen.getByRole('button',{name:'Business comparisons'}));
 expect(screen.getByRole('table',{name:'Meta operating segments'}).textContent).toContain('-4.13');
});
it('a target switch rejects an outstanding Apple response and resets selected peer to Meta',async()=>{
 let finish!:(d:ComparablesPackage)=>void;const load=vi.fn((ticker:string)=>ticker==='AAPL'?new Promise<ComparablesPackage>(resolve=>{finish=resolve;}):Promise.resolve(validateComparables(meta,'META')));
 const view=render(<TradingComparables ticker="AAPL" load={load}/>);view.rerender(<TradingComparables ticker="META" load={load}/>);
 await screen.findByRole('article',{name:'Meta Ads comparison'});await act(async()=>finish(validateComparables(apple,'AAPL')));
 expect(screen.queryByRole('article',{name:'Apple Mac comparison'})).toBeNull();expect(screen.getByRole('region',{name:'Selected peer financial detail'}).textContent).toContain('META');
});
it('the same global flag disconnects every supported target',()=>{
 tradingComparables.enabled=false;try{for(const ticker of ['GOOGL','AAPL','META']){expect(comparablesAvailable(ticker)).toBe(false);}}finally{tradingComparables.enabled=true;}
});
it('groups section 6 with section 5 in the valuation chapter',()=>{
 render(<ChapterBand chapter="valuation" comparables={comparablesAvailable('GOOGL')}/>);
 const nav=screen.getByRole('navigation',{name:'Valuation sections'});
 expect(within(nav).getByRole('link',{name:'Trading comparables'}).getAttribute('href')).toBe('#company-trading-comparables');expect(screen.getByText('05–06 / Valuation methods')).toBeTruthy();
});
describe('data boundary',()=>{
 it('rejects market figures instead of silently introducing a default',()=>{const d=structuredClone(raw);(d.market as Record<string,unknown>).exit_default=15;expect(()=>validateComparables(d,'GOOGL')).toThrow();});
 it('rejects a mismatched issuer and incorrect growth',()=>{expect(()=>validateComparables(raw,'META')).toThrow();const d=structuredClone(raw);d.growth.GOOGL_cloud.growth=.2;expect(()=>validateComparables(d,'GOOGL')).toThrow();});
 it('rejects substituting Alphabet peers into an Apple package',()=>{const d=structuredClone(apple);d.peer_order[1]='META';expect(()=>validateComparables(d,'AAPL')).toThrow();});
 it('uses only the isolated static path and passes cancellation',async()=>{const signal=new AbortController().signal;const fetch=vi.fn().mockResolvedValue({ok:true,json:async()=>raw});vi.stubGlobal('fetch',fetch);await fetchComparables('GOOGL',signal);expect(fetch).toHaveBeenCalledWith('/features/trading-comparables/GOOGL.json',{signal});});
});
