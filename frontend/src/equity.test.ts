import {it,expect} from 'vitest';
import Decimal from 'decimal.js';
import {execFileSync} from 'node:child_process';
import {resolve} from 'node:path';
import {emptyEquity,millionsToUnits,buildEquityRequest,equityErrors} from './equity';
import {makeDraft} from './model';
import type {CaseDoc} from './model';
import fixture from '../../examples/valuation/synthetic-base.json';
export function completeBridge(){return {...emptyEquity(),assets:'0.000012',financing:'0.000020',claims:'0.000003',shares:'0.000004',date:'2025-12-31',claimsTreatment:'amount' as const,assetsCoverage:'selected' as const,financingCoverage:'selected' as const,claimsCoverage:'selected' as const,shareBasis:'issued' as const,classes:'Synthetic common',equivalence:'single_common_class' as const,awards:'none' as const,nonOverlap:true};}
it('converts millions exactly, including small shares and signed text, isolated from Decimal context',()=>{
 const old=Decimal.precision;try{Decimal.set({precision:2});expect(millionsToUnits('1.123456789')).toBe('1123456.789');expect(millionsToUnits('.000004')).toBe('4');expect(millionsToUnits('-0.0000001')).toBe('-0.1');expect(millionsToUnits('0')).toBe('0');expect(millionsToUnits('')).toBeNull();expect(Decimal.precision).toBe(2);}finally{Decimal.set({precision:old});}
 for(const bad of ['-','.','1,000','12%','1e2','NaN','Infinity','$1'])expect(()=>millionsToUnits(bad)).toThrow();
});
it('starts every bridge amount and declaration unset without changing EV-only requests',()=>{
 const e=emptyEquity(),draft=makeDraft(fixture as CaseDoc);expect(equityErrors(e,'2025-12-31')).toHaveProperty('claimsTreatment');expect(e.assets).toBe('');expect(e.nonOverlap).toBe(false);expect(()=>buildEquityRequest(draft,e)).toThrow();expect(draft.doc.schema_version).toBe('investor-case-v1');
});
it('keeps explicit zero, missing amounts, unassessed claims and null omissions distinct',()=>{
 const draft=makeDraft(fixture as CaseDoc),e=completeBridge();e.assets='0';expect(equityErrors(e,'2025-12-31')).toEqual({});
 expect((buildEquityRequest(draft,e).bridge.components as {amount:string}[])[0].amount).toBe('0');
 e.assets='';expect(()=>buildEquityRequest(draft,e)).toThrow();e.assets='0';
 const omitted={...e,claimsTreatment:'none' as const,awards:'omitted' as const,assetsCoverage:'omitted' as const};
 const req=buildEquityRequest(draft,omitted);expect((req.bridge.components as unknown[])).toHaveLength(2);
 const notes=req.bridge.observations as {value:null;origin:string;rationale:string}[];expect(notes).toHaveLength(3);expect(notes.every(n=>n.value===null)).toBe(true);expect(notes.map(n=>n.rationale).join(' ')).toContain('unbounded');
 expect(req.preparation.notes).toBeNull();expect(req).not.toHaveProperty('analyst');expect(req.bridge.unresolved_requirements).toEqual([]);
});
it('requires date, explicit class/award population and declared non-overlap',()=>{
 const e=completeBridge();expect(equityErrors({...e,date:'2026-01-01'},'2025-12-31')).toHaveProperty('date');
 for(const key of ['shareBasis','classes','equivalence','awards','assetsCoverage','financingCoverage','claimsCoverage'] as const)expect(equityErrors({...e,[key]:''},'2025-12-31')).toHaveProperty(key);
 expect(equityErrors({...e,awards:'shares'},'2025-12-31')).toHaveProperty('shareBasis');expect(equityErrors({...e,awards:'shares',shareBasis:'basic_equivalent'},'2025-12-31')).toEqual({});expect(equityErrors({...e,awards:'claims',claimsTreatment:'none'},'2025-12-31')).toHaveProperty('awards');expect(equityErrors({...e,nonOverlap:false},'2025-12-31')).toHaveProperty('nonOverlap');
});
it('matches complete financial components against equivalent temporary CLI equity cases; inherited financial rejection stays server-side',()=>{
 const draft=makeDraft(fixture as CaseDoc);draft.doc.preparation.notes='  Optional personal text\nonly  ';const req=buildEquityRequest(draft,completeBridge());const before=JSON.stringify(req);
 const program=`import json,sys,tempfile,subprocess\nfrom pathlib import Path\nfrom valuation_platform.valuation.case_inputs import read_case,CaseInputError\ndoc=json.load(sys.stdin)\nold=dict(doc);old.pop('preparation');old['schema_version']='analyst-case-v2';old['analyst']={'author':'Synthetic CLI comparison','timestamp_utc':'2026-10-21T10:00:00Z','rationale':'Synthetic engineering comparison only'};old['scope']='Synthetic comparison; not financial approval'\nwith tempfile.TemporaryDirectory(prefix='investor-equity-cli-') as directory:\n outputs=[]\n for name,d in [('anonymous',doc),('legacy',old)]:\n  path=Path(directory)/(name+'.json');path.write_text(json.dumps(d));outputs.append(json.loads(subprocess.check_output([sys.executable,'scripts/run_analyst_case.py',str(path),'--run'])))\n a,b=outputs;assert a['stage_b']==b['stage_b'];assert a['stage_c']==b['stage_c'];assert a['submitted_inputs']!=b['submitted_inputs']\n from decimal import Decimal\n assert Decimal(a['stage_c']['equity_value'])==Decimal('66.577060352')\n assert Decimal(a['stage_c']['value_per_share'])==Decimal('16.644265088')\n assert a['submitted_inputs']['preparation']['notes']==doc['preparation']['notes']\nfor field,value in [('shares','0'),('shares','-1'),('shares',None),('unit','million shares')]:\n bad=json.loads(json.dumps(doc));bad['bridge']['shares'][field]=value\n try:read_case(json.dumps(bad));raise AssertionError('accepted invalid shares')\n except CaseInputError:pass\nfor field in ['overlap_references','alternative_references']:\n bad=json.loads(json.dumps(doc));bad['bridge']['components'][0][field]=['financing']\n try:read_case(json.dumps(bad));raise AssertionError('accepted overlap')\n except CaseInputError:pass\nprint('Complete Stage B/C financial components match; metadata intentionally differs; temporary files removed')`;
 const root=resolve('..');const out=execFileSync(resolve(root,'.venv/bin/python'),['-c',program],{cwd:root,input:JSON.stringify(req),encoding:'utf8',env:{...process.env,PYTHONPATH:'src',PYTHONDONTWRITEBYTECODE:'1'}});
 expect(out).toContain('Complete Stage B/C financial components match');expect(JSON.stringify(req)).toBe(before);
});
