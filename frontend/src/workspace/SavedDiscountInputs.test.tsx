import {it,expect,vi} from 'vitest';
import {render,screen,fireEvent,act} from '@testing-library/react';
import {SavedDiscountInputs} from './SavedDiscountInputs';
import {request} from '../api';
const hash='a'.repeat(64);
function snapshot(ticker='AAPL'){
 return {schema_version:'saved-discount-inputs-v1',ticker,economic_hash:hash,status:'CONFIGURED_CONVENTION',cost_of_equity:'0.08935',cost_of_equity_percent:'8.935',base_wacc:'0.0827275',information_review:'2026-11-02',model_origin:'2025-09-27',automatic_adoption:false,scenario_wacc_offset_applied_to_cost_of_equity:false,
 operands:{risk_free:'0.0505',erp:'0.037',beta:'1.05',spread:'0.006',equity_weight:'0.85',debt_weight:'0.15',tax_shield:'0.2'},sources:[{id:'treasury',title:'Treasury snapshot',url:'https://home.treasury.gov/fixture',sha256:'b'.repeat(64)},{id:'erp',title:'ERP snapshot',url:'https://pages.stern.nyu.edu/fixture',sha256:'c'.repeat(64)}],observed_macro_inputs:[{key:'treasury_10y',end:'2026-10-28',value:'0.0505'},{key:'implied_erp',end:'2026-10-01',value:'0.037'}],limitations:['Configured beta and target weights are assumptions.']};
}
it('loads only on opening, displays dated sources, and requires explicit adoption',async()=>{
 const choose=vi.fn(),load=vi.fn(async()=>snapshot()) as unknown as typeof request;
 const view=render(<SavedDiscountInputs ticker="AAPL" profileHash={hash} active={false} choose={choose} load={load}/>);expect(load).not.toHaveBeenCalled();
 view.rerender(<SavedDiscountInputs ticker="AAPL" profileHash={hash} active choose={choose} load={load}/>);
 const use=await screen.findByRole('button',{name:'Use saved CAPM cost of equity (8.94%)'});expect(choose).not.toHaveBeenCalled();
 fireEvent.click(use);expect(choose).toHaveBeenCalledWith('8.935');expect(screen.getByText(/2026-10-28/)).toBeTruthy();expect(screen.getByRole('link',{name:'Treasury snapshot'}).getAttribute('href')).toMatch(/^https:/);
});
it('rejects mismatched profile or ticker without adopting',async()=>{
 const choose=vi.fn(),load=vi.fn(async()=>snapshot('META')) as unknown as typeof request;
 render(<SavedDiscountInputs ticker="AAPL" profileHash={hash} active choose={choose} load={load}/>);
 await screen.findByText(/could not be matched/);expect(choose).not.toHaveBeenCalled();expect(screen.queryByRole('button',{name:/Use saved CAPM/})).toBeNull();
});
it('never resurrects a late suggestion after the issuer changes',async()=>{
 let resolve!:(value:unknown)=>void;const choose=vi.fn();
 const load=vi.fn((path:string)=>path.endsWith('AAPL')?new Promise(r=>resolve=r):Promise.resolve(snapshot('META'))) as unknown as typeof request;
 const view=render(<SavedDiscountInputs ticker="AAPL" profileHash={hash} active choose={choose} load={load}/>);
 view.rerender(<SavedDiscountInputs ticker="META" profileHash={hash} active choose={choose} load={load}/>);await screen.findByRole('button',{name:/Use saved CAPM/});
 await act(async()=>resolve(snapshot('AAPL')));fireEvent.click(screen.getByRole('button',{name:/Use saved CAPM/}));expect(choose).toHaveBeenCalledTimes(1);
});
it('a stale or missing saved rate offers manual review instead of a replacement',async()=>{
 const choose=vi.fn(),load=vi.fn(async()=>({...snapshot(),status:'UNAVAILABLE',cost_of_equity:null,cost_of_equity_percent:null,sources:[],observed_macro_inputs:[]})) as unknown as typeof request;
 render(<SavedDiscountInputs ticker="AAPL" profileHash={hash} active choose={choose} load={load}/>);
 await screen.findByText(/missing, incompatible or stale/);expect(choose).not.toHaveBeenCalled();expect(screen.queryByRole('button',{name:/Use saved CAPM/})).toBeNull();
});
