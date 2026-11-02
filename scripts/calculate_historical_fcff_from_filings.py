"""Calculate source-only historical CFO-convention FCFF; preserve actual gaps.

Offline: existing retained SEC response bytes, original approvals and selections.
Reuses the established primary/instance verifier. No estimate module is imported.
"""
import argparse
import base64
from copy import copy
import csv
from datetime import date
from decimal import Context, Decimal, localcontext
import gzip
import hashlib
from io import StringIO
import json
from pathlib import Path
import re

from prepare_msft_analyst_package import Filing, InlineFacts
from valuation_platform.analyst import cash_flow_inputs as cash
from valuation_platform.analyst.nwc import Artifact, Period
from valuation_platform.review.filing_fcff import METHOD, calculate
from valuation_platform.valuation.consumer import ANCHORS, load_revenue_anchor

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = "docs/company-data-preparation/historical-fcff-filing-calculations.json"
CSV_PATH = "docs/company-data-preparation/historical-fcff-filing-calculations.csv"
REPORT_PATH = "docs/historical-fcff-filing-calculations.md"
KINDS = ("googl-fy2025", "aapl-fy2025", "meta-fy2025")
INTEREST_CONCEPTS = ("InterestExpense", "InterestExpenseNonoperating")


class RetainedFiling(Filing):
    """Read a selected retained source, never rebuild an analyst package."""
    def __init__(self, root, row, manifests):
        identity = row["identity"]
        self.source_identity = dict(identity)
        self.period = Period(identity["cik"], identity["accession"],
                             date.fromisoformat(identity["annual_start"]), date.fromisoformat(identity["annual_end"]))
        self.year = self.period.annual_end.year
        receipts, references = [], []
        for source in row["sources"]:
            path = source["path"]
            if path not in manifests:
                manifests[path] = json.loads((root / path).read_text())
            entry = manifests[path]["artifacts"][int(source["pointer"].rsplit("/", 1)[-1])]
            encoded = entry["response_body_gzip_base64"]
            body = gzip.decompress(base64.b64decode("".join(encoded) if type(encoded) is list else encoded, validate=True))
            url = source.get("url", source.get("source_url"))
            if (entry.get("source_url", entry.get("url")) != url
                    or len(body) != source["byte_length"] or len(body) != entry["byte_length"]
                    or hashlib.sha256(body).hexdigest() != source["sha256"]
                    or entry["sha256"] != source["sha256"]):
                raise ValueError("Retained source URL/body/hash/length mismatch")
            receipt = cash.Receipt(Artifact(url, identity["accession"], entry["representation"],
                                           entry["digest_type"], entry["sha256"], body),
                                   entry["byte_length"], entry["retrieved_at_utc"], entry["http_status"],
                                   entry.get("retrieval_mode", "retained receipt; original mode unspecified"))
            receipts.append(receipt)
            references.append({"source_reference": path + "#" + source["pointer"],
                               "url": url, "sha256": receipt.artifact.sha256,
                               "byte_length": receipt.byte_length, "http_status": receipt.http_status,
                               "retrieved_at_utc": receipt.retrieved_at_utc})
        self.root, self.contexts, self.units, self.namespaces = cash._instance(tuple(receipts), self.period)
        self.primary = next(r for r in receipts if r.artifact.url.endswith(".htm"))
        self.instance = next(r for r in receipts if r.artifact.url.endswith("_htm.xml"))
        self.inline = InlineFacts()
        self.inline.feed(self.primary.artifact.body.decode())
        self.text = re.sub(r"\s+", " ", " ".join(self.inline.text))
        self.facts, self.entries, self.references = {}, [], references

    def extract(self, concept, target, namespace="us-gaap"):
        # The source's own FY identity was already checked above. A later
        # comparative targets different dates without changing source accession.
        selector = copy(self)
        selector.period = Period(self.period.cik, self.period.accession,
                                 date.fromisoformat(target["annual_start"]), date.fromisoformat(target["annual_end"]))
        selector.facts = {}
        selector.fact("selected", concept, "Exact annual primary-inline and extracted-instance observation", namespace=namespace)
        return dict(selector.facts["selected"], source_identity=self.source_identity,
                    target_annual_start=target["annual_start"], target_annual_end=target["annual_end"],
                    sources=self.references)

    def annual_interest_inventory(self, target):
        rows = []
        for ordinal, fact in enumerate(self.root):
            local = fact.tag.split("}")[-1]
            if "interest" not in local.lower() or "NoncontrollingInterest" in local or not fact.get("contextRef"):
                continue
            context = self.contexts[fact.get("contextRef")]
            if cash._context(context) != (target["cik"], date.fromisoformat(target["annual_start"]), date.fromisoformat(target["annual_end"])):
                continue
            unit = self.units.get(fact.get("unitRef"))
            if unit is None or len(unit) != 1 or unit[0].text.rsplit(":", 1)[-1] != "USD":
                continue
            rows.append({"namespace": fact.tag[1:].split("}")[0], "concept": fact.tag.split("}")[-1],
                         "raw_value": fact.text, "precision": fact.get("decimals"),
                         "ordinal": ordinal, "context_id": fact.get("contextRef")})
        return rows

    def total_interest(self, target):
        candidates = [x for x in self.annual_interest_inventory(target) if x["concept"] in INTEREST_CONCEPTS]
        if not candidates:
            return None
        if len({(c["namespace"], c["concept"]) for c in candidates}) != 1:
            raise ValueError("Competing total-interest populations require review")
        candidate = candidates[0]
        return self.extract(candidate["concept"], target, candidate["namespace"])


def build(root=ROOT):
    companies, manifests = [], {}
    with localcontext(Context(prec=100)):
        for kind in KINDS:
            load_revenue_anchor(kind, root)
            spec = ANCHORS[kind]
            payload = (root / spec["package"]).read_bytes()
            package = json.loads(payload)
            prefix = spec["ticker"].lower()
            rows = package["periods"] if prefix == "meta" else package[prefix + "_history_review"]["periods"]
            views = package["current_history" if prefix == "meta" else prefix + "_current_history"]["periods"]
            filings = [RetainedFiling(root, row, manifests) for row in rows]
            periods = []
            for index, (row, view, filing) in enumerate(zip(rows, views, filings, strict=True)):
                identity = row["identity"]
                if identity != view["identity"]:
                    raise ValueError("Accepted/source annual identity mismatch")
                selected = view["inputs"]
                source_base = f"/periods/{index}" if prefix == "meta" else f"/{prefix}_history_review/periods/{index}"

                def accepted(value, sign):
                    key = value["source_reference"].rsplit("/", 1)[-1]
                    retained = row["facts"][key]
                    point = filing.extract(retained["concept"], identity, retained["namespace"])
                    if (value["source_reference"] != source_base + "/facts/" + key
                            or value["origin"] != "reported" or value["unit"] != "USD"
                            or value.get("multiplier", value.get("sign_multiplier")) != sign
                            or Decimal(value["raw_value"]) != Decimal(point["value"])
                            or Decimal(value["value"]) != Decimal(point["value"]) * sign
                            or Decimal(retained["value"]) != Decimal(point["value"])
                            or value["precision"] != retained["precision"]
                            or retained["precision"] not in point["precision_variants"]):
                        raise ValueError("Accepted amount/source/sign/precision mismatch")
                    return dict(point, accepted_reference=spec["package"] + "#" + value["source_reference"])

                inputs = {
                    "cfo": accepted(selected["reported_cfo"], 1),
                    "cash_ppe": accepted(selected["cash_capex"], -1),
                    "tax_provision": accepted(selected["reported_tax_context"]["provision"], 1),
                    "pretax_income": accepted(selected["reported_tax_context"]["pretax"], 1),
                }
                inventory = filing.annual_interest_inventory(identity)
                interest = filing.total_interest(identity)
                if interest is None and prefix == "meta" and index < 2:
                    # Later 2023 Note14 explicitly reports 2021=23m / 2022=185m.
                    # Do not infer complete interest from finance-only/Notes-only tags.
                    interest = filings[2].total_interest(identity)
                inputs["interest_expense"] = interest
                result = (calculate(*(inputs[k]["value"] for k in (
                    "cfo", "cash_ppe", "interest_expense", "tax_provision", "pretax_income")))
                    if interest is not None else None)
                periods.append({
                    "identity": identity, "fiscal_year_label": "FY" + identity["annual_end"][:4],
                    "inputs": inputs, "fcff": result,
                    "status": "CALCULATED_FROM_REPORTED_OPERANDS_UNDER_STATED_CONVENTION" if result else "MISSING_REQUIRED_INTEREST_DISCLOSURE",
                    "cash_fcf_usd": str(Decimal(inputs["cfo"]["value"]) - Decimal(inputs["cash_ppe"]["value"])),
                    "interest_search": {"current_filing_annual_monetary_facts": inventory,
                        "primary_inline_interest_cost_fact_count": sum(any(s in a.get("name", "").lower() for s in (
                            "interestexpense", "interestpaid", "interestpayment", "interestcost"))
                            for a, _ in list(filing.inline.facts.values()) + filing.inline.unaddressed_facts),
                        "primary_cash_interest_caption_present": bool(re.search(r"cash paid for interest|interest paid", filing.text, re.I)),
                        "missing_is_zero": False},
                })
            companies.append({"ticker": spec["ticker"], "package": spec["package"],
                              "package_sha256": hashlib.sha256(payload).hexdigest(), "periods": periods})
    return {"schema_version": "historical-fcff-filing-calculations-v1", "as_of": "2026-11-02",
            "scope": "FY2021-FY2025 retained reported-anchor window; no FY2026 estimate",
            "methodology": METHOD, "formula": "CFO + interest expense * (1 - tax provision / pretax income) - cash PP&E",
            "input_estimates_permitted": False,
            "tax_convention": "Use the exact ratio of reported total tax provision to reported pretax income for the after-tax interest adjustment. This is an explicit allocation convention, not a reported actual interest tax shield.",
            "perimeter": "Conventional reported-CFO basis: noncash adjustments, including SBC, remain in CFO; cash PP&E investment; expensed interest only, not capitalized interest or a second finance-lease interest add-back.",
            "model_difference": "Not the existing SBC-expensed/operating-only/finance-investment-adjusted forecast basis. No automatic chart or forecast calibration integration.",
            "precision": "Verification means traceable reported rounded operands and reproducible arithmetic under this convention, not a unique GAAP-reported FCFF or exact counterfactual unlevered taxes.",
            "calculated_periods": sum(p["fcff"] is not None for c in companies for p in c["periods"]),
            "missing_periods": sum(p["fcff"] is None for c in companies for p in c["periods"]),
            "companies": companies}


def csv_output(review):
    stream = StringIO(newline="")
    fields = ["ticker", "fiscal_year", "period_start", "period_end", "cfo_usd", "cash_ppe_usd",
              "interest_expense_usd", "tax_provision_usd", "pretax_income_usd", "reported_etr",
              "fcff_usd", "fcff_billions", "cash_fcf_usd", "status", "primary_filing", "interest_primary_filing"]
    writer = csv.DictWriter(stream, fields, lineterminator="\n")
    writer.writeheader()
    for company in review["companies"]:
        for p in company["periods"]:
            i, result = p["inputs"], p["fcff"]
            primary = lambda point: next(s["url"] for s in point["sources"] if s["url"].endswith(".htm"))
            writer.writerow(dict(ticker=company["ticker"], fiscal_year=p["fiscal_year_label"],
                period_start=p["identity"]["annual_start"], period_end=p["identity"]["annual_end"],
                cfo_usd=i["cfo"]["value"], cash_ppe_usd=i["cash_ppe"]["value"],
                interest_expense_usd=i["interest_expense"]["value"] if i["interest_expense"] else "",
                tax_provision_usd=i["tax_provision"]["value"], pretax_income_usd=i["pretax_income"]["value"],
                reported_etr=result["reported_etr"] if result else "", fcff_usd=result["amount_usd"] if result else "",
                fcff_billions=result["display_billions"] if result else "", cash_fcf_usd=p["cash_fcf_usd"],
                status=p["status"], primary_filing=primary(i["cfo"]),
                interest_primary_filing=primary(i["interest_expense"]) if i["interest_expense"] else ""))
    return stream.getvalue()


def render(review):
    def millions(value):
        return f"{Decimal(value) / 1000000:,.0f}"
    lines = ["# Historical FCFF — filing-only calculations", "",
        "November 2, 2026. Alphabet, Apple and Meta; FY2021–FY2025, matching the",
        "platform's retained reported-anchor history. No extrapolated FY2026 is used.", "",
        "**13 periods calculated; 2 remain undisclosed-input gaps.** The previous",
        "lease allocations, backcasts and net-nonoperating-cash proxy estimates are",
        "withdrawn for this task. No missing amount is filled with zero or an estimate.", "",
        "## Definition used", "",
        "**FCFF = reported CFO + reported interest expense × (1 − reported ETR) − cash PP&E.**",
        "**Reported ETR = reported income-tax provision ÷ reported pretax income.**", "",
        "This is the conventional CFO-based FCFF relationship described by the",
        "[CFA Institute](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/free-cash-flow-valuation).",
        "Every numerical operand is a reported figure, checked against both primary",
        "inline disclosure and extracted XBRL. ETR is calculated from the reported",
        "monetary amounts rather than a rounded printed percentage. Exact rational",
        "arithmetic is retained alongside decimal/display results.", "",
        "**The tax allocation is still a stated convention.** Reported consolidated ETR",
        "is not a separately disclosed marginal rate, actual interest tax benefit or",
        "counterfactual unlevered cash-tax bill. A filing-only calculation is verifiable",
        "under this definition; it is not a unique GAAP-reported or assumption-free",
        "economic FCFF number. No forecast tax rate or estimated monetary input is used.", "",
        "## Results — USD billions", "",
        "| Company | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |",
        "|---|---:|---:|---:|---:|---:|"]
    for c in review["companies"]:
        lines.append("| " + c["ticker"] + " | " + " | ".join(p["fcff"]["display_billions"] if p["fcff"] else "Unavailable*" for p in c["periods"]) + " |")
    lines += ["", "*Apple's FY2024/25 annual reports do not separately disclose total",
        "interest expense or cash interest paid. The required amounts are absent from",
        "both the primary inline financial disclosures and annual monetary XBRL facts.",
        "Their reported net Other income/expense (269m/−321m) is a mixture, not an",
        "interest-expense amount. Coupon × year-end debt, prior-year interest, annualized",
        "quarters and lease allocations would be estimates and are not substituted.", "",
        "Apple's independently verifiable CFO less cash PP&E is 108.807B for FY2024",
        "and 98.767B for FY2025. Those are cash FCF figures, not missing FCFF values.", "",
        "## Full operand schedules — USD millions", "",
        "CFO/cash PP&E/tax/profit use each original selected annual filing. META's",
        "FY2021/22 total interest 23m/185m comes from its explicit FY2023 Note 14",
        "comparatives, with source accession and target dates kept distinct. This",
        "avoids treating a finance-only or Notes-only observation as complete interest.", "",
        "META FY2021 retains original cash PP&E 18,567m; the later comparative 18,690m",
        "is a different reported selection and is not silently substituted.", ""]
    for c in review["companies"]:
        lines += ["### " + c["ticker"], "",
            "| FY | CFO | Cash PP&E | Interest expense | Tax provision | Pretax income | Calculated FCFF |",
            "|---|---:|---:|---:|---:|---:|---:|"]
        for p in c["periods"]:
            i, result = p["inputs"], p["fcff"]
            with localcontext(Context(prec=50)):
                fcff = f"{Decimal(result['amount_usd']) / 1000000:,.3f}" if result else "Unavailable"
            vals = [p["fiscal_year_label"]] + [millions(i[k]["value"]) if i[k] else "Undisclosed" for k in (
                "cfo", "cash_ppe", "interest_expense", "tax_provision", "pretax_income")] + [fcff]
            lines.append("| " + " | ".join(vals) + " |")
        lines += ["", "Primary source filings:", ""]
        for p in c["periods"]:
            source = next(s["url"] for s in p["inputs"]["cfo"]["sources"] if s["url"].endswith(".htm"))
            lines.append(f"- [{p['fiscal_year_label']} 10-K]({source}) — {p['identity']['annual_start']} to {p['identity']['annual_end']}.")
        lines += [""]
    example = review["companies"][0]["periods"][-1]
    with localcontext(Context(prec=50)):
        amount_m = f"{Decimal(example['fcff']['amount_usd']) / 1000000:,.6f}"
    lines += ["## Example — Alphabet FY2025", "",
        f"`164,713 + 736 × (1 − 26,656 / 158,826) − 91,447 = {amount_m} USD millions`.", "",
        "The previous estimate 42.41B used additional estimated adjustments; it is not",
        "this filing-only calculation and should not be reused as a verified figure.", "",
        "## Relationship to the platform model", "",
        "This series follows the reported-CFO convention. It retains the cash-flow",
        "statement's noncash adjustments (including SBC), uses cash PP&E only, and",
        "adds back total expensed interest once. Interest capitalized in assets is",
        "not added again as an income-statement expense; separately disclosed lease",
        "interest is not added on top of a total that already contains it.", "",
        "The existing forecast instead expenses SBC, models finance-asset additions",
        "and targets operating-only cash flows. This report does not assert identical",
        "financial perimeters or automatically change that forecast, chart or EV.",
        "A fully reconciled operating-only series would require additional disclosed",
        "tax/nonoperating/investment allocations; original gaps remain explicit.", "",
        "## Audit and reproduction", "",
        "- [Machine calculation and exact primary/XBRL evidence](company-data-preparation/historical-fcff-filing-calculations.json).",
        "- [Flat operand/result CSV](company-data-preparation/historical-fcff-filing-calculations.csv).",
        "- Offline replay: `PYTHONPATH=src .venv/bin/python scripts/calculate_historical_fcff_from_filings.py --check`.",
        "- Original package/frozen/source/approval bytes are preserved. Source receipt",
        "  hashes, lengths, URLs, contexts, units, dates and primary/instance numeric",
        "  representations are checked. Missing interest is null, never zero.",
        "- All 36 review/history tests pass, including 9 new source-only tests covering",
        "  independent rational arithmetic, actual/zero/missing inputs, exact source",
        "  confirmations, receipt tampering, Meta later comparatives, Apple gaps,",
        "  estimate-path isolation and byte-preserving package/replay checks.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    review = build()
    outputs = {JSON_PATH: json.dumps(review, sort_keys=True, indent=2) + "\n", CSV_PATH: csv_output(review), REPORT_PATH: render(review)}
    for name, content in outputs.items():
        path = ROOT / name
        if args.check:
            if path.read_bytes() != content.encode():
                raise SystemExit("Filing-only FCFF replay differs: " + name)
        else:
            path.write_bytes(content.encode())
    print(f"{review['calculated_periods']} FCFF calculations; {review['missing_periods']} disclosed-input gaps; no estimated inputs")


if __name__ == "__main__":
    main()
