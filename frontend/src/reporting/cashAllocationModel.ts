import type {QuarterlyReport} from './model';
export const flowKeys=['cfo','ppe','marketablePurchases','marketableSales','otherPurchases','otherSales','acquisitions','otherInvesting','investing','awards','buybacks','dividends','debtProceeds','debtRepayments','minority','commonIssued','preferredIssued','otherFinancing','financing','fx','change'] as const;
export type FlowKey=typeof flowKeys[number];
export type CashKey=FlowKey|'opening'|'closing';
export type CashValues=Record<CashKey,number|null>;
export type CashFact={value:number;reported_value:number;sign:number;concept:string;context_ids:string[];dimensions:string[][];start:string|null;end:string|null;instant:string|null;filed:string;source_url:string;source_sha256:string};
export type CashPeriod={id:string;label?:string;start:string;end:string;method:string;operand_ids?:string[];values:CashValues;evidence:Record<string,CashFact|{method:string;terms:{coefficient:number;period_id:string}[]}|null>};
export type PPEKey='technical'|'office'|'other'|'service'|'pending'|'depreciation'|'net';
export type PPEBalance={year:string;date:string;values:Record<PPEKey,number>;evidence:Record<PPEKey,CashFact>;servers_network_share_approx:number;composition_basis:string};
export type CashAllocationReport={schema_version:1;policy:string;ticker:string;as_of:string;currency:'USD';history_snapshot_sha256:string;history_source_snapshot_sha256:string;basis:string;annual:CashPeriod[];quarterly:CashPeriod[];ttm:CashPeriod[];reported_periods:Record<string,CashPeriod>;ppe:PPEBalance[];sources:Record<string,{source_url:string;filed:string;sha256:string}>;limitations:string[]};
export type AllocationMode='annual'|'quarterly'|'ttm';
export const cashLabels:Record<CashKey,string>={cfo:'Operating cash flow',ppe:'Property & equipment purchases',marketablePurchases:'Marketable securities purchases',marketableSales:'Marketable maturities & sales',otherPurchases:'Non-marketable securities purchases',otherSales:'Non-marketable maturities & sales',acquisitions:'Acquisitions & intangible assets',otherInvesting:'Other investing activities',investing:'Net investing cash flow',awards:'Net stock-award payments',buybacks:'Share repurchases',dividends:'Dividend payments',debtProceeds:'Debt proceeds, net of issuance costs',debtRepayments:'Debt & capital-lease repayments',minority:'Sales of subsidiary interests',commonIssued:'Common stock issued',preferredIssued:'Convertible preferred stock issued',otherFinancing:'Other financing activities',financing:'Net financing cash flow',fx:'Exchange-rate effect',change:'Change in cash',opening:'Opening cash',closing:'Closing cash'};
const optional=new Set<CashKey>(['dividends','minority','commonIssued','preferredIssued','otherFinancing']);
const paymentKeys=new Set<CashKey>(['ppe','marketablePurchases','otherPurchases','acquisitions','otherInvesting','awards','buybacks','dividends','debtRepayments']);
const investing:CashKey[]=['ppe','marketablePurchases','marketableSales','otherPurchases','otherSales','acquisitions','otherInvesting'];
const financing:CashKey[]=['awards','buybacks','dividends','debtProceeds','debtRepayments','minority','commonIssued','preferredIssued','otherFinancing'];
export const cashAmount=(r:CashPeriod,k:CashKey)=>r.values[k]??0;
const keys:CashKey[]=[...flowKeys,'opening','closing'];
function requireValue(ok:unknown,message:string):asserts ok{if(!ok)throw Error(message);}
export function reconcileCash(r:CashPeriod){
 for(const k of keys)requireValue(r.values[k]===null?optional.has(k):Number.isSafeInteger(r.values[k]),'Missing or unsafe cash amount');
 const n=(k:CashKey)=>cashAmount(r,k);
 requireValue(investing.reduce((s,k)=>s+n(k),0)===n('investing'),'Investing reconciliation failed');
 requireValue(financing.reduce((s,k)=>s+n(k),0)===n('financing'),'Financing reconciliation failed');
 requireValue(n('cfo')+n('investing')+n('financing')+n('fx')===n('change'),'Cash movement reconciliation failed');
 requireValue(n('opening')+n('change')===n('closing'),'Closing cash reconciliation failed');
}
export function validateAllocation(value:unknown,ticker:string,history:QuarterlyReport):CashAllocationReport{
 const p=value as CashAllocationReport;
 requireValue(p?.schema_version===1&&p.policy==='alphabet-cash-allocation-v1'&&ticker==='GOOGL'&&p.ticker===ticker&&p.currency==='USD'&&p.as_of===history.as_of&&p.history_source_snapshot_sha256===history.source_snapshot_sha256&&/^[a-f0-9]{64}$/.test(p.history_snapshot_sha256),'Unsupported cash-allocation package');
 requireValue(p.annual?.length===5&&p.quarterly?.length===20&&p.ttm?.length===17&&p.ppe?.length===2&&p.sources&&p.reported_periods,'Incomplete cash-allocation history');
 const sources=Object.values(p.sources);
 const validateFact=(f:CashFact)=>{requireValue(f&&Number.isSafeInteger(f.value)&&Number.isSafeInteger(f.reported_value)&&(f.sign===1||f.sign===-1)&&f.reported_value*f.sign===f.value&&Array.isArray(f.context_ids)&&f.context_ids.length&&Array.isArray(f.dimensions)&&f.filed<=p.as_of&&f.source_url.startsWith('https://www.sec.gov/Archives/edgar/data/1652044/')&&sources.some(s=>s.source_url===f.source_url&&s.sha256===f.source_sha256&&s.filed===f.filed),'Invalid cash-flow source evidence');};
 for(const [id,r]of Object.entries(p.reported_periods)){
  requireValue(r.id===id&&r.method==='reported'&&r.start<r.end,'Invalid reported period');reconcileCash(r);
  for(const k of keys){const f=r.evidence[k] as CashFact|null;if(r.values[k]===null){requireValue(f===null&&optional.has(k),'Missing caption has false evidence');continue;}validateFact(f!);requireValue(f!.dimensions.length===0&&f!.sign===(paymentKeys.has(k)?-1:1)&&f!.value===r.values[k]&&(k==='opening'?f!.instant===new Date(Date.parse(r.start+'T00:00:00Z')-86400000).toISOString().slice(0,10):k==='closing'?f!.instant===r.end:f!.start===r.start&&f!.end===r.end),'Wrong cash-flow context');}
 }
 const assertDerived=(r:CashPeriod,inputs:CashPeriod[],coeffs:number[])=>{
  reconcileCash(r);
  requireValue(r.operand_ids?.length===inputs.length&&inputs.every((v,i)=>v&&r.operand_ids![i]===v.id),'Wrong derivation operands');
  for(const k of flowKeys){const present=inputs.some(q=>q.values[k]!==null),expected=present?inputs.reduce((n,q,i)=>n+cashAmount(q,k)*coeffs[i],0):null;requireValue(r.values[k]===expected,'Derived cash amount contradicts operands');}
  requireValue(r.values.opening===(coeffs.every(c=>c===1)?inputs[0].values.opening:inputs[1].values.closing)&&r.values.closing===(coeffs.every(c=>c===1)?inputs.at(-1)!.values.closing:inputs[0].values.closing),'Wrong opening/closing balance');
 };
 const annuals=history.validation.annual_tie_outs as {metric:string;fiscal_year:number;annual:{accession:string;start:string;end:string;value:number}}[];
 const expectedAnnuals=annuals.filter(a=>a.metric==='cfo').sort((a,b)=>a.fiscal_year-b.fiscal_year).slice(-5);
 for(const [i,r]of p.annual.entries()){const a=expectedAnnuals[i];requireValue(a&&r.id===`FY${a.fiscal_year}`&&r.start===a.annual.start&&r.end===a.annual.end&&r.values.cfo===a.annual.value,'Wrong annual cohort');assertDerived(r,r.operand_ids!.map(id=>p.reported_periods[id]),[1]);requireValue(r.operand_ids![0].startsWith(a.annual.accession+':'),'Wrong annual accession');}
 for(const [i,r]of p.quarterly.entries()){
  const h=history.rows[i],ops=h.evidence.cfo.operands,ids=ops.map(o=>`${o.accession}:${o.start}:${o.end}`);
  requireValue(r.id===h.id&&r.start===h.start&&r.end===h.end&&r.values.cfo===h.values.cfo&&-cashAmount(r,'ppe')===h.values.cash_capex&&r.operand_ids?.join('|')===ids.join('|'),'Cash history contradicts accepted quarter');
  assertDerived(r,ids.map(id=>p.reported_periods[id]),ops.length===1?[1]:[1,-1]);
 }
 for(const [i,r]of p.ttm.entries()){const input=p.quarterly.slice(i,i+4);requireValue(r.id===input[3].id&&r.start===input[0].start&&r.end===input[3].end,'Wrong TTM window');assertDerived(r,input,[1,1,1,1]);}
 for(const [i,r]of p.ppe.entries()){
  const v=r.values;
  requireValue(r.year===String(Number(p.annual.at(-1)!.id.slice(2))-1+i)&&r.date===r.year+'-12-31'&&r.servers_network_share_approx===0.6&&r.composition_basis,'Unreviewed PP&E balance policy');
  requireValue(Object.keys(v).length===7&&Object.values(v).every(n=>Number.isSafeInteger(n)&&n>=0)&&v.technical+v.office+v.other===v.service&&v.service+v.pending-v.depreciation===v.net,'PP&E does not reconcile');
  for(const k of Object.keys(v) as PPEKey[]){const f=r.evidence[k];validateFact(f);requireValue(f.value===v[k]&&f.instant===r.date&&f.sign===1,'Wrong PP&E evidence date');const member={technical:'TechnicalInfrastructureMember',office:'OfficeSpaceMember',other:'CorporateAndOtherAssetsMember',service:'DepreciablePropertyPlantAndEquipmentMember',pending:'AssetUnderConstructionMember'}[k as Exclude<PPEKey,'net'|'depreciation'>];requireValue(member?f.dimensions.length===1&&f.dimensions[0][0].endsWith('}PropertyPlantAndEquipmentByTypeAxis')&&f.dimensions[0][1].endsWith('}'+member):f.dimensions.length===0,'Wrong PP&E dimensions');}
 }
 return p;
}
export async function fetchAllocation(ticker:string,history:QuarterlyReport,signal:AbortSignal){
 const response=await fetch(`${(import.meta as ImportMeta & {env:{BASE_URL:string}}).env.BASE_URL}cash-allocation/${ticker}.json`,{signal});
 if(!response.ok)throw Error('Cash allocation unavailable');
 return validateAllocation(await response.json(),ticker,history);
}
export type AllocationNode={id:string;label:string;flow:number;value:number;kind:string;lines:[string,number][];copy:string;color:string};
export function allocationModel(row:CashPeriod){
 const n=(k:CashKey)=>cashAmount(row,k),nodes:AllocationNode[]=[];
 const add=(id:string,label:string,flow:number,fields:CashKey[],copy:string,color:string,reverse=false)=>{if(!flow)return;nodes.push({id,label,flow,value:Math.abs(flow),kind:flow>0?'Cash source':'Cash use',lines:fields.filter(k=>row.values[k]!==null).map(k=>[cashLabels[k],n(k)*(reverse?-1:1)]),copy,color});};
 add('cfo','Operating cash flow',n('cfo'),['cfo'],'Net cash from operating activities, after the operating-cash reconciliation.','#21485a');
 const debt=n('debtProceeds')+n('debtRepayments');add('debt',debt>=0?'Net debt raised':'Net debt repaid',debt,['debtProceeds','debtRepayments'],'Debt proceeds less debt and capital-lease repayments.','#7a8d98');
 add('minority','Subsidiary interests sold',n('minority'),['minority'],'Financing proceeds from sales of subsidiary interests.','#88778d');
 add('business','Business investment',n('ppe')+n('acquisitions'),['ppe','acquisitions'],'Cash PP&E plus acquisitions net of cash acquired and intangible-asset purchases.','#a48031',true);
 add('returns','Shareholder returns',n('buybacks')+n('dividends'),['buybacks','dividends'],'Stock repurchases and reported dividends; stock-award payments are separate.','#21485a',true);
 const securities=n('marketablePurchases')+n('marketableSales')+n('otherPurchases')+n('otherSales');add('securities',securities<=0?'Net securities investment':'Net securities released',securities,['marketablePurchases','marketableSales','otherPurchases','otherSales'],'Net financial-investment cash flow, separate from PP&E and acquisitions.','#397965');
 add('awards','Stock-award payments',n('awards'),['awards'],'Financing cash payments related to stock-based awards, separate from noncash SBC expense.','#88778d',true);
 add('other','Other investing',n('otherInvesting'),['otherInvesting'],'The reported other-investing caption, not a balancing residual.','#7a8d98');
 add('equity','Equity issued',n('commonIssued')+n('preferredIssued'),['commonIssued','preferredIssued'],'Separately reported common and convertible-preferred issuance proceeds.','#397965');
 add('finOther','Other financing',n('otherFinancing'),['otherFinancing'],'The separately reported other-financing caption.','#7a8d98');
 const beforeFX=n('cfo')+n('investing')+n('financing');add('retained',beforeFX>=0?'Cash added before FX':'Cash drawn before FX',-beforeFX,[],'Positive accumulation is a use; a drawdown is a source. Exchange-rate effects appear in the cash-balance reconciliation.','#183b4b');
 const retained=nodes.find(n=>n.id==='retained');if(retained)retained.lines=[['Net cash flow before FX',beforeFX],['Exchange-rate effect',n('fx')],['Reported change in cash',n('change')]];
 const sources=nodes.filter(n=>n.flow>0),uses=nodes.filter(n=>n.flow<0),pool=sources.reduce((s,n)=>s+n.value,0);
 requireValue(pool===uses.reduce((s,n)=>s+n.value,0)&&pool>0,'Allocation pool does not reconcile');
 return{nodes,sources,uses,pool,beforeFX,business:-(n('ppe')+n('acquisitions')),returns:-(n('buybacks')+n('dividends'))};
}
