import {browserEnabled} from './browser-engine/mode';
export class ApiError extends Error {
  constructor(public code: string, message: string, public details: string[] = []) { super(message); }
}
export const unavailableMessage = 'Calculations are temporarily unavailable. Your inputs are still here. Please try again later.';
export const timeoutMessage = browserEnabled() ? 'The calculation exceeded the on-device waiting limit and was stopped. Your inputs are still here. Please retry explicitly.' : 'The calculation exceeded the waiting limit. Your inputs are still here. Please retry explicitly; server work may continue until its own deadline.';
export function failureMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.code === 'busy') return 'Another calculation is in progress. Your inputs are still here. Please retry shortly.';
    if (error.code === 'deadline_exceeded') return timeoutMessage;
    if (error.code === 'request_cancelled') return error.message;
    if (['service_unavailable', 'connection_error', 'http_error', 'not_ready', 'shutting_down', 'calculation_failed', 'worker_failed', 'internal_error'].includes(error.code)) return unavailableMessage;
    return `${error.code}: ${error.message}`;
  }
  return unavailableMessage;
}
// Render-boundary shape checks only; numerical validation belongs to the selected engine.
const object = (value: unknown): value is Record<string, unknown> => value !== null && typeof value === 'object' && !Array.isArray(value);
const text = (value: unknown): value is string => typeof value === 'string';
const decimal = (value: unknown) => text(value) && /^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$/.test(value);
function renderableResult(data: Record<string, unknown>, requireEquity: boolean): boolean {
  const b = data.stage_b, submitted = data.submitted_inputs;
  if (!text(data.case_name) || !text(data.input_basis) || !Array.isArray(data.limitations) || !data.limitations.every(text) || !object(submitted)) return false;
  if (object(submitted.preparation) ? !text(submitted.preparation.timestamp_utc) || !(submitted.preparation.notes === null || text(submitted.preparation.notes)) : !object(submitted.analyst) || !text(submitted.analyst.rationale) || !text(submitted.scope)) return false;
  if (!object(b) || !object(b.stage_a) || (b.terminal_method==='exit_multiple'?(!object(b.terminal_basis)||!decimal(b.terminal_basis.year_five_ebit??b.terminal_basis.final_year_ebit)||!decimal(b.terminal_basis.exit_ev_ebit_multiple)||b.terminal!==undefined):(!object(b.terminal)||!decimal(b.terminal.fcff))) || !object(b.timing) || !text(b.timing.notice) || !text(b.timing.analytical_t0)) return false;
  if (!['enterprise_value','pv_explicit_fcff','pv_terminal_value','terminal_value'].every(key => decimal(b[key]))) return false;
  const horizon=submitted.schema_version==='investor-case-v4'||submitted.schema_version==='analyst-case-v4'?10:5;
  if(horizon===10&&submitted.forecast_horizon!==10)return false;
  if (!Array.isArray(b.stage_a.years) || b.stage_a.years.length !== horizon || !b.stage_a.years.every(y => object(y) && text(y.fiscal_year_label) && ['revenue','ebit','tax','nopat','d_and_a','investment','working_capital_cash_requirement','fcff'].every(key => decimal(y[key])))) return false;
  if (!Array.isArray(b.years) || b.years.length !== horizon || !b.years.every(y => object(y) && decimal(y.discount_factor) && decimal(y.pv_fcff))) return false;
  if(submitted.schema_version==='investor-case-v3'||submitted.schema_version==='analyst-case-v3'||submitted.schema_version==='investor-case-v4'||submitted.schema_version==='analyst-case-v4'){
    const method=object(submitted.terminal_valuation)?submitted.terminal_valuation.method:null,comparison=data.terminal_comparison;
    if(!['perpetual_growth','exit_multiple'].includes(String(method))||b.terminal_method!==method||!object(comparison)||comparison.selected_method!==method||!object(comparison.submitted_inputs)||!object(comparison.results))return false;
    for(const name of ['perpetual_growth','exit_multiple']){
      const entry=comparison.results[name];if(!object(entry))return false;
      if(entry.status==='CURRENT'){if(!object(entry.stage_b)||entry.stage_b.terminal_method!==name||!['enterprise_value','pv_explicit_fcff','pv_terminal_value','terminal_value'].every(k=>decimal(entry.stage_b&&object(entry.stage_b)?entry.stage_b[k]:undefined)))return false;}
      else if(entry.status!=='AWAITING_INPUTS'||name===method||!text(entry.reason))return false;
    }
    if(!(comparison.ev_difference_exit_minus_perpetual===null||decimal(comparison.ev_difference_exit_minus_perpetual)))return false;
    const implied=comparison.implied_year_five_ev_ebit??comparison.implied_final_year_ev_ebit;
    if(implied!==undefined&&(!object(implied)||!(implied.value===null||decimal(implied.value))||!(implied.reason===null||text(implied.reason))))return false;
  }
  const c = data.stage_c;
  if (c === undefined) return !requireEquity;
  if (!object(c) || !object(c.inputs) || !object(c.inputs.shares) || !object(c.stage_b) || !decimal(c.stage_b.enterprise_value)) return false;
  if (!['eligible_assets','financing_claims','other_equity_claims','equity_value','valuation_shares','value_per_share'].every(key => decimal(c[key]))) return false;
  const shares = c.inputs.shares;
  return ['class_id','observation_date','rationale'].every(key => text(shares[key])) &&
    Array.isArray(c.inputs.observations) && c.inputs.observations.every(o => object(o) && ['observation_id','disposition','rationale'].every(key => text(o[key]))) &&
    Array.isArray(c.contributions) && c.contributions.every(line => object(line) && object(line.component) && text(line.component.component_id) && decimal(line.signed_contribution));
}
function renderableSensitivity(data:Record<string,unknown>):boolean{
 if(!['investor-sensitivity-results-v1','investor-sensitivity-results-v2','analyst-sensitivity-results-v1','investor-sensitivity-results-v3'].includes(String(data.schema_version))||!object(data.submitted_inputs)||!object(data.selected_case)||!object(data.reference_result)||!object(data.selection)||!text(data.selection.analytical_date)||!(data.selection.information_cutoff===null||text(data.selection.information_cutoff))||!text(data.held_fixed)||!Array.isArray(data.limitations)||!data.limitations.every(text))return false;
 const equity=data.selected_case.calculation_scope==='EQUITY_PER_SHARE';
 if(!renderableResult(data.reference_result,equity))return false;
 const exit=data.schema_version==='investor-sensitivity-results-v3',w=data.wacc_values,g=exit?data.exit_ev_ebit_multiple_values:data.terminal_growth_values,rows=data.cells;
 if(!Array.isArray(w)||!Array.isArray(g)||!w.length||!g.length||w.length>11||g.length>11||!w.every(decimal)||!g.every(decimal)||!Array.isArray(rows)||rows.length!==w.length)return false;
 return rows.every((row,i)=>Array.isArray(row)&&row.length===g.length&&row.every((cell,j)=>{
  if(!object(cell)||cell.wacc!==w[i]||(exit?cell.exit_ev_ebit_multiple:cell.terminal_growth)!==g[j]||!object(cell.metrics))return false;
  const m=cell.metrics;if(cell.status==='INVALID')return text(cell.reason)&&cell.changes===null&&Object.values(m).every(v=>v===null);
  return cell.status==='VALID'&&['enterprise_value','pv_explicit_fcff','pv_terminal_value','terminal_value',...(exit?[object(data.selected_case)&&data.selected_case.schema_version==='investor-case-v4'?'final_year_ebit':'year_five_ebit']:['terminal_revenue','terminal_fcff'])].every(k=>decimal(m[k]))&&(m.terminal_contribution===null||decimal(m.terminal_contribution))&&text(m.terminal_contribution_note)&&(equity?decimal(m.equity_value)&&decimal(m.value_per_share):m.equity_value===null&&m.value_per_share===null);
 }));
}
function renderableReverse(data:Record<string,unknown>):boolean{
 if(!['analyst-reverse-dcf-results-v1','investor-reverse-dcf-results-v1','investor-reverse-dcf-results-v2'].includes(String(data.schema_version))||!object(data.submitted_inputs)||!object(data.selected_case)||!object(data.reference_result)||!object(data.selection)||!text(data.selection.analytical_date)||!(data.selection.information_cutoff===null||text(data.selection.information_cutoff))||!text(data.held_fixed)||!text(data.reason)||!object(data.monotonicity)||!text(data.monotonicity.direction)||!text(data.monotonicity.reason)||!object(data.numerical_policy)||!Number.isInteger(data.iterations)||!Number.isInteger(data.evaluations)||!Array.isArray(data.limitations)||!data.limitations.every(text))return false;
 const target=data.submitted_inputs.target,bounds=data.submitted_inputs.growth_bounds;if(!object(target)||!decimal(target.amount)||!['USD','USD/share'].includes(String(target.unit))||!text(target.date)||!object(bounds)||!decimal(bounds.lower)||!decimal(bounds.upper))return false;
 const equity=target.metric==='VALUE_PER_SHARE';if(!renderableResult(data.reference_result,equity))return false;
 const bracket=data.final_bracket;if(bracket!==null&&(!object(bracket)||!['lower_growth','upper_growth','width'].every(k=>decimal(bracket[k]))))return false;
 if(data.status!=='SUCCESS')return ['UNREACHABLE_TARGET','FLAT_RESPONSE','UNIQUENESS_NOT_CERTIFIED','ITERATION_LIMIT','NUMERICAL_VERIFICATION_FAILED'].includes(String(data.status))&&data.solution===null;
 const v=data.solution;return object(v)&&['constant_annual_growth','achieved_metric','signed_residual','absolute_residual','residual_tolerance'].every(k=>decimal(v[k]))&&typeof v.exact_endpoint==='boolean'&&object(v.forward_result)&&renderableResult(v.forward_result,equity);
}
function renderableAppleAnalyst(data:Record<string,unknown>):boolean{
 if(data.schema_version!=='apple-analyst-result-v1'||data.ticker!=='AAPL'||!text(data.policy_version)||!text(data.model_origin)||!object(data.assumptions)||!object(data.submitted_inputs)||data.submitted_inputs.schema_version!=='apple-analyst-request-v1'||data.exact_full_historical_fcfe_claim!==false||data.automatic_history_calibration!==false)return false;
 if(!Array.isArray(data.readiness)||data.readiness.length!==5||!data.readiness.every(r=>object(r)&&text(r.id)&&text(r.label)&&r.status==='ANALYST_READY_WITH_QUALIFICATIONS'&&text(r.detail)))return false;
 if(!Array.isArray(data.historical)||data.historical.length!==5||!data.historical.every((r,i)=>object(r)&&r.fiscal_year===2021+i&&['fcff_usd','fcfe_usd','economic_fcfe_usd','other_financing_usd'].every(k=>decimal(r[k]))))return false;
 if(!object(data.fcff)||!['enterprise_value_usd','equity_value_usd','value_per_share_usd','wacc'].every(k=>decimal(object(data.fcff)?data.fcff[k]:null))||!object(data.fcfe)||!['operating_equity_value_usd','equity_value_usd','value_per_share_usd','cost_of_equity'].every(k=>decimal(object(data.fcfe)?data.fcfe[k]:null))||data.fcfe.debt_subtracted_after_fcfe_discounting!==false)return false;
 return Array.isArray(data.qualifications)&&data.qualifications.every(text)&&Array.isArray(data.source_urls)&&data.source_urls.every(text)&&Array.isArray(data.sensitivities)&&data.sensitivities.every(s=>object(s)&&text(s.label)&&decimal(s.fcff_value_per_share_usd)&&decimal(s.fcfe_value_per_share_usd));
}
function renderableCompanyAnalyst(data:Record<string,unknown>):boolean{
 if(data.schema_version!=='company-analyst-result-v1'||!['META','GOOGL'].includes(String(data.ticker))||!text(data.name)||!text(data.policy_version)||!text(data.model_origin)||!object(data.assumptions)||!object(data.submitted_inputs)||data.submitted_inputs.schema_version!=='company-analyst-request-v1'||data.submitted_inputs.ticker!==data.ticker||data.exact_full_historical_fcfe_claim!==false||data.automatic_history_calibration!==false)return false;
 if(!Array.isArray(data.readiness)||data.readiness.length!==5||!data.readiness.every(r=>object(r)&&text(r.id)&&text(r.label)&&r.status==='ANALYST_READY_WITH_QUALIFICATIONS'&&text(r.detail)))return false;
 if(!Array.isArray(data.historical)||data.historical.length!==5||!data.historical.every((r,i)=>object(r)&&r.fiscal_year===2021+i&&['fcff_usd','fcfe_usd','consolidated_fcfe_usd','economic_fcfe_usd','other_financing_usd'].every(k=>decimal(r[k]))))return false;
 if(!object(data.fcff)||!['enterprise_value_usd','equity_value_usd','value_per_share_usd','wacc'].every(k=>decimal(object(data.fcff)?data.fcff[k]:null))||!object(data.fcfe)||!['operating_equity_value_usd','equity_value_usd','value_per_share_usd','cost_of_equity'].every(k=>decimal(object(data.fcfe)?data.fcfe[k]:null))||data.fcfe.debt_subtracted_after_fcfe_discounting!==false)return false;
 return object(data.bridge)&&['gross_cash_usd','eligible_cash_usd','additional_assets_usd','nci_claim_usd','valuation_shares'].every(k=>decimal(object(data.bridge)?data.bridge[k]:null))&&Array.isArray(data.qualifications)&&data.qualifications.every(text)&&Array.isArray(data.source_urls)&&data.source_urls.every(text)&&Array.isArray(data.sensitivities)&&data.sensitivities.every(s=>object(s)&&text(s.label)&&decimal(s.fcff_value_per_share_usd)&&decimal(s.fcfe_value_per_share_usd));
}
function renderableFcfe(data:Record<string,unknown>):boolean{
 if(data.schema_version!=='fcfe-forecast-result-v1'||!object(data.submitted_inputs)||data.submitted_inputs.schema_version!=='fcfe-forecast-request-v1'||!['DECLARED_PARENT_COMMON','CONSOLIDATED_BEFORE_NCI_ATTRIBUTION'].includes(String(data.scope))||data.scope!==data.submitted_inputs.scope||data.semantic_input_review!=='USER_ASSUMPTIONS_NOT_INDEPENDENTLY_CERTIFIED'||data.value_per_share!==null||data.debt_subtracted_after_fcfe_discounting!==false||!Array.isArray(data.limitations)||!data.limitations.every(text))return false;
 const base=data.submitted_inputs.base_case;if(!object(base)||!Array.isArray(base.forecast_years)||![5,10].includes(base.forecast_years.length))return false;
 if(!['cost_of_equity','pv_explicit_fcfe_usd','terminal_equity_value_usd','pv_terminal_equity_usd','equity_value_usd'].every(k=>decimal(data[k])))return false;
 const numeric=['fcfe_usd','fcff_usd','opening_debt_usd','closing_debt_usd','net_borrowing_usd','interest_tax_shield_usd','net_income_usd','equity_tax_usd','interest_expense_usd','cash_debt_issued_usd','new_finance_asset_funding_usd','principal_repaid_usd'];
 return Array.isArray(data.years)&&data.years.length===base.forecast_years.length&&data.years.every((y,i)=>object(y)&&y.period_index===i+1&&text(y.fiscal_year_label)&&[...numeric,'discount_factor','pv_fcfe_usd'].every(k=>decimal(y[k])))&&object(data.terminal)&&numeric.every(k=>decimal(object(data.terminal)?data.terminal[k]:null));
}
export async function request<T>(path: string, body?: unknown, signal?: AbortSignal): Promise<T> {
  const controller = new AbortController();
  let timedOut = false;
  const abort = () => controller.abort();
  signal?.addEventListener('abort', abort, {once: true});
  if (signal?.aborted) controller.abort();
  const timer = setTimeout(() => {timedOut = true; controller.abort();}, 50000);
  try {
    const response = browserEnabled() ? await (await import('./browser-engine/client')).browserResponse(path,body,controller.signal) : await fetch(path, {
      method: body === undefined ? 'GET' : 'POST', signal: controller.signal,
      headers: body === undefined ? undefined : {'Content-Type': 'application/json'},
      body: body === undefined ? undefined : JSON.stringify(body), cache: 'no-store', credentials: 'omit',
    });
    // Gateway HTML and untrusted server messages never enter the review UI.
    if (response.status === 429) throw new ApiError('busy', 'Another calculation is in progress. Please retry shortly.');
    let data;
    try {data = await response.json();} catch {throw new ApiError(response.status === 504 ? 'deadline_exceeded' : 'service_unavailable', response.status === 504 ? timeoutMessage : unavailableMessage);}
    if (!data || typeof data !== 'object' || Array.isArray(data)) throw new ApiError('service_unavailable', unavailableMessage);
    if (!response.ok) {
      const error = data.error;
      const known = ['invalid_case','busy','request_too_large','deadline_exceeded','internal_error','not_ready','shutting_down','calculation_failed','worker_failed','body_timeout'];
      const code = known.includes(error?.code) ? error.code : 'http_error';
      const details = Array.isArray(error?.details) ? error.details.filter((d: unknown) => typeof d === 'string').slice(0,20).map((d: string) => d.slice(0,200)) : [];
      const message = code === 'invalid_case' ? 'Review the indicated inputs.' : code === 'request_too_large' ? 'The submitted input is too large. Reduce optional notes or component references.' : unavailableMessage;
      throw new ApiError(code, message, details);
    }
    if(path==='/api/v1/review/run'){
      if(data.schema_version!=='investor-review-result-v1'||!object(data.result)||!renderableResult(data.result,object(body)&&body.calculation_scope==='EQUITY_PER_SHARE')||!object(data.review)||!['UNAVAILABLE','SCOPE_QUALIFIED'].includes(String(data.review.status))||!decimal(data.review.model_ev)||!Array.isArray(data.review.limitations)||!data.review.limitations.every(text)||!Array.isArray(data.review.reasons)||!data.review.reasons.every(text)||!['forecast_cagr','market_cap','market_implied_ev','ev_relative_difference','market_implied_growth','growth_gap_percentage_points','equity_difference','per_share_difference'].every(k=>data.review[k]===null||decimal(data.review[k]))||!(data.review.market===null||(object(data.review.market)&&decimal(data.review.market.price)&&['session_date','timezone','delay','fallback','share_class','adjustment','source_url'].every(k=>text(data.review.market[k])))))throw new ApiError('service_unavailable',unavailableMessage);
      return data as T;
    }
    if (path.endsWith('/run')) {
      const scenarios=path==='/api/v1/scenarios/run';
      const valid=path==='/api/v1/analyst/run'?renderableCompanyAnalyst(data):path==='/api/v1/apple/analyst/run'?renderableAppleAnalyst(data):path==='/api/v1/fcfe/run'?renderableFcfe(data):path==='/api/v1/reverse/run'?renderableReverse(data):path==='/api/v1/sensitivity/run'?renderableSensitivity(data):scenarios
        ? ['investor-scenario-results-v1','investor-scenario-results-v2','analyst-scenario-results-v1','investor-scenario-results-v3'].includes(data.schema_version)&&Array.isArray(data.scenarios)&&data.scenarios.length===3&&object(data.submitted_inputs)&&Array.isArray(data.limitations)&&data.limitations.every(text)&&
          data.scenarios.every((entry:unknown,i:number)=>object(entry)&&entry.label===['Bear','Base','Bull'][i]&&text(entry.analytical_date)&&(entry.information_cutoff===null||text(entry.information_cutoff))&&object(entry.result)&&renderableResult(entry.result,object(body)&&Array.isArray(body.scenarios)&&body.scenarios.some(e=>object(e)&&object(e.case)&&e.case.calculation_scope==='EQUITY_PER_SHARE')))
        : renderableResult(data,object(body)&&body.calculation_scope==='EQUITY_PER_SHARE');
      if(!valid)throw new ApiError('service_unavailable',unavailableMessage);
    }
    return data as T;
  } catch (e) {
    if (e instanceof ApiError) throw e;
    if (controller.signal.aborted && !timedOut) throw new ApiError('request_cancelled', 'Calculation cancelled. Your inputs are still here. Retry when ready.');
    if (timedOut) throw new ApiError('deadline_exceeded', timeoutMessage);
    throw new ApiError('service_unavailable', unavailableMessage);
  } finally {
    clearTimeout(timer); signal?.removeEventListener('abort', abort);
  }
}
// Revision tokens protect even when a transport ignores abort or replies out of order.
export class Revisions {
  private revision = 0;
  private sequence = 0;
  edit() { this.revision++; this.sequence++; }
  begin() { return {revision: this.revision, sequence: ++this.sequence}; }
  current(token: {revision: number; sequence: number}) { return token.revision === this.revision && token.sequence === this.sequence; }
}
