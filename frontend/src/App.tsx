import {useEffect, useRef, useState} from 'react';
import {annual, terminal, makeDraft, buildRequest, fieldErrors, InputErrors, money, annualState, annualPath, quickValues, applyQuick, copyYearFive, samePercentage, generatedCaseName, enduringLimitations} from './model';
import type {Catalog, Draft, Errors, Result, AnnualKey, QuickValues} from './model';
import {ApiError, request, Revisions} from './api';
import {ResultReview} from './Results';
export {ResultReview} from './Results';

function percentageDiagnostic(detail: string): string {
  const colon = detail.indexOf(':');
  if (colon < 0) return detail;
  const path = detail.slice(0,colon).replace(/^case\./,'');
  if (!/^(forecast_years\[\d+\]\.|terminal\.|wacc$|terminal_growth$)/.test(path)) return detail;
  const message = detail.slice(colon+1).trim();
  const translated = message === 'UNSET; supply a fractional Decimal string'
    ? 'Required. Enter a percentage; 20 means 20%.'
    : /^(Forecast|Terminal operating) tax rate must be between 0 and 1$/.test(message)
      ? 'Operating tax must be between 0% and 100%.' : message;
  return `${detail.slice(0,colon)}: ${translated}`;
}

type Props = {load?: typeof request};
function Confirmation({title, children, confirmLabel, cancelLabel, confirm, cancel}: {
  title: string; children: React.ReactNode; confirmLabel: string; cancelLabel: string;
  confirm: () => void; cancel: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const accept = useRef<HTMLButtonElement>(null);
  const keep = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    const opener = document.activeElement as HTMLElement | null;
    const modal = dialog.current!;
    modal.showModal();
    keep.current?.focus(); // Enter must not discard/replace by default.
    return () => {
      modal.close();
      if (opener?.isConnected) opener.focus();
    };
  }, []);
  return <dialog ref={dialog} role="alertdialog" aria-modal="true" aria-label={title}
    className="confirmation" onCancel={event=>{event.preventDefault();cancel();}}
    onKeyDown={event=>{
      if (event.key === 'Tab') {
        event.preventDefault();
        (document.activeElement === keep.current ? accept : keep).current?.focus();
      }
    }}>
    <h2>{title}</h2><p>{children}</p><div className="actions">
      <button ref={accept} onClick={confirm}>{confirmLabel}</button>
      <button ref={keep} onClick={cancel}>{cancelLabel}</button>
    </div>
  </dialog>;
}
export default function App({load = request}: Props) {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [selected, setSelected] = useState('');
  const [draft, setDraft] = useState<Draft | null>(null);
  const [quick, setQuick] = useState<QuickValues | null>(null);
  const [unapplied, setUnapplied] = useState<AnnualKey[]>([]);
  const [pendingApply, setPendingApply] = useState<Partial<QuickValues> | null>(null);
  const [annualOpen, setAnnualOpen] = useState(false);
  const [terminalOpen, setTerminalOpen] = useState(false);
  const [detailsOpen, setDetailsOpen] = useState(false);
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
    setBusy(null); setStale(true); setErrors({}); setMessages([]); setPendingApply(null);
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
    const next = template ? makeDraft(template) : null;
    setDraft(next); setQuick(next ? quickValues(next) : null); setUnapplied([]);
    setAnnualOpen(false); setTerminalOpen(false); setDetailsOpen(false);
    setStatus(kind === 'demo' ? 'Synthetic demonstration loaded explicitly. Anchor revenue is synthetic $100; all rates and declarations are examples.' : 'All company assumptions start unset. Apply annual values, set terminal ratios and calculate. Analysis details are optional.');
    setPendingSelection(null);
  };
  const choose = (kind: string) => {
    if (kind === selected) return;
    const populated = draft && (unapplied.length > 0 || quick && Object.values(quick).some(v => v.trim()) || Object.values(draft.rates).some(v => v.trim()) || draft.doc.preparation.notes !== null || draft.doc.case_name !== generatedCaseName(draft.doc.anchor.kind));
    if (populated) setPendingSelection(kind); else switchTo(kind);
  };
  async function submit(action: 'validate' | 'run') {
    if (!draft) return;
    const token = revisions.current.begin();
    const controller = new AbortController(); active.current?.abort(); active.current = controller;
    setMessages([]); setErrors({}); setBusy(action);
    if (action === 'run') setStale(true);
    try {
      if (unapplied.length) throw new InputErrors(Object.fromEntries(unapplied.map(key => [`quick.${key}`, 'Apply or discard this quick-entry draft before continuing.'])));
      const body = buildRequest(draft);
      const data = await load<Result | {status: string}>(`/api/v1/cases/${action}`, body, controller.signal);
      if (!revisions.current.current(token)) return;
      if (action === 'run') { setResult(data as Result); setStale(false); setStatus('Calculation complete — enterprise value only. Financial consistency and evidence completeness are not approved.'); }
      else setStatus('Input checks passed. No valuation calculated; economic consistency still needs review.');
    } catch (e) {
      if (!revisions.current.current(token)) return;
      if (e instanceof InputErrors) {setErrors(e.fields); setMessages(Object.entries(e.fields).map(([p,m]) => `${p}: ${m}`));}
      else if (e instanceof ApiError) {
        // Translate only known fraction-based diagnostics for percentage editors.
        // The raw API response and financial validation remain unchanged.
        const details = e.details.map(percentageDiagnostic);
        setErrors(fieldErrors(details)); setMessages([`${e.code}: ${e.message}`, ...details]);
      }
      else setMessages(['Unexpected local UI error. Entries are preserved.']);
      setStatus('Request did not succeed. Review the message below and retry explicitly; entries are preserved.');
    } finally {
      if (revisions.current.current(token)) {setBusy(null); active.current = null;}
    }
  }
  const input = (path: string, label: string, value: string, change: (value: string) => void, multiline = false) => {
    const fieldError = errors[path] ?? (path==='limitations' ? Object.entries(errors).find(([key])=>key.startsWith('limitations['))?.[1] : undefined);
    const props = {id: path, value, onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => change(e.target.value),
      'aria-invalid': Boolean(fieldError), 'aria-describedby': fieldError ? `${path}-error` : undefined};
    return <div className="field" key={path}><label htmlFor={path}>{label}</label>
      {multiline ? <textarea {...props} rows={3} /> : <input {...props} type="text" />}
      {fieldError && <span id={`${path}-error`} className="field-error">{fieldError}</span>}
    </div>;
  };
  const rateInput = (path: string, label: string) => input(path, label, draft!.rates[path], value => edit(next => {next.rates[path] = value;}));
  const reportInputError = (e: unknown) => {
    if (e instanceof InputErrors) {
      setErrors(e.fields); setMessages(Object.entries(e.fields).map(([path,message]) => `${path}: ${message}`));
    }
  };
  const performApply = (values: Partial<QuickValues>) => {
    if (!draft) return;
    const next = applyQuick(draft,values);
    invalidate(); setDraft(next);
    setUnapplied(old => old.filter(key => !(key in values)));
    setStatus('Applied once to the five forecast years. Annual and terminal inputs remain independently editable.');
  };
  const proposeApply = (keys: AnnualKey[]) => {
    if (!draft || !quick) return;
    const values = Object.fromEntries(keys.map(key => [key,quick[key]])) as Partial<QuickValues>;
    try {
      applyQuick(draft,values); // Presence/decimal-text check only, with no mutation.
      const overwrites = keys.some(key => draft.doc.forecast_years.some((_,i) => {
        const value = draft.rates[annualPath(key,i)];
        return value.trim() && !samePercentage(value,quick[key]);
      }));
      if (overwrites) setPendingApply(values); else performApply(values);
    } catch(e) {reportInputError(e);}
  };
  const copyTerminal = () => {
    if (!draft) return;
    try {
      const next=copyYearFive(draft); invalidate(); setDraft(next); setTerminalOpen(true);
      setStatus('Copied year-five operating ratios once. Terminal growth and WACC were not copied; future annual edits will not update terminal ratios.');
    } catch(e) {reportInputError(e); setAnnualOpen(true);}
  };
  const entry = catalog?.entries.find(e => e.kind === selected);
  const missingTerminal = draft ? terminal.filter(([key])=>!draft.rates[`terminal.${key}`].trim()).map(([,label])=>label.replace('Terminal ','')) : [];
  const pathLabel = (path: string) => {
    const match = /^forecast_years\[(\d)\]\.(.+)$/.exec(path);
    if (match && draft) return `${annual.find(([key])=>key===match[2])?.[1] ?? match[2]} — ${draft.doc.forecast_years[Number(match[1])].fiscal_year_label}`;
    if (/^(?:case\.)?limitations(?:\[|$)/.test(path)) return 'Limitations';
    if (path.startsWith('quick.')) return `${annual.find(([key])=>key===path.slice(6))?.[1] ?? path} quick entry`;
    if (path.startsWith('terminal.')) return terminal.find(([key])=>key===path.slice(9))?.[1] ?? path;
    return ({'case.case_name':'Case name',case_name:'Case name','preparation.notes':'Optional personal notes','preparation.timestamp_utc':'Preparation time',wacc:'WACC',terminal_growth:'Terminal growth'} as Record<string,string>)[path] ?? path;
  };
  const goToField = (path: string) => {
    const field=path.replace(/^case\./,'').replace(/^limitations\[\d+\]$/,'limitations');
    if (field.startsWith('forecast_years')) setAnnualOpen(true);
    else if (field.startsWith('terminal.')) setTerminalOpen(true);
    else if (!field.startsWith('quick.') && !['wacc','terminal_growth'].includes(field)) setDetailsOpen(true);
    requestAnimationFrame(()=>document.getElementById(field)?.focus());
  };
  const quickRow = (key: AnnualKey, label: string, hint: string) => {
    const state=annualState(draft!,key);
    const pending=unapplied.includes(key);
    const pathText=state.varies ? 'Varies by year — annual inputs used' : state.missing ? 'Unset — five annual values required' : `Five-year path: ${state.value}% every year`;
    return <div className="quick-row" key={key}>
      {input(`quick.${key}`,`${label} (%)`,quick![key],value=>{
        invalidate(); setQuick(old=>({...old!,[key]:value})); setUnapplied(old=>old.includes(key)?old:[...old,key]);
      })}
      <button onClick={()=>proposeApply([key])} aria-label={`Apply ${label} to five years`}>Apply</button>
      <p className={pending?'quick-status pending':'quick-status'} aria-live="polite">{pending ? 'Unapplied draft — apply or discard before calculating.' : pathText}</p>
      {pending && <button className="text-button" onClick={()=>{
        invalidate(); setQuick(old=>({...old!,[key]:state.varies?'':state.value})); setUnapplied(old=>old.filter(k=>k!==key));
      }}>Discard {label} draft</button>}
      <small>{hint}</small>
    </div>;
  };
  return <main>
    <header className="workbench-header"><div><div className="eyebrow">LOCAL VALUATION WORKBENCH</div><h1>Start with your assumptions.</h1><p>Retained historical observations. Your forecast. Enterprise value.</p></div>
      <div className="company-choice"><label htmlFor="company">Company</label><select id="company" value={selected==='demo'?'':selected} onChange={e=>choose(e.target.value)} disabled={!catalog}>
        <option value="">Select a company</option>{catalog?.entries.map(e=><option key={e.kind} value={e.kind}>{e.company} · FY2025</option>)}
      </select><button className="text-button" disabled={!catalog} onClick={()=>choose('demo')}>Load synthetic demonstration</button></div>
    </header>
    {!catalog && <p role="status">Loading retained company data… Check the local server if it is unavailable.</p>}
    {pendingSelection!==null && <Confirmation title="Discard populated edits?" confirmLabel="Discard and switch" cancelLabel="Keep editing" confirm={()=>switchTo(pendingSelection)} cancel={()=>setPendingSelection(null)}>Switching will discard populated annual inputs, quick-entry drafts, case details and results. No copy is saved.</Confirmation>}
    {entry && <section className="history-strip"><div><strong>{entry.company} · reported FY2025 revenue: {money(entry.revenue)} USD millions</strong><p>{entry.identity.annual_start} → {entry.identity.annual_end}. Fixed retained data, not automatically refreshed. Forecast inputs below are your estimates.</p></div>
      <details><summary>Filing, sources and historical limitations</summary><p>{entry.identity.form} · {entry.identity.accession} · CIK {entry.identity.cik}. Source precision {entry.precision} (−6: nearest million). Base unit {entry.unit}.</p><p>Fiscal-end analytical date: {entry.identity.annual_end}; later-filed information is used. A separate filing-acceptance timestamp is not supplied.</p><ul>{entry.source_links.map((url,i)=><li key={url}><a href={url} target="_blank" rel="noreferrer">Retained SEC filing source {i+1}</a></li>)}</ul><p>No verified information cutoff is established. Preparation time and personal notes do not certify information availability or source review.</p><ul>{enduringLimitations(entry.limitations).map((line,i)=><li key={i}>{line}</li>)}</ul></details>
    </section>}
    {selected==='demo' && <div className="notice"><strong>Synthetic demonstration — $100 revenue anchor.</strong> All example rates and declarations are synthetic, not company data or an investment case.</div>}
    {draft && quick ? <>
      <div className="workbench-grid"><section className="assumptions" aria-labelledby="assumptions-title"><h2 id="assumptions-title">Forecast assumptions</h2><p className="hint">Percentage entry: 10 means 10%. Apply creates a flat five-year path once; it is not an automatic company forecast.</p>
        <div className="assumption-columns"><div><h3>Main drivers</h3>
          {quickRow('revenue_growth','Annual revenue growth','Applied to each of the five years, not a cumulative five-year growth rate.')}
          {quickRow('operating_margin','Operating margin','Includes SBC, operating-lease service costs and aligned D&A expense once.')}
          <div className="discount-grid">{rateInput('wacc','WACC (%)')}{rateInput('terminal_growth','Terminal growth (%)')}</div>
        </div><div><h3>Required cash-flow inputs</h3><p className="hint">Four headline rates alone cannot construct FCFF.</p>
          {quickRow('forecast_tax_rate','Operating tax rate','Operating tax on positive EBIT; no immediate loss benefit.')}
          {quickRow('d_and_a_percent_revenue','Expense D&A / revenue','Must align with expenses included in operating margins.')}
          {quickRow('capex_percent_revenue','Investment / revenue','Cash PP&E + non-overlapping new finance-leased operating assets; excludes principal.')}
          {quickRow('change_in_operating_nwc_percent_revenue','WC cash requirement / full revenue','Positive consumes cash; negative releases cash. Uses full forecast revenue.')}
        </div></div>
        <button onClick={()=>proposeApply(annual.map(([key])=>key))}>Apply all six to five years</button>
        <p className="hint">Only applied annual inputs are submitted. Quick entries are drafts, never continuing links.</p>
        {pendingApply && <Confirmation title="Replace annual inputs?" confirmLabel="Replace annual inputs" cancelLabel="Keep annual edits" confirm={()=>performApply(pendingApply)} cancel={()=>setPendingApply(null)}>This replaces existing annual values with a flat path for: {Object.keys(pendingApply).map(key=>annual.find(([k])=>k===key)?.[1]).join(', ')}. Other rows and terminal assumptions stay independent.</Confirmation>}
        <details open={annualOpen} onToggle={e=>setAnnualOpen(e.currentTarget.open)}><summary>Advanced annual editing</summary><p>These are the authoritative annual inputs. Editing a year changes no other year or terminal ratio.</p>
          <div className="table-scroll" tabIndex={0} role="region" aria-label="Five-year assumption table"><table><thead><tr><th scope="col">Assumption (%)</th>{draft.doc.forecast_years.map(y=><th scope="col" key={y.period_index}>{y.fiscal_year_label}</th>)}</tr></thead><tbody>{annual.map(([key,label])=><tr key={key}><th scope="row">{label}</th>{draft.doc.forecast_years.map((year,i)=><td key={i}>{rateInput(annualPath(key,i),`${label} ${year.fiscal_year_label} (%)`)}</td>)}</tr>)}</tbody></table></div>
        </details>
        <div className="terminal-section"><h3>Terminal operating assumptions</h3><p className={missingTerminal.length?'missing-note':'hint'}>{missingTerminal.length ? `Missing terminal inputs: ${missingTerminal.join('; ')}.` : 'All five terminal operating ratios supplied.'}</p>
          <button onClick={copyTerminal}>Use year-five operating ratios for the terminal year</button><p className="hint">Copies once, assuming sustainable year-five margins and reinvestment. Does not copy growth or WACC; later annual edits do not update terminal inputs.</p>
          <details open={terminalOpen} onToggle={e=>setTerminalOpen(e.currentTarget.open)}><summary>Edit terminal ratios ({missingTerminal.length} missing)</summary><div className="rate-grid">{terminal.map(([key,label])=>rateInput(`terminal.${key}`,`${label} (%)`))}</div></details>
        </div>
        <details open={detailsOpen} onToggle={e=>setDetailsOpen(e.currentTarget.open)}><summary>Analysis details</summary>
          <p>Anonymous investor calculation. Forecasts are user-entered and not independently reviewed. No verified person, professional analyst or investment rationale is asserted.</p>
          {input('case_name','Case name',draft.doc.case_name,value=>edit(n=>{n.doc.case_name=value;}))}
          <p>Prepared at: <time>{draft.doc.preparation.timestamp_utc}</time>. Generated when this draft was created and retained through submissions; not a valuation date, information cutoff or evidence review.</p>
          {input('preparation.notes','Optional personal notes',draft.doc.preparation.notes??'',value=>edit(n=>{n.doc.preparation.notes=value;}),true)}
          <p className="hint">Empty notes are absent (null). Notes are your wording, not verified sources or an investment rationale. Limit: 2,048 characters.</p>
          <p>{Object.values(draft.rates).filter(value=>value.trim()).length} of 37 numerical inputs entered; financial validation still applies. Company templates begin unset, without defaults or historical calibration.</p>
          <ul>{draft.doc.limitations.map((line,i)=><li key={i}>{line}</li>)}</ul>
          <details><summary>Exact submitted request and source bindings</summary><pre>{(()=>{try{return JSON.stringify(buildRequest(draft),null,2);}catch{return 'Correct invalid percentage entries to inspect the request.';}})()}</pre></details>
        </details>
        <div className="run-controls">{unapplied.length>0 && <p className="missing-note">Unapplied quick-entry drafts: {unapplied.map(key=>annual.find(([k])=>k===key)?.[1]).join(', ')}. Apply or discard them before calculating.</p>}
          <div className="actions"><button className="primary" disabled={Boolean(busy)} onClick={()=>void submit('run')}>Calculate enterprise value</button><button disabled={Boolean(busy)} onClick={()=>void submit('validate')}>Check inputs</button></div>
          <p role="status" aria-live="polite">{busy ? `${busy==='run'?'Calculating':'Checking inputs'}… Edits cancel this request.` : status}</p>
          {messages.length>0 && <div role="alert" className="errors"><h3>{Object.keys(errors).length ? 'Inputs need attention' : 'Request did not succeed'}</h3><ul>{messages.map((message,i)=>{
            const colon=message.indexOf(':');const path=message.slice(0,colon);
            return <li key={i}>{errors[path.replace(/^case\./,'')] ? <button className="text-button" onClick={()=>goToField(path)}>{pathLabel(path)}: {message.slice(colon+1)}</button> : message}</li>;
          })}</ul><p>{Object.keys(errors).length ? 'Correct the indicated inputs and check again; server error lists are bounded.' : 'Review the service message and retry explicitly when available; changing assumptions is not required to recover from a service failure.'} Inputs are preserved.</p></div>}
        </div>
      </section><aside aria-label="Valuation review">{result ? <ResultReview result={result} stale={stale}/> : <section className="result-placeholder"><div className="section-number">ENTERPRISE VALUE</div><h2>Your result appears here.</h2><p>Supply six annual assumptions, WACC, terminal growth, five terminal ratios then calculate explicitly. Analysis details and personal notes are optional.</p><p>EV values the operating business. It is not equity value or value per share.</p></section>}</aside></div>
    </> : <section className="empty-state"><h2>Select a retained company to begin.</h2><p>Company forecasts start unset. The separate demonstration uses a synthetic $100 revenue anchor.</p></section>}
    {!draft && messages.length>0 && <div role="alert" className="errors">{messages.join(' ')}</div>}
    <footer>Local only · No automatic saving · Phase 1 expansion paused · Developer-tested workflow, not investor acceptance or a replacement for professional Excel modeling.</footer>
  </main>;
}
