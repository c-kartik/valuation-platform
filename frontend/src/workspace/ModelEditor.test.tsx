import {it,expect,vi} from 'vitest';
import {render,screen,fireEvent,waitFor,within} from '@testing-library/react';
import Decimal from 'decimal.js';
import {ModelEditor} from './ModelEditor';
import {createSession} from './useWorkspace';
import {buildRequest,percentageToFraction} from '../model';
import type {CaseDoc,Draft} from '../model';
import type {PreloadProfile} from './preload';
import fixture from '../../../examples/valuation/synthetic-base.json';
function setup(overridden=false){
 const company=createSession(fixture as CaseDoc),draft=company.cases.Base.draft;
 for(const p of Object.keys(draft.rates))draft.rates[p]='18.1234567890123456789';
 Object.assign(draft.rates,{'forecast_years[0].revenue_growth':'23.91112441337222805161','forecast_years[0].forecast_tax_rate':'18',wacc:'8.9408',terminal_growth:'3.005','terminal.working_capital_cash_requirement_percent_revenue':'0.582524271844660194','terminal.d_and_a_percent_revenue':'0.004','exit_ev_ebit_multiple':''});
 const rates=Object.fromEntries(Object.entries(draft.rates).map(([p,v])=>[p,p==='exit_ev_ebit_multiple'?null:percentageToFraction(v)]));
 const profile={schema_version:'preload-profile-v1',economic_hash:'a'.repeat(64),generated_at:'2026-10-31T00:00:00Z',economic:{issuer:{ticker:'FIXTURE',issuer:'Synthetic UI fixture',listing_class:'Common'},anchor:draft.doc.anchor,anchor_revenue:'100000000',dates:{model_origin:'2025-12-31',information_review:'2026-10-31',timing:'Synthetic fixture'},fields:Object.fromEntries(Object.entries(rates).map(([p,value])=>[p,{value,status:value===null?'MISSING_EVIDENCE':'CONFIGURED_CONVENTION',classification:['FORECAST_ESTIMATE'],basis:'SYNTHETIC_FIXTURE',unit:'fraction',rule:'test',operands:{value},sources:[],periods:[],limitation:'Software fixture only'}])),scenarios:{Base:rates,Bear:rates,Bull:rates},policy:{version:'synthetic'},configuration:{},configuration_provenance:{},sources:[],observations:[],diagnostics:[],optional_bridge:{status:'UNSUPPORTED',reason:'Fixture'}}} as PreloadProfile;
 company.preload={profile,status:'ready',failure:''};
 if(overridden){draft.rates.wacc='9.777777777777777777';company.cases.Base.overrides=['wacc'];}
 const session={...company,...company.cases.Base,draft},submit=vi.fn(async(_d:Draft,_paths:string[],_resets:string[])=>true),close=vi.fn();
 render(<ModelEditor company="FIXTURE" label="Base" session={session} submit={submit} close={close}/>);
 return {draft,submit,close};
}
const input=(name:string)=>screen.getByLabelText(name,{exact:true})as HTMLInputElement;
const change=(name:string,value:string)=>fireEvent.change(input(name),{target:{value}});
async function update(){fireEvent.click(screen.getByRole('button',{name:'Update valuation'}));await waitFor(()=>expect(screen.getByRole('button',{name:'Update valuation'})).toBeTruthy());}
it('displays every percentage at two decimals but submits the untouched exact request after focus/blur',async()=>{
 const {draft,submit}=setup();const before=buildRequest(draft);
 expect(input('Synthetic period 1 Revenue growth').value).toBe('23.91');expect(input('Synthetic period 1 Operating tax rate').value).toBe('18.00');expect(input('WACC').value).toBe('8.94');expect(input('Terminal growth').value).toBe('3.00');expect(input('Long-term working-capital cash needs / revenue').value).toBe('0.58');
 expect(within(screen.getByRole('table')).getAllByRole('textbox').every(e=>/^-?\d+\.\d{2}$/.test((e as HTMLInputElement).value))).toBe(true);
 expect(document.querySelector('.cw-editor-table td>small')).toBeNull();
 for(const e of screen.getAllByRole('textbox')){fireEvent.focus(e);fireEvent.blur(e);}
 await update();expect(submit).toHaveBeenCalledTimes(1);expect(buildRequest(submit.mock.calls[0][0])).toEqual(before);expect(submit.mock.calls[0][0].rates).toEqual(draft.rates);expect(submit.mock.calls[0][1]).toEqual([]);expect(submit.mock.calls[0][2]).toEqual([]);
});
it('allows intermediate typing, rounds edited percentages on blur and keeps every untouched operand exact',async()=>{
 const {draft,submit}=setup(),before=structuredClone(draft.rates);
 for(const v of ['','-','.','-.','12.345']){change('Synthetic period 1 Revenue growth',v);expect(input('Synthetic period 1 Revenue growth').value).toBe(v);}
 fireEvent.blur(input('Synthetic period 1 Revenue growth'));expect(input('Synthetic period 1 Revenue growth').value).toBe('12.34');await update();const sent=submit.mock.calls[0][0];expect(sent.rates).toEqual({...before,'forecast_years[0].revenue_growth':'12.34'});expect(buildRequest(sent).forecast_years[0].revenue_growth).toBe('0.1234');expect(draft.rates).toEqual(before);
});
it('normalizes an edited field on Update even without a synthetic blur, including terminal ratios',async()=>{
 const {draft,submit}=setup();change('WACC','9.876');change('Long-term operating investment / revenue','22.555');await update();expect(submit.mock.calls[0][0].rates).toEqual({...draft.rates,wacc:'9.88','terminal.investment_percent_revenue':'22.56'});
});
it('reset restores the full-precision estimate and removes override intent, while displaying two decimals',async()=>{
 const {submit}=setup(true);expect(input('WACC').value).toBe('9.78');change('WACC','10.123');fireEvent.blur(input('WACC'));fireEvent.click(input('WACC').closest('.cv-inline-field')!.parentElement!.querySelector('button')!);expect(input('WACC').value).toBe('8.94');await update();expect(submit.mock.calls[0][0].rates.wacc).toBe('8.9408');expect(submit.mock.calls[0][1]).not.toContain('wacc');expect(submit.mock.calls[0][2]).toContain('wacc');
});
it.each(['','-','.','NaN','1e2','10%'])('retains empty/invalid %s instead of coercing it to zero',async value=>{
 const {submit}=setup();change('WACC',value);fireEvent.blur(input('WACC'));expect(input('WACC').value).toBe(value);fireEvent.click(screen.getByRole('button',{name:'Update valuation'}));await waitFor(()=>expect(input('WACC').getAttribute('aria-invalid')).toBe('true'));expect(submit).not.toHaveBeenCalled();
});
it('retains method drafts, validates an unset multiple and never applies percentage rounding to multiples',async()=>{
 const {draft,submit}=setup();fireEvent.click(screen.getByRole('radio',{name:'Exit multiple'}));expect(input('Year-five EV/EBIT').value).toBe('');fireEvent.click(screen.getByRole('button',{name:'Update valuation'}));await waitFor(()=>expect(document.activeElement).toBe(input('Year-five EV/EBIT')));expect(submit).not.toHaveBeenCalled();change('Year-five EV/EBIT','15.1234567890123456789');fireEvent.blur(input('Year-five EV/EBIT'));fireEvent.click(screen.getByRole('radio',{name:'Perpetual growth'}));expect(input('Terminal growth').value).toBe('3.00');fireEvent.click(screen.getByRole('radio',{name:'Exit multiple'}));expect(input('Year-five EV/EBIT').value).toBe('15.1234567890123456789');await update();expect(submit.mock.calls[0][0].rates).toEqual({...draft.rates,exit_ev_ebit_multiple:'15.1234567890123456789'});
});
it('keeps decimal formatting isolated from caller precision and distinguishes tiny untouched values from edited zero',async()=>{
 const before=Decimal.precision,rounding=Decimal.rounding;Decimal.set({precision:2,rounding:Decimal.ROUND_UP});try{const {draft,submit}=setup();expect(input('WACC').value).toBe('8.94');expect(input('Long-term depreciation & amortization / revenue').value).toBe('0.00');change('WACC','9.885');fireEvent.blur(input('WACC'));expect(input('WACC').value).toBe('9.88');await update();expect(submit.mock.calls[0][0].rates.terminal_growth).toBe(draft.rates.terminal_growth);expect(submit.mock.calls[0][0].rates['terminal.d_and_a_percent_revenue']).toBe('0.004');expect(Decimal.precision).toBe(2);expect(Decimal.rounding).toBe(Decimal.ROUND_UP);}finally{Decimal.set({precision:before,rounding});}
});
