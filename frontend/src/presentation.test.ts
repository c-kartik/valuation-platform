import {it,expect} from 'vitest';
import Decimal from 'decimal.js';
import {execFileSync} from 'node:child_process';
import {resolve} from 'node:path';
import {terminalContribution,chartPoints} from './presentation';

it('matches actual CLI ratio display for zero, negative, over-100%, ordinary and HALF_EVEN ties',()=>{
 const pairs=[['4','0'],['4','-1'],['4','2'],['-4','2'],['49.8706661376','77.577060352'],['0.012345','1'],['0.012355','1']];
 const script=`import json,runpy,sys\nfrom pathlib import Path\nm=runpy.run_path('scripts/run_analyst_case.py')\nr=m['run_case'](m['load_case'](Path('examples/valuation/synthetic-base.json')),Path('.'))\nlines=[]\nfor pv,ev in json.loads(sys.stdin.read()):\n r['stage_b']['pv_terminal_value']=pv;r['stage_b']['enterprise_value']=ev\n lines.append(next(x for x in m['render_summary'](r).splitlines() if x.startswith('Discounted terminal value / EV contribution:')))\nprint(json.dumps(lines))`;
 const root=resolve('..');
 const output=JSON.parse(execFileSync(resolve(root,'.venv/bin/python'),['-c',script],{cwd:root,input:JSON.stringify(pairs),encoding:'utf8',env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}})) as string[];
 pairs.forEach(([pv,ev],i)=>{
  const got=terminalContribution(pv,ev);expect(output[i].toLowerCase()).toContain(got.text.toLowerCase());
 });
 expect(terminalContribution('4','2').note).toMatch(/exceeds 100%/);expect(terminalContribution('4','-1').note).toMatch(/EV is negative/);expect(terminalContribution('-4','2').text).toBe('-200.00%');
});
it('isolates ratio arithmetic and preserves raw strings',()=>{
 const before={precision:Decimal.precision,rounding:Decimal.rounding};
 try{Decimal.set({precision:2,rounding:Decimal.ROUND_DOWN});expect(terminalContribution('2','3').text).toBe('66.67%');expect(Decimal.precision).toBe(2);}finally{Decimal.set(before);}
});
it('bounds chart-only coordinates for negative, zero and extreme amounts',()=>{
 for(const values of [['0','0','0','0','0'],['-3','-2','0','2','3'],['1e900','-2e900','3e900','0','4e900']]){
  const before=[...values];const points=chartPoints(values)!;expect(points).toHaveLength(5);points.forEach(p=>{expect(Number.isFinite(p.x)&&Number.isFinite(p.y)).toBe(true);expect(p.y).toBeGreaterThanOrEqual(20);expect(p.y).toBeLessThanOrEqual(180);});expect(values).toEqual(before);
 }
 expect(chartPoints(['1e9999','0','0','0','0'])).toBeNull();expect(chartPoints(['Infinity','0','0','0','0'])).toBeNull();
});

import {readableMoney,readableLimitation} from './presentation';
it('scales USD for readable headlines with display-only HALF_EVEN rounding and isolated context',()=>{
 const original={precision:Decimal.precision,rounding:Decimal.rounding};
 try {
  Decimal.set({precision:2,rounding:Decimal.ROUND_UP});
  expect(readableMoney('200966000000')).toBe('$200.97bn');
  expect(readableMoney('100')).toBe('$100.00');
  expect(readableMoney('0')).toBe('$0.00');
  expect(readableMoney('-1234567')).toBe('−$1.23m');
  expect(readableMoney('12345.125')).toBe('$12,345.12');
  expect(readableMoney('12345.135')).toBe('$12,345.14');
  expect(Decimal.precision).toBe(2);expect(Decimal.rounding).toBe(Decimal.ROUND_UP);
 } finally {Decimal.set(original);}
});
it('preserves financial unknowns while removing a known internal reference from display only',()=>{
 const original='No bridge/share intake; historical debt/reinvestment/D&A limitations and unbounded omissions remain unchanged.';
 expect(readableLimitation(original)).toContain('unbounded omissions');expect(readableLimitation(original)).toContain('Cash/debt/share adjustments are excluded');
 expect(readableLimitation('A supplied limitation')).toBe('A supplied limitation');expect(original).toContain('intake');
});

it('keeps a positive fractional share denominator exact in millions and isolates Decimal context',async()=>{
 const {shareMillions}=await import('./presentation');const old={precision:Decimal.precision,rounding:Decimal.rounding};
 try{Decimal.set({precision:2,rounding:Decimal.ROUND_UP});expect(shareMillions('0.1')).toBe('0.0000001');expect(shareMillions('20000000')).toBe('20');expect(shareMillions('1234567890.123456789')).toBe('1,234.567890123456789');expect(Decimal.precision).toBe(2);}finally{Decimal.set(old);}
});


it('restricts display-only price comparisons to the selected fiscal date and isolates rounding',async()=>{
 const {comparisonDifference}=await import('./presentation');const old={precision:Decimal.precision,rounding:Decimal.rounding};
 try{
  Decimal.set({precision:2,rounding:Decimal.ROUND_UP});
  expect(comparisonDifference('7.5','5','2025-09-27','2025-09-27')).toBe('50.0');
  expect(comparisonDifference('-2','5','2025-09-27','2025-09-27')).toBe('-140.0');
  expect(comparisonDifference('1.2345','1','2025-12-31','2025-12-31')).toBe('23.4');
  expect(comparisonDifference('7.5','5','2025-12-31','2025-09-27')).toBeNull();
  for(const price of ['','0','-1','NaN','Infinity','invalid'])expect(comparisonDifference('7.5',price,'2025-09-27','2025-09-27')).toBeNull();
  expect(Decimal.precision).toBe(2);expect(Decimal.rounding).toBe(Decimal.ROUND_UP);
 }finally{Decimal.set(old);}
});
