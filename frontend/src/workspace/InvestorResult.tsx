import type {Result} from '../model';
import {readableMoney,terminalContribution} from '../presentation';
import {ForecastChart} from './ForecastChart';
import {MarketPanel} from './MarketPanel';
import {ExportData} from './ExportData';
export function InvestorResult({result,stale,marketStale=false}:{result:Result;stale:boolean;marketStale?:boolean}){
 const b=result.stage_b,t=terminalContribution(b.pv_terminal_value,b.enterprise_value);
 return <article className="ir-result" aria-label="Enterprise value result">{stale&&<p className="p-notice" role="status">Stale result — inputs changed; calculate again.</p>}<section className="p-panel ir-value"><span className="p-eyebrow">YOUR MANUAL FORECAST</span><h2>Enterprise value</h2><strong>{readableMoney(b.enterprise_value)}</strong><p>Operating business value, before cash, claims and shares.</p><dl className="p-reconcile"><div><dt>Five-year cash-flow PV</dt><dd>{readableMoney(b.pv_explicit_fcff)}</dd></div><div><dt>Discounted terminal value</dt><dd>{readableMoney(b.pv_terminal_value)}</dd></div><div><dt>Terminal contribution / EV</dt><dd>{t.text}</dd></div></dl>{!/This measures/.test(t.note)&&/negative|exceeds/.test(t.note)&&<p>{t.note}</p>}<p>Fiscal-end analytical origin {b.timing.analytical_t0}, using later-filed information; not a current-date valuation or historical backtest.</p></section><MarketPanel result={result} stale={stale||marketStale}/><ForecastChart cases={[{label:'Base',result}]}/><ExportData value={result} name={result.case_name}/></article>;
}
