import {comparablesAvailable} from './config';
import {peersFor, type ComparablesPackage} from './types';

export function validateComparables(value: unknown, ticker: string): ComparablesPackage {
  const d = value as ComparablesPackage;
  if (!d || d.schema_version !== 1 || d.target !== ticker || d.currency !== 'USD' ||
      !['GOOGL','AAPL','META'].includes(ticker) || d.quarter_end !== (ticker==='AAPL'?'2026-09-26':'2026-09-30') ||
      !d.market || (['valuation_date','prices','multiples','exit_default'] as const).some(k => d.market[k] !== null)) throw new Error('Unsupported comparables package');
  const order=peersFor(d);
  if(new Set(order).size!==order.length||!order.includes(d.target))throw new Error('Invalid peer selection');
  for (const ticker of order) {
    const p = d.peers?.[ticker];
    if (!p || !p.ttm || !['revenue','ebit','cfo','cash_capex','sbc'].every(k => Number.isFinite(p.ttm[k as keyof typeof p.ttm])) ||
        p.ttm.revenue <= 0 || !p.revenue_operands || ![1,3].includes(p.revenue_operands.length) || !p.balances ||
        !p.revenue_operands.every(o => Number.isFinite(o.value) && /^https:\/\/www\.sec\.gov\/Archives\//.test(o.source_url))) {
      throw new Error('Incomplete peer financials');
    }
  }
  if(ticker!=='GOOGL'){
    const expected=ticker==='AAPL'?['AAPL','DELL','HPQ','MSFT','GOOGL','AMZN','NFLX']:['META','GOOGL','SNAP','PINS','RDDT','TTD','AMZN'];
    if(order.join(',')!==expected.join(',')||!d.presentation?.groups?.length||!d.presentation.business_tables?.length||!d.presentation.growth_rows?.length)throw new Error('Unreviewed target peer map');
  }
  const keys=d.presentation?[...d.presentation.groups.flatMap(g=>g.cards.map(c=>c.growth_key)),...d.presentation.growth_rows.map(r=>r.growth_key)]:['GOOGL_cloud','AMZN_aws','MSFT_azure','GOOGL_advertising','META_advertising','RDDT_advertising','PINS_total','GOOGL_search','GOOGL_youtube_ads','GOOGL_network'];
  for (const key of keys) {
    const g = d.growth?.[key];
    if (!g || !Number.isFinite(g.current) || !Number.isFinite(g.prior) || g.prior <= 0 ||
        !Number.isFinite(g.growth) || Math.abs(g.growth! - (g.current/g.prior-1)) > 1e-10) throw new Error('Invalid comparative growth');
  }
  if(d.presentation){
    for(const group of d.presentation.groups){
      if(!group.title||!group.note||!group.cards.length||!group.cards.some(c=>c.target))throw new Error('Incomplete comparison group');
      for(const card of group.cards){
        const g=d.growth[card.growth_key];
        if(!g.current_end||!g.prior_end||!g.basis||!card.scope||(card.income!==null&&!Number.isFinite(card.income)))throw new Error('Incomplete comparison basis');
      }
    }
    for(const table of d.presentation.business_tables){
      if(!table.columns.length||table.rows.some(r=>r.length!==table.columns.length||r.some(v=>typeof v==='number'&&!Number.isFinite(v))))throw new Error('Incomplete business table');
    }
    return d;
  }
  for (const [issuer, keys] of Object.entries({GOOGL:['cloud','cloud_ebit','services','services_ebit','other_bets','other_bets_ebit','corporate_ebit','hedging','revenue','ebit','subscriptions_platforms_devices'],
    META:['advertising','family_of_apps','family_of_apps_ebit','reality_labs','reality_labs_ebit'], AMZN:['aws','aws_ebit','subscriptions'], MSFT:['azure','m365'], RDDT:['advertising']})) {
    if (!keys.every(k => Number.isFinite(d.businesses?.[issuer]?.[k]))) throw new Error('Incomplete business disclosures');
  }
  return d;
}
export async function fetchComparables(ticker: string, signal?: AbortSignal): Promise<ComparablesPackage> {
  if (!comparablesAvailable(ticker)) throw new Error('Comparables disconnected for this company');
  const response = await fetch(`${(import.meta as ImportMeta & {env:{BASE_URL:string}}).env.BASE_URL}features/trading-comparables/${ticker}.json`, {signal});
  if (!response.ok) throw new Error('Comparables unavailable');
  return validateComparables(await response.json(), ticker);
}
