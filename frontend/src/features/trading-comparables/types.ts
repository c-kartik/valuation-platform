export const peerTickers = ['GOOGL','META','PINS','RDDT','TTD','MSFT','AMZN'] as const;
export type PeerTicker = typeof peerTickers[number];
export type Operand = {value: number; start: string; end: string; filed?: string; source_url: string};
export type Peer = {
  name: string; role: string; note: string;
  ttm: Record<'revenue'|'ebit'|'cfo'|'cash_capex'|'sbc', number>;
  quarter_growth: number; quarter_revenue: number;
  revenue_operands: Operand[];
  balances: Record<string, number|null>; financials_url: string;
};
export type Growth = {prior: number; current: number; growth: number|null; operands: Operand[]};
export type ComparablesPackage = {
  schema_version: 1; target: 'GOOGL'; as_of: string; quarter_start: string; quarter_end: string; currency: 'USD';
  peers: Record<PeerTicker, Peer>; businesses: Record<string, Record<string, number|null>>;
  growth: Record<string, Growth>;
  validation: {selected_filing_checks: number; business_reconciliations: number};
  limitations: string[];
  market: {valuation_date: null; prices: null; multiples: null; exit_default: null};
};
