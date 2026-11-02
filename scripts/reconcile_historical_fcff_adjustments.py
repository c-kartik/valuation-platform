"""Source-bound tax, liability-note, noncash-cost and investment schedules.

Reads retained official filings for the three-issuer FY2021-FY2025 scope. New
comparatives are explicit evidence overlays; source packages/approvals are read-only.
"""
import argparse
from copy import copy
import csv
from datetime import date
from decimal import Context, Decimal, localcontext
from fractions import Fraction
import hashlib
from io import StringIO
import json
from pathlib import Path
import re

from calculate_historical_fcff_from_filings import RetainedFiling, KINDS
from test_operating_fcff_from_filings import statement_terms, classify, point_from
from prepare_trillion_review_batch import primary_fact
from valuation_platform.analyst import cash_flow_inputs as cash, statement_delivery as statements
from valuation_platform.analyst.nwc import Period
from valuation_platform.review.operating_fcff import amount, serialized
from valuation_platform.review.fcff_adjustments import tax_schedule, partition, named_investment
from valuation_platform.valuation.consumer import ANCHORS, load_revenue_anchor

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = "docs/company-data-preparation/historical-fcff-adjustment-schedules.json"
REPORT_PATH = "docs/historical-fcff-adjustment-schedules.md"
TAX_CSV = "docs/company-data-preparation/historical-fcff-tax-schedules.csv"
WC_CSV = "docs/company-data-preparation/historical-fcff-liability-components.csv"
INVESTMENT_CSV = "docs/company-data-preparation/historical-fcff-investment-schedules.csv"
CURRENT_APPLE = ("CurrentFederalTaxExpenseBenefit", "CurrentStateAndLocalTaxExpenseBenefit", "CurrentForeignTaxExpenseBenefit")
DEFERRED_APPLE = ("DeferredFederalIncomeTaxExpenseBenefit", "DeferredStateAndLocalIncomeTaxExpenseBenefit", "DeferredForeignIncomeTaxExpenseBenefit")


def selector(filing, identity):
    view = copy(filing)
    view.period = Period(identity["cik"], filing.period.accession, date.fromisoformat(identity["annual_start"]), date.fromisoformat(identity["annual_end"]))
    view.facts = {}
    return view


def exact(filing, identity, concept, *, namespace="us-gaap", instant=False, optional=False):
    """Absence is optional only after checking the actual exact-period inventory."""
    namespace = filing.namespaces.get(namespace, namespace)
    target = (identity["cik"], None if instant else date.fromisoformat(identity["annual_start"]), date.fromisoformat(identity["annual_end"]))
    matching = [node for node in filing.root if node.tag == "{"+namespace+"}"+concept
                and node.get("contextRef") and cash._context(filing.contexts[node.get("contextRef")]) == target]
    if not matching:
        if optional: return None
        raise ValueError("Required disclosed observation missing: "+concept)
    view = selector(filing, identity)
    view.fact("selected", concept, "Exact source tax/asset observation for adjustment schedule", namespace=namespace, instant=instant)
    return dict(view.facts["selected"], source_identity=filing.source_identity,
                target_identity=identity, sources=filing.references)


def note_table(filing, identity, ticker):
    """Select the identifiable liability-note table by its disclosed row family."""
    if not hasattr(filing, "tables"):
        filing.tables = statements.parse({"body": filing.primary.artifact.body}, improved=True)
    parent = "OtherLiabilitiesCurrent" if ticker == "AAPL" else "AccruedLiabilitiesCurrent"
    anchor = {"AAPL": "OtherAccruedLiabilitiesCurrent", "GOOGL": "AccruedPurchasesOfPropertyAndEquipmentCurrent", "META": "EmployeeRelatedLiabilitiesCurrent"}[ticker]
    target = (identity["cik"], None, date.fromisoformat(identity["annual_end"]))
    candidates = []
    for ti, table in enumerate(filing.tables):
        selected = []
        for ri, row in enumerate(table):
            for ci, cell in enumerate(row):
                for item in cell["facts"]:
                    a = item["attrs"]
                    if cash._context(filing.contexts[a["contextref"]]) != target: continue
                    prefix, concept = a["name"].split(":")
                    if concept in ("OtherLiabilitiesNoncurrent", "OtherAccruedLiabilitiesNoncurrent"): continue
                    selected.append((ri, ci, item, concept, row[0]["text"]))
        concepts = {s[3] for s in selected}
        if parent not in concepts or anchor not in concepts: continue
        points = []
        for ri, ci, item, concept, caption in selected:
            point = primary_fact({"filing": selector(filing, identity)}, item, ti, ri, ci, caption, instant=True)
            points.append(dict(point, evidence_depth="exact_primary_inline_and_instance_verified",
                               source_identity=filing.source_identity, target_identity=identity, sources=filing.references))
        parents = [p for p in points if p["concept"] == parent]
        if len(parents) != 1: raise ValueError("Unique note parent required")
        children = [p for p in points if p["concept"] != parent]
        control = partition(parents[0]["value"], [p["value"] for p in children])
        candidates.append({"parent": parents[0], "children": children, "control": control})
    if len(candidates) > 1: raise ValueError("Competing liability-note tables require explicit review")
    return candidates[0] if candidates else None


def component_role(concept):
    if concept in ("AccruedIncomeTaxesCurrent",): return "INCOME_TAX_SCHEDULE"
    if concept == "TaxesPayableCurrent": return "MIXED_TAXES_NOT_ALL_INCOME_TAX"
    if concept in ("AccruedPurchasesOfPropertyAndEquipmentCurrent", "PropertyAndEquipmentAccruedLiabilitiesCurrent"):
        return "CAPITAL_CREDITOR_INVESTMENT_SCHEDULE"
    if concept in ("AccruedCustomerLiabilitiesCurrent", "EmployeeRelatedLiabilitiesCurrent", "AccruedDistributionAndMarketingCurrent"):
        return "NAMED_OPERATING_BALANCE"
    if concept == "OperatingLeaseLiabilityCurrent": return "OPERATING_LEASE_SERVICE_POLICY_BALANCE"
    if concept in ("LegalRelatedAccruedLiabilitiesCurrent", "LossContingencyAccrualCarryingValueCurrent"):
        return "LEGAL_REGULATORY_SEPARATE_REVIEW_NOT_AUTOMATIC_EXCLUSION"
    if concept == "CommissionsPayableToBrokerDealersAndClearingOrganizations": return "NONOPERATING_INVESTMENT_SETTLEMENT"
    return "MIXED_UNALLOCATED_BALANCE"


def quarter_charge(filing, identity):
    """The disclosed Q3 2025 charge stays a Q3 fact within the annual record."""
    target = dict(identity, annual_start="2025-07-01", annual_end="2025-09-30")
    return exact(filing, target, "IncomeTaxExpenseBenefitDiscreteChargeRelatedToNewLegislation", namespace="meta")


def build(root=ROOT):
    manifests, companies = {}, []
    for kind in KINDS:
        load_revenue_anchor(kind, root)
        spec = ANCHORS[kind]; ticker = spec["ticker"]; prefix = ticker.lower()
        payload = (root/spec["package"]).read_bytes(); package = json.loads(payload)
        rows = package["periods"] if prefix == "meta" else package[prefix+"_history_review"]["periods"]
        if [r["identity"]["annual_end"][:4] for r in rows] != [str(y) for y in range(2021,2026)]:
            raise ValueError("Five selected FY2021-FY2025 annuals required")
        filings = [RetainedFiling(root, row, manifests) for row in rows]
        periods = []
        for index, (row, filing) in enumerate(zip(rows, filings, strict=True)):
            identity, year = row["identity"], 2021+index
            terms, cfo = statement_terms(row, filing)
            for term in terms: term["role"] = classify(term)
            provision = exact(filing, identity, "IncomeTaxExpenseBenefit")
            if ticker == "AAPL":
                current = [exact(filing, identity, c) for c in CURRENT_APPLE]
                deferred = [exact(filing, identity, c) for c in DEFERRED_APPLE]
            else:
                current = [exact(filing, identity, "CurrentIncomeTaxExpenseBenefit")]
                deferred = [exact(filing, identity, "TotalDeferredIncomeTaxExpenseBenefit",
                                  namespace="fb" if year == 2021 else "meta")] if ticker == "META" and year < 2024 else [exact(filing, identity, "DeferredIncomeTaxExpenseBenefit")]
            paid = exact(filing, identity, "IncomeTaxesPaidNet")
            original_paid, cash_selection = paid, None
            if ticker == "GOOGL" and year == 2024:
                precise = exact(filings[4], identity, "IncomeTaxesPaidNet")
                if amount(precise["value"]) == amount(paid["value"]) or precise["precision"] != "-6" or paid["precision"] != "-8":
                    raise ValueError("Expected explicitly reviewed 2024 cash-tax precision comparison changed")
                if abs(amount(precise["value"])-amount(paid["value"])) > 50000000:
                    raise ValueError("Later comparative falls outside original rounded disclosure")
                cash_selection = {"original": original_paid, "selected": precise,
                    "reason": "FY2025 Note14 explicitly reports the same FY2024 net cash-tax population at million precision; preserve original 27.4B separately"}
                paid = precise
            cf_deferred = [t for t in terms if t["source"]["concept"] in ("DeferredIncomeTaxesAndTaxCredits", "DeferredIncomeTaxExpenseBenefit")]
            if len(cf_deferred) > 1: raise ValueError("Separate CFO deferred-tax population is ambiguous")
            taxes = tax_schedule(provision["value"], [p["value"] for p in current], [p["value"] for p in deferred], paid["value"],
                                 cf_deferred[0]["cash_contribution_usd"] if cf_deferred else None)
            taxes["inputs"] = {"total_provision": provision, "current_components": current, "deferred_components": deferred,
                               "cash_paid": paid, "separate_cfo_deferred": cf_deferred[0] if cf_deferred else None}
            taxes["cash_tax_selection"] = cash_selection
            charge = None
            if ticker == "AAPL" and year >= 2024:
                charge = exact(filing, identity, "EffectiveIncomeTaxRateReconciliationImpactOfTheStateAidDecisionAmount", namespace="aapl")
            if ticker == "META" and year == 2025: charge = quarter_charge(filing, identity)
            pretax = point_from(filing, identity, row["facts"]["pretax"])
            taxes["discrete_item_review"] = None if charge is None else {
                "reported_item": charge,
                "tax_provision_excluding_only_this_item": serialized(amount(provision["value"])-amount(charge["value"])),
                "accounting_etr_excluding_only_this_item": serialized((amount(provision["value"])-amount(charge["value"]))/amount(pretax["value"]))["amount_usd"],
                "pretax_source": pretax, "historical_cash_flow_adjustment_applied": False,
                "future_operating_tax_rate_approved": False,
                "notice": "Isolated accounting normalization illustration; not a cash refund, operating-tax allocation or recommended forecast tax rate"}
            if ticker == "META" and year == 2025:
                taxes["discrete_item_review"]["identified_non_cash_valuation_allowance_charge"] = exact(filing, identity,
                    "DeferredTaxAssetsValuationAllowanceDiscreteChargeRelatedToNewLegislation", namespace="meta", instant=True)
            original_note = note_table(filing, identity, ticker)
            chosen_note, comparative = original_note, None
            # Explicit, researched source overlays; never generic silent precedence.
            supplemental_index = 2 if ticker in ("AAPL","GOOGL") and year == 2022 else (4 if ticker == "AAPL" and year == 2024 else None)
            if supplemental_index is not None:
                richer = note_table(filings[supplemental_index], identity, ticker)
                if richer is None: raise ValueError("Reviewed comparative note disclosure missing")
                original_parent = (original_note["parent"] if original_note else exact(filing, identity,
                    "OtherLiabilitiesCurrent" if ticker == "AAPL" else "AccruedLiabilitiesCurrent", instant=True))
                if amount(original_parent["value"]) != amount(richer["parent"]["value"]):
                    raise ValueError("Comparative liability parent differs; no silent restatement")
                chosen_note = richer
                comparative = {"original_note": original_note, "original_parent": original_parent,
                    "reason": "Later explicit comparative identifies income taxes within the unchanged parent" if year == 2022 else "FY2025 Note6 separately identifies FY2024 distribution/marketing within the unchanged parent"}
            if chosen_note:
                for child in chosen_note["children"]: child["analyst_classification"] = component_role(child["concept"])
            wc = {"liability_note_partition": chosen_note, "comparative_selection": comparative,
                  "status": "DISCLOSED_CLOSING_PARENT_PARTITION_VERIFIED" if chosen_note else "CLOSING_PARENT_NOT_SEPARATELY_PARTITIONED_IN_REVIEWED_NOTES",
                  "cash_movement_rows": [t for t in terms if t["role"] in ("named_trade_movement", "mixed_asset_liability_movement", "separate_income_tax_movement")],
                  "verified_operating_cash_working_capital": None,
                  "policy": "Classify disclosed balances; keep their source scope. Tax/capital/financing balances are separate schedules. A book balance or change never replaces a source cash movement; mixed rows remain unallocated."}
            ppe = exact(filing, identity, "PaymentsToAcquirePropertyPlantAndEquipment")
            finance = exact(filing, identity, "RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability", optional=True)
            finance_selection = None
            if finance is None and ticker == "GOOGL" and year in (2022,2023):
                finance = exact(filings[3], identity, "RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability")
                finance_selection = "Explicit FY2024 Note4 comparative, preserving FY2024 source accession and original target year"
            inv = named_investment(ppe["value"], finance["value"] if finance else None)
            inv["inputs"] = {"cash_ppe": ppe, "finance_asset_additions": finance,
                "combined_operating_and_finance_additions": exact(filing, identity, "RightofUseAssetsObtainedinExchangeforOperatingandFinanceLeaseLiabilities", namespace="aapl", optional=True) if ticker == "AAPL" else None,
                "finance_principal_payments_support_only": exact(filing, identity, "FinanceLeasePrincipalPayments", optional=True),
                "capital_unpaid_supplement_support_only": exact(filing, identity, "CapitalExpendituresIncurredButNotYetPaid", optional=True)}
            inv["finance_comparative_selection"] = finance_selection
            inv["policy"] = "Operating leases remain service costs; finance leases are asset financing. Named cash PP&E plus separately disclosed finance additions counts investment at inception, not principal again. Combined ROU additions are not allocated by asset-stock mix. Capital-payable support is not automatically added to cash investment."
            da_rows = [t for t in terms if t["role"] in ("reported_da_or_combined_impairment", "separate_operating_noncash_charge")]
            sbc = [t for t in terms if t["source"]["concept"] == "ShareBasedCompensation"]
            if len(sbc) != 1: raise ValueError("Actual reported SBC cash-flow adjustment required")
            costs = {"reported_noncash_rows": da_rows, "sbc_cfo_addback": sbc[0],
                "reported_depreciation_support": exact(filing, identity, "Depreciation", optional=True),
                "note_intangible_amortization_support": exact(filing, identity, "AmortizationOfIntangibleAssets", optional=True),
                "finance_amortization_support_not_extra_addback": exact(filing, identity, "FinanceLeaseRightOfUseAssetAmortization", optional=True),
                "policy": "Keep SBC expensed, reverse only its actual CFO add-back in a CFO bridge. Add identified operating noncash charges once. No note-minus-CFO residual becomes amortization; no second lease amortization. If EBIT was already normalized for an impairment, do not add it again.",
                "complete_income_recognized_da": None}
            periods.append({"identity": identity, "fiscal_year_label": "FY"+str(year), "taxes": taxes,
                "working_capital": wc, "noncash_costs_and_sbc": costs, "investment": inv,
                "reported_cfo_control": cfo, "full_cfo_term_count": len(terms),
                "actual_cash_fcf": serialized(amount(cfo["value"])-amount(ppe["value"])),
                "verified_operating_fcff": None,
                "unresolved_allocations": ["Consolidated cash taxes to unlevered core operations versus financing/nonoperating income",
                    "Tax, capital/lease, legal and other effects inside disclosed cash-movement/Other rows",
                    "Complete income-recognized noncash cost and investment scope consistent with the forecast"]})
        companies.append({"ticker": ticker, "package": spec["package"], "package_sha256": hashlib.sha256(payload).hexdigest(), "periods": periods})
    # Adjacent liability book changes are diagnostics, never cash allocations.
    for company in companies:
        previous = None
        for p in company["periods"]:
            note = p["working_capital"]["liability_note_partition"]
            p["working_capital"]["adjacent_book_changes_support_only"] = []
            if note and previous:
                by_concept = {x["concept"]: x for x in previous["children"]}
                for child in note["children"]:
                    old = by_concept.get(child["concept"])
                    # A changed caption/scope is not an automatically comparable series.
                    if old and old["primary_table"]["caption"] == child["primary_table"]["caption"]:
                        p["working_capital"]["adjacent_book_changes_support_only"].append({"concept": child["concept"],
                            "opening": old, "closing": child, "book_change": serialized(amount(child["value"])-amount(old["value"])),
                            "is_cash_movement": False, "cash_adjustment_applied": False})
            previous = note
    return {"schema_version": "historical-fcff-adjustment-schedules-v1", "as_of": "2026-11-02",
        "scope": "GOOGL/AAPL/META FY2021-FY2025", "estimated_inputs_permitted": False,
        "tax_bridges_verified": sum(len(c["periods"]) for c in companies),
        "closing_liability_partitions_verified": sum(p["working_capital"]["liability_note_partition"] is not None for c in companies for p in c["periods"]),
        "named_cash_plus_finance_investment_subtotals": sum(p["investment"]["cash_ppe_plus_disclosed_finance_additions"] is not None for c in companies for p in c["periods"]),
        "complete_operating_fcff_publication_authorized": False, "live_integration": False,
        "companies": companies}


def primary_url(point):
    return next(s['url'] for s in point['sources'] if s['url'].endswith('.htm'))


def csv_outputs(data):
    def output(fields, rows):
        stream = StringIO(newline=''); writer = csv.DictWriter(stream, fields, lineterminator='\n')
        writer.writeheader(); writer.writerows(rows); return stream.getvalue()
    tax_rows, wc_rows, investment_rows = [], [], []
    for company in data['companies']:
        for p in company['periods']:
            ticker, year = company['ticker'], p['fiscal_year_label']; t = p['taxes']; inv = p['investment']
            tax_rows.append(dict(ticker=ticker, fiscal_year=year,
                provision_usd=t['total_provision']['amount_usd'], current_usd=t['current_provision']['amount_usd'],
                deferred_usd=t['deferred_provision']['amount_usd'], cash_paid_usd=t['cash_paid']['amount_usd'],
                current_less_cash_usd=t['current_provision_minus_cash_paid']['amount_usd'],
                cfo_deferred_less_note_deferred_usd=t['cfo_deferred_minus_note_deferred']['amount_usd'] if t['cfo_deferred_minus_note_deferred'] else '',
                cash_source=primary_url(t['inputs']['cash_paid']), cash_source_fiscal_end=t['inputs']['cash_paid']['source_identity']['annual_end'],
                cash_source_precision=t['inputs']['cash_paid']['precision'], status=t['status']))
            note = p['working_capital']['liability_note_partition']
            if note:
                for point in [dict(note['parent'], analyst_classification='PARENT_CONTROL')]+note['children']:
                    wc_rows.append(dict(ticker=ticker, fiscal_year=year, caption=point['primary_table']['caption'],
                        concept=point['concept'], amount_usd=point['value'], classification=point['analyst_classification'],
                        source=primary_url(point), source_fiscal_end=point['source_identity']['annual_end'],
                        table=point['primary_table']['table'], row=point['primary_table']['row'], column=point['primary_table']['column'],
                        cash_adjustment_applied=False))
            finance = inv['inputs']['finance_asset_additions']; subtotal = inv['cash_ppe_plus_disclosed_finance_additions']
            investment_rows.append(dict(ticker=ticker, fiscal_year=year, cash_ppe_usd=inv['cash_ppe']['amount_usd'],
                finance_additions_usd=finance['value'] if finance else '', cash_plus_finance_usd=subtotal['amount_usd'] if subtotal else '',
                finance_source=primary_url(finance) if finance else '', finance_source_fiscal_end=finance['source_identity']['annual_end'] if finance else '',
                finance_principal_deducted=False, complete_operating_investment_verified=False))
    return {TAX_CSV: output(tuple(tax_rows[0]), tax_rows), WC_CSV: output(tuple(wc_rows[0]), wc_rows),
            INVESTMENT_CSV: output(tuple(investment_rows[0]), investment_rows)}


def render(data):
    def million(value):
        number = amount(value)
        with localcontext(Context(prec=50)):
            return f'{Decimal(number.numerator)/Decimal(number.denominator)/1000000:,.0f}'
    def derived_million(point): return million(point['amount_usd'])
    lines = ['# Historical FCFF — company adjustment schedules', '', 'November 2, 2026 · Alphabet, Apple and Meta · FY2021–FY2025', '',
        '**Completed: 15 tax-provision reconciliations, 14 disclosed liability-parent partitions, and 9 named cash-plus-financed-investment subtotals.**',
        'Every amount comes from retained SEC filings. No missing interest, lease split or cash-movement allocation is estimated.', '',
        'These schedules resolve specific component questions. They retain the remaining distinction between consolidated cash flow and unlevered operating FCFF.',
        'Historical cash amounts, isolated accounting-normalization illustrations and unresolved allocations are separate. The live chart/DCF is unchanged.', '',
        '## Tax expense versus cash taxes — USD millions', '',
        'Current tax provision plus deferred tax provision equals the reported total in all 15 periods. Cash taxes are a separately reported flow.',
        'The current-provision/cash difference is a reconciliation difference, not a newly inferred tax-payable movement or an adjustment to subtract from WC.', '',
        '| Company | FY | Current provision | Deferred provision | Total provision | Cash paid, net | Current less cash | CFO deferred minus note deferred |',
        '|---|---|---:|---:|---:|---:|---:|---:|']
    for c in data['companies']:
        for p in c['periods']:
            t = p['taxes']; values = [t[k] for k in ('current_provision','deferred_provision','total_provision','cash_paid','current_provision_minus_cash_paid')]
            gap = t['cfo_deferred_minus_note_deferred']
            lines.append('| '+c['ticker']+' | '+p['fiscal_year_label']+' | '+' | '.join(derived_million(v) for v in values)+' | '+(derived_million(gap) if gap else 'Not separately displayed')+' |')
    lines += ['', '### What this resolves', '',
        '- **Meta FY2025:** total provision25,474 = current6,719 + deferred18,755; net cash taxes7,578. The earlier6.63B method test must not be read as a verified cash-FCFF figure. CFO separately reverses18,738 of deferred taxes,17 less than the provision-note component. That17 is not a rounding plug or an extra WC deduction.',
        '- **Apple FY2025:** provision20,719 = current22,058 − deferred benefit1,339; net cash taxes43,369. Current expense versus cash payments differs by21,311. This establishes tax timing/noncash distinctions without assigning that amount to any particular Other cash-flow row.',
        '- **Apple FY2023–25:** deferred tax provision is recoverable from the three jurisdictional components even though the CFO statement no longer displays it separately. Those note components cannot be inserted into mixed CFO Other as if they were the same population.',
        '- **Alphabet FY2024:** original net cash taxes27,400 were reported to100m precision. FY2025 Note14 explicitly supplies27,353 for the same FY2024 population at1m precision. This schedule selects that later comparative and retains both source accessions/precisions; prior source packages are unchanged.', '',
        '### Discrete tax items — accounting illustrations only', '',
        '| Company / FY | Identified reported item | Reported provision excluding only this item | Accounting ETR excluding only this item |',
        '|---|---:|---:|---:|']
    for c in data['companies']:
        for p in c['periods']:
            item = p['taxes']['discrete_item_review']
            if item:
                with localcontext(Context(prec=50)):
                    rate = f"{Decimal(item['accounting_etr_excluding_only_this_item'])*100:.2f}"
                lines.append(f"| {c['ticker']} / {p['fiscal_year_label']} | {million(item['reported_item']['value'])} | {derived_million(item['tax_provision_excluding_only_this_item'])} | {rate}% |")
    lines += ['', 'Apple FY2024 uses the exact10,246 State Aid tax-reconciliation line, not the rounded10.2B prose amount. FY2025 removes the separately reported486 benefit only in this illustration.',
        'Meta reports its15,930 discrete OBBBA charge as a Q3 July–September2025 fact inside the annual filing; the original quarter dates and−7 precision are preserved. Its separately tagged14,030 valuation-allowance charge is identified as noncash; it is not the full closing valuation-allowance balance.',
        '**None of these illustrations is a cash refund, a change to historical cash taxes, an approved future operating-tax rate, or a license to add the same tax effect twice.** Ongoing tax-law effects still matter for future tax assumptions.', '',
        '## Working-capital classification', '',
        'Each closing liability parent below equals the sum of its independently disclosed note rows. Explicit tax, capital, investment, operating and mixed categories are separated.',
        'This is a balance classification. It does not turn book changes into cash movements, and it does not establish that the full CFO Other/accrued row is operating-only.', '',
        '| Company | FY | Parent | Named operating/service balances | Tax balances* | Capital creditors | Legal/regulatory review | Investment settlement | Mixed Other |',
        '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for c in data['companies']:
        for p in c['periods']:
            note = p['working_capital']['liability_note_partition']
            if not note:
                lines.append(f"| {c['ticker']} | {p['fiscal_year_label']} | No detailed partition selected | — | — | — | — | — | — |")
                continue
            categories = [['NAMED_OPERATING_BALANCE','OPERATING_LEASE_SERVICE_POLICY_BALANCE'],['INCOME_TAX_SCHEDULE','MIXED_TAXES_NOT_ALL_INCOME_TAX'],
                          ['CAPITAL_CREDITOR_INVESTMENT_SCHEDULE'],['LEGAL_REGULATORY_SEPARATE_REVIEW_NOT_AUTOMATIC_EXCLUSION'],
                          ['NONOPERATING_INVESTMENT_SETTLEMENT'],['MIXED_UNALLOCATED_BALANCE']]
            totals = [sum((amount(x['value']) for x in note['children'] if x['analyst_classification'] in group),Fraction()) for group in categories]
            displays = [million(str(x)) if any(child['analyst_classification'] in group for child in note['children']) else '—' for x, group in zip(totals, categories, strict=True)]
            lines.append('| '+c['ticker']+' | '+p['fiscal_year_label']+' | '+million(note['parent']['value'])+' | '+' | '.join(displays)+' |')
    lines += ['', '*Meta\'s “Accrued taxes” includes a broader tax population; it is not relabelled as entirely income tax. Alphabet FY2021 current tax808 is separately disclosed outside this note parent, so it is not subtracted from the parent a second time.', '',
        '### Newly resolved comparative disclosures', '',
        '- **Apple FY2022:** FY2023 Note5 separates6,552 income taxes and54,293 Other within the unchanged60,845 current-liability parent. The original FY2022 total is preserved.',
        '- **Apple FY2024:** FY2025 Note6 separates26,601 taxes +7,679 distribution/marketing +44,024 remaining Other =78,304. The original FY2024 note instead grouped51,703 as Other. The new detail is an explicit comparative overlay.',
        '- **Alphabet FY2022:** FY2023 Note7 identifies1,632 income taxes inside the unchanged37,866 parent; the prior residual Other is not assumed entirely operational.', '',
        '### Cash movements still requiring allocation', '',
        'Apple FY2025 current income-tax payable falls from26,601 to13,016, a book change of−13,585. Its cash-flow statement reports−11,076 for the broader current/noncurrent Other liabilities row.',
        '**Subtracting those two figures would not prove an operating cash residual.** The scopes differ, and tax expense, cash settlement, FX, acquisition and classification effects require their own bridge.',
        'The earlier20,273 mixed-row exposure is likewise not a tax amount or an error amount. The machine schedule retains the actual signed cash rows and comparable book diagnostics separately.',
        'Apple FY2021 lacks a selected detailed current-liability partition. All periods still contain disclosed mixed balances/cash rows; no unknown component is assigned zero or an immateriality threshold.', '',
        '## D&A, impairment and stock compensation', '',
        '| Company | FY | Disclosed CFO D&A / combined noncash cost | Separate operating noncash charges/reversals | SBC CFO add-back kept out of operating build |',
        '|---|---|---:|---:|---:|']
    for c in data['companies']:
        for p in c['periods']:
            costs = p['noncash_costs_and_sbc']; rows = costs['reported_noncash_rows']
            totals = [sum((amount(t['cash_contribution_usd']) for t in rows if t['role']==role),Fraction()) for role in ('reported_da_or_combined_impairment','separate_operating_noncash_charge')]
            displays=[million(str(value)) if any(t['role']==role for t in rows) else '—' for value, role in zip(totals, ('reported_da_or_combined_impairment','separate_operating_noncash_charge'), strict=True)]
            lines.append('| '+c['ticker']+' | '+p['fiscal_year_label']+' | '+' | '.join(displays)+' | '+million(costs['sbc_cfo_addback']['cash_contribution_usd'])+' |')
    lines += ['', 'Alphabet FY2021/22 captions combine depreciation/amortization with impairment; they are not renamed pure D&A. Meta\'s facilities/data-center reversals remain separate from D&A.',
        'Reported note depreciation, intangible amortization and finance amortization are retained separately in the JSON. Differences caused by scope, inventory timing or source rounding are not invented amortization.',
        'Keep SBC as an economic expense. In a CFO bridge, reverse its actual reported add-back once. In an EBIT bridge it is already expensed, so there is no second expense deduction. This choice does not separately value existing awards or approve an equity/share calculation.',
        'An impairment removed when normalizing EBIT must not also be added back as an expense still present in that EBIT. Operating lease service costs stay expensed; finance amortization is not added on top of an already inclusive D&A caption without evidence.', '',
        '## Cash and financed investment — USD millions', '',
        '| Company | FY | Cash PP&E | Separately disclosed finance-asset additions | Named subtotal |',
        '|---|---|---:|---:|---:|']
    for c in data['companies']:
        for p in c['periods']:
            i=p['investment']; finance=i['inputs']['finance_asset_additions']; subtotal=i['cash_ppe_plus_disclosed_finance_additions']
            lines.append('| '+c['ticker']+' | '+p['fiscal_year_label']+' | '+derived_million(i['cash_ppe'])+' | '+(million(finance['value']) if finance else 'Not separately selected')+' | '+(derived_million(subtotal) if subtotal else 'Unresolved')+' |')
    lines += ['', 'Alphabet FY2022/23 finance additions577/564 come from explicit FY2024 Note4 comparatives. Source and target years remain distinct. FY2021 remains unselected.',
        'Apple discloses combined operating/finance ROU additions; none of the five combined figures is allocated using closing asset stocks. Separate finance additions therefore remain unresolved.',
        'The9 subtotals are named cash-PP&E-plus-finance-addition populations, not complete economic reinvestment. Finance principal payments and current capital payables are not deducted again. Acquisition/intangible and other financed investment allocations remain separate.',
        'Meta\'s accrued PP&E liability-note component and broader supplemental unpaid-capital amount have different scopes. Alphabet\'s annual noncash capital disclosure is not substituted for a closing creditor balance. No unexplained difference becomes another Capex term.', '',
        '## Source ledger and conclusion', '',
        'All15 current/deferred provision controls and all14 disclosed parent/child controls reconcile exactly. The full CFO source controls remain intact. Later comparative selections are additive evidence overlays, not edits of original sources, normalization or approval records.',
        'The schedules finish the source-supported classifications available within this scope. Remaining operating allocations are explicitly listed per year; complete operating cash tax, cash WC, model-aligned investment and final FCFF remain null where unsupported.',
        'Historical CFO less cash PP&E remains a separately named actual cash-FCF calculation. Isolated tax-normalization illustrations do not replace it. No adjusted FCFF is published to the chart or used to change EV.', '',
        '- [All exact facts, receipts, primary-cell coordinates, calculations and unresolved allocations](company-data-preparation/historical-fcff-adjustment-schedules.json).',
        '- [Tax schedules CSV](company-data-preparation/historical-fcff-tax-schedules.csv).',
        '- [Liability-note components CSV](company-data-preparation/historical-fcff-liability-components.csv).',
        '- [Investment schedules CSV](company-data-preparation/historical-fcff-investment-schedules.csv).',
        '- Replay: `PYTHONPATH=src .venv/bin/python scripts/reconcile_historical_fcff_adjustments.py --check`.', '',
        '### Primary annual filings', '']
    for c in data['companies']:
        lines.append('- '+c['ticker']+': '+', '.join('['+p['fiscal_year_label']+']('+primary_url(p['reported_cfo_control'])+')' for p in c['periods'])+'.')
    lines.append('')
    return re.sub(r'(?<=[a-z])(?=\d)', ' ', '\n'.join(lines))


def outputs(data):
    return {JSON_PATH: json.dumps(data,sort_keys=True,indent=2)+'\n', REPORT_PATH: render(data), **csv_outputs(data)}


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--check',action='store_true');args=parser.parse_args()
    data=build()
    for name,text in outputs(data).items():
        path=ROOT/name
        if args.check:
            if path.read_bytes()!=text.encode(): raise SystemExit('Adjustment schedule replay differs: '+name)
        else: path.write_bytes(text.encode())
    print(f"{data['tax_bridges_verified']} tax bridges; {data['closing_liability_partitions_verified']} liability partitions; {data['named_cash_plus_finance_investment_subtotals']} named investment subtotals")


if __name__=='__main__':main()
