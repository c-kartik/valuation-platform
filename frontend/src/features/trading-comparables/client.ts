import {comparablesAvailable} from './config';
import {peerTickers, type ComparablesPackage} from './types';

export function validateComparables(value: unknown, ticker: string): ComparablesPackage {
  const d = value as ComparablesPackage;
  if (!d || d.schema_version !== 1 || d.target !== ticker || d.currency !== 'USD' ||
      d.quarter_start !== '2026-07-01' || d.quarter_end !== '2026-09-30' ||
      !d.market || (['valuation_date','prices','multiples','exit_default'] as const).some(k => d.market[k] !== null)) throw new Error('Unsupported comparables package');
  for (const ticker of peerTickers) {
    const p = d.peers?.[ticker];
    if (!p || !p.ttm || !['revenue','ebit','cfo','cash_capex','sbc'].every(k => Number.isFinite(p.ttm[k as keyof typeof p.ttm])) ||
        p.ttm.revenue <= 0 || !p.revenue_operands || p.revenue_operands.length !== 3 ||
        !p.revenue_operands.every(o => Number.isFinite(o.value) && /^https:\/\/www\.sec\.gov\/Archives\//.test(o.source_url))) {
      throw new Error('Incomplete peer financials');
    }
  }
  for (const key of ['GOOGL_cloud','AMZN_aws','MSFT_azure','GOOGL_advertising','META_advertising','RDDT_advertising','PINS_total','GOOGL_search','GOOGL_youtube_ads','GOOGL_network']) {
    const g = d.growth?.[key];
    if (!g || !Number.isFinite(g.current) || !Number.isFinite(g.prior) || g.prior <= 0 ||
        !Number.isFinite(g.growth) || Math.abs(g.growth! - (g.current/g.prior-1)) > 1e-10) throw new Error('Invalid comparative growth');
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
