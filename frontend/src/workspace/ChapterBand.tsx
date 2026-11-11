const chapters={
 financials:{id:'company-financials',title:'Financials',eyebrow:'01–02 / Financial statements',links:[['Historical trends','#company-history'],['Revenue mix','#company-revenue-mix']]},
 cash:{id:'company-cash-analysis',title:'Cash Flow Analysis',eyebrow:'03–04 / Cash generation & allocation',links:[['Earnings to cash','#company-cash-bridge'],['Capital allocation','#company-cash-allocation']]},
 valuation:{id:'valuation-chapter',title:'Valuation',eyebrow:'05 / Forward valuation',links:[['DCF','#valuation-main'],['Model & assumptions','#model-workspace']]},
} as const;
/** Option 2 presentation only: retains the existing feature targets and controls. */
export function ChapterBand({chapter,comparables=false}:{chapter:keyof typeof chapters;comparables?:boolean}){
 const group=chapters[chapter];
 const includeComparables=chapter==='valuation'&&comparables;
 return <header id={group.id} className="oc-chapter-band" aria-labelledby={`${group.id}-heading`}><div><span className="oc-chapter-eyebrow">{includeComparables?'05–06 / Valuation methods':group.eyebrow}</span><h2 id={`${group.id}-heading`}>{group.title}</h2></div><nav aria-label={`${group.title} sections`}>{group.links.map(([label,href])=><a key={href} href={href}>{label}</a>)}{includeComparables&&<a href="#company-trading-comparables">Trading comparables</a>}</nav></header>;
}
