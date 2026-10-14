"""Read-only retained coverage and independent fixture replay; no acceptance."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from valuation_platform.analyst import prepared_assembly as a, preparation_validation as v

def main():
    summary,histories=a.build()
    if summary!=json.loads((a.ROOT/a.REPORT).read_text()):
        raise SystemExit('Original assembly summary changed')
    fixtures=json.loads((a.ROOT/v.FIXTURES).read_text())['fixtures']
    spot=v.spot_checks(histories,fixtures,v.statement_artifacts())
    coverage=v.coverage(histories,spot)
    for filename,result in (('preparation-independent-results.json',spot),('preparation-coverage-results.json',coverage)):
        if result!=json.loads((a.ROOT/'docs'/filename).read_text()):
            raise SystemExit('Committed report differs: '+filename)
    print(a.canonical(dict(spot_checks=spot['counts'],coverage=coverage['totals'],
                           independent_artifact_backlog=len(spot['artifact_backlog']),
                           financial_sufficiency='NOT_ASSESSED',phase_closure=False)))

if __name__=='__main__':main()
