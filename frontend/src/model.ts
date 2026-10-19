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
export type Draft = { doc: CaseDoc; rates: Record<string, string> };
export type Errors = Record<string, string>;
export type Year = Record<string, string | number>;
export type Result = {
  case_name: string; input_basis: string; submitted_inputs: CaseDoc; limitations: string[];
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
export function makeDraft(template: CaseDoc, demo = false): Draft {
  const doc = structuredClone(template);
  if (!demo) {
    doc.case_name = ''; doc.scope = ''; doc.analyst = {author: null, timestamp_utc: null, rationale: null};
  }
  const rates: Record<string, string> = {};
  doc.forecast_years.forEach((year, i) => annual.forEach(([key]) => {
    rates[`forecast_years[${i}].${key}`] = fractionToPercentage(year[key]);
  }));
  rates.wacc = fractionToPercentage(doc.wacc); rates.terminal_growth = fractionToPercentage(doc.terminal_growth);
  terminal.forEach(([key]) => { rates[`terminal.${key}`] = fractionToPercentage(doc.terminal[key]); });
  return {doc, rates};
}
export function buildRequest(draft: Draft): CaseDoc {
  const doc = structuredClone(draft.doc);
  const errors: Errors = {};
  const convert = (path: string) => {
    try { return percentageToFraction(draft.rates[path]); }
    catch (e) { errors[path] = (e as Error).message; return null; }
  };
  doc.forecast_years.forEach((year, i) => annual.forEach(([key]) => { year[key] = convert(`forecast_years[${i}].${key}`); }));
  doc.wacc = convert('wacc'); doc.terminal_growth = convert('terminal_growth');
  terminal.forEach(([key]) => { doc.terminal[key] = convert(`terminal.${key}`); });
  if (Object.keys(errors).length) throw new InputErrors(errors);
  return doc; // Explicit legacy v1 EV-only object: never add Stage C or cutoff fields.
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
