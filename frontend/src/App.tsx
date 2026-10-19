import {useEffect, useRef, useState} from 'react';
import {annual, terminal, makeDraft, buildRequest, fieldErrors, InputErrors, money, display} from './model';
import type {Catalog, Draft, Errors, Result} from './model';
import {ApiError, request, Revisions} from './api';

type Props = {load?: typeof request};
export default function App({load = request}: Props) {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [selected, setSelected] = useState('');
  const [draft, setDraft] = useState<Draft | null>(null);
  const [pendingSelection, setPendingSelection] = useState<string | null>(null);
  const [errors, setErrors] = useState<Errors>({});
  const [messages, setMessages] = useState<string[]>([]);
  const [status, setStatus] = useState('Choose a retained anchor or the separate synthetic demonstration.');
  const [busy, setBusy] = useState<string | null>(null);
  const [result, setResult] = useState<Result | null>(null);
  const [stale, setStale] = useState(false);
  const revisions = useRef(new Revisions());
  const active = useRef<AbortController | null>(null);
  useEffect(() => {
    const abort = new AbortController();
    load<Catalog>('/api/v1/catalog', undefined, abort.signal).then(data => {
      if (!abort.signal.aborted) setCatalog(data);
    }).catch(e => { if (!abort.signal.aborted) setMessages([(e as Error).message]); });
    return () => { abort.abort(); active.current?.abort(); };
  }, [load]);
  const invalidate = () => {
    revisions.current.edit(); active.current?.abort(); active.current = null;
    setBusy(null); setStale(true); setErrors({}); setMessages([]);
    setStatus('Inputs changed. Validate and calculate again; any previous result is stale.');
  };
  const edit = (change: (next: Draft) => void) => {
    if (!draft) return;
    invalidate(); const next = structuredClone(draft); change(next); setDraft(next);
  };
  const switchTo = (kind: string) => {
    if (!catalog) return;
    invalidate(); setSelected(kind); setResult(null); setStale(false);
    const template = kind === 'demo' ? catalog.synthetic_demo : catalog.entries.find(e => e.kind === kind)?.template;
    setDraft(template ? makeDraft(template, kind === 'demo') : null);
    setStatus(kind === 'demo' ? 'Synthetic demonstration loaded explicitly. Anchor revenue is synthetic $100; all rates and declarations are examples.' : 'All 37 numerical inputs are unset. Enter your own metadata and assumptions.');
    setPendingSelection(null);
  };
  const choose = (kind: string) => {
    if (kind === selected) return;
    const populated = draft && (Object.values(draft.rates).some(v => v.trim()) || draft.doc.case_name || Object.values(draft.doc.analyst).some(Boolean) || draft.doc.scope);
    if (populated) setPendingSelection(kind); else switchTo(kind);
  };
  async function submit(action: 'validate' | 'run') {
    if (!draft) return;
    const token = revisions.current.begin();
    const controller = new AbortController(); active.current?.abort(); active.current = controller;
    setMessages([]); setErrors({}); setBusy(action);
    if (action === 'run') setStale(true);
    try {
      const body = buildRequest(draft);
      const data = await load<Result | {status: string}>(`/api/v1/cases/${action}`, body, controller.signal);
      if (!revisions.current.current(token)) return;
      if (action === 'run') { setResult(data as Result); setStale(false); setStatus('Calculation complete — enterprise value only. Financial consistency and evidence completeness are not approved.'); }
      else setStatus('Structural validation passed. No calculation performed; this is not economic approval.');
    } catch (e) {
      if (!revisions.current.current(token)) return;
      if (e instanceof InputErrors) {setErrors(e.fields); setMessages(Object.entries(e.fields).map(([p,m]) => `${p}: ${m}`));}
      else if (e instanceof ApiError) {setErrors(fieldErrors(e.details)); setMessages([`${e.code}: ${e.message}`, ...e.details]);}
      else setMessages(['Unexpected local UI error. Entries are preserved.']);
      setStatus('Request did not succeed. Correct the inputs or retry explicitly; entries are preserved.');
    } finally {
      if (revisions.current.current(token)) {setBusy(null); active.current = null;}
    }
  }
  const input = (path: string, label: string, value: string, change: (value: string) => void, multiline = false) => {
    const props = {id: path, value, onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => change(e.target.value),
      'aria-invalid': Boolean(errors[path]), 'aria-describedby': errors[path] ? `${path}-error` : undefined};
    return <div className="field" key={path}><label htmlFor={path}>{label}</label>
      {multiline ? <textarea {...props} rows={3} /> : <input {...props} type="text" />}
      {errors[path] && <span id={`${path}-error`} className="field-error">{errors[path]}</span>}
    </div>;
  };
  const rateInput = (path: string, label: string) => input(path, label, draft!.rates[path], value => edit(next => {next.rates[path] = value;}));
  const entry = catalog?.entries.find(e => e.kind === selected);
  return <main>
    <header><div className="eyebrow">LOCAL ANALYST WORKSPACE · MANUAL FCFF</div><h1>Review a case.<br/><span>Make the assumptions explicit.</span></h1>
      <p>Five-year operating forecast → discounted cash flows → enterprise value. Retained historical anchors, analyst-entered estimates, Python calculations.</p>
      <div className="notice">Local only · Phase 1 expansion paused · No automatic saving · No investment approval</div>
    </header>
    <section aria-labelledby="basis-title"><div className="section-number">A / HISTORICAL BASIS</div><h2 id="basis-title">Choose the starting point</h2>
      {!catalog && <p role="status">Loading the local catalog… Start the packaged Python API if it is unavailable.</p>}
      <div className="field"><label htmlFor="company">Historical anchor</label><select id="company" value={selected} onChange={e => choose(e.target.value)} disabled={!catalog}>
        <option value="">Select a basis</option>{catalog?.entries.map(e => <option key={e.kind} value={e.kind}>{e.company} · retained FY2025</option>)}
        <option value="demo">Synthetic demonstration · $100 revenue (not company data)</option>
      </select></div>
      {pendingSelection !== null && <div role="alertdialog" aria-label="Discard populated edits?" className="notice"><p>Switching basis will discard populated entries and results. No copy is saved.</p><button onClick={() => switchTo(pendingSelection)}>Discard and switch</button> <button onClick={() => setPendingSelection(null)}>Keep editing</button></div>}
      {entry && <div className="basis-card"><h3>{entry.company} · FY2025 reported anchor</h3><p><strong>{money(entry.revenue)} USD millions</strong> · base unit {entry.unit} · retained XBRL precision {entry.precision} (−6: nearest million)</p>
        <p>{entry.identity.annual_start} → {entry.identity.annual_end} · {entry.identity.form} · accession {entry.identity.accession} · CIK {entry.identity.cik}</p>
        <p>Fiscal-end analytical date: {entry.identity.annual_end}. Filing identity is retained; a separate filing-acceptance timestamp is not supplied by this catalog.</p>
        <ul>{entry.source_links.map((url,i) => <li key={url}><a href={url} target="_blank" rel="noreferrer">Retained SEC filing source {i+1}</a></li>)}</ul>
        <p>{catalog?.timing_notice}</p><details><summary>Historical limitations</summary><ul>{entry.limitations.map((line,i) => <li key={i}>{line}</li>)}</ul></details>
      </div>}
      {selected === 'demo' && <div className="notice"><strong>Separate synthetic demonstration.</strong> Anchor revenue is synthetic $100, not META/GOOGL/AAPL revenue. All example forecasts, metadata and economics are synthetic.</div>}
      {draft && <><div className="metadata">
        {input('case_name', 'Case name', draft.doc.case_name, value => edit(n => {n.doc.case_name = value;}))}
        {input('analyst.author', 'Preparer', draft.doc.analyst.author ?? '', value => edit(n => {n.doc.analyst.author = value;}))}
        {input('analyst.timestamp_utc', 'Prepared at (ISO timestamp with UTC offset)', draft.doc.analyst.timestamp_utc ?? '', value => edit(n => {n.doc.analyst.timestamp_utc = value;}))}
      </div>
        {input('analyst.rationale', 'Analyst rationale — source basis, estimates and joint consistency', draft.doc.analyst.rationale ?? '', value => edit(n => {n.doc.analyst.rationale = value;}), true)}
        {input('scope', 'Forecast scope and information-cutoff disclosure', draft.doc.scope, value => edit(n => {n.doc.scope = value;}), true)}
        <p className="hint">No structured cutoff field exists in this single-case contract. State your cutoff here; the API does not enforce it. Identity/rationale are declarations, not authenticated approvals.</p>
        {input('limitations', 'Declared limitations (one per line; retained limitations initially shown)', draft.doc.limitations.join('\n'), value => edit(n => {n.doc.limitations = value.split('\n');}), true)}
      </>}
    </section>
    {draft && <>
      <section aria-labelledby="forecast-title"><div className="section-number">B / OPERATING FORECAST</div><h2 id="forecast-title">Five years, individually supplied</h2>
        <p>Enter percentages: <strong>10 = 10%</strong>, not 0.10. Blank means unset. No history-based defaults.</p>
        <div className="table-scroll" tabIndex={0} role="region" aria-label="Five-year assumption table, scroll horizontally on narrow screens"><table><thead><tr><th scope="col">Assumption (%)</th>{draft.doc.forecast_years.map(y => <th scope="col" key={y.period_index}>{y.fiscal_year_label}</th>)}</tr></thead><tbody>
          {annual.map(([key,label]) => <tr key={key}><th scope="row">{label}<small>{catalog?.input_definitions[key]}</small></th>{draft.doc.forecast_years.map((year,i) => <td key={i}>{rateInput(`forecast_years[${i}].${key}`, `${label} ${year.fiscal_year_label} (%)`)}</td>)}</tr>)}
        </tbody></table></div>
        <p className="hint">Margins include SBC and operating-lease service costs. D&A must align with expense in margins, including finance-asset depreciation once. Investment includes cash PP&E plus non-overlapping new finance-leased operating assets, excluding principal. Working-capital cash requirement uses full forecast revenue: positive uses cash; negative releases cash.</p>
      </section>
      <section aria-labelledby="terminal-title"><div className="section-number">C / TERMINAL & DISCOUNT</div><h2 id="terminal-title">State the steady-state assumptions</h2><p>Supply all five terminal ratios independently. Nothing copies from year five. Review growth, tax, replacement/growth investment and D&A together.</p>
        <div className="rate-grid">{rateInput('wacc','Constant WACC (%)')}{rateInput('terminal_growth','Terminal growth (%)')}{terminal.map(([key,label]) => rateInput(`terminal.${key}`,`${label} (%)`))}</div>
      </section>
      <section aria-labelledby="review-title"><div className="section-number">D / VALIDATE & REVIEW</div><h2 id="review-title">Check first. Run explicitly.</h2>
        <div className="actions"><button disabled={Boolean(busy)} onClick={() => void submit('validate')}>Validate</button><button className="primary" disabled={Boolean(busy)} onClick={() => void submit('run')}>Calculate enterprise value</button></div>
        <p role="status" aria-live="polite">{busy ? `${busy === 'run' ? 'Calculating' : 'Validating'}… Entries remain editable; an edit cancels this request.` : status}</p>
        {messages.length > 0 && <div role="alert" className="errors"><h3>Request needs attention</h3><ul>{messages.map((message,i) => <li key={i}>{message}</li>)}</ul><p>API error lists are bounded; correct these fields and validate again to reveal any remaining errors.</p></div>}
        {result && <ResultReview result={result} stale={stale} />}
        <details><summary>Current declarations and exact API request</summary><p>Percentage entries convert to fractional Decimal strings. Raw returned quantities remain unrounded in the result trace.</p><pre>{(() => {try {return JSON.stringify(buildRequest(draft),null,2);} catch {return 'Correct invalid percentage entries to review the exact request.';}})()}</pre></details>
      </section>
    </>}
    {!draft && messages.length > 0 && <div role="alert" className="errors">{messages.join(' ')}</div>}
    <footer>Enterprise value is not equity value or value per share. No equity, scenario, sensitivity or reverse-DCF screens in this milestone.</footer>
  </main>;
}

export function ResultReview({result, stale}: {result: Result; stale: boolean}) {
  const b = result.stage_b;
  const components = [['Revenue','revenue'],['EBIT','ebit'],['Operating tax','tax'],['NOPAT','nopat'],['D&A','d_and_a'],['Investment','investment'],['Working-capital cash requirement','working_capital_cash_requirement'],['FCFF','fcff']] as const;
  const financialRow = (label: string, values: (string | number)[]) => <tr key={label}><th scope="row">{label}</th>{values.map((v,i) => <td key={i}>{money(v)}</td>)}</tr>;
  return <article aria-label="Enterprise value result" className={stale ? 'result stale' : 'result'}>
    {stale && <div className="errors" role="status"><strong>STALE RESULT — inputs changed or a new run is pending. These figures belong to the earlier submitted case.</strong></div>}
    <h3>{result.case_name}</h3><p>{result.input_basis} · Submitted declarations; no economic approval. {b.timing.notice}</p>
    <p>Fiscal-end analytical date: {b.timing.analytical_t0} · Cutoff: {b.timing.information_cutoff}</p>
    <div className="ev"><span>Enterprise value · USD millions</span><strong>{money(b.enterprise_value)}</strong><small>Not equity or per-share value. Display rounding only.</small></div>
    <div className="table-scroll" tabIndex={0} role="region" aria-label="Annual cash flows, USD millions"><table><caption>Annual components · USD millions (discount factors are unitless)</caption><thead><tr><th scope="col">Component</th>{b.stage_a.years.map(y => <th scope="col" key={String(y.period_index)}>{y.fiscal_year_label}</th>)}</tr></thead><tbody>
      {components.map(([label,key]) => financialRow(label,b.stage_a.years.map(y => y[key])))}
      <tr><th scope="row">Discount factor (unitless)</th>{b.years.map((y,i) => <td key={i}>{display(y.discount_factor,'1',6)}</td>)}</tr>
      {financialRow('Discounted FCFF',b.years.map(y => y.pv_fcff))}
    </tbody></table></div>
    <p>Negative FCFF is retained as a cash outflow. Operating taxes reduce EBIT; D&A is added back once; investment and positive WC use cash.</p>
    <dl className="reconciliation">{[['Explicit-period PV','pv_explicit_fcff'],['+ Discounted terminal value','pv_terminal_value'],['= Enterprise value','enterprise_value'],['Terminal FCFF','fcff'],['Terminal value at year 5','terminal_value']].map(([label,key]) => <div key={key}><dt>{label} (USD millions)</dt><dd>{money(key === 'fcff' ? b.terminal.fcff : b[key as 'enterprise_value'])}</dd></div>)}</dl>
    <p className="hint">Terminal contribution ratio: not supplied by the current API; deferred in this UI. Review the terminal PV beside EV above. Zero-EV ratios would be undefined; negative or over-100% ratios must not be clamped. The existing CLI summary provides that ratio.</p>
    <details><summary>Submitted assumptions, rationale, timing, limitations and full-precision trace</summary>
      <ul>{result.limitations.map((line,i) => <li key={i}>{line}</li>)}</ul><pre>{JSON.stringify(result,null,2)}</pre>
    </details>
  </article>;
}
