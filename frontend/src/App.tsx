import {useEffect, useRef, useState} from 'react';
import {annual, terminal, makeDraft, buildRequest, fieldErrors, InputErrors, annualState, annualPath, editQuick, replaceAnnual, copyYearFive, samePercentage, generatedCaseName, enduringLimitations, entryErrors, reviewErrors, displayPath, terminalDifferences} from './model';
import type {Catalog, Draft, Errors, Result, AnnualKey} from './model';
import {ApiError, request, Revisions} from './api';
import {ResultReview} from './Results';
import {readableMoney, readableLimitation} from './presentation';
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
      ? 'Operating tax must be between 0% and 100%.'
      : message === 'Revenue growth must be at least -1' ? 'Annual revenue growth must be at least −100%.'
      : message === 'WACC must be greater than zero' ? 'WACC must be greater than 0%.'
      : message === 'Terminal growth must be greater than -1' ? 'Long-term revenue growth must be greater than −100%.'
      : message === 'Terminal growth must be less than WACC' ? 'Long-term revenue growth must be below WACC.'
      : message;
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
  const [pendingReplacement, setPendingReplacement] = useState<AnnualKey | null>(null);
  const [pendingCopy, setPendingCopy] = useState<string[]>([]);
  const [annualOpen, setAnnualOpen] = useState(false);
  const [terminalOpen, setTerminalOpen] = useState(false);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [pendingSelection, setPendingSelection] = useState<string | null>(null);
  const [serverErrors, setServerErrors] = useState<Errors>({});
  const [touched, setTouched] = useState<Record<string,boolean>>({});
  const [submitted, setSubmitted] = useState(false);
  const edited = useRef(new Set<string>());
  const blurSequence = useRef(0);
  const blurRequest = useRef<AbortController | null>(null);
  const [messages, setMessages] = useState<string[]>([]);
  const [status, setStatus] = useState('Choose a company or the separate synthetic demonstration.');
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
    return () => { abort.abort(); active.current?.abort(); blurRequest.current?.abort(); };
  }, [load]);
  const invalidate = (paths: string[] = []) => {
    revisions.current.edit(); active.current?.abort(); active.current = null;
    blurSequence.current++; blurRequest.current?.abort();
    setBusy(null); setStale(true); setMessages([]); setPendingReplacement(null); setPendingCopy([]);
    setStatus('Inputs changed. Calculate again when ready.');
    const affected = new Set(paths);
    if (paths.some(p=>['wacc','terminal_growth'].includes(p))) affected.add('terminal_growth (relative to wacc)');
    setServerErrors(old=>Object.fromEntries(Object.entries(old).filter(([p])=>!affected.has(p))));
  };
  const edit = (paths: string[], change: (next: Draft) => void) => {
    if (!draft) return;
    paths.forEach(p=>edited.current.add(p));
    invalidate(paths); const next = structuredClone(draft); change(next); setDraft(next);
  };
  const switchTo = (kind: string) => {
    if (!catalog) return;
    invalidate(); setSelected(kind); setResult(null); setStale(false);
    const template = kind === 'demo' ? catalog.synthetic_demo : catalog.entries.find(e => e.kind === kind)?.template;
    setDraft(template ? makeDraft(template) : null);
    setTouched({}); setSubmitted(false); setServerErrors({}); edited.current.clear();
    setAnnualOpen(false); setTerminalOpen(false); setDetailsOpen(false);
    setStatus(kind === 'demo' ? 'Synthetic demonstration loaded explicitly. Anchor revenue is synthetic $100; all rates are examples.' : 'Enter your forecast assumptions. Notes are optional.');
    setPendingSelection(null);
  };
  const choose = (kind: string) => {
    if (kind === selected) return;
    const populated = draft && (Object.keys(draft.replacements).length || Object.values(draft.rates).some(v => v.trim()) || draft.doc.preparation.notes !== null || draft.doc.case_name !== generatedCaseName(draft.doc.anchor.kind));
    if (populated) setPendingSelection(kind); else switchTo(kind);
  };
  const allErrors = draft ? reviewErrors(draft,{...serverErrors,...entryErrors(draft)}) : {};
  const touchedGroups = new Set(Object.keys(touched).map(path=>draft ? displayPath(draft,path) : path));
  const errors = Object.fromEntries(Object.entries(allErrors).filter(([path])=>submitted || touchedGroups.has(path)));
  const reveal = (raw: Errors) => {
    if (!draft) return;
    const grouped=reviewErrors(draft,raw);
    setStatus(`Review ${Object.keys(grouped).length} input issue(s). Entries are preserved.`);
    if (Object.keys(grouped).length) goToField(Object.keys(grouped)[0]);
  };
  async function blur(path: string) {
    if (!draft || !edited.current.has(path)) return;
    edited.current.delete(path);
    const annualKey=path.startsWith('quick.') ? path.slice(6) as AnnualKey : null;
    const annualTouches=annualKey ? Object.fromEntries(draft.doc.forecast_years.map((_,i)=>[annualPath(annualKey,i),true])) : {};
    setTouched(old=>({...old,...annualTouches,[path]:true}));
    // Syntax/presence guidance is local. Numerical domains remain Python's job.
    // Partial cases remain null; never invent operands to obtain a field check.
    let body;
    try {body=buildRequest(draft);} catch {return;}
    const sequence=++blurSequence.current;
    blurRequest.current?.abort(); const controller=new AbortController(); blurRequest.current=controller;
    try {
      await load('/api/v1/cases/validate',body,controller.signal);
      if (sequence===blurSequence.current) setServerErrors({});
    } catch(e) {
      if (sequence!==blurSequence.current) return;
      if (e instanceof ApiError && e.code==='invalid_case') setServerErrors(fieldErrors(e.details.map(percentageDiagnostic)));
      // Background validation failure is not a financial error. Explicit submission
      // reports service failures; it never reuses a background result as approval.
    }
  }
  async function submit(action: 'validate' | 'run') {
    if (!draft) return;
    blurSequence.current++; blurRequest.current?.abort(); setSubmitted(true);
    const token = revisions.current.begin();
    const controller = new AbortController(); active.current?.abort(); active.current = controller;
    setMessages([]); setBusy(action);
    if (action === 'run') setStale(true);
    try {
      const local=entryErrors(draft);
      if (Object.keys(local).length) throw new InputErrors(local);
      const body = buildRequest(draft);
      const data = await load<Result | {status: string}>(`/api/v1/cases/${action}`, body, controller.signal);
      if (!revisions.current.current(token)) return;
      setServerErrors({});
      if (action === 'run') { setResult(data as Result); setStale(false); setStatus('Calculation complete — enterprise value only. Inputs have not been economically approved.'); }
      else setStatus('Input checks passed. No valuation calculated; economic consistency still needs review.');
    } catch (e) {
      if (!revisions.current.current(token)) return;
      if (e instanceof InputErrors) reveal({...serverErrors,...e.fields});
      else if (e instanceof ApiError && e.code==='invalid_case' && e.details.length) {
        const fields=fieldErrors(e.details.map(percentageDiagnostic));
        setServerErrors(fields); reveal(fields);
      }
      else {
        setMessages([e instanceof ApiError ? `${e.code}: ${e.message}` : 'Unexpected local UI error. Entries are preserved.']);
        setStatus('Service request did not succeed. Entries are preserved; retry explicitly.');
      }
    } finally {
      if (revisions.current.current(token)) {setBusy(null); active.current = null;}
    }
  }
  const input = (path: string, label: string, value: string, change: (value: string) => void, multiline = false, hint = '') => {
    const fieldError = errors[path] ?? (draft && path.startsWith('forecast_years') && (submitted || touched[path]) ? errors[displayPath(draft,path)] : undefined);
    const props = {id: path, value, onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => change(e.target.value), onBlur: ()=>void blur(path),
      'aria-invalid': Boolean(fieldError), 'aria-describedby': [hint ? `${path}-help` : '',fieldError ? `${path}-error` : ''].filter(Boolean).join(' ') || undefined};
    return <div className="field" key={path}><label htmlFor={path}>{label}</label>
      {multiline ? <textarea {...props} rows={3} /> : <input {...props} type="text" />}
      {hint && <details className="field-help"><summary aria-label={`Help: ${label}`}>?</summary><small id={`${path}-help`}>{hint}</small></details>}
      {fieldError && <span id={`${path}-error`} className="field-error">{fieldError}</span>}
    </div>;
  };
  const rateInput = (path: string, label: string, hint = '') => input(path,label,draft!.rates[path],value=>edit([path],next=>{
    next.rates[path]=value;
    const match=/^forecast_years\[\d+\]\.(.+)$/.exec(path);
    if (match) delete next.replacements[match[1] as AnnualKey];
  }),false,hint);
  const performReplacement = (key: AnnualKey) => {
    if (!draft) return;
    const next=replaceAnnual(draft,key);
    invalidate(draft.doc.forecast_years.map((_,i)=>annualPath(key,i))); setDraft(next);
    setStatus('One rate now applies to all five years. Other inputs and long-term assumptions are unchanged.');
    requestAnimationFrame(()=>document.getElementById(`quick.${key}`)?.focus());
  };
  const proposeReplacement = (key: AnnualKey) => {
    if (!draft) return;
    try {replaceAnnual(draft,key);setPendingReplacement(key);}
    catch {
      if (!(key in draft.replacements)) edit([`quick.${key}`],next=>{next.replacements[key]='';});
      setTouched(old=>({...old,[`quick.${key}`]:true})); document.getElementById(`quick.${key}`)?.focus();
    }
  };
  const keepAnnual = (key: AnnualKey) => {
    edit([`quick.${key}`],next=>{delete next.replacements[key];});
    setStatus('Annual values kept. No uniform replacement was made.');
  };
  const performCopy = () => {
    if (!draft) return;
    const next=copyYearFive(draft); invalidate(terminal.map(([key])=>`terminal.${key}`)); setDraft(next); setTerminalOpen(true);
    setStatus('Final-year operating assumptions copied once. Discount rate and long-term growth are unchanged; later annual edits stay independent.');
  };
  const copyTerminal = () => {
    if (!draft) return;
    try {
      const next=copyYearFive(draft);
      const changed=terminal.filter(([key])=>draft.rates[`terminal.${key}`].trim() && !samePercentage(draft.rates[`terminal.${key}`],next.rates[`terminal.${key}`])).map(([,label])=>label);
      if (changed.length) setPendingCopy(changed); else performCopy();
    } catch(e) {
      if (e instanceof InputErrors) {
        const paths=reviewErrors(draft,e.fields); setTouched(old=>({...old,...Object.fromEntries(Object.keys(paths).map(p=>[p,true]))}));
        reveal(e.fields);
      }
    }
  };
  const entry = catalog?.entries.find(e => e.kind === selected);
  const missingTerminal = draft ? terminal.filter(([key])=>!draft.rates[`terminal.${key}`].trim()).map(([,label])=>label.replace('Long-term ','')) : [];
  const pathLabel = (path: string) => {
    const match = /^forecast_years\[(\d)\]\.(.+)$/.exec(path);
    if (match && draft) return `${annual.find(([key])=>key===match[2])?.[1] ?? match[2]} — ${draft.doc.forecast_years[Number(match[1])].fiscal_year_label}`;
    if (/^(?:case\.)?limitations(?:\[|$)/.test(path)) return 'Limitations';
    if (path.startsWith('quick.')) return annual.find(([key])=>key===path.slice(6))?.[1] ?? path;
    if (path.startsWith('terminal.')) return terminal.find(([key])=>key===path.slice(9))?.[1] ?? path;
    return ({'case.case_name':'Case name',case_name:'Case name','preparation.notes':'Optional personal notes','preparation.timestamp_utc':'Preparation time',wacc:'Discount rate — WACC',terminal_growth:'Long-term revenue growth'} as Record<string,string>)[path] ?? path;
  };
  const goToField = (path: string) => {
    const field=path.replace(/^case\./,'').replace(/^limitations\[\d+\]$/,'limitations');
    if (field.startsWith('forecast_years')) setAnnualOpen(true);
    else if (field.startsWith('terminal.')) setTerminalOpen(true);
    else if (!field.startsWith('quick.') && !['wacc','terminal_growth'].includes(field)) setDetailsOpen(true);
    requestAnimationFrame(()=>(document.getElementById(field) ?? document.getElementById('input-issues'))?.focus());
  };
  const quickRow = (key: AnnualKey, label: string, hint: string) => {
    const state=annualState(draft!,key);
    const replacing=key in draft!.replacements;
    return <div className="quick-row" key={key}>
      {input(`quick.${key}`,`${label} (%)`,replacing ? draft!.replacements[key]! : state.varies ? '' : state.value,value=>{
        const paths=state.varies || replacing ? [`quick.${key}`] : draft!.doc.forecast_years.map((_,i)=>annualPath(key,i));
        edited.current.add(`quick.${key}`); invalidate(paths); setDraft(editQuick(draft!,key,value));
      },false,hint)}
      {state.varies && <p className="quick-status">Varies by year</p>}
      {(state.varies || replacing) && <>
        <button onClick={()=>proposeReplacement(key)} aria-label={`Use ${label} for all five years`}>Use for all five years</button>
        {replacing && <button className="text-button" onClick={()=>keepAnnual(key)}>Keep annual values for {label}</button>}
        <small>A replacement is a proposal until confirmed. Calculate cannot use the old path while a proposal is displayed.</small>
      </>}
    </div>;
  };
  return <main>
    <header className="workbench-header"><div><h1>DCF Calculator</h1><span className="eyebrow">Enterprise value</span></div>
      <div className="company-choice"><label htmlFor="company">Company</label><select id="company" value={selected==='demo'?'':selected} onChange={e=>choose(e.target.value)} disabled={!catalog}>
        <option value="">Select a company</option>{catalog?.entries.map(e=><option key={e.kind} value={e.kind}>{e.company} · FY2025</option>)}
      </select><button className="text-button" disabled={!catalog} onClick={()=>choose('demo')}>Load synthetic demonstration</button></div>
    </header>
    {!catalog && <p role="status">Loading company data… Check the local server if it is unavailable.</p>}
    {pendingSelection!==null && <Confirmation title="Discard populated edits?" confirmLabel="Discard and switch" cancelLabel="Keep editing" confirm={()=>switchTo(pendingSelection)} cancel={()=>setPendingSelection(null)}>Switching will discard populated annual inputs, replacement proposals, analysis details and results. No copy is saved.</Confirmation>}
    {entry && <section className="history-strip"><div className="company-summary"><strong>{entry.company} · FY2025</strong><span>Reported revenue <b>{readableMoney(entry.revenue)}</b> USD</span></div><p>Fixed historical data, not live. Forecasts are user-entered and not independently reviewed.</p>
      <details><summary>Data &amp; methodology</summary><p>Fiscal period: {entry.identity.annual_start} → {entry.identity.annual_end}.</p><p>{entry.identity.form} · {entry.identity.accession} · CIK {entry.identity.cik}. Source precision {entry.precision} (−6: nearest million). Base unit {entry.unit}.</p><p>Fiscal-end analytical date: {entry.identity.annual_end}; later-filed information is used. A separate filing-acceptance timestamp is not supplied.</p><ul>{entry.source_links.map((url,i)=><li key={url}><a href={url} target="_blank" rel="noreferrer">SEC filing source {i+1}</a></li>)}</ul><p>No verified information cutoff is established. Preparation time and personal notes do not certify information availability or source review.</p><ul>{enduringLimitations(entry.limitations).map((line,i)=><li key={i}>{readableLimitation(line)}</li>)}</ul></details>
    </section>}
    {selected==='demo' && <div className="notice"><strong>Synthetic demonstration — USD $100 revenue anchor.</strong> All example rates and declarations are synthetic, not company data or an investment case.</div>}
    {draft ? <>
      <div className="workbench-grid"><section className="assumptions" aria-labelledby="assumptions-title"><div className="section-heading"><h2 id="assumptions-title">Forecast assumptions</h2><span className="completion">{Object.values(draft.rates).filter(value=>!value.trim()).length} of 37 unset</span></div><p className="hint">Enter percentages: 10 = 10%. Quick entries apply to all five years.</p>
        <div className="assumption-columns"><div><h3>Growth &amp; profitability</h3><div className="rate-grid">
          {quickRow('revenue_growth','Annual revenue growth','Compounds each year from the selected historical revenue anchor.')}
          {quickRow('operating_margin','Operating profit margin','EBIT divided by revenue. Includes SBC, operating-lease service costs and aligned D&A expense once.')}
        </div></div><div><h3>Valuation</h3><div className="rate-grid">
          {rateInput('wacc','Discount rate — WACC (%)','The constant rate used to discount operating cash flows.')}{rateInput('terminal_growth','Long-term revenue growth (%)','Applies after the five-year forecast and must remain below WACC.')}
        </div></div></div>
        <h3>Cash-flow assumptions</h3><div className="cash-grid">
          {quickRow('forecast_tax_rate','Operating tax rate','Tax on positive operating profit; no immediate benefit for losses.')}
          {quickRow('d_and_a_percent_revenue','D&A / revenue','Expense-aligned depreciation and amortization. Must align with expenses included in operating margins, including finance-asset depreciation once.')}
          {quickRow('capex_percent_revenue','Investment / revenue','Cash PP&E + non-overlapping new finance-leased operating assets; excludes finance-lease principal. Do not duplicate capital-creditor settlements.')}
          {quickRow('change_in_operating_nwc_percent_revenue','Working-capital cash needs / revenue','Uses full annual forecast revenue, not the change in revenue. Positive uses cash; negative releases cash. Historical CFO movements are not automatic forecast inputs.')}
        </div>
        {pendingReplacement && <Confirmation title="Replace annual inputs?" confirmLabel="Replace annual inputs" cancelLabel="Keep annual edits" confirm={()=>performReplacement(pendingReplacement)} cancel={()=>keepAnnual(pendingReplacement)}>
          Use {annual.find(([key])=>key===pendingReplacement)?.[1]} of {draft.replacements[pendingReplacement]}% for {draft.doc.forecast_years.map(y=>y.fiscal_year_label).join(', ')}? Other fields and long-term assumptions stay unchanged.
        </Confirmation>}
        <details open={annualOpen} onToggle={e=>setAnnualOpen(e.currentTarget.open)}><summary>Edit individual years</summary><p>Edit each year independently. Changes do not update long-term ratios.</p>
          <div className="table-scroll" tabIndex={0} role="region" aria-label="Five-year assumption table"><table><thead><tr><th scope="col">Assumption (%)</th>{draft.doc.forecast_years.map(y=><th scope="col" key={y.period_index}>{y.fiscal_year_label}</th>)}</tr></thead><tbody>{annual.map(([key,label])=><tr key={key}><th scope="row">{label}</th>{draft.doc.forecast_years.map((year,i)=><td key={i}>{rateInput(annualPath(key,i),`${label} ${year.fiscal_year_label} (%)`)}</td>)}</tr>)}</tbody></table></div>
        </details>
        <div className="terminal-section"><div className="section-heading"><div><h3>Long-term assumptions</h3><span className="hint">{missingTerminal.length ? `${missingTerminal.length} of 5 ratios unset` : '5 ratios entered · independent of annual edits'}</span></div><button onClick={copyTerminal}>Copy final-year assumptions</button></div><p className="hint">Copy only if final-year operating ratios are sustainable.</p>
          <details><summary>About long-term assumptions</summary><p>Copies margin, tax, D&A, investment and working-capital cash needs once. Growth and WACC are not copied. Check that reinvestment supports sustainable growth; later annual edits stay independent.</p></details>
          {pendingCopy.length>0 && <Confirmation title="Replace long-term assumptions?" confirmLabel="Replace long-term assumptions" cancelLabel="Keep long-term assumptions" confirm={performCopy} cancel={()=>setPendingCopy([])}>
            Copy from {draft.doc.forecast_years[4].fiscal_year_label}. Populated values that would change: {pendingCopy.join('; ')}. Later annual edits will not update them.
          </Confirmation>}
          {!missingTerminal.length && <p className="hint">{terminalDifferences(draft).length ? `${terminalDifferences(draft).length} ratios differ from the final year.` : 'Operating ratios currently match the final year; they remain independent.'}</p>}
          <details open={terminalOpen} onToggle={e=>setTerminalOpen(e.currentTarget.open)}><summary>Edit long-term operating ratios</summary>{terminalDifferences(draft).length>0 && <p className="hint">Differs from final year: {terminalDifferences(draft).join('; ')}.</p>}<div className="rate-grid">{terminal.map(([key,label])=>rateInput(`terminal.${key}`,`${label} (%)`))}</div></details>
        </div>
        <details open={detailsOpen} onToggle={e=>setDetailsOpen(e.currentTarget.open)}><summary>Analysis details</summary>
          <p>Anonymous investor calculation. Forecasts are user-entered and not independently reviewed. No verified person, professional analyst or investment rationale is asserted.</p>
          {input('case_name','Case name',draft.doc.case_name,value=>edit(['case_name'],n=>{n.doc.case_name=value;}))}
          <p>Prepared at: <time>{draft.doc.preparation.timestamp_utc}</time>. Generated when this draft was created and retained through submissions; not a valuation date, information cutoff or evidence review.</p>
          {input('preparation.notes','Optional personal notes',draft.doc.preparation.notes??'',value=>edit(['preparation.notes'],n=>{n.doc.preparation.notes=value;}),true)}
          <p className="hint">Empty notes are absent (null). Notes are your wording, not verified sources or an investment rationale. Limit: 2,048 characters.</p>
          <p>{Object.values(draft.rates).filter(value=>value.trim()).length} of 37 numerical inputs entered; financial validation still applies. Company templates begin unset, without defaults or historical calibration.</p>
          <ul>{draft.doc.limitations.map((line,i)=><li key={i}>{readableLimitation(line)}</li>)}</ul>
          <details><summary>Full-precision request and provenance</summary><pre>{(()=>{try{return JSON.stringify(buildRequest(draft),null,2);}catch{return 'Correct invalid percentage entries to inspect the request.';}})()}</pre></details>
        </details>
        <div className="run-controls">
          <div className="actions"><button className="primary" disabled={Boolean(busy)} onClick={()=>void submit('run')}>Calculate enterprise value</button></div>
          <p role="status" aria-live="polite">{busy ? `${busy==='run'?'Calculating':'Checking inputs'}… Edits cancel this request.` : status}</p>
          {submitted && Object.keys(errors).length>0 && <div id="input-issues" tabIndex={-1} className="errors" role="region" aria-label="Input issues"><h3>Review {Object.keys(errors).length} input issue(s)</h3>
            <ul>{Object.entries(errors).slice(0,3).map(([path,message])=><li key={path}><button className="text-button" onClick={()=>goToField(path)}>{pathLabel(path)}: {message}</button></li>)}</ul>
            {Object.keys(errors).length>3 && <details><summary>All input issues</summary><ul>{Object.entries(errors).slice(3).map(([path,message])=><li key={path}><button className="text-button" onClick={()=>goToField(path)}>{pathLabel(path)}: {message}</button></li>)}</ul></details>}
            <p>Correct these entries and calculate again. Further financial checks may follow correction.</p>
          </div>}
          {messages.length>0 && <div role="alert" className="errors"><h3>Service request did not succeed</h3>{messages.map((message,i)=><p key={i}>{message}</p>)}<p>Retry explicitly when the service is available. Entries are preserved; changing assumptions is not required to recover from a service failure.</p></div>}
        </div>
      </section><aside aria-label="Valuation review">{result ? <ResultReview result={result} stale={stale}/> : <section className="result-placeholder"><h2>Enterprise value</h2><p>Enter assumptions, then calculate.</p><small>Operating business value; excludes the cash/debt/share bridge.</small></section>}</aside></div>
    </> : <section className="empty-state"><h2>Select a company to begin.</h2><p>Company forecasts start unset. The separate demonstration uses a synthetic $100 revenue anchor.</p></section>}
    {!draft && messages.length>0 && <div role="alert" className="errors">{messages.join(' ')}</div>}
    <footer>No automatic saving <span>· Local environment</span></footer>
  </main>;
}
