import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {D,InputError,type Doc} from './decimal';
import {runRequest} from './dispatch';
import type {EngineData} from './case';
const fixtures:Doc[]=JSON.parse(readFileSync(resolve('src/browser-engine/fixtures/parity.json'),'utf8'));
const extraFixtures:Doc[]=JSON.parse(readFileSync(resolve('src/browser-engine/fixtures/extra-parity.json'),'utf8'));
const load=(file:string)=>JSON.parse(readFileSync(resolve('public/browser-data',file),'utf8'));
const data:EngineData={anchors:load('anchors.json'),policies:load('policies.json'),metadata:load('metadata.json')};
const decimal=/^-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?$/;
let numericalChecks=0;
function compare(actual:any,expected:any,path='result'){
 if(typeof expected==='string'&&typeof actual==='string'&&decimal.test(expected)&&decimal.test(actual)){
  const a=new D(actual),e=new D(expected);numericalChecks++;
  // 32 units in the last place at precision 50 bounds representation/associativity
  // differences. No display/materiality waiver; proof fractions must be exact.
  const envelope=new D(32).times(new D(10).pow(Math.max(a.e,e.e)-49));
  if(/numerator|denominator/.test(path))expect(actual,path).toBe(expected);
  else expect(a.minus(e).abs().lte(envelope),`${path}: ${actual} vs ${expected}`).toBe(true);
  return;
 }
 if(Array.isArray(expected)){expect(Array.isArray(actual),path).toBe(true);expect(actual.length,path).toBe(expected.length);expected.forEach((x,i)=>compare(actual[i],x,path+'['+i+']'));return;}
 if(expected&&typeof expected==='object'){
  expect(actual&&typeof actual==='object',path).toBeTruthy();expect(Object.keys(actual).sort(),path).toEqual(Object.keys(expected).sort());for(const k of Object.keys(expected))compare(actual[k],expected[k],path+'.'+k);return;
 }
 expect(actual,path).toEqual(expected);
}
describe('Independent browser calculations versus retained Python reference',()=>{
 for(const fixture of [...fixtures,...extraFixtures]){it(fixture.name,()=>{
  if(fixture.status>=400){expect(()=>runRequest(fixture.path,fixture.body as Doc,data)).toThrow(InputError);return;}
  compare(runRequest(fixture.path,fixture.body as Doc,data),fixture.expected);
 });}
 afterAll(()=>console.info('Full precision numerical comparisons:',numericalChecks));
});
export {data,compare};
