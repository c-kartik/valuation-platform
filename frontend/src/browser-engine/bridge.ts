import {D,clone,sum,keys,number,requireInput,text,refs,day,type Doc} from './decimal';
const roles=['ELIGIBLE_ASSET','FINANCING_CLAIM','OTHER_EQUITY_CLAIM'];
const origins=['reported','derived','proxy','manual_input','analyst_override','synthetic'];
function identity(v:Doc){keys(v,['author','timestamp_utc','rationale'],'review');Object.values(v).forEach(x=>text(x,'review'));requireInput(/(?:Z|\+00:00)$/.test(v.timestamp_utc)&&!isNaN(Date.parse(v.timestamp_utc)),'review: UTC timestamp required');}
function precision(v:any){requireInput(typeof v==='string'&&/^(INF|-?\d+)$/.test(v),'bridge: explicit precision required');}
export function validateBridge(b:Doc,doc:Doc){
 keys(b,['components','observations','shares','coverage','input_basis','valuation_class_id','unresolved_requirements','convention_version'],'bridge');
 requireInput(['meta-base-equity-bridge-v1','manual-equity-bridge-v1'].includes(b.convention_version),'bridge: unsupported convention');
 requireInput(b.input_basis===doc.input_basis,'bridge.input_basis: must match case');
 requireInput(Array.isArray(b.unresolved_requirements)&&b.unresolved_requirements.length===0,'bridge: unresolved requirements');
 for(const key of ['components','observations','coverage'])requireInput(Array.isArray(b[key]),'bridge.'+key+': array required');
 const ids=new Set<string>(),populations=new Set<string>();
 for(const c of b.components){
  keys(c,['component_id','company_cik','role','amount','as_of','population_id','origin','precision','source_references','decision_references','rationale','overlap_references','alternative_references','overlaps_forecast','unit','scale'],'bridge.component');
  for(const k of ['component_id','population_id','rationale'])text(c[k],k);
  requireInput(!ids.has(c.component_id)&&!populations.has(c.population_id),'bridge: repeated component/population');ids.add(c.component_id);populations.add(c.population_id);
  requireInput(roles.includes(c.role)&&origins.includes(c.origin),'bridge: invalid role/origin');number(c.amount,'bridge.amount',0);precision(c.precision);
  requireInput(c.company_cik===doc.anchor.cik&&c.as_of===doc.anchor.annual_end&&c.unit==='USD'&&c.scale===1,'bridge: company/date/unit mismatch');
  requireInput(c.overlaps_forecast===false,'bridge: forecast overlap');
  refs(c.source_references,'sources',true);refs(c.decision_references,'decisions',true);refs(c.overlap_references,'overlap');refs(c.alternative_references,'alternatives');
 }
 const notes=new Map<string,Doc>();
 for(const n of b.observations){
  keys(n,['observation_id','company_cik','role','disposition','population_id','value','as_of','unit','precision','origin','source_references','decision_references','rationale'],'bridge.observation');
  for(const k of ['observation_id','population_id','unit','rationale'])text(n[k],k);
  requireInput(!ids.has(n.observation_id),'bridge: repeated observation ID');ids.add(n.observation_id);notes.set(n.observation_id,n);
  requireInput(n.company_cik===doc.anchor.cik&&roles.includes(n.role)&&['SUPPORT','EXCLUDED','OMISSION'].includes(n.disposition)&&[...origins,'unavailable'].includes(n.origin),'bridge: invalid observation');
  if(n.as_of!==null)day(n.as_of,'observation.as_of');
  if(n.value!==null){number(n.value,'observation.value');precision(n.precision);}else requireInput(n.precision===null,'bridge: absent amount cannot have precision');
  requireInput(n.disposition!=='OMISSION'||n.value===null,'bridge: omission must retain null');refs(n.source_references,'sources',n.value!==null);refs(n.decision_references,'decisions',true);
 }
 for(const c of b.components)for(const r of [...c.overlap_references,...c.alternative_references])requireInput(notes.has(r),'bridge: numeric, self or unresolved overlap/alternative reference');
 requireInput(b.coverage.length===3&&new Set(b.coverage.map((x:Doc)=>x.role)).size===3,'bridge: all three coverage roles required');
 const omissions:string[]=[];
 for(const c of b.coverage){
  keys(c,['role','population_ids','omission_references','review','decision_references'],'coverage');requireInput(roles.includes(c.role),'coverage: invalid role');identity(c.review);refs(c.population_ids,'populations');refs(c.omission_references,'omissions');refs(c.decision_references,'decisions',true);
  const expected=b.components.filter((x:Doc)=>x.role===c.role).map((x:Doc)=>x.population_id).sort();requireInput(JSON.stringify([...c.population_ids].sort())===JSON.stringify(expected),'coverage: must name exactly supplied role operands');requireInput(c.population_ids.length||c.omission_references.length,'coverage: empty population needs omission');
  for(const r of c.omission_references){const n=notes.get(r);requireInput(n&&n.disposition==='OMISSION'&&n.role===c.role,'coverage: matching omission required');omissions.push(r);}
 }
 requireInput(new Set(omissions).size===omissions.length&&omissions.length===[...notes.values()].filter(x=>x.disposition==='OMISSION').length,'coverage: every omission must bind once');
 const s=b.shares;keys(s,['company_cik','shares','observation_date','class_id','equivalence_convention','award_policy','award_policy_references','source_references','decision_references','precision','rationale','unit','scale'],'bridge.shares');number(s.shares,'shares','1e-100');precision(s.precision);text(s.class_id,'class');text(s.rationale,'rationale');
 requireInput(s.class_id===b.valuation_class_id&&s.company_cik===doc.anchor.cik&&s.observation_date===doc.anchor.annual_end&&s.unit==='shares'&&s.scale===1,'shares: company/date/class/unit mismatch');
 requireInput(['single_common_class','explicit_common_unit_equivalence'].includes(s.equivalence_convention)&&s.award_policy==='sbc_expensed_no_duplicate_service_charge_v1','shares: unsupported class/award policy');
 for(const k of ['award_policy_references','source_references','decision_references'])refs(s[k],k,true);
}
export function runBridge(stage:Doc,b:Doc){
 const components=clone(b.components).sort((a:Doc,c:Doc)=>a.component_id.localeCompare(c.component_id));
 const totals=roles.map(role=>sum(components.filter((x:Doc)=>x.role===role).map((x:Doc)=>x.amount)));
 const equity=new D(stage.enterprise_value).plus(totals[0]).minus(totals[1]).minus(totals[2]);
 return {schema:'stage-c-equity-bridge-v1',convention_version:b.convention_version,numeric_policy:{precision:50,rounding:'ROUND_HALF_EVEN',amount_unit:'USD',share_unit:'shares',intermediate_quantization:false},semantic_input_review:'NOT_ASSESSED_BY_CALCULATOR',
 limitations:['Source/decision/review references are declarations, not authenticated approvals.','Declared coverage/class/overlap checks cannot prove completeness or hidden economic overlap.',`No automatic award valuation, dilution, proceeds or actual ${b.convention_version==='meta-base-equity-bridge-v1'?'META':'company'} selections.`],stage_b:clone(stage),
 inputs:{...clone(b),components,observations:clone(b.observations).sort((a:Doc,c:Doc)=>a.observation_id.localeCompare(c.observation_id)),coverage:clone(b.coverage).sort((a:Doc,c:Doc)=>a.role.localeCompare(c.role))},
 contributions:components.map((component:Doc)=>({component,signed_contribution:new D(component.amount).times(component.role==='ELIGIBLE_ASSET'?1:-1).toString()})),
 eligible_assets:totals[0].toString(),financing_claims:totals[1].toString(),other_equity_claims:totals[2].toString(),equity_value:equity.toString(),valuation_shares:new D(b.shares.shares).toString(),value_per_share:equity.div(b.shares.shares).toString()};
}
