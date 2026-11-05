import {D,financingNumber as number,keys,requireInput,clone,sum,type Doc} from './decimal';
import {runCase,validateCase,selectedMethod,operatingYear,type EngineData} from './case';
export const fundingFields=['interest_expense_usd','cash_debt_issued_usd','new_finance_asset_funding_usd','principal_repaid_usd'];
export function validateFcfe(doc:Doc,data:EngineData){
 keys(doc,['schema_version','base_case','scope','cost_of_equity','opening_debt_usd','financing_years','terminal_growth','terminal_financing'],'fcfe');
 requireInput(doc.schema_version==='fcfe-forecast-request-v1'&&['DECLARED_PARENT_COMMON','CONSOLIDATED_BEFORE_NCI_ATTRIBUTION'].includes(doc.scope),'fcfe: supported schema and explicit ownership scope required');
 validateCase(doc.base_case,data);requireInput(!doc.base_case.bridge&&selectedMethod(doc.base_case).method==='perpetual_growth','fcfe.base_case: operating perpetual-growth case required');
 number(doc.cost_of_equity,'cost_of_equity','0.000001',1);number(doc.opening_debt_usd,'opening_debt_usd',0);requireInput(number(doc.terminal_growth,'terminal_growth','-0.99').lt(doc.cost_of_equity),'terminal_growth: must be below cost of equity');
 requireInput(Array.isArray(doc.financing_years)&&doc.financing_years.length===doc.base_case.forecast_years.length,'financing_years: one explicit row per year required');
 doc.financing_years.forEach((r:Doc,i:number)=>{keys(r,['period_index',...fundingFields],'financing_years');requireInput(r.period_index===i+1,'financing_years: consecutive indices required');fundingFields.forEach(k=>number(r[k],k,0));});
 keys(doc.terminal_financing,fundingFields,'terminal_financing');fundingFields.forEach(k=>number(doc.terminal_financing[k],k,0));
}
export function financingBridge(o:Doc,taxRate:string,f:Doc,opening:any):Doc{
 const ebit=new D(o.ebit),da=new D(o.d_and_a),investment=new D(o.investment),wc=new D(o.working_capital_cash_requirement),base=new D(o.fcff),tax=new D(taxRate),debt=new D(opening);
 requireInput(ebit.minus(D.max(ebit,0).times(tax)).plus(da).minus(investment).minus(wc).eq(base),'fcfe: operating FCFF component mismatch');
 const [interest,issue,assets,repay]=fundingFields.map(k=>new D(f[k]));
 requireInput(!interest.gt(0)||debt.plus(issue).plus(assets).gt(0),'interest_expense_usd: interest requires identified financing');requireInput(assets.lte(investment),'new_finance_asset_funding_usd: exceeds matched investment');
 const closing=debt.plus(issue).plus(assets).minus(repay);requireInput(closing.gte(0),'principal_repaid_usd: exceeds opening debt and financing');
 const unleveredTax=D.max(ebit,0).times(tax),equityTax=D.max(ebit.minus(interest),0).times(tax),shield=unleveredTax.minus(equityTax),income=ebit.minus(interest).minus(equityTax),borrowing=issue.plus(assets).minus(repay);
 const fcfe=income.plus(da).minus(investment).minus(wc).plus(borrowing),other=base.minus(interest).plus(shield).plus(borrowing),rounding=fcfe.minus(other);
 const magnitude=sum([ebit,da,investment,wc,base,interest,borrowing,unleveredTax,equityTax,shield,income,fcfe,other].map(v=>v.abs()));const envelope=new D(8).times(new D(10).pow((magnitude.isZero()?0:magnitude.e)-49));requireInput(rounding.abs().lte(envelope),'Independent income/FCFF financing bridges disagree');
 return {...Object.fromEntries(fundingFields.map(k=>[k,String(f[k])])),opening_debt_usd:debt.toString(),closing_debt_usd:closing.toString(),net_borrowing_usd:borrowing.toString(),interest_tax_shield_usd:shield.toString(),equity_tax_usd:equityTax.toString(),net_income_usd:income.toString(),fcff_usd:base.toString(),fcfe_usd:fcfe.toString(),...(!rounding.isZero()?{income_bridge_rounding_difference_usd:rounding.toString(),income_bridge_rounding_envelope_usd:envelope.toString(),rounding_difference_is_cash_adjustment:false}:{})};
}
export function runFcfe(doc:Doc,data:EngineData):Doc{
 validateFcfe(doc,data);const base=runCase(doc.base_case,data),ke=new D(doc.cost_of_equity),growth=new D(doc.terminal_growth);let debt=new D(doc.opening_debt_usd),pv=new D(0);
 const rows=base.stage_b.stage_a.years.map((o:Doc,i:number)=>{const row=financingBridge(o,doc.base_case.forecast_years[i].forecast_tax_rate,doc.financing_years[i],debt);debt=new D(row.closing_debt_usd);const factor=new D(1).div(new D(1).plus(ke).pow(i+1)),value=new D(row.fcfe_usd).times(factor);pv=pv.plus(value);return {period_index:i+1,fiscal_year_label:o.fiscal_year_label,...row,discount_factor:factor.toString(),pv_fcfe_usd:value.toString()};});
 const t=selectedMethod(doc.base_case).terminal,revenue=new D(base.stage_b.stage_a.years.at(-1).revenue).times(new D(1).plus(growth));
 const terminal=financingBridge(operatingYear(rows.length+1,'Independent FCFE terminal',revenue,t),t.operating_tax_rate,doc.terminal_financing,debt);
 requireInput(new D(terminal.net_borrowing_usd).minus(debt.times(growth)).abs().lte('0.000001'),'terminal_financing: net financing must equal final debt × terminal growth');requireInput(new D(terminal.fcfe_usd).gt(0),'terminal_financing: positive sustainable terminal FCFE required');
 const tv=new D(terminal.fcfe_usd).div(ke.minus(growth)),pvtv=tv.div(new D(1).plus(ke).pow(rows.length));
 return {schema_version:'fcfe-forecast-result-v1',submitted_inputs:clone(doc),scope:doc.scope,semantic_input_review:'USER_ASSUMPTIONS_NOT_INDEPENDENTLY_CERTIFIED',years:rows,terminal,cost_of_equity:doc.cost_of_equity,pv_explicit_fcfe_usd:pv.toString(),terminal_equity_value_usd:tv.toString(),pv_terminal_equity_usd:pvtv.toString(),equity_value_usd:pv.plus(pvtv).toString(),value_per_share:null,debt_subtracted_after_fcfe_discounting:false,limitations:data.metadata.fcfeLimitations};
}
