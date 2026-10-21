import Decimal from 'decimal.js';

export const annual = [
  ['revenue_growth', 'Revenue growth'], ['operating_margin', 'Operating margin'],
  ['forecast_tax_rate', 'Operating tax'], ['d_and_a_percent_revenue', 'Expense-aligned D&A / revenue'],
  ['capex_percent_revenue', 'Investment / revenue'],
  ['change_in_operating_nwc_percent_revenue', 'Working-capital cash requirement / full revenue'],
] as const;
export const terminal = [
  ['operating_margin', 'Terminal operating margin'], ['operating_tax_rate', 'Terminal operating tax'],
  ['d_and_a_percent_revenue', 'Terminal expense-aligned D&A / revenue'],
  ['investment_percent_revenue', 'Terminal investment / revenue'],
  ['working_capital_cash_requirement_percent_revenue', 'Terminal WC cash requirement / full revenue'],
] as const;
export type CaseDoc = {
  schema_version: 'analyst-case-v1'; case_name: string; input_basis: string;
  analyst: { author: string | null; timestamp_utc: string | null; rationale: string | null };
  scope: string; limitations: string[]; conventions: Record<string, string>;
  anchor: { kind: string; cik: number; accession: string; annual_start: string; annual_end: string; form: string };
  forecast_years: ({ period_index: number; fiscal_year_label: string } & Record<typeof annual[number][0], string | null>)[];
  wacc: string | null; terminal_growth: string | null;
  terminal: Record<typeof terminal[number][0], string | null>;
};
export type Entry = {
  kind: string; company: string; identity: CaseDoc['anchor']; revenue: string; unit: string;
  precision: string; source_links: string[]; limitations: string[]; template: CaseDoc;
};
export type Catalog = {schema_version: string; entries: Entry[]; synthetic_demo: CaseDoc;
  timing_notice: string; input_definitions: Record<string, string>};
export type InvestorDoc = Omit<CaseDoc, 'schema_version' | 'analyst' | 'scope'> & {
  schema_version: 'investor-case-v1';
  preparation: {provenance: 'ANONYMOUS_INVESTOR'; timestamp_utc: string; notes: string | null};
};
export type Draft = { doc: InvestorDoc; rates: Record<string, string> };
export type Errors = Record<string, string>;
export type Year = Record<string, string | number>;
export type Result = {
  case_name: string; input_basis: string; submitted_inputs: CaseDoc | InvestorDoc; limitations: string[];
  stage_b: {
    timing: {analytical_t0: string; notice: string; information_cutoff: string};
    stage_a: {anchor: Record<string, unknown>; years: Year[]}; years: Year[]; terminal: Year;
    terminal_value: string; pv_terminal_value: string; pv_explicit_fcff: string; enterprise_value: string;
  };
};
// Shift the decimal point as text: no binary floating arithmetic, including for inputs.
function shift(text: string, places: number): string {
  const match = /^(-?)(\d*)(?:\.(\d*))?$/.exec(text.trim());
  if (!match || (!match[2] && !match[3]) || text.length > 128) throw new Error('Enter a decimal percentage, e.g. 10 or -2.5; no % sign or exponent.');
  const [, sign, whole, fraction = ''] = match;
  const digits = whole + fraction;
  const point = whole.length + places;
  const left = point <= 0 ? '0' : (digits.slice(0, point) + '0'.repeat(Math.max(0, point - digits.length)));
  const right = point <= 0 ? '0'.repeat(-point) + digits : digits.slice(point);
  return sign + (left.replace(/^0+(?=\d)/, '') || '0') + (right ? '.' + right : '');
}
export const percentageToFraction = (value: string): string | null => value.trim() === '' ? null : shift(value, -2);
export const fractionToPercentage = (value: string | null): string => value === null ? '' : shift(value, 2);
const templateInstruction = 'All 37 numerical assumptions and analyst identity/date/rationale are unset; no defaults or historical calibration.';
export const enduringLimitations = (lines: string[]) => lines.filter(line => line !== templateInstruction);
export const generatedCaseName = (kind: string) => `${kind === 'synthetic-fixture-v1' ? 'Synthetic demonstration' : kind.toUpperCase()} · Investor calculation`;
export function makeDraft(template: CaseDoc, timestamp = new Date().toISOString()): Draft {
  // Legacy template declarations are not anonymous users' rationale or identity.
  const {analyst: _analyst, scope: _scope, schema_version: _version, ...financial} = structuredClone(template);
  const doc: InvestorDoc = {...financial, schema_version: 'investor-case-v1',
    case_name: generatedCaseName(template.anchor.kind),
    preparation: {provenance: 'ANONYMOUS_INVESTOR', timestamp_utc: timestamp, notes: null},
    limitations: enduringLimitations(financial.limitations),
  };
  const rates: Record<string, string> = {};
  doc.forecast_years.forEach((year, i) => annual.forEach(([key]) => {
    rates[`forecast_years[${i}].${key}`] = fractionToPercentage(year[key]);
  }));
  rates.wacc = fractionToPercentage(doc.wacc); rates.terminal_growth = fractionToPercentage(doc.terminal_growth);
  terminal.forEach(([key]) => { rates[`terminal.${key}`] = fractionToPercentage(doc.terminal[key]); });
  return {doc, rates};
}
export function buildRequest(draft: Draft): InvestorDoc {
  const doc = structuredClone(draft.doc);
  if (!doc.preparation.notes?.trim()) doc.preparation.notes = null;
  const errors: Errors = {};
  const convert = (path: string) => {
    try { return percentageToFraction(draft.rates[path]); }
    catch (e) { errors[path] = (e as Error).message; return null; }
  };
  doc.forecast_years.forEach((year, i) => annual.forEach(([key]) => { year[key] = convert(`forecast_years[${i}].${key}`); }));
  doc.wacc = convert('wacc'); doc.terminal_growth = convert('terminal_growth');
  terminal.forEach(([key]) => { doc.terminal[key] = convert(`terminal.${key}`); });
  if (Object.keys(errors).length) throw new InputErrors(errors);
  return doc; // Explicit investor EV-only object: no invented analyst rationale or cutoff.
}
export class InputErrors extends Error {
  constructor(public fields: Errors) { super('Correct the highlighted percentage entries.'); }
}
const DisplayDecimal = Decimal.clone({precision: 220, rounding: Decimal.ROUND_HALF_EVEN});
export function display(value: string | number | null | undefined, scale = '1', places = 2): string {
  if (value === null || value === undefined) return 'Undefined';
  const text = String(value);
  const fixed = new DisplayDecimal(text).div(scale).toFixed(places);
  const [whole, frac] = fixed.split('.');
  return whole.replace(/\B(?=(\d{3})+(?!\d))/g, ',') + (frac === undefined ? '' : '.' + frac);
}
export function money(value: string | number | null | undefined): string {
  if (value === null || value === undefined) return 'Undefined';
  const amount = new DisplayDecimal(String(value));
  // Display only: retain visible small synthetic-dollar flows, use two places otherwise.
  return display(value, '1000000', !amount.isZero() && amount.abs().lt('10000') ? 8 : 2);
}
export function fieldErrors(details: string[]): Errors {
  const result: Errors = {};
  details.forEach(detail => {
    const colon = detail.indexOf(':');
    if (colon < 0) return;
    const path = detail.slice(0, colon).replace(/^case\./, '');
    result[path] = detail.slice(colon + 1).trim();
  });
  return result;
}

export type AnnualKey = typeof annual[number][0];
export type QuickValues = Record<AnnualKey, string>;
export const annualPath = (key: AnnualKey, i: number) => `forecast_years[${i}].${key}`;
export function samePercentage(a: string, b: string): boolean {
  try {
    const x = percentageToFraction(a), y = percentageToFraction(b);
    return x === null || y === null ? x === y : new DisplayDecimal(x).eq(y);
  } catch { return a === b; }
}
export function annualState(draft: Draft, key: AnnualKey): {value: string; varies: boolean; missing: number} {
  const values = draft.doc.forecast_years.map((_,i) => draft.rates[annualPath(key,i)]);
  return {value: values[0], varies: values.some(v => !samePercentage(v, values[0])), missing: values.filter(v => !v.trim()).length};
}
export function quickValues(draft: Draft): QuickValues {
  return Object.fromEntries(annual.map(([key]) => {
    const state = annualState(draft,key);
    return [key, state.varies ? '' : state.value];
  })) as QuickValues;
}
export function applyQuick(draft: Draft, values: Partial<QuickValues>): Draft {
  const errors: Errors = {};
  for (const [key,value] of Object.entries(values)) {
    try { if (percentageToFraction(value!) === null) errors[`quick.${key}`] = 'Enter a percentage before applying.'; }
    catch(e) { errors[`quick.${key}`] = (e as Error).message; }
  }
  if (Object.keys(errors).length) throw new InputErrors(errors);
  const next = structuredClone(draft);
  for (const [key,value] of Object.entries(values)) {
    next.doc.forecast_years.forEach((_,i) => { next.rates[annualPath(key as AnnualKey,i)] = value!; });
  }
  return next;
}
export const terminalSources = [
  ['operating_margin','operating_margin'], ['operating_tax_rate','forecast_tax_rate'],
  ['d_and_a_percent_revenue','d_and_a_percent_revenue'], ['investment_percent_revenue','capex_percent_revenue'],
  ['working_capital_cash_requirement_percent_revenue','change_in_operating_nwc_percent_revenue'],
] as const;
export function copyYearFive(draft: Draft): Draft {
  const errors: Errors = {};
  for (const [,source] of terminalSources) {
    const path = annualPath(source,4);
    try { if (percentageToFraction(draft.rates[path]) === null) errors[path] = 'Enter year five before copying terminal ratios.'; }
    catch(e) {errors[path] = (e as Error).message;}
  }
  if (Object.keys(errors).length) throw new InputErrors(errors);
  const next = structuredClone(draft);
  terminalSources.forEach(([target,source]) => {next.rates[`terminal.${target}`] = draft.rates[annualPath(source,4)];});
  return next;
}
