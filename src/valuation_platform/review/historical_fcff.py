"""Read-only preparation for a three-issuer historical FCFF consumer.

Reuses accepted histories; does not activate judgments, fetch filings, or feed
valuations. Cash CFO less cash PP&E is a separately named intermediate measure.
Unresolved economic adjustments remain null, never implicit zero adjustments.
"""
from datetime import date
from decimal import Context, Decimal, localcontext
import base64
import gzip
import hashlib
import json
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

from valuation_platform.valuation.consumer import ANCHORS, load_revenue_anchor


SCHEMA = "historical-fcff-review-v1"
KINDS = ("googl-fy2025", "aapl-fy2025", "meta-fy2025")
PROPOSAL = "historical-cfo-to-operating-fcff-v1-proposal"
# Different labels for the same supporting role, not issuer-specific formulas.
SUPPORT = {
    "meta": {
        "cash_interest_candidate": "cash_interest",
        "finance_interest_candidate": "finance_interest_cash",
        "finance_additions_candidate": "noncash_finance_rou",
    },
    "aapl": {
        "cash_interest_candidate": "cash_interest_net",
        "combined_lease_additions_support": "RightofUseAssetsObtainedinExchangeforOperatingandFinanceLeaseLiabilities",
        "finance_asset_stock_support": "finance_rou",
        "operating_asset_stock_support": "op_rou",
    },
    "googl": {
        "finance_interest_candidate": "FinanceLeaseInterestPaymentOnLiability",
        "finance_additions_candidate": "RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability",
        "interest_expense_support": "InterestExpenseNonoperating",
        "capitalized_interest_support": "InterestCostsCapitalized",
    },
}
REQUIREMENTS = {
    "financing_cash": "Identify financing interest actually included in CFO, with borrowing/lease overlap resolved. Expense and principal are not cash-interest substitutes.",
    "nonoperating_cash": "Identify excluded investment/nonoperating cash remaining in CFO. Do not subtract accrual gains already reversed by the cash-flow reconciliation.",
    "operating_taxes": "Specify a historical unlevered operating-tax treatment and its financing/nonoperating tax effects. Cash taxes, provision and reported ETR are different populations.",
    "sbc_alignment": "Retain compensation as an expense consistently with the forecast. Review reversal of the actual CFO SBC add-back, not a second deduction of the expense proxy.",
    "finance_investment": "Identify non-overlapping additions to financed operating assets. Combined operating/finance additions and liability changes are not finance-investment substitutes.",
    "investment_perimeter": "Review cash PP&E, capitalized interest, capital-creditor settlements and acquisitions against the forecast investment/growth perimeter; count each once.",
}


def _amount(value):
    if type(value) is not str:
        raise ValueError("Retained decimal string required")
    result = Decimal(value)
    if not result.is_finite():
        raise ValueError("Finite retained amount required")
    return result


def _occurrence(fact, identity, instant=False):
    if fact.get("unit") != "USD" or fact.get("as_of") != (identity["annual_end"] if instant else None):
        raise ValueError("Same-period USD population required")
    amount = _amount(fact["value"])
    matches = [o for o in fact["occurrences"] if
               o["start"] == (None if instant else identity["annual_start"]) and o["end"] == identity["annual_end"]
               and not o["dimensions"] and _amount(o["raw_value"]) == amount
               and o["unit_id"].lower() == "usd"]
    if not matches:
        raise ValueError("Exact same-period undimensioned flow occurrence required")
    # Preserve actual occurrence precision, including a rounded note whose
    # inherited fact-level precision differs. Never improve source precision.
    return matches[0]


def _proof(row, cfo):
    """Recheck independent displayed arithmetic; never form a CFO residual."""
    reconciliation = row["cfo_reconciliation"]
    if "terms" in reconciliation:
        if reconciliation["supported"] is not True or reconciliation["residual_used"] is not False:
            raise ValueError("Supported independent CFO check required")
        terms = reconciliation["terms"]
        if len({t["fact"] for t in terms}) != len(terms):
            raise ValueError("Duplicate CFO term")
        contributions = []
        for term in terms:
            fact = row["facts"][term["fact"]]
            _occurrence(fact, row["identity"])
            if type(term["multiplier"]) is not int or term["multiplier"] not in (-1, 1):
                raise ValueError("Explicit CFO contribution sign required")
            contribution = _amount(fact["value"]) * term["multiplier"]
            if contribution != _amount(term["contribution_usd"]):
                raise ValueError("CFO term/source disagreement")
            contributions.append(contribution)
        expected = _amount(reconciliation["value_usd"])
        reference = "cfo_reconciliation"
    else:
        check = row.get("independent_display_check")
        if check is not None:
            reference = "independent_display_check"
        else:
            checks = [p for p in reconciliation["populations"] if p["status"] == "SUPPORTED"]
            if reconciliation["status"] != "SUPPORTED" or len(checks) != 1:
                raise ValueError("Unique supported CFO population required")
            check = checks[0]
            reference = "cfo_reconciliation/populations/0"
        if check["status"] != "SUPPORTED":
            raise ValueError("Unsupported independent CFO check")
        contributions = [_amount(r["value"]) for r in check["rows"]]
        expected = _amount(check["cfo"]["value"])
        if _amount(check["difference"]) != 0:
            raise ValueError("Pilot requires exact displayed CFO arithmetic")
    total = sum(contributions, Decimal(0))
    if total != expected or total != cfo:
        raise ValueError("Displayed CFO does not reconcile to selected CFO")
    return {"status": "EXACT_RECHECK", "reference_suffix": reference,
            "row_sum_usd": str(total), "reported_cfo_usd": str(cfo),
            "difference_usd": "0", "term_count": len(contributions),
            "additional_working_capital_deduction": False}


def prepare_company(root, kind):
    """Build a source-bound review; no historical FCFF publication authority."""
    if kind not in KINDS:
        raise ValueError("Three-issuer pilot only")
    load_revenue_anchor(kind, root)  # Existing source/review/audit revision checks.
    spec = ANCHORS[kind]
    path = root / spec["package"]
    payload = path.read_bytes()
    package = json.loads(payload)
    prefix = spec["ticker"].lower()
    source_key = "periods" if prefix == "meta" else prefix + "_history_review/periods"
    view_key = "current_history" if prefix == "meta" else prefix + "_current_history"
    audit_key = "history_approval" if prefix == "meta" else prefix + "_history_approval"
    rows = package["periods"] if prefix == "meta" else package[prefix + "_history_review"]["periods"]
    views = package[view_key]["periods"]
    result = []
    # All finite monetary operations are exact in an isolated Decimal context.
    with localcontext(Context(prec=100)):
        for index, (row, view) in enumerate(zip(rows, views, strict=True)):
            identity = row["identity"]
            start, end = (date.fromisoformat(identity[k]) for k in ("annual_start", "annual_end"))
            if (identity != view["identity"] or identity["cik"] != spec["identity"]["cik"]
                    or identity["form"] != "10-K" or not 330 <= (end-start).days <= 380):
                raise ValueError("Incompatible annual population")
            base = f"/{source_key}/{index}"

            def observation(key, instant=False):
                fact = row["facts"][key]
                occurrence = _occurrence(fact, identity, instant)
                urls = [s.get("url", s.get("source_url", "")) for s in row["sources"]]
                urls = [u for u in urls if urlsplit(u).scheme == "https"
                        and urlsplit(u).hostname == "www.sec.gov"
                        and identity["accession"].replace("-", "") in urlsplit(u).path]
                if not urls:
                    raise ValueError("Same-accession SEC sources required")
                return {"amount_usd": fact["value"], "classification": "REPORTED_SUPPORT",
                        "unit": "USD", "precision": occurrence["precision"],
                        "as_of": fact.get("as_of"),
                        "retained_fact_precision": fact["precision"],
                        "concept": fact["concept"], "context_id": occurrence["context_id"],
                        "occurrence_ordinal": occurrence["ordinal"],
                        "source_reference": spec["package"] + "#" + base + "/facts/" + key,
                        "sources": urls}

            def accepted(value, multiplier):
                key = value["source_reference"].rsplit("/", 1)[-1]
                point = observation(key)
                if (value["source_reference"] != base + "/facts/" + key
                        or value["origin"] != "reported" or value["unit"] != "USD"
                        or value["precision"] != point["retained_fact_precision"]
                        or value["raw_value"] != point["amount_usd"]
                        or value.get("multiplier", value.get("sign_multiplier")) != multiplier
                        or _amount(value["value"]) != _amount(point["amount_usd"]) * multiplier):
                    raise ValueError("Accepted amount/source/sign mismatch")
                return dict(point, amount_usd=value["value"], sign_multiplier=multiplier,
                            raw_value=value["raw_value"], classification="ACCEPTED_REPORTED_INPUT")

            inputs = view["inputs"]
            cfo = accepted(inputs["reported_cfo"], 1)
            capex = accepted(inputs["cash_capex"], -1)
            if _amount(capex["raw_value"]) < 0:
                raise ValueError("Cash PP&E payment magnitude required")
            sbc = accepted(inputs["stock_based_compensation"]["addback"], 1)
            tax_context = inputs["reported_tax_context"]
            tax = {k: accepted(tax_context[k], -1 if k == "cash_taxes" else 1)
                   for k in ("cash_taxes", "provision", "pretax")}
            proof = _proof(row, _amount(cfo["amount_usd"]))
            proof["source_reference"] = spec["package"] + "#" + base + "/" + proof.pop("reference_suffix")
            support = {role: observation(key) if key in row["facts"] else None
                       for role, key in SUPPORT[prefix].items() if "stock_support" not in role}
            support.update({role: observation(key, instant=True) for role, key in SUPPORT[prefix].items()
                            if "stock_support" in role})
            # Pure nonoperating reconciliation lines only. Mixed Other is not
            # reclassified wholesale. Empty selections remain an explicit
            # estimate limitation, not proof there are no additional effects.
            nonoperating = []
            pure_concepts = {"DebtAndEquitySecuritiesGainLoss", "EquitySecuritiesFvNiGainLoss",
                             "UnrealizedGainLossOnMarketableAndNonmarketableEquityInvestments"}
            rec = row["cfo_reconciliation"]
            if "terms" in rec:
                for j, term in enumerate(rec["terms"]):
                    if row["facts"][term["fact"]]["concept"] in pure_concepts:
                        nonoperating.append({"amount_usd": term["contribution_usd"],
                            "source_reference": spec["package"] + "#" + base + f"/cfo_reconciliation/terms/{j}"})
            else:
                check = row.get("independent_display_check") or rec["populations"][0]
                suffix = "independent_display_check" if row.get("independent_display_check") else "cfo_reconciliation/populations/0"
                for j, term in enumerate(check["rows"]):
                    if term.get("concept", term.get("fact", {}).get("concept")) in pure_concepts:
                        nonoperating.append({"amount_usd": term["value"],
                            "source_reference": spec["package"] + "#" + base + f"/{suffix}/rows/{j}"})
            result.append({
                "identity": identity, "fiscal_year_label": "FY" + str(end.year),
                "inputs": {"reported_cfo": cfo, "signed_cash_ppe": capex, "ebit": accepted(inputs["ebit"], 1),
                           "cfo_sbc_addback": sbc, "reported_tax_context": tax},
                "cfo_check": proof, "supporting_observations": support,
                "identified_nonoperating_cfo_contributions": nonoperating,
                "cash_fcf": {"amount_usd": str(_amount(cfo["amount_usd"]) + _amount(capex["amount_usd"])),
                             "classification": "DERIVED_CFO_LESS_CASH_PPE_NOT_FCFF",
                             "formula": "reported_cfo + signed_cash_ppe",
                             "operands": [cfo["source_reference"], capex["source_reference"]],
                             "unit": "USD", "precision": str(max(int(cfo["precision"]), int(capex["precision"]))),
                             "valuation_input": False},
                "fcff": None, "status": "PENDING_ECONOMIC_RECONCILIATION",
                "adjustments": [{"id": key, "amount_usd": None, "status": "UNRESOLVED",
                                 "requirement": requirement} for key, requirement in REQUIREMENTS.items()],
            })
    if len(result) != 5:
        raise ValueError("Five selected pilot annuals required")
    company = {"ticker": spec["ticker"], "package": spec["package"],
            "package_sha256": hashlib.sha256(payload).hexdigest(),
            "historical_approval_sha256": package[audit_key]["sha256"],
            "periods": result}
    if prefix == "googl":
        _alphabet_comparatives(root, rows[3], company)
    _estimates(company)
    return company


def _alphabet_comparatives(root, source_row, company):
    """Review-only later comparatives from the existing verified FY2024 receipt.

    Do not insert these observations into original FY2022/23 accepted histories.
    They retain FY2024 source accession and original fact-period dates separately.
    """
    source = next(s for s in source_row["sources"] if s["source_id"] == "FY2024-instance")
    manifest = json.loads((root / source["path"]).read_text())
    artifact = manifest["artifacts"][int(source["pointer"].rsplit("/", 1)[-1])]
    body = gzip.decompress(base64.b64decode(artifact["response_body_gzip_base64"], validate=True))
    if (hashlib.sha256(body).hexdigest() != source["sha256"] or artifact["sha256"] != source["sha256"]
            or len(body) != artifact["byte_length"] or artifact["http_status"] != 200
            or artifact["source_url"] != source["source_url"]
            or artifact["accession"] != source_row["identity"]["accession"]
            or artifact["representation"] != "sec_response_body_bytes"
            or artifact["digest_type"] != "sha256_sec_response_body_bytes"):
        raise ValueError("Later comparative retained receipt mismatch")
    tree = ET.fromstring(body)
    ns = {"x": "http://www.xbrl.org/2003/instance", "d": "http://xbrl.org/2006/xbrldi"}
    contexts = {c.get("id"): c for c in tree.findall("x:context", ns)}
    for period in company["periods"][1:3]:
        identity = period["identity"]
        candidates = []
        for ordinal, fact in enumerate(tree):
            if fact.tag != "{http://fasb.org/us-gaap/2024}RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability":
                continue
            context = contexts[fact.get("contextRef")]
            if (context.findtext("x:period/x:startDate", namespaces=ns) != identity["annual_start"]
                    or context.findtext("x:period/x:endDate", namespaces=ns) != identity["annual_end"]
                    or context.findall(".//d:explicitMember", ns) or context.findall(".//d:typedMember", ns)
                    or int(context.findtext("x:entity/x:identifier", namespaces=ns)) != identity["cik"]):
                continue
            unit = tree.find(f"x:unit[@id='{fact.get('unitRef')}']/x:measure", ns)
            if unit is None or unit.text != "iso4217:USD":
                raise ValueError("USD comparative required")
            _amount(fact.text)
            candidates.append({"amount_usd": fact.text, "precision": fact.get("decimals"), "unit": "USD",
                "classification": "LATER_REPORTED_COMPARATIVE_REVIEW_ONLY",
                "source_accession": source_row["identity"]["accession"],
                "fact_period_start": identity["annual_start"], "fact_period_end": identity["annual_end"],
                "source_reference": source["path"] + "#" + source["pointer"],
                "source_sha256": source["sha256"], "context_id": fact.get("contextRef"),
                "xml_id": fact.get("id"), "occurrence_ordinal": ordinal,
                "sources": [artifact["source_url"]],
                "limitation": "FY2024 later disclosure; not approval to restate the original accepted history."})
        if len(candidates) != 1:
            raise ValueError("Unique later finance-additions comparative required")
        period["supporting_observations"]["later_finance_additions_comparative"] = candidates[0]


def _estimates(company):
    """Explicit point estimates for review, never accepted historical FCFF.

    Net nonoperating income includes financing interest. Adjust it once rather
    than adding overlapping borrowing and finance-lease interest observations.
    Known securities-gain CFO reversals reduce this accrual-to-cash proxy so
    unrealized gains already removed from CFO are not removed a second time.
    """
    with localcontext(Context(prec=50)):
        ratios = []
        if company["ticker"] == "GOOGL":
            for period in company["periods"]:
                support = period["supporting_observations"]
                point = support.get("finance_additions_candidate") or support.get("later_finance_additions_comparative")
                if point:
                    ratios.append(_amount(point["amount_usd"]) / _amount(period["inputs"]["signed_cash_ppe"]["raw_value"]))
            ratios.sort()
            median_ratio = (ratios[1] + ratios[2]) / 2
        for period in company["periods"]:
            inputs, support = period["inputs"], period["supporting_observations"]
            pretax = _amount(inputs["reported_tax_context"]["pretax"]["amount_usd"])
            provision = _amount(inputs["reported_tax_context"]["provision"]["amount_usd"])
            if pretax <= 0 or not 0 <= provision / pretax <= 1:
                raise ValueError("Separate tax estimate needed outside pilot ETR domain")
            tax_rate = provision / pretax
            net_nonoperating = pretax - _amount(inputs["ebit"]["amount_usd"])
            cfo_reversals = sum((_amount(x["amount_usd"]) for x in period["identified_nonoperating_cfo_contributions"]), Decimal(0))
            cash_proxy = net_nonoperating + cfo_reversals
            after_tax_adjustment = -cash_proxy * (1 - tax_rate)
            point = support.get("finance_additions_candidate") or support.get("later_finance_additions_comparative")
            if point:
                financed = _amount(point["amount_usd"])
                finance_basis = {"kind": point["classification"], "source_reference": point["source_reference"],
                                 "assumption": "Named finance-asset additions treated as incremental non-overlapping operating investment for review."}
            elif company["ticker"] == "AAPL":
                finance_stock = _amount(support["finance_asset_stock_support"]["amount_usd"])
                operating_stock = _amount(support["operating_asset_stock_support"]["amount_usd"])
                share = finance_stock / (finance_stock + operating_stock)
                financed = _amount(support["combined_lease_additions_support"]["amount_usd"]) * share
                finance_basis = {"kind": "ANALYST_ALLOCATION_ESTIMATE", "finance_asset_share": str(share),
                    "formula": "combined lease additions * closing net finance ROU assets / closing net total ROU assets",
                    "source_references": [support[k]["source_reference"] for k in (
                        "combined_lease_additions_support", "finance_asset_stock_support", "operating_asset_stock_support")],
                    "assumption": "Stock mix approximates flow mix; different asset ages, lease terms, remeasurements and timing can make this inaccurate. Not a reported allocation."}
            elif company["ticker"] == "GOOGL" and period["fiscal_year_label"] == "FY2021":
                financed = _amount(inputs["signed_cash_ppe"]["raw_value"]) * median_ratio
                finance_basis = {"kind": "ANALYST_BACKCAST_ESTIMATE", "finance_additions_to_cash_ppe_ratio": str(median_ratio),
                    "reference_years": ["FY2022", "FY2023", "FY2024", "FY2025"],
                    "formula": "FY2021 cash PP&E * median FY2022-FY2025 finance additions / cash PP&E ratio",
                    "assumption": "Later investment mix approximates FY2021. Ex-post backcast; not contemporaneous information or a reported amount."}
            else:
                raise ValueError("No reviewed financed-investment estimate rule")
            value = (_amount(period["cash_fcf"]["amount_usd"])
                     - _amount(inputs["cfo_sbc_addback"]["amount_usd"]) + after_tax_adjustment - financed)
            period["fcff_estimate_for_review"] = {
                "amount_usd": str(value), "display_billions": f"{value / Decimal(1000000000):.2f}",
                "classification": "REVIEW_ESTIMATE_NOT_ACCEPTED_FCFF", "methodology": "historical-cfo-proxy-v1-review",
                "chart_publication_enabled": False, "valuation_input": False,
                "precision_notice": "Extra arithmetic digits do not improve rounded source precision or quantify estimation uncertainty; display to 0.01B only.",
                "formula": "cash_fcf - cfo_sbc_addback - (pretax - EBIT + identified nonoperating CFO contributions) * (1 - reported ETR) - financed_investment_estimate",
                "reported_etr_proxy": str(tax_rate), "net_nonoperating_accrual_usd": str(net_nonoperating),
                "identified_nonoperating_cfo_contributions_usd": str(cfo_reversals),
                "net_nonoperating_cash_proxy_usd": str(cash_proxy),
                "after_tax_net_nonoperating_adjustment_usd": str(after_tax_adjustment),
                "financed_investment_estimate_usd": str(financed), "finance_estimate_basis": finance_basis,
                "assumptions": [
                    "Annual consolidated reported ETR proxies the tax effect of the net nonoperating/financing adjustment, not a separately reported operating cash-tax rate.",
                    "Net nonoperating accrual income plus identified pure nonoperating CFO reversals proxies remaining nonoperating cash. Accrual/cash timing and tax attribution are not fully reconciled.",
                    "Mixed Other and working-capital lines stay in CFO; unallocated nonoperating/tax/SBC effects are not separately estimated. This omission can be material and is not a reported zero.",
                    "Original cash PP&E is retained without a separate capitalized-interest/capital-creditor/acquisition adjustment. This is an omission assumption, not exhaustive investment coverage.",
                    "Reversing the actual CFO SBC add-back retains the compensation cost already in earnings; do not deduct the expense proxy again.",
                    "No new D&A add-back, book NWC reconstruction, lease principal deduction or separate overlapping interest add-back.",
                ],
                "limitation": "Point estimate with unquantified classification, tax and timing uncertainty; not a confidence interval, source-reported FCFF, or approved forecast calibration.",
            }


def build_review(root):
    return {"schema_version": SCHEMA, "proposed_methodology": PROPOSAL,
            "methodology_status": "PROPOSED_NOT_ACTIVATED", "chart_publication_enabled": False,
            "estimate_authority": "User: Allow clearly labeled estimates for review. This authorizes review preparation, not activation of these specific estimates.",
            "scope": "FY2021-FY2025 GOOGL/AAPL/META only; existing reported anchors unchanged",
            "formula_proposal": "CFO - cash PP&E - CFO SBC add-back + financing cash adjustment + nonoperating cash adjustment + operating tax adjustment - non-overlapping financed operating investment + investment perimeter adjustment",
            "restrictions": ["No second D&A add-back or working-capital deduction from CFO.",
                             "No review tax proxy, lease allocation/backcast or omission becomes an approved input by calculation; no missing amount is recast as reported zero.",
                             "No forecast, EV, equity bridge or historical chart values are changed."],
            "companies": [prepare_company(root, kind) for kind in KINDS]}
