export function percentageDiagnostic(detail: string): string {
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
