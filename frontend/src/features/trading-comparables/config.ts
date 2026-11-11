/** The single disconnect switch. False removes mounting, lazy loading and links. */
export const tradingComparables = {enabled: true, targets: ['GOOGL'] as readonly string[]};
export function comparablesAvailable(ticker: string, enabled = tradingComparables.enabled) {
  return enabled && tradingComparables.targets.includes(ticker);
}
