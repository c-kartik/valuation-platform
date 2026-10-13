"""Reproducible offline tax/SBC observation replay, no economic calculations."""
import json
from valuation_platform.analyst import retained_tax_sbc as observations, nvda_income_inputs as shared

if __name__=='__main__':
    ledger,_=observations.build()
    if ledger!=json.loads((shared.ROOT/'docs/retained-tax-sbc-ledger.json').read_text()):
        raise SystemExit('Retained tax/SBC ledger differs')
    print(json.dumps({k:ledger[k] for k in ('selected_periods','issuer_count','outcomes','observation_counts','summary')},indent=2))
