export const peerTickers = ['GOOGL','META','PINS','RDDT','TTD','MSFT','AMZN'] as const;
export type TargetTicker = 'GOOGL'|'AAPL'|'META';
export type PeerTicker = typeof peerTickers[number]|'AAPL'|'DELL'|'HPQ'|'NFLX'|'SNAP';
export type Operand = {value: number; start: string; end: string; filed?: string; source_url: string};
export type Peer = {
  name: string; role: string; note: string;
  ttm: Record<'revenue'|'ebit'|'cfo'|'cash_capex'|'sbc', number>;
  quarter_growth: number; quarter_revenue: number;
  revenue_operands: Operand[];
  balances: Record<string, number|null>; financials_url: string;
  ttm_end?: string; quarter_start?: string; quarter_end?: string; quarter_growth_basis?: string;
};
export type Growth = {prior: number; current: number; growth: number|null; operands: Operand[];
  current_start?:string; current_end?:string; prior_end?:string; basis?:string};
export type ComparisonCard = {name:string;scope:string;growth_key:string;income:number|null;target:boolean};
export type BusinessTable = {title:string;note:string;columns:{label:string;format:'text'|'bn'|'pct'}[];rows:(string|number|null)[][]};
export type Presentation = {groups:{title:string;eyebrow:string;note:string;cards:ComparisonCard[]}[];
  growth_table_title:string;growth_rows:{label:string;growth_key:string}[];business_tables:BusinessTable[]};
export type ComparablesPackage = {
  schema_version: 1; target: TargetTicker; as_of: string; quarter_start: string; quarter_end: string; currency: 'USD';
  peers: Record<string, Peer>; peer_order?:PeerTicker[]; businesses: Record<string, Record<string, number|null>>;
  growth: Record<string, Growth>;
  validation: {selected_filing_checks: number; business_reconciliations: number};
  limitations: string[];
  market: {valuation_date: null; prices: null; multiples: null; exit_default: null};
  presentation?:Presentation;
};
export function peersFor(d:ComparablesPackage): readonly PeerTicker[]{return d.peer_order??peerTickers;}
