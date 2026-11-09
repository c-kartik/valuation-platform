import type {QuarterlyReport} from './model';
export const flowKeys=['cfo','ppe','marketablePurchases','marketableSales','otherPurchases','otherSales','acquisitions','otherInvesting','investing','awards','buybacks','dividends','debtProceeds','debtRepayments','minority','commonIssued','preferredIssued','otherFinancing','financing','fx','change'] as const;
export type FlowKey=typeof flowKeys[number];
export const extraFlowKeys=['marketableMaturities','commercialPaper','financeLeasePayments','heldForSalePurchases','ventureDistributions','bankOverdrafts','ppeSales'] as const;
export const issuerFlowKeys=[...flowKeys,...extraFlowKeys];
export type ExtraFlowKey=typeof extraFlowKeys[number];
export type CashKey=FlowKey|ExtraFlowKey|'opening'|'closing';
export type CashValues=Record<FlowKey|'opening'|'closing',number|null>&Partial<Record<ExtraFlowKey,number|null>>;
export type CashFact={value:number;reported_value:number;sign:number;concept:string;context_ids:string[];dimensions:string[][];start:string|null;end:string|null;instant:string|null;filed:string;source_url:string;source_sha256:string};
export type CashPeriod={id:string;label?:string;start:string;end:string;method:string;operand_ids?:string[];statement_source_url?:string;excluded_note_facts?:Record<string,{fact:CashFact;reason:string}>;values:CashValues;evidence:Record<string,CashFact|{method:string;terms:{coefficient:number;period_id:string}[]}|null>};
export type PPEKey=string;
export type PPEBalance={year:string;date:string;values:Record<PPEKey,number>;evidence:Record<PPEKey,CashFact>;servers_network_share_approx:number|null;composition_basis:string};
export type CashAllocationReport={schema_version:1;policy:string;ticker:string;as_of:string;currency:'USD';extension_manifest_sha256:string;company_facts_sha256:string;history_snapshot_sha256:string;history_source_snapshot_sha256:string;basis:string;annual:CashPeriod[];quarterly:CashPeriod[];ttm:CashPeriod[];reported_periods:Record<string,CashPeriod>;ppe:PPEBalance[];ppe_categories?:{id:string;label:string}[];statement_evidence?:Record<string,{source_url:string;sha256:string;concepts:string[]}>;sources:Record<string,{source_url:string;filed:string;sha256:string}>;limitations:string[]};
export type AllocationMode='annual'|'quarterly'|'ttm';
export const cashLabels:Record<CashKey,string>={marketableMaturities:'Marketable securities maturities',commercialPaper:'Net commercial-paper proceeds / repayments',financeLeasePayments:'Finance-lease principal repayments',heldForSalePurchases:'Purchases of held-for-sale assets',ventureDistributions:'Venture distribution',bankOverdrafts:'Net bank-overdraft proceeds / repayments',ppeSales:'Property & equipment sale proceeds',cfo:'Operating cash flow',ppe:'Property & equipment purchases',marketablePurchases:'Marketable securities purchases',marketableSales:'Marketable maturities & sales',otherPurchases:'Non-marketable securities purchases',otherSales:'Non-marketable maturities & sales',acquisitions:'Acquisitions & intangible assets',otherInvesting:'Other investing activities',investing:'Net investing cash flow',awards:'Net stock-award payments',buybacks:'Share repurchases',dividends:'Dividend payments',debtProceeds:'Debt proceeds, net of issuance costs',debtRepayments:'Debt & capital-lease repayments',minority:'Sales of subsidiary interests',commonIssued:'Common stock issued',preferredIssued:'Convertible preferred stock issued',otherFinancing:'Other financing activities',financing:'Net financing cash flow',fx:'Exchange-rate effect',change:'Change in cash',opening:'Opening cash',closing:'Closing cash'};
const optional=new Set<CashKey>(['dividends','minority','commonIssued','preferredIssued','otherFinancing']);
const paymentKeys=new Set<CashKey>(['ppe','marketablePurchases','otherPurchases','acquisitions','otherInvesting','awards','buybacks','dividends','debtRepayments','financeLeasePayments','heldForSalePurchases']);
const investing:CashKey[]=['ppe','marketablePurchases','marketableSales','otherPurchases','otherSales','acquisitions','otherInvesting','marketableMaturities','heldForSalePurchases','ventureDistributions','ppeSales'];
const financing:CashKey[]=['awards','buybacks','dividends','debtProceeds','debtRepayments','minority','commonIssued','preferredIssued','otherFinancing','commercialPaper','financeLeasePayments','bankOverdrafts'];
export const cashAmount=(r:CashPeriod,k:CashKey)=>r.values[k]??0;
const keys:CashKey[]=[...flowKeys,'opening','closing'];
export const supportedAllocationTickers=['GOOGL','AAPL','META'];
export const reportFlowKeys=(p:CashAllocationReport)=>p.ticker==='GOOGL'?flowKeys:issuerFlowKeys;
const issuerRequired=new Set<CashKey>(['cfo','ppe','marketablePurchases','marketableSales','otherInvesting','investing','awards','buybacks','financing','change','opening','closing']);
function requireValue(ok:unknown,message:string):asserts ok{if(!ok)throw Error(message);}
export function reconcileCash(r:CashPeriod,issuer=false){
 for(const k of issuer?[...issuerFlowKeys,'opening','closing'] as CashKey[]:keys)requireValue(r.values[k]===null?(issuer?!issuerRequired.has(k):optional.has(k)):Number.isSafeInteger(r.values[k]),'Missing or unsafe cash amount');
 const n=(k:CashKey)=>cashAmount(r,k);
 requireValue(investing.reduce((s,k)=>s+n(k),0)===n('investing'),'Investing reconciliation failed');
 requireValue(financing.reduce((s,k)=>s+n(k),0)===n('financing'),'Financing reconciliation failed');
 requireValue(n('cfo')+n('investing')+n('financing')+n('fx')===n('change'),'Cash movement reconciliation failed');
 requireValue(n('opening')+n('change')===n('closing'),'Closing cash reconciliation failed');
}
export function validateAllocation(value:unknown,ticker:string,history:QuarterlyReport):CashAllocationReport{
 const p=value as CashAllocationReport;
 const config=({GOOGL:{policy:'alphabet-cash-allocation-v2',cik:1652044,years:5,quarters:23},AAPL:{policy:'aapl-cash-allocation-v1',cik:320193,years:6,quarters:24},META:{policy:'meta-cash-allocation-v1',cik:1326801,years:5,quarters:23}} as Record<string,{policy:string;cik:number;years:number;quarters:number}>)[ticker];
 requireValue(config&&p?.schema_version===1&&p.policy===config.policy&&p.ticker===ticker&&history.ticker===ticker&&p.currency==='USD'&&p.as_of===history.as_of&&p.history_source_snapshot_sha256===history.source_snapshot_sha256&&/^[a-f0-9]{64}$/.test(p.history_snapshot_sha256),'Unsupported cash-allocation package');
 requireValue(p.annual?.length===config.years&&p.quarterly?.length===config.quarters&&p.ttm?.length===config.quarters-3&&p.ppe?.length===2&&p.sources&&p.reported_periods,'Incomplete cash-allocation history');
 const issuer=ticker!=='GOOGL',flows=reportFlowKeys(p),selectedKeys:CashKey[]=[...flows,'opening','closing'];
 const sources=Object.values(p.sources);
 if(issuer)requireValue(p.statement_evidence&&Object.keys(p.statement_evidence).length===Object.keys(p.sources).length,'Missing primary cash-flow statements');
 const validateFact=(f:CashFact)=>{requireValue(f&&Number.isSafeInteger(f.value)&&Number.isSafeInteger(f.reported_value)&&(f.sign===1||f.sign===-1)&&f.reported_value*f.sign===f.value&&Array.isArray(f.context_ids)&&f.context_ids.length&&Array.isArray(f.dimensions)&&f.filed<=p.as_of&&f.source_url.startsWith(`https://www.sec.gov/Archives/edgar/data/${config.cik}/`)&&sources.some(s=>s.source_url===f.source_url&&s.sha256===f.source_sha256&&s.filed===f.filed),'Invalid cash-flow source evidence');};
 for(const [id,r]of Object.entries(p.reported_periods)){
  requireValue(r.id===id&&r.method==='reported'&&r.start<r.end,'Invalid reported period');reconcileCash(r,issuer);
  if(issuer){const statement=p.statement_evidence![id.split(':')[0]];requireValue(statement&&r.statement_source_url===statement.source_url&&/^[a-f0-9]{64}$/.test(statement.sha256)&&statement.source_url.startsWith(`https://www.sec.gov/Archives/edgar/data/${config.cik}/`)&&statement.concepts.length>0,'Invalid cash-flow statement role');for(const k of flows){const f=r.evidence[k]as CashFact|null;if(f)requireValue(statement.concepts.some(c=>c.split(':').at(-1)===f.concept.split('}').at(-1)),'Note-only fact counted as a statement component');}}
  for(const k of selectedKeys){const f=r.evidence[k] as CashFact|null;if(r.values[k]===null){requireValue(f===null&&(issuer?!issuerRequired.has(k):optional.has(k)),'Missing caption has false evidence');continue;}validateFact(f!);requireValue(f!.dimensions.length===0&&f!.sign===(paymentKeys.has(k)?-1:1)&&f!.value===r.values[k]&&(k==='opening'?f!.instant===new Date(Date.parse(r.start+'T00:00:00Z')-86400000).toISOString().slice(0,10):k==='closing'?f!.instant===r.end:f!.start===r.start&&f!.end===r.end),'Wrong cash-flow context');}
 }
 const assertDerived=(r:CashPeriod,inputs:CashPeriod[],coeffs:number[])=>{
  reconcileCash(r,issuer);
  requireValue(r.operand_ids?.length===inputs.length&&inputs.every((v,i)=>v&&r.operand_ids![i]===v.id),'Wrong derivation operands');
  for(const k of flows){const present=inputs.some(q=>q.values[k]!==null),expected=present?inputs.reduce((n,q,i)=>n+cashAmount(q,k)*coeffs[i],0):null;requireValue(r.values[k]===expected,'Derived cash amount contradicts operands');}
  requireValue(r.values.opening===(coeffs.every(c=>c===1)?inputs[0].values.opening:inputs[1].values.closing)&&r.values.closing===(coeffs.every(c=>c===1)?inputs.at(-1)!.values.closing:inputs[0].values.closing),'Wrong opening/closing balance');
 };
 const annuals=history.validation.annual_tie_outs as {metric:string;fiscal_year:number;annual:{accession:string;start:string;end:string;value:number}}[];
 const expectedAnnuals=annuals.filter(a=>a.metric==='cfo'&&a.fiscal_year>=2021).sort((a,b)=>a.fiscal_year-b.fiscal_year);
 for(const [i,r]of p.annual.entries()){const a=expectedAnnuals[i];requireValue(a&&r.id===`FY${a.fiscal_year}`&&r.start===a.annual.start&&r.end===a.annual.end&&r.values.cfo===a.annual.value,'Wrong annual cohort');assertDerived(r,r.operand_ids!.map(id=>p.reported_periods[id]),[1]);requireValue(r.operand_ids![0].startsWith(a.annual.accession+':'),'Wrong annual accession');}
 const early=({GOOGL:{starts:['2021-01-01','2021-04-01','2021-07-01'],ends:['2021-03-31','2021-06-30','2021-09-30'],accessions:['0001652044-21-000020','0001652044-21-000047','0001652044-21-000057']},META:{starts:['2021-01-01','2021-04-01','2021-07-01'],ends:['2021-03-31','2021-06-30','2021-09-30'],accessions:['0001326801-21-000033','0001326801-21-000049','0001326801-21-000065']},AAPL:{starts:['2020-09-27','2020-12-27','2021-03-28','2021-06-27'],ends:['2020-12-26','2021-03-27','2021-06-26','2021-09-25'],accessions:['0000320193-21-000010','0000320193-21-000056','0000320193-21-000065',expectedAnnuals[0].annual.accession]}} as Record<string,{starts:string[];ends:string[];accessions:string[]}>)[ticker];
 requireValue(/^[a-f0-9]{64}$/.test(p.extension_manifest_sha256)&&/^[a-f0-9]{64}$/.test(p.company_facts_sha256),'Missing extension evidence');
 for(const [i,r]of p.quarterly.entries()){
  const h=history.rows.find(h=>h.id===r.id),quarter=i%4+1;
  requireValue(r.id===`FY${2021+Math.floor(i/4)}-Q${quarter}`,'Wrong fiscal quarter identity');
  const ids=h?h.evidence.cfo.operands.map(o=>`${o.accession}:${o.start}:${o.end}`):early.accessions.slice(Math.max(0,i-1),i+1).reverse().map((a,j)=>`${a}:${early.starts[0]}:${early.ends[i-j]}`);
  if(!h)requireValue(i<early.starts.length&&r.start===early.starts[i]&&r.end===early.ends[i],'Wrong FY2021 extension period');
  else requireValue(r.start===h.start&&r.end===h.end&&r.values.cfo===h.values.cfo&&-cashAmount(r,'ppe')===h.values.cash_capex,'Cash history contradicts accepted quarter');
  requireValue(r.operand_ids?.join('|')===ids.join('|'),'Wrong quarterly filing operands');
  if(i)requireValue(Date.parse(p.quarterly[i-1].end+'T00:00:00Z')+86400000===Date.parse(r.start+'T00:00:00Z'),'Nonconsecutive cash-allocation quarters');
  assertDerived(r,ids.map(id=>p.reported_periods[id]),ids.length===1?[1]:[1,-1]);
 }
 for(const a of p.annual){const rows=p.quarterly.filter(q=>q.id.startsWith(a.id+'-'));requireValue(rows.length===4,'Incomplete cash-allocation annual cohort');for(const k of flows)requireValue(rows.reduce((sum,q)=>sum+cashAmount(q,k),0)===cashAmount(a,k),'Annual cash-allocation quarter tie failed');}
 for(const [i,r]of p.ttm.entries()){const input=p.quarterly.slice(i,i+4);requireValue(r.id===input[3].id&&r.start===input[0].start&&r.end===input[3].end,'Wrong TTM window');assertDerived(r,input,[1,1,1,1]);}
 const categorySpecs:Record<string,[string,string,string|null][]>= {
 AAPL:[['landBuildings','Land and buildings','LandAndBuildingMember'],['machinery','Machinery, equipment & internal-use software','MachineryEquipmentAndInternalUseSoftwareMember'],['leasehold','Leasehold improvements','LeaseholdImprovementsMember']],
 META:[['land','Land','LandMember'],['servers','Servers and network assets','ServersAndNetworkAssetsComponentsStoredBySuppliersMember'],['buildings','Buildings','BuildingMember'],['leasehold','Leasehold improvements','LeaseholdImprovementsMember'],['equipment','Equipment and other','EquipmentAndOtherMember'],['financeLeases','Finance-lease right-of-use assets',null],['pending','Construction in progress','ConstructionInProgressMember']]};
 if(issuer){const spec=categorySpecs[ticker];requireValue(p.ppe_categories?.length===spec.length&&p.ppe_categories.every((c,i)=>c.id===spec[i][0]&&c.label===spec[i][1]),'Unreviewed PP&E categories');}
 for(const [i,r]of p.ppe.entries()){
  const v=r.values,a=expectedAnnuals[expectedAnnuals.length-2+i];
  requireValue(r.year===String(a.fiscal_year)&&r.date===a.annual.end&&r.composition_basis,'Unreviewed PP&E balance date');
  requireValue(Object.values(v).every(n=>Number.isSafeInteger(n)&&n>=0),'Unsafe PP&E amount');
  if(!issuer)requireValue(r.servers_network_share_approx===0.6&&Object.keys(v).length===7&&v.technical+v.office+v.other===v.service&&v.service+v.pending-v.depreciation===v.net,'PP&E does not reconcile');
  else requireValue(r.servers_network_share_approx===null&&Object.keys(v).length===categorySpecs[ticker].length+3&&categorySpecs[ticker].reduce((sum,[k])=>sum+v[k],0)===v.gross&&v.gross-v.depreciation===v.net,'PP&E does not reconcile');
  for(const k of Object.keys(v)){
   const f=r.evidence[k];validateFact(f);requireValue(f.value===v[k]&&f.instant===r.date&&f.sign===1,'Wrong PP&E evidence date');
   const members:Record<string,string>={technical:'TechnicalInfrastructureMember',office:'OfficeSpaceMember',other:'CorporateAndOtherAssetsMember',service:'DepreciablePropertyPlantAndEquipmentMember',pending:'AssetUnderConstructionMember'};
   const member=issuer?categorySpecs[ticker].find(([id])=>id===k)?.[2]:members[k];
   requireValue(member?f.dimensions.length===1&&f.dimensions[0][0].endsWith('}PropertyPlantAndEquipmentByTypeAxis')&&f.dimensions[0][1].endsWith('}'+member):f.dimensions.length===0,'Wrong PP&E dimensions');
  }
 }

 return p;
}
export async function fetchAllocation(ticker:string,history:QuarterlyReport,signal:AbortSignal){
 const response=await fetch(`${(import.meta as ImportMeta & {env:{BASE_URL:string}}).env.BASE_URL}cash-allocation/${ticker}.json`,{signal});
 if(!response.ok)throw Error('Cash allocation unavailable');
 return validateAllocation(await response.json(),ticker,history);
}
export type AllocationNode={id:string;label:string;flow:number;value:number;kind:string;lines:[string,number][];copy:string;color:string};
export function allocationLabels(ticker:string){return {...cashLabels,...(ticker!=='GOOGL'?{awards:'Taxes paid on net settlement of equity awards'}:{}),...(ticker==='AAPL'?{acquisitions:'Acquisitions, net of cash acquired',otherPurchases:'Other investment purchases',otherSales:'Other investment sales / proceeds'}:{})};}
export function allocationModel(row:CashPeriod,ticker='GOOGL'){
 const names=allocationLabels(ticker);
 const n=(k:CashKey)=>cashAmount(row,k),nodes:AllocationNode[]=[];
 const add=(id:string,label:string,flow:number,fields:CashKey[],copy:string,color:string,reverse=false)=>{if(!flow)return;nodes.push({id,label,flow,value:Math.abs(flow),kind:flow>0?'Cash source':'Cash use',lines:fields.filter(k=>row.values[k]!==null&&row.values[k]!==undefined).map(k=>[names[k],n(k)*(reverse?-1:1)]),copy,color});};
 add('cfo','Operating cash flow',n('cfo'),['cfo'],'Net cash from operating activities, after the operating-cash reconciliation.','#21485a');
 const debt=n('debtProceeds')+n('debtRepayments')+n('commercialPaper')+n('financeLeasePayments')+n('bankOverdrafts');add('debt',debt>=0?'Net debt raised':'Net debt repaid',debt,['debtProceeds','debtRepayments','commercialPaper','financeLeasePayments','bankOverdrafts'],'Net debt, commercial-paper and overdraft cash flows, including separately reported finance-lease principal repayments.','#7a8d98');
 add('minority','Subsidiary interests sold',n('minority'),['minority'],'Financing proceeds from sales of subsidiary interests.','#88778d');
 add('business','Business investment',n('ppe')+n('acquisitions'),['ppe','acquisitions'],ticker==='AAPL'?'Cash PP&E plus acquisitions net of cash acquired.':'Cash PP&E plus acquisitions net of cash acquired and intangible-asset purchases.','#a48031',true);
 add('returns','Shareholder returns',n('buybacks')+n('dividends'),['buybacks','dividends'],'Stock repurchases and reported dividends; stock-award payments are separate.','#21485a',true);
 const securities=n('marketablePurchases')+n('marketableSales')+n('marketableMaturities')+n('otherPurchases')+n('otherSales');add('securities',securities<=0?'Net securities investment':'Net securities released',securities,['marketablePurchases','marketableSales','marketableMaturities','otherPurchases','otherSales'],'Net cash flows from reported securities and other financial-investment captions, separate from PP&E and acquisitions.','#397965');
 add('awards',ticker==='GOOGL'?'Stock-award payments':'Equity-award tax payments',n('awards'),['awards'],ticker==='GOOGL'?'Financing cash payments related to stock-based awards, separate from noncash SBC expense.':'Reported taxes paid on net share settlement of equity awards, separate from noncash SBC and share repurchases.','#88778d',true);
 add('other','Other investing',n('otherInvesting'),['otherInvesting'],'The reported other-investing caption, not a balancing residual.','#7a8d98');
 add('equity','Equity issued',n('commonIssued')+n('preferredIssued'),['commonIssued','preferredIssued'],'Separately reported common and convertible-preferred issuance proceeds.','#397965');
 add('finOther','Other financing',n('otherFinancing'),['otherFinancing'],'The separately reported other-financing caption.','#7a8d98');
 add('disposals','Asset sale proceeds',n('ppeSales'),['ppeSales'],'Reported cash proceeds from sales of property and equipment.','#7a8d98');
 add('heldAssets','Held-for-sale assets',n('heldForSalePurchases'),['heldForSalePurchases'],'Separately reported purchases of held-for-sale assets, not ordinary cash PP&E capex.','#a48031',true);
 add('venture','Venture distribution',n('ventureDistributions'),['ventureDistributions'],'Separately reported venture cash distribution, not operating cash flow.','#397965');
 const beforeFX=n('cfo')+n('investing')+n('financing');add('retained',beforeFX>=0?'Cash added before FX':'Cash drawn before FX',-beforeFX,[],'Positive accumulation is a use; a drawdown is a source. Exchange-rate effects appear in the cash-balance reconciliation.','#183b4b');
 const retained=nodes.find(n=>n.id==='retained');if(retained)retained.lines=[['Net cash flow before FX',beforeFX],...(row.values.fx===null?[]:[['Exchange-rate effect',n('fx')] as [string,number]]),['Reported change in cash',n('change')]];
 const sources=nodes.filter(n=>n.flow>0),uses=nodes.filter(n=>n.flow<0),pool=sources.reduce((s,n)=>s+n.value,0);
 requireValue(pool===uses.reduce((s,n)=>s+n.value,0)&&pool>0,'Allocation pool does not reconcile');
 return{nodes,sources,uses,pool,beforeFX,business:-(n('ppe')+n('acquisitions')),returns:-(n('buybacks')+n('dividends'))};
}
