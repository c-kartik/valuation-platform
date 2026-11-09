import {it,expect,vi} from 'vitest';
import {render,screen,fireEvent,waitFor} from '@testing-library/react';
import googl from '../../public/research-data/GOOGL.json';
import apple from '../../public/research-data/AAPL.json';
import meta from '../../public/research-data/META.json';
import {QuarterlyOverview} from './QuarterlyOverview';
import {validateReport} from './model';
const fixtures:Record<string,unknown>={GOOGL:googl,AAPL:apple,META:meta};
const loader=async(ticker:string)=>validateReport(fixtures[ticker],ticker);
it('shows twenty actual fiscal quarters, preserves negative FCF, and synchronizes bridge selection',async()=>{
 render(<QuarterlyOverview ticker="GOOGL" loadReport={loader}/>);
 const chart=await screen.findByRole('slider',{name:'Explore historical quarters'});
 expect(chart.getAttribute('aria-valuemax')).toBe('19');
 expect(screen.queryByRole('combobox')).toBeNull();
 expect(document.querySelector('.qr-bridge')!.textContent).toContain('−$9.07B');
 fireEvent.keyDown(chart,{key:'Home'});
 expect(document.querySelector('.qr-bridge')!.textContent).toContain('FY2021 Q4');
 fireEvent.click(screen.getByRole('button',{name:'Margins'}));
 expect(screen.getByRole('img',{name:/Quarterly Operating margin, FCF margin; percent/})).toBeTruthy();
 expect(document.querySelector('.qr-stats')!.textContent).toContain('%');
});
it('loads each issuer independently and uses Apple fiscal dates',async()=>{
 const load=vi.fn(loader),view=render(<QuarterlyOverview ticker="GOOGL" loadReport={load}/>);
 await screen.findByRole('slider',{name:'Explore historical quarters'});
 view.rerender(<QuarterlyOverview ticker="AAPL" loadReport={load}/>);
 await waitFor(()=>expect(document.querySelector('.qr-readout-quarter')!.textContent).toContain('2026-09-26'));
 view.rerender(<QuarterlyOverview ticker="META" loadReport={load}/>);
 await screen.findByText(/FY2021-Q4–FY2026-Q3/);
 expect(load.mock.calls.map(c=>c[0])).toEqual(['GOOGL','AAPL','META']);
});
it('isolates unavailable reporting and permits retry without invoking a valuation',async()=>{
 const load=vi.fn(loader).mockRejectedValueOnce(Error('offline'));
 render(<QuarterlyOverview ticker="GOOGL" loadReport={load}/>);
 fireEvent.click(await screen.findByRole('button',{name:'Retry quarterly history'}));
 await screen.findByRole('slider',{name:'Explore historical quarters'});expect(load).toHaveBeenCalledTimes(2);
});
it('rejects wrong company, missing amounts and broken reconciliation; accepts all reviewed packages',()=>{
 for(const [ticker,data]of Object.entries(fixtures))expect(validateReport(data,ticker).rows).toHaveLength(20);
 expect(()=>validateReport(googl,'META')).toThrow();
 for(const value of [null,NaN,1]){const broken=structuredClone(googl);(broken.rows[0].values as Record<string,unknown>).cfo=value;expect(()=>validateReport(broken,'GOOGL')).toThrow();}
});
it('previews all metric values on pointer movement, restores selection on leave and pins on keyboard navigation',async()=>{
 render(<QuarterlyOverview ticker="GOOGL" loadReport={loader}/>);
 const chart=await screen.findByRole('slider',{name:'Explore historical quarters'});
 // Pointer coordinates in the full chart map to the nearest actual quarter.
 fireEvent(chart,new MouseEvent('pointermove',{bubbles:true,clientX:48,clientY:80}));
 expect(screen.getByRole('tooltip').textContent).toContain('FY2021 Q4');
 expect(document.querySelector('.qr-readout-quarter')!.textContent).toContain('exploring');
 expect(document.querySelector('.qr-bridge')!.textContent).toContain('FY2026 Q3');
 fireEvent.pointerLeave(chart);
 expect(screen.queryByRole('tooltip')).toBeNull();
 expect(document.querySelector('.qr-readout-quarter')!.textContent).toContain('FY2026 Q3');
 fireEvent.focus(chart);fireEvent.keyDown(chart,{key:'Home'});
 expect(chart.getAttribute('aria-valuenow')).toBe('0');
 expect(document.querySelector('.qr-bridge')!.textContent).toContain('FY2021 Q4');
 fireEvent.keyDown(chart,{key:'ArrowRight'});
 expect(screen.getByRole('tooltip').textContent).toContain('FY2022 Q1');
 expect(document.querySelector('.qr-readout-quarter')!.textContent).toContain('FY2022 Q1');
 fireEvent.keyDown(chart,{key:'End'});
 expect(chart.getAttribute('aria-valuenow')).toBe('19');
 fireEvent.keyDown(chart,{key:'Escape'});expect(screen.queryByRole('tooltip')).toBeNull();
});

it('toggles individual chart series while preserving at least one visible line',async()=>{
 render(<QuarterlyOverview ticker="GOOGL" loadReport={loader}/>);
 const revenue=await screen.findByRole('button',{name:'Toggle Revenue'});
 fireEvent.click(revenue);
 expect(revenue.getAttribute('aria-pressed')).toBe('false');
 expect(document.querySelectorAll('.qr-series')).toHaveLength(3);
 fireEvent.click(screen.getByRole('button',{name:'Toggle Operating cash flow'}));
 fireEvent.click(screen.getByRole('button',{name:'Toggle Cash capex'}));
 expect((screen.getByRole('button',{name:'Toggle Free cash flow'}) as HTMLButtonElement).disabled).toBe(true);
 fireEvent.click(revenue);expect(document.querySelectorAll('.qr-series')).toHaveLength(2);
});

it('rejects stale derived margins, mismatched fiscal labels and contradictory YTD operands',()=>{
 for(const mutate of [
  (p:typeof googl)=>{p.rows[0].values.operating_margin+=.01;},
  (p:typeof googl)=>{p.rows[0].values.fcf_margin+=.01;},
  (p:typeof googl)=>{p.rows[0].fiscal_year+=1;},
  (p:typeof googl)=>{p.rows[0].quarter=1;},
  (p:typeof googl)=>{p.rows[1].start='2022-01-02';},
  (p:typeof googl)=>{p.rows[0].evidence.cfo.operands[0].value+=1;},
  (p:typeof googl)=>{p.rows[0].evidence.cfo.operands[1].end='2021-09-29';},
 ]){const broken=structuredClone(googl);mutate(broken);expect(()=>validateReport(broken,'GOOGL')).toThrow();}
});
