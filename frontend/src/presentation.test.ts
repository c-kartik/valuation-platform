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
