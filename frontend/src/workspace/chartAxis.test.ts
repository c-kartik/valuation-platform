import {it,expect} from 'vitest';
import Decimal from 'decimal.js';
import {financialAxis} from './chartAxis';
it('uses rounded outward ticks for large monetary series, with no raw-maximum divisions',()=>{
 const a=financialAxis(['402836000000','648770000000']);expect(a.ticks.map(a.label)).toEqual(['0','200','400','600','800']);expect(a.step).toBe('200000000000');
});
it('includes zero and every value for signed, flat, zero, tiny and very large series with distinct exact labels',()=>{
 for(const values of [['0','0'],[],['100','100'],['-2000000000','0'],['-150','400'],['0.00000000000000000001','0.00000000000000000002'],['-1e35','9e35']]){
  const a=financialAxis(values);expect(new Decimal(a.lower).lte(0)).toBe(true);expect(new Decimal(a.upper).gte(0)).toBe(true);expect(a.ticks).toContain('0');expect(new Set(a.ticks.map(a.label)).size).toBe(a.ticks.length);expect(a.ticks.map(a.label).every(v=>!/[eE]/.test(v))).toBe(true);
  for(const v of values){expect(new Decimal(a.lower).lte(v)).toBe(true);expect(new Decimal(a.upper).gte(v)).toBe(true);expect(a.position(v)).toBeGreaterThanOrEqual(0);expect(a.position(v)).toBeLessThanOrEqual(1);}
  expect(a.ticks.map(a.label).every(v=>v.length<=14)).toBe(true);expect(a.position(a.lower)).toBe(0);expect(a.position(a.upper)).toBe(1);
 }
});
it('chooses one common scale for a compared metric and isolates global Decimal configuration',()=>{
 const before=Decimal.precision,round=Decimal.rounding;const expected=financialAxis(['-1','9']);
 try{Decimal.set({precision:3,rounding:Decimal.ROUND_DOWN});const a=financialAxis(['-1','9']);expect(a.ticks).toEqual(expected.ticks);expect(a.ticks.map(a.label)).toEqual(expected.ticks.map(expected.label));expect(Decimal.precision).toBe(3);expect(Decimal.rounding).toBe(Decimal.ROUND_DOWN);}finally{Decimal.set({precision:before,rounding:round});}
 expect(()=>financialAxis(['NaN'])).toThrow('Finite');expect(()=>financialAxis(['1e1001'])).toThrow('budget');expect(()=>financialAxis(['1'.repeat(1025)])).toThrow('budget');expect(financialAxis(['0.00000000000000000001']).scaleNote).toContain('Axis tick labels ×');
});
