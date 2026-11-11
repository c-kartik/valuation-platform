import {Component, lazy, Suspense, type ReactNode} from 'react';
import {comparablesAvailable} from './config';
export {comparablesAvailable} from './config';
const Container = lazy(() => import('./TradingComparables'));

class IsolatedBoundary extends Component<{children: ReactNode}, {failed: boolean}> {
  state = {failed: false};
  static getDerivedStateFromError() {return {failed: true};}
  render() {
    return this.state.failed ? <section id="company-trading-comparables" aria-label="Trading comparables"><h2>Trading comparables</h2><p role="status">This section could not be displayed. The DCF remains available.</p></section> : this.props.children;
  }
}
/** No valuation state/actions cross this boundary; disabled/unsupported mounts nothing. */
export function TradingComparablesFeature({ticker, enabled}: {ticker: string; enabled?: boolean}) {
  if (!comparablesAvailable(ticker, enabled)) return null;
  return <IsolatedBoundary key={ticker}><Suspense fallback={<section id="company-trading-comparables" aria-label="Trading comparables"><p role="status">Loading trading comparables…</p></section>}><Container ticker={ticker}/></Suspense></IsolatedBoundary>;
}
