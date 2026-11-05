import {clone,keys,requireInput,text,day,same,type Doc} from './decimal';
import {runCase,validateCase,type EngineData} from './case';
export const labels=['Bear','Base','Bull'];
export function validateScenarios(doc:Doc,data:EngineData){
 keys(doc,['schema_version','scenario_set_name','scenarios'],'scenario_set');requireInput(['analyst-scenario-set-v1','investor-scenario-set-v1','investor-scenario-set-v2','investor-scenario-set-v3'].includes(doc.schema_version),'scenario_set: unsupported schema');text(doc.scenario_set_name,'scenario_set_name');
 requireInput(Array.isArray(doc.scenarios)&&doc.scenarios.length===3&&new Set(doc.scenarios.map((x:Doc)=>x.label)).size===3,'scenarios: exactly Bear, Base and Bull required');
 for(const e of doc.scenarios){keys(e,['label','analytical_date','information_cutoff','case'],'scenario');requireInput(labels.includes(e.label),'scenario.label: invalid label');validateCase(e.case,data);day(e.analytical_date,'analytical_date');requireInput(e.analytical_date===e.case.anchor.annual_end,'scenario analytical_date must match anchor');if(e.information_cutoff!==null){day(e.information_cutoff,'information_cutoff');requireInput(e.information_cutoff>=e.analytical_date,'information_cutoff precedes analytical_date');}else requireInput(['investor-scenario-set-v2','investor-scenario-set-v3'].includes(doc.schema_version),'scenario: explicit information cutoff required');if(doc.schema_version.startsWith('investor'))requireInput(e.case.schema_version.startsWith('investor'),'scenario: investor case required');}
 const ref=doc.scenarios[0];for(const e of doc.scenarios.slice(1)){
  for(const k of ['anchor','input_basis','conventions','bridge'])requireInput(same(e.case[k],ref.case[k]),'scenario: '+k+' must match across scenarios');
  for(const k of ['analytical_date','information_cutoff'])requireInput(e[k]===ref[k],'scenario: date/cutoff mismatch');requireInput(same(e.case.forecast_years.map((y:Doc)=>[y.period_index,y.fiscal_year_label]),ref.case.forecast_years.map((y:Doc)=>[y.period_index,y.fiscal_year_label])),'scenario: periods/labels mismatch');
 }
}
export function runScenarios(doc:Doc,data:EngineData):Doc{
 validateScenarios(doc,data);return {schema_version:doc.schema_version==='investor-scenario-set-v3'?'investor-scenario-results-v3':doc.schema_version.replace('-set-','-results-'),scenario_set_name:doc.scenario_set_name,submitted_inputs:clone(doc),scenarios:labels.map(label=>{const s=doc.scenarios.find((x:Doc)=>x.label===label);return {label,analytical_date:s.analytical_date,information_cutoff:s.information_cutoff,result:runCase(s.case,data)};}),...clone(data.metadata.scenarios)};
}
export function sourceCase(doc:Doc,data:EngineData,allowNull:boolean){
 const s=doc.source;requireInput(s&&['single_case','scenario_set'].includes(s.kind),'source.kind: choose single_case or scenario_set');let c:Doc,date:string,cutoff:any,label:any=null;
 if(s.kind==='single_case'){keys(s,['kind','case','analytical_date','information_cutoff'],'source');c=s.case;date=s.analytical_date;cutoff=s.information_cutoff;validateCase(c,data);}
 else {keys(s,['kind','scenario_set','scenario_label'],'source');validateScenarios(s.scenario_set,data);requireInput(labels.includes(s.scenario_label),'source: explicit scenario required');const selected=s.scenario_set.scenarios.find((x:Doc)=>x.label===s.scenario_label);c=selected.case;date=selected.analytical_date;cutoff=selected.information_cutoff;label=s.scenario_label;}
 day(date,'source.analytical_date');requireInput(date===c.anchor.annual_end,'source.analytical_date: must equal case anchor');if(cutoff===null)requireInput(allowNull,'source.information_cutoff: explicit date required');else{day(cutoff,'source.information_cutoff');requireInput(cutoff>=date,'source.information_cutoff precedes analytical_date');}
 if(doc.schema_version.startsWith('investor'))requireInput(c.schema_version.startsWith('investor'),'source: investor case required');return {case:c,selection:{source_kind:s.kind,scenario_label:label,analytical_date:date,information_cutoff:cutoff}};
}
