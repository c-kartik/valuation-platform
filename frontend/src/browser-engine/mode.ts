declare const __VALUATION_BROWSER_ONLY__: boolean;
export function browserEnabled(){
 return (typeof __VALUATION_BROWSER_ONLY__!=='undefined'&&__VALUATION_BROWSER_ONLY__)||
  (typeof window!=='undefined'&&new URLSearchParams(window.location.search).get('engine')==='browser');
}
