import {useEffect,useState} from 'react';
import type {MouseEvent} from 'react';
import {request} from '../api';
import type {Catalog} from '../model';
import {EngineNotice} from '../browser-engine/EngineNotice';
import {CompanySearch} from './CompanySearch';
import type {SearchCompany} from './CompanySearch';
import {Workspace} from './Workspace';
import './platformLanding.css';
const names:Record<string,string>={GOOGL:'Alphabet',AAPL:'Apple',META:'Meta'};
export function preparedCompanies(catalog:Catalog):SearchCompany[]{
 const seen=new Set<string>();
 return catalog.entries.filter(e=>{if(!e.company||!e.kind||!e.template||seen.has(e.company))return false;seen.add(e.company);return true;}).map(e=>({kind:e.kind,company:e.company,name:names[e.company]??e.company}));
}
export function companyUrl(ticker:string|null){const url=new URL(window.location.href);if(ticker)url.searchParams.set('company',ticker);else url.searchParams.delete('company');url.hash='';return url.pathname+url.search;}
export function PlatformApp({load=request}:{load?:typeof request}){
 const [catalog,setCatalog]=useState<Catalog|null>(null),[error,setError]=useState(false),[attempt,setAttempt]=useState(0),[ticker,setTicker]=useState(()=>new URLSearchParams(window.location.search).get('company')?.toUpperCase()??'');
 useEffect(()=>{const abort=new AbortController();setError(false);load<Catalog>('/api/v1/catalog',undefined,abort.signal).then(c=>{if(!Array.isArray(c.entries)||!preparedCompanies(c).length)throw Error('No prepared companies');if(!abort.signal.aborted)setCatalog(c);}).catch(()=>{if(!abort.signal.aborted)setError(true);});return()=>abort.abort();},[load,attempt]);
 useEffect(()=>{const back=()=>setTicker(new URLSearchParams(window.location.search).get('company')?.toUpperCase()??'');window.addEventListener('popstate',back);return()=>window.removeEventListener('popstate',back);},[]);
 const companies=catalog?preparedCompanies(catalog):[],selected=companies.find(c=>c.company===ticker);
 function navigate(company:string|null){window.history.pushState(null,'',companyUrl(company));setTicker(company??'');window.scrollTo({top:0});}
 function follow(event:MouseEvent<HTMLAnchorElement>,company:string|null){if(event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;event.preventDefault();navigate(company);}
 useEffect(()=>{document.title=selected?`${selected.name} · Valuation | K. Chaturvedi`:'Valuation | K. Chaturvedi';},[selected?.company]);
 if(selected)return <Workspace load={load} initialCompany={selected.company} onCompanyChange={company=>navigate(company)} homeHref={companyUrl(null)} onHome={()=>navigate(null)}/>;
 return <div className="platform-landing"><EngineNotice><span className="pl-nav-label">Valuation</span></EngineNotice><main className="pl-main"><section className="pl-hero" aria-labelledby="platform-heading"><p className="pl-eyebrow">Equity Valuation Platform</p><h1 id="platform-heading">Financial Analysis &amp;<br/>Equity Valuation</h1><p className="pl-intro">Explore company financials, follow where the cash goes, and build a discounted cash flow valuation with your own assumptions.</p>
 <div className="pl-search-area"><CompanySearch companies={companies} selected="" disabled={!catalog} label="Find a company" placeholder={catalog?`Search ${companies.length} ${companies.length===1?'company':'companies'} by name or ticker`:'Loading companies…'} onSelect={kind=>{const c=companies.find(c=>c.kind===kind);if(c)navigate(c.company);}}/>
 {ticker&&!selected&&catalog&&<p className="pl-status" role="status">{ticker} is not in the prepared company list. Choose a company below.</p>}
 {error&&<p className="pl-status" role="status">The company list could not be loaded. <button type="button" onClick={()=>setAttempt(n=>n+1)}>Retry company list</button></p>}
 </div>
 {catalog&&<section className="pl-suggestions" aria-label="Suggested companies"><p className="pl-eyebrow">Suggested companies</p><div>{companies.slice(0,3).map(c=><a key={c.company} href={companyUrl(c.company)} onClick={e=>follow(e,c.company)}><span className="pl-company-ticker">{c.company}</span><strong>{c.name}</strong><span className="pl-company-action">Explore company <span aria-hidden="true">↗</span></span></a>)}</div></section>}
 </section><section className="pl-features" aria-label="What you can explore"><div><span className="pl-step">01 / Financials</span><h2>Filings Insight</h2><p>Quarterly trends, revenue mix and the bridge from earnings to cash.</p></div><div><span className="pl-step">02 / Capital allocation</span><h2>Cash Flow Analysis</h2><p>Explore investment, shareholder returns and the assets behind the business.</p></div><div><span className="pl-step">03 / Valuation</span><h2>Test your assumptions</h2><p>Editable DCF models, scenarios, sensitivity analysis and Excel downloads.</p></div></section><footer className="pl-footer"><p>Financials sourced from SEC filings. Valuations reflect model assumptions.</p><a href="https://github.com/c-kartik/valuation-platform">Source &amp; methodology ↗</a></footer></main></div>;
}
