import {readFileSync} from 'node:fs';
import Decimal from 'decimal.js';
import {D,InputError,type Doc} from './decimal';
import {runRequest,checkBudget} from './dispatch';
const load=(file:string)=>JSON.parse(readFileSync(file,'utf8'));
const fixtures:Doc[]=load('src/browser-engine/fixtures/parity.json');
const data={anchors:load('public/browser-data/anchors.json'),policies:load('public/browser-data/policies.json'),metadata:load('public/browser-data/metadata.json')};
it('retains validation-only response scopes without performing a valuation',()=>{
 for(const name of ['synthetic-base','synthetic-equity','synthetic-scenarios-equity','synthetic-sensitivity-equity','synthetic-reverse-equity','synthetic-fcfe-5']){
  const f=fixtures.find(x=>x.name===name)!;const r=runRequest(f.path.replace('/run','/validate'),f.body,data);expect(r.status).toBe('valid');expect(r.calculation_performed).toBe(false);if(name==='synthetic-fcfe-5')expect(r).not.toHaveProperty('calculation_scope');else expect(r.calculation_scope).toBe(name==='synthetic-base'?'ENTERPRISE_VALUE':'EQUITY_PER_SHARE');expect(r).not.toHaveProperty('stage_b');
 }
});
it('rejects malformed root values on every calculation route',()=>{for(const path of ['/api/v1/cases/run','/api/v1/fcfe/run','/api/v1/analyst/run','/api/v1/reverse/run'])for(const value of [null,[],42,'invalid'])expect(()=>runRequest(path,value as any,data)).toThrow(InputError);});
it('preserves bounded input arithmetic and structural limits',()=>{for(const value of [{amount:'1e101'},{amount:'1'.repeat(65)},{value:1.1},{values:Array(129).fill(null)},{scope:'x'.repeat(4097)}])expect(()=>checkBudget(value)).toThrow(InputError);});
it('cannot inherit a changed global Decimal rounding policy',()=>{const f=fixtures.find(x=>x.name==='AAPL-Base-5')!,before=runRequest(f.path,f.body,data).stage_b.enterprise_value;const old=Decimal.precision,rounding=Decimal.rounding;try{Decimal.set({precision:2,rounding:Decimal.ROUND_UP});expect(D.precision).toBe(50);expect(runRequest(f.path,f.body,data).stage_b.enterprise_value).toBe(before);}finally{Decimal.set({precision:old,rounding});}});
