import {useEffect, useState} from 'react';
import {fetchComparables} from './client';
import {peerTickers, type ComparablesPackage, type PeerTicker, type Growth} from './types';
import './tradingComparables.css';

const bn = (v: number|null) => v === null ? 'Unavailable' : (v/1e9).toFixed(2);
const money = (v: number|null) => v === null ? 'Not disclosed' : `${v<0?'−':''}$${(Math.abs(v)/1e9).toFixed(2)}B`;
const pct = (v: number|null) => v === null ? 'Unavailable' : `${(v*100).toFixed(1)}%`;
const growth = (v: number|null) => v === null ? 'Unavailable' : `${v>=0?'+':''}${pct(v)}`;
type Tab = 'financials'|'business'|'valuation';

function GrowthReadout({value}: {value: Growth}) {
  return <div className="tc-growth"><span>Quarter revenue growth · YoY</span><strong>{growth(value.growth)}</strong><small>vs {money(value.prior)} · Jul–Sep 2025</small></div>;
}
function Table({headers, rows, label}: {headers: string[]; rows: React.ReactNode[][]; label: string}) {
  return <div className="tc-table-scroll"><table aria-label={label}><thead><tr>{headers.map(h => <th key={h} scope="col">{h}</th>)}</tr></thead><tbody>{rows.map((row,i) => <tr key={i}>{row.map((cell,j) => j===0 ? <th key={j} scope="row">{cell}</th> : <td key={j}>{cell}</td>)}</tr>)}</tbody></table></div>;
}
function DirectComparisons({data: d}: {data: ComparablesPackage}) {
  const g = d.businesses.GOOGL, a = d.businesses.AMZN;
  const cloud = [
    {name:'Google Cloud', scope:'GCP + Workspace + other enterprise services', key:'GOOGL_cloud', ebit:g.cloud_ebit},
    {name:'AWS', scope:'Amazon Web Services segment', key:'AMZN_aws', ebit:a.aws_ebit},
    {name:'Azure', scope:'Microsoft Azure product revenue', key:'MSFT_azure', ebit:null},
  ];
  const ads = [
    {name:'Google Ads', scope:'Search · YouTube ads · Network', key:'GOOGL_advertising'},
    {name:'Meta Ads', scope:'Family of Apps advertising', key:'META_advertising'},
    {name:'Reddit Ads', scope:'Disclosed advertising revenue', key:'RDDT_advertising'},
    {name:'Pinterest', scope:'Total-company revenue proxy', key:'PINS_total'},
  ];
  return <>
    <div className="tc-subheading"><div><span className="tc-eyebrow">Cloud infrastructure & services</span><h3>GCP / Google Cloud vs AWS & Azure</h3></div><span>Quarter ended {d.quarter_end}</span></div>
    <div className="tc-cloud-grid">{cloud.map((c,i) => <article key={c.key} className={i===0?'tc-reference':''} aria-label={`${c.name} comparison`}><span className="tc-eyebrow">{i===0?'Alphabet':'Cloud peer'}</span><h4>{c.name}</h4><p className="tc-scope">{c.scope}</p><span>Quarter revenue</span><strong className="tc-big-number">{money(d.growth[c.key].current)}</strong><dl><div><dt>Operating income</dt><dd>{money(c.ebit)}</dd></div><div><dt>Operating margin</dt><dd>{c.ebit===null?'Not disclosed':pct(c.ebit/d.growth[c.key].current)}</dd></div></dl><GrowthReadout value={d.growth[c.key]}/></article>)}</div>
    <p className="tc-note">GCP-only revenue and profit are not separately disclosed. Google Cloud includes Workspace. AWS and Google Cloud use different segment cost allocations. Azure-only operating profit is unavailable.</p>
    <div className="tc-subheading"><div><span className="tc-eyebrow">Digital advertising</span><h3>Google Ads vs Meta, Reddit & Pinterest</h3></div><span>Same reported quarter · USD</span></div>
    <div className="tc-ads-grid">{ads.map((c,i) => <article key={c.key} className={i===0?'tc-reference':''} aria-label={`${c.name} comparison`}><span className="tc-eyebrow">{i===0?'Alphabet':'Advertising peer'}</span><h4>{c.name}</h4><p className="tc-scope">{c.scope}</p><strong className="tc-big-number">{money(d.growth[c.key].current)}</strong><span>{c.key==='PINS_total'?'Company total · proxy':'Advertising revenue'}</span><GrowthReadout value={d.growth[c.key]}/></article>)}</div>
    <h4 className="tc-spaced">Inside Google advertising</h4>
    <Table label="Google advertising revenue and growth" headers={['Reported component','Jul–Sep 2025, $B','Jul–Sep 2026, $B','YoY growth']} rows={[
      ['Google Search & other','GOOGL_search'],['YouTube advertising','GOOGL_youtube_ads'],['Google Network','GOOGL_network'],
    ].map(([name,key]) => [name,bn(d.growth[key].prior),bn(d.growth[key].current),growth(d.growth[key].growth)])}/>
    <p className="tc-note">Nominal USD growth uses the same filing’s prior-year quarter, including its comparative presentation. Google Ads growth is based on summed revenue, not averaged growth rates. Pinterest is a company-level proxy. Advertising-only EBIT is not consistently available.</p>
  </>;
}

function PeerFinancials({data: d}: {data: ComparablesPackage}) {
  const [selected,setSelected] = useState<PeerTicker>('GOOGL');
  const p = d.peers[selected];
  return <>
    <h3>Scale, profitability & reinvestment</h3><p className="tc-note">TTM ended {d.quarter_end} · USD billions · Consolidated companies</p>
    <Table label="Peer financial comparison" headers={['Company / proposed role','Revenue','EBIT','EBIT margin','Cash capex / sales','SBC / sales']} rows={peerTickers.map(t => {
      const q=d.peers[t],v=q.ttm;
      return [<button className="tc-peer-button" aria-pressed={selected===t} onClick={()=>setSelected(t)}>{q.name}<small>{t} · {q.role}</small></button>,bn(v.revenue),bn(v.ebit),pct(v.ebit/v.revenue),pct(v.cash_capex/v.revenue),pct(v.sbc/v.revenue)];
    })}/>
    <section className="tc-selected" aria-label="Selected peer financial detail" aria-live="polite"><div className="tc-subheading"><div><span className="tc-eyebrow">{selected} · {p.role}</span><h3>{p.name}</h3></div><span>Quarter revenue growth {growth(p.quarter_growth)} YoY</span></div>
      <dl className="tc-cash-strip">{[['Operating cash flow',p.ttm.cfo],['Gross cash capex',p.ttm.cash_capex],['Cash FCF',p.ttm.cfo-p.ttm.cash_capex],['Stock-based compensation',p.ttm.sbc]].map(([name,value]) => <div key={name}><dt>{name}</dt><dd>{money(value as number)}</dd></div>)}</dl><p>{p.note}</p>
      <details><summary>Source data & TTM calculation</summary><Table label={`${p.name} TTM revenue operands`} headers={['Revenue calculation','Period','USD billions','SEC source']} rows={p.revenue_operands.map((o,i) => [i===0?'Latest fiscal annual':i===1?'+ Current fiscal YTD':'− Prior fiscal YTD',`${o.start} → ${o.end}`,bn(o.value),<a href={o.source_url} target="_blank" rel="noreferrer">{o.filed} filing ↗</a>])}/><p className="tc-note">TTM = annual + current YTD − same-filing prior YTD. Quarter growth above uses prepared July–September quarters; revision vintages may differ. Cash FCF is CFO less gross cash purchases, not FCFF/FCFE. Gross capex differs from net capex and lease-funded investment.</p></details>
    </section>
  </>;
}

function BusinessDetails({data:d}: {data: ComparablesPackage}) {
  const g=d.businesses.GOOGL,m=d.businesses.META;
  return <><h3>Reported profit units</h3><p className="tc-note">Quarter ended {d.quarter_end} · USD billions</p><Table label="Reported services profitability" headers={['Reported unit','Revenue','Operating income','Operating margin']} rows={[
    ['Google Services',bn(g.services),bn(g.services_ebit),pct(g.services_ebit!/g.services!)],
    ['Meta Family of Apps',bn(m.family_of_apps),bn(m.family_of_apps_ebit),pct(m.family_of_apps_ebit!/m.family_of_apps!)],
    ['Meta Reality Labs',bn(m.reality_labs),bn(m.reality_labs_ebit),pct(m.reality_labs_ebit!/m.reality_labs!)],
  ]}/><p className="tc-note">These are management reporting units, not pure advertising profit or separately traded companies. Google Services also includes subscriptions, platforms and devices.</p>
  <h4 className="tc-spaced">Subscriptions & other exposures</h4><Table label="Subscription and other revenue exposures" headers={['Reported category','Revenue, $B','Limitation']} rows={[
    ['Google subscriptions, platforms & devices',bn(g.subscriptions_platforms_devices),'Combined revenue; no component EBIT'],
    ['Amazon subscriptions',bn(d.businesses.AMZN.subscriptions),'No standalone EBIT'],
    ['Microsoft 365 cloud',bn(d.businesses.MSFT.m365),'Different enterprise/consumer mix'],
    ['Other Bets',bn(g.other_bets),'Aggregate revenue and loss; no pooled multiple'],
  ]}/>
  <details><summary>Alphabet segment reconciliation</summary><Table label="Alphabet revenue reconciliation" headers={['Revenue reconciliation','USD billions']} rows={[
    ['Google Services',bn(g.services)],['Google Cloud',bn(g.cloud)],['Other Bets',bn(g.other_bets)],['Hedging gains / losses',bn(g.hedging)],['Consolidated revenue',bn(g.revenue)],
  ]}/><Table label="Alphabet EBIT reconciliation" headers={['Operating income reconciliation','USD billions']} rows={[
    ['Google Services',bn(g.services_ebit)],['Google Cloud',bn(g.cloud_ebit)],['Other Bets',bn(g.other_bets_ebit)],['Alphabet-level activities',bn(g.corporate_ebit)],['Consolidated operating income',bn(g.ebit)],
  ]}/><p className="tc-note">Reconciles exactly in unrounded USD; displayed rounding may affect visible sums.</p></details></>;
}
function ValuationInputs({data:d}: {data: ComparablesPackage}) {
  return <><div className="tc-valuation-grid"><section><h3>Financial evidence</h3><dl>{[['Revenue & operating income','Prepared'],['Business disclosures','Available by issuer'],['Comparable EBITDA','Scope review'],['Debt, leases, investments & NCI','Classification review'],['Market-date shares & prices','Pending']].map(([name,value]) => <div key={name}><dt>{name}</dt><dd>{value}</dd></div>)}</dl></section><section className="tc-exit"><span className="tc-eyebrow">Exit EV / EBIT</span><h3>Not selected</h3><p>Peer evidence informs a future market-supported assumption. No exit multiple or market valuation is inferred from these financials.</p><dl>{['Share price','Market capitalisation','Enterprise value','EV / EBIT'].map(n => <div key={n}><dt>{n}</dt><dd>Pending</dd></div>)}</dl></section></div>
    <h4 className="tc-spaced">Reported balance candidates</h4><p className="tc-note">{d.quarter_end} · USD billions · Raw observations, not an approved EV bridge. Unavailable never means zero.</p><Table label="Reported balance candidates" headers={['Company','Cash','Current investments','Term debt: current','Term debt: noncurrent','Convertible debt: noncurrent']} rows={peerTickers.map(t => [d.peers[t].name,...['cash','short_term_investments','long_term_debt_current','long_term_debt_noncurrent','convertible_debt_noncurrent'].map(k=>bn(d.peers[t].balances[k]))])}/><p className="tc-note">Pinterest convertible debt is retained separately. Investment eligibility, restricted cash, leases, other claims and share classes need review before EV calculations. No prices or market-data rights are supplied by this feature.</p></>;
}

export default function TradingComparables({ticker, load=fetchComparables}: {ticker:string; load?:typeof fetchComparables}) {
  const [loaded,setLoaded]=useState<{ticker:string;data:ComparablesPackage}|null>(null);
  const [error,setError]=useState(false),[attempt,setAttempt]=useState(0),[tab,setTab]=useState<Tab>('financials');
  useEffect(()=>{const abort=new AbortController();setLoaded(null);setError(false);setTab('financials');load(ticker,abort.signal).then(data=>{if(!abort.signal.aborted&&data.target===ticker)setLoaded({ticker,data});}).catch(()=>{if(!abort.signal.aborted)setError(true);});return()=>abort.abort();},[ticker,load,attempt]);
  const d=loaded?.ticker===ticker?loaded.data:null;
  return <section className="tc-container" id="company-trading-comparables" aria-labelledby="tc-heading" data-feature="trading-comparables"><header className="tc-heading"><div><span className="tc-eyebrow">06 / Relative valuation</span><h2 id="tc-heading">Trading comparables</h2></div>{d&&<span>SEC financial snapshot · {d.as_of}<small>Alphabet · 6 proposed peers</small></span>}</header>
    {!d?<p role="status">{error?<>Comparables could not be loaded. The DCF remains available. <button onClick={()=>setAttempt(n=>n+1)}>Retry comparables</button></>:'Loading peer financials…'}</p>:<>
      <DirectComparisons data={d}/>
      <nav className="tc-tabs" aria-label="Trading comparables views">{(['financials','business','valuation'] as const).map(key=><button key={key} aria-pressed={tab===key} onClick={()=>setTab(key)}>{key==='financials'?'Peer financials':key==='business'?'Business comparisons':'Valuation & inputs'}</button>)}</nav>
      <div hidden={tab!=='financials'}><PeerFinancials data={d}/></div><div hidden={tab!=='business'}><BusinessDetails data={d}/></div><div hidden={tab!=='valuation'}><ValuationInputs data={d}/></div>
      <details className="tc-methodology"><summary>Comparables sources, methodology & review status</summary><p>Official SEC Company Facts and retained filing-level XBRL. {d.validation.selected_filing_checks} selected operand checks and {d.validation.business_reconciliations} business reconciliations passed within their documented scope; this is not full historical certification.</p><ul>{d.limitations.map(l=><li key={l}>{l}</li>)}</ul><div className="tc-source-links">{peerTickers.map(t=><a key={t} href={d.peers[t].financials_url} target="_blank" rel="noreferrer">{t} interim filing ↗</a>)}</div><p>Financial cutoff is separate from a market valuation date and the DCF’s analytical anchor. This section neither reads nor changes DCF assumptions or results.</p></details>
    </>}
  </section>;
}
