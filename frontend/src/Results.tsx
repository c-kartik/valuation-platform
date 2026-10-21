import {money,display} from './model';
import type {Result} from './model';
import {chartPoints,terminalContribution,readableMoney,readableLimitation} from './presentation';

function Trend({label,values,years}: {label:string; values:string[]; years:string[]}) {
  const points=chartPoints(values);
  return <figure className="trend"><figcaption>{label} <small>USD millions</small></figcaption>
    {points ? <svg viewBox="0 0 300 210" role="img" aria-label={`${label} trend; rounded values in the forecast table; unrounded values in the trace`}>
      <line x1="20" x2="285" y1="100" y2="100" stroke="#bacac2"/><text x="3" y="96">0</text>
      <polyline points={points.map(p=>`${p.x},${p.y}`).join(' ')} fill="none" stroke={label==='Revenue'?'#25735a':'#3c6f9c'} strokeWidth="3"/>
      {points.map((p,i)=><g key={i}><circle cx={p.x} cy={p.y} r="4" fill={label==='Revenue'?'#25735a':'#3c6f9c'}><title>{years[i]}: {money(values[i])} USD millions</title></circle><text x={p.x} y="202" textAnchor="middle">Y{i+1}</text></g>)}
    </svg> : <p>Chart unavailable for this magnitude; review the exact table.</p>}
    <div className="trend-range"><span>Y1: {money(values[0])}</span><span>Y5: {money(values[4])}</span></div>
  </figure>;
}
export function ResultReview({result,stale}: {result:Result;stale:boolean}) {
  const b=result.stage_b;
  const contribution=terminalContribution(b.pv_terminal_value,b.enterprise_value);
  const components=[['Operating tax','tax'],['NOPAT','nopat'],['D&A','d_and_a'],['Investment','investment'],['Working-capital cash requirement','working_capital_cash_requirement']] as const;
  return <article aria-label="Enterprise value result" className={stale?'result stale':'result'}>
    {stale && <div className="errors" role="status"><strong>STALE RESULT — inputs changed or a new run is pending. These figures belong to the earlier submitted case.</strong></div>}
    <div className="section-number">RESULT · {result.input_basis==='SYNTHETIC_FIXTURE'?'SYNTHETIC DEMONSTRATION':'MANUAL FORECAST'}</div>
    <h2>Enterprise value</h2>
    <div className="ev"><strong>{readableMoney(b.enterprise_value)} <span className="currency">USD</span></strong><small>Operating business value; excludes the cash/debt/share bridge.</small></div>
    <div className="terminal-metric"><span>Terminal contribution</span><strong>{contribution.text}</strong><small>{contribution.note}</small></div>
    <div className="charts"><Trend label="Revenue" values={b.stage_a.years.map(y=>String(y.revenue))} years={b.stage_a.years.map(y=>String(y.fiscal_year_label))}/><Trend label="FCFF" values={b.stage_a.years.map(y=>String(y.fcff))} years={b.stage_a.years.map(y=>String(y.fiscal_year_label))}/></div>
    <details><summary>Five-year forecast</summary><div className="table-scroll" tabIndex={0} role="region" aria-label="Compact five-year forecast"><table className="compact-table"><caption>Five-year forecast · USD millions</caption><thead><tr><th scope="col">Year</th><th scope="col">Revenue</th><th scope="col">EBIT</th><th scope="col">FCFF</th></tr></thead><tbody>{b.stage_a.years.map(y=><tr key={String(y.period_index)}><th scope="row">{y.fiscal_year_label}</th><td title={`Unrounded USD: ${y.revenue}`}>{money(y.revenue)}</td><td title={`Unrounded USD: ${y.ebit}`}>{money(y.ebit)}</td><td title={`Unrounded USD: ${y.fcff}`}>{money(y.fcff)}</td></tr>)}</tbody></table></div>
    <p className="hint">Negative FCFF remains a cash outflow. Display rounding does not change raw values; rounded components may not sum.</p></details>
    <details><summary>Cash-flow details and EV reconciliation</summary>
      <div className="table-scroll" tabIndex={0} role="region" aria-label="Detailed cash flows, USD millions"><table><caption>Annual components · USD millions (discount factors are unitless)</caption><thead><tr><th scope="col">Component</th>{b.stage_a.years.map(y=><th scope="col" key={String(y.period_index)}>{y.fiscal_year_label}</th>)}</tr></thead><tbody>
        {components.map(([label,key])=><tr key={key}><th scope="row">{label}</th>{b.stage_a.years.map((y,i)=><td key={i}>{money(y[key])}</td>)}</tr>)}
        <tr><th scope="row">Discount factor (unitless)</th>{b.years.map((y,i)=><td key={i}>{display(y.discount_factor,'1',6)}</td>)}</tr>
        <tr><th scope="row">Discounted FCFF</th>{b.years.map((y,i)=><td key={i}>{money(y.pv_fcff)}</td>)}</tr>
      </tbody></table></div>
      <dl className="reconciliation">{[['Explicit-period PV',b.pv_explicit_fcff],['+ Discounted terminal value',b.pv_terminal_value],['= Enterprise value',b.enterprise_value],['Terminal FCFF',String(b.terminal.fcff)],['Terminal value at year 5',b.terminal_value]].map(([label,value])=><div key={label}><dt>{label} (USD millions)</dt><dd>{money(value)}</dd></div>)}</dl>
    </details>
    <details><summary>Assumptions, limitations &amp; provenance</summary><p>Case: <span>{result.case_name}</span></p><p>{b.timing.notice}</p><p>Analytical date: {b.timing.analytical_t0}. No verified information cutoff is established by this calculator.</p>
      {'preparation' in result.submitted_inputs ? <>
        <p>Anonymous investor calculation · prepared at {result.submitted_inputs.preparation.timestamp_utc}. Preparation time is not the analytical date, information cutoff or evidence review.</p>
        <p>No investment rationale supplied. Forecast inputs are user-entered and not independently reviewed.</p>
        <p className="personal-notes"><strong>Optional personal notes:</strong> {result.submitted_inputs.preparation.notes ?? 'Absent'}</p>
      </> : <><p><strong>Rationale:</strong> {result.submitted_inputs.analyst.rationale}</p><p><strong>Scope:</strong> {result.submitted_inputs.scope}</p></>}
      <ul>{result.limitations.map((line,i)=><li key={i}>{readableLimitation(line)}</li>)}</ul>
      <details><summary>Full-precision inputs and calculation trace</summary>
        <div className="table-scroll" tabIndex={0} role="region" aria-label="Unrounded annual values in USD"><table className="compact-table"><caption>Exact returned annual values · USD (unrounded strings)</caption><thead><tr><th scope="col">Year</th><th scope="col">Revenue</th><th scope="col">EBIT</th><th scope="col">FCFF</th></tr></thead><tbody>{b.stage_a.years.map(y=><tr key={String(y.period_index)}><th scope="row">{y.fiscal_year_label}</th><td>{y.revenue}</td><td>{y.ebit}</td><td>{y.fcff}</td></tr>)}</tbody></table></div>
        <pre>{JSON.stringify(result,null,2)}</pre></details>
    </details>
  </article>;
}
