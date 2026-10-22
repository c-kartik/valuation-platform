export class ApiError extends Error {
  constructor(public code: string, message: string, public details: string[] = []) { super(message); }
}
export const unavailableMessage = 'Calculations are temporarily unavailable. Your inputs are still here. Please try again later.';
export function failureMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.code === 'busy') return 'Another calculation is in progress. Your inputs are still here. Please retry shortly.';
    if (error.code === 'request_cancelled') return error.message;
    if (['service_unavailable', 'connection_error', 'http_error', 'not_ready', 'shutting_down', 'calculation_failed', 'worker_failed', 'internal_error', 'deadline_exceeded'].includes(error.code)) return unavailableMessage;
    return `${error.code}: ${error.message}`;
  }
  return unavailableMessage;
}
// Render-boundary shape checks only; economic/numerical validation remains in Python.
const object = (value: unknown): value is Record<string, unknown> => value !== null && typeof value === 'object' && !Array.isArray(value);
const text = (value: unknown): value is string => typeof value === 'string';
const decimal = (value: unknown) => text(value) && /^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$/.test(value);
function renderableResult(data: Record<string, unknown>, requireEquity: boolean): boolean {
  const b = data.stage_b, submitted = data.submitted_inputs;
  if (!text(data.case_name) || !text(data.input_basis) || !Array.isArray(data.limitations) || !data.limitations.every(text) || !object(submitted)) return false;
  if (object(submitted.preparation) ? !text(submitted.preparation.timestamp_utc) || !(submitted.preparation.notes === null || text(submitted.preparation.notes)) : !object(submitted.analyst) || !text(submitted.analyst.rationale) || !text(submitted.scope)) return false;
  if (!object(b) || !object(b.stage_a) || !object(b.terminal) || !decimal(b.terminal.fcff) || !object(b.timing) || !text(b.timing.notice) || !text(b.timing.analytical_t0)) return false;
  if (!['enterprise_value','pv_explicit_fcff','pv_terminal_value','terminal_value'].every(key => decimal(b[key]))) return false;
  if (!Array.isArray(b.stage_a.years) || b.stage_a.years.length !== 5 || !b.stage_a.years.every(y => object(y) && text(y.fiscal_year_label) && ['revenue','ebit','tax','nopat','d_and_a','investment','working_capital_cash_requirement','fcff'].every(key => decimal(y[key])))) return false;
  if (!Array.isArray(b.years) || b.years.length !== 5 || !b.years.every(y => object(y) && decimal(y.discount_factor) && decimal(y.pv_fcff))) return false;
  const c = data.stage_c;
  if (c === undefined) return !requireEquity;
  if (!object(c) || !object(c.inputs) || !object(c.inputs.shares) || !object(c.stage_b) || !decimal(c.stage_b.enterprise_value)) return false;
  if (!['eligible_assets','financing_claims','other_equity_claims','equity_value','valuation_shares','value_per_share'].every(key => decimal(c[key]))) return false;
  const shares = c.inputs.shares;
  return ['class_id','observation_date','rationale'].every(key => text(shares[key])) &&
    Array.isArray(c.inputs.observations) && c.inputs.observations.every(o => object(o) && ['observation_id','disposition','rationale'].every(key => text(o[key]))) &&
    Array.isArray(c.contributions) && c.contributions.every(line => object(line) && object(line.component) && text(line.component.component_id) && decimal(line.signed_contribution));
}
export async function request<T>(path: string, body?: unknown, signal?: AbortSignal): Promise<T> {
  const controller = new AbortController();
  let timedOut = false;
  const abort = () => controller.abort();
  signal?.addEventListener('abort', abort, {once: true});
  if (signal?.aborted) controller.abort();
  const timer = setTimeout(() => {timedOut = true; controller.abort();}, 50000);
  try {
    const response = await fetch(path, {
      method: body === undefined ? 'GET' : 'POST', signal: controller.signal,
      headers: body === undefined ? undefined : {'Content-Type': 'application/json'},
      body: body === undefined ? undefined : JSON.stringify(body), cache: 'no-store', credentials: 'omit',
    });
    // Gateway HTML and untrusted server messages never enter the review UI.
    if (response.status === 429) throw new ApiError('busy', 'Another calculation is in progress. Please retry shortly.');
    let data;
    try {data = await response.json();} catch {throw new ApiError('service_unavailable', unavailableMessage);}
    if (!data || typeof data !== 'object' || Array.isArray(data)) throw new ApiError('service_unavailable', unavailableMessage);
    if (!response.ok) {
      const error = data.error;
      const known = ['invalid_case','busy','request_too_large','deadline_exceeded','internal_error','not_ready','shutting_down','calculation_failed','worker_failed','body_timeout'];
      const code = known.includes(error?.code) ? error.code : 'http_error';
      const details = Array.isArray(error?.details) ? error.details.filter((d: unknown) => typeof d === 'string').slice(0,20).map((d: string) => d.slice(0,200)) : [];
      const message = code === 'invalid_case' ? 'Review the indicated inputs.' : code === 'request_too_large' ? 'The submitted input is too large. Reduce optional notes or component references.' : unavailableMessage;
      throw new ApiError(code, message, details);
    }
    if (path.endsWith('/run') && !renderableResult(data, object(body) && body.calculation_scope === 'EQUITY_PER_SHARE')) throw new ApiError('service_unavailable', unavailableMessage);
    return data as T;
  } catch (e) {
    if (e instanceof ApiError) throw e;
    if (controller.signal.aborted && !timedOut) throw new ApiError('request_cancelled', 'Calculation cancelled. Your inputs are still here. Retry when ready.');
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
