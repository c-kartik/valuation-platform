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
 await screen.findByRole('combobox',{name:'Financial reporting quarter'});
 expect(screen.getAllByRole('option')).toHaveLength(20);
 expect(document.querySelector('.qr-bridge')!.textContent).toContain('−$9.07B');
 fireEvent.change(screen.getByRole('combobox'),{target:{value:'0'}});
 expect(document.querySelector('.qr-bridge')!.textContent).toContain('FY2021 Q4');
 fireEvent.click(screen.getByRole('button',{name:'Margins'}));
 expect(screen.getByRole('img',{name:/Quarterly Operating margin, FCF margin; percent/})).toBeTruthy();
 expect(document.querySelector('.qr-stats')!.textContent).toContain('%');
});
it('loads each issuer independently and uses Apple fiscal dates',async()=>{
 const load=vi.fn(loader),view=render(<QuarterlyOverview ticker="GOOGL" loadReport={load}/>);
 await screen.findByRole('combobox');
 view.rerender(<QuarterlyOverview ticker="AAPL" loadReport={load}/>);
 await waitFor(()=>expect(screen.getAllByRole('option').at(-1)!.textContent).toContain('2026-09-26'));
 view.rerender(<QuarterlyOverview ticker="META" loadReport={load}/>);
 await screen.findByText(/FY2021-Q4–FY2026-Q3/);
 expect(load.mock.calls.map(c=>c[0])).toEqual(['GOOGL','AAPL','META']);
});
it('isolates unavailable reporting and permits retry without invoking a valuation',async()=>{
 const load=vi.fn(loader).mockRejectedValueOnce(Error('offline'));
 render(<QuarterlyOverview ticker="GOOGL" loadReport={load}/>);
 fireEvent.click(await screen.findByRole('button',{name:'Retry quarterly history'}));
 await screen.findByRole('combobox');expect(load).toHaveBeenCalledTimes(2);
});
it('rejects wrong company, missing amounts and broken reconciliation; accepts all reviewed packages',()=>{
 for(const [ticker,data]of Object.entries(fixtures))expect(validateReport(data,ticker).rows).toHaveLength(20);
 expect(()=>validateReport(googl,'META')).toThrow();
 for(const value of [null,NaN,1]){const broken=structuredClone(googl);(broken.rows[0].values as Record<string,unknown>).cfo=value;expect(()=>validateReport(broken,'GOOGL')).toThrow();}
});
