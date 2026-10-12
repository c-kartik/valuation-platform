"""Offline mapping checks only: no WP0 adapter, resolution or financial approval.

Exact values/occurrences come from existing byte-pinned, source-verifying loaders.
The only arithmetic check is their previously reviewed reported CFO statement.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from valuation_platform.analyst import historical_inputs as h
from valuation_platform.analyst import cash_flow_inputs as msft
from valuation_platform.analyst import aapl_cash_flow_inputs as aapl
from valuation_platform.analyst import googl_cash_flow_inputs as googl

MAPPING = ROOT / "docs/pilot-historical-input-mappings.json"
REGISTRIES = {
    "MSFT": ("docs/company-data-preparation/msft-reported-cash-flow-bundles.json",
             "c3c35e020066f0887d9d8fe493f975afe9e6f0ea4b1785d2f341691ebb49d993"),
    "AAPL": ("docs/company-data-preparation/aapl-reported-cash-flow-bundle.json",
             "d185b995c566d6bfb3b165627283b5ab52edc8ead1e62332d3d9458d0667b747"),
    "GOOGL": ("docs/company-data-preparation/googl-reported-cash-flow-bundle.json",
              "97ca73213b6bb46dfdaec67f930d3abd0cfbd6d1a17e50047998c0b2764f509f"),
}
ROLES = {
    "NetCashProvidedByUsedInOperatingActivities": (h.Field.CFO, "reported_consolidated_cfo", "cfo"),
    "PaymentsToAcquirePropertyPlantAndEquipment": (h.Field.CAPEX, "reported_cash_ppe_purchase", "cash_ppe"),
    "ShareBasedCompensation": (h.Field.SBC, "sbc_cfo_addback", "recognized_sbc"),
    "AllocatedShareBasedCompensationExpense": (h.Field.SBC, "sbc_note_expense", "recognized_sbc"),
    "IncomeTaxesPaidNet": (h.Field.TAX, "cash_tax_paid_net", "cash_tax"),
    "IncomeTaxExpenseBenefit": (h.Field.TAX, "accrued_tax_provision", "tax_provision"),
    "DeferredIncomeTaxExpenseBenefit": (h.Field.DEFERRED_TAX, "deferred_tax_provision", "deferred_tax"),
    "DeferredIncomeTaxesAndTaxCredits": (h.Field.DEFERRED_TAX, "cfo_deferred_tax_adjustment", "deferred_tax"),
    "Depreciation": (h.Field.DA, "depreciation_observation", "depreciation"),
    "DepreciationDepletionAndAmortization": (h.Field.DA, "combined_da_cfo_addback", "da_addback"),
    "DepreciationAmortizationAndOther": (h.Field.DA, "mixed_da_and_other_cfo_addback", "mixed_da_other"),
    "FinanceLeaseRightOfUseAssetAmortization": (h.Field.DA, "finance_lease_asset_amortization_expense", "finance_lease_amortization"),
}


class MappingError(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise MappingError(reason)


def load_document():
    def unique(pairs):
        out = {}
        for key, value in pairs:
            require(key not in out, "Duplicate mapping key")
            out[key] = value
        return out
    return json.loads(MAPPING.read_text(), object_pairs_hook=unique)


def load_bundles():
    """Only existing four registrations; loaders verify original receipts/facts."""
    result = {}
    for module, loader in ((msft, msft.load_msft_bundle), (aapl, aapl.load_aapl_bundle),
                           (googl, googl.load_googl_bundle)):
        for bundle_id in module.registered_bundle_ids():
            result[bundle_id] = loader(bundle_id)
    return result


def role_for(issuer, bundle, input_id):
    """Review labels for these four packages, never a generic concept cascade."""
    if input_id.startswith("IncreaseDecreaseIn"):
        return h.Field.CF_WORKING_CAPITAL, "reported_cash_flow_movement", input_id
    result = ROLES.get(input_id)
    if result is None:
        return None
    field, role, population = result
    if input_id == "DeferredIncomeTaxExpenseBenefit" and issuer == "MSFT" and bundle.period.annual_end.year == 2025:
        role = "cfo_deferred_adjustment_with_provision_confirmation"
    if input_id == "Depreciation":
        role = "depreciation_cfo_addback" if issuer == "GOOGL" else "depreciation_note_expense"
    return field, role, population


def validate(document=None, bundles=None):
    """Return diagnostics, not historical-input models or mapped financial outputs."""
    doc = load_document() if document is None else document
    bundles = load_bundles() if bundles is None else bundles
    require(set(doc) == {"schema", "contract", "version", "period_count", "field_family_count", "scope", "periods"},
            "Exact mapping document shape required")
    require(doc["schema"] == "pilot-historical-input-mappings-v1" and doc["contract"] == h.SCHEMA
            and type(doc["version"]) is int and doc["version"] == 1, "Mapping identity/version mismatch")
    require(doc["period_count"] == 4 and doc["field_family_count"] == len(h.Field)
            and len(doc["periods"]) == 4, "Four periods / fourteen families required")
    expected_ids = {"msft-reported-cash-flow-fy2025", "msft-reported-cash-flow-fy2026",
                    "aapl-reported-cash-flow-fy2025", "googl-reported-cash-flow-fy2024"}
    require(set(bundles) == expected_ids and {r["bundle_id"] for r in doc["periods"]} == expected_ids,
            "Exact four existing pilot identities required")
    report = {}
    for row in doc["periods"]:
        require(set(row) == {"issuer", "bundle_id", "registry_path", "registry_sha256", "registry_bundle_pointer",
                "period", "evidence_review", "fields", "reported_cfo_check", "supplementary_input_ids",
                "source_unknowns_pointer", "limitations_pointer"}, "Exact period mapping shape required")
        b = bundles[row["bundle_id"]]
        require(row["issuer"] in REGISTRIES, "Unknown issuer")
        path, digest = REGISTRIES[row["issuer"]]
        require((row["registry_path"], row["registry_sha256"]) == (path, digest), "Immutable registry binding mismatch")
        body = (ROOT / path).read_bytes()
        require(hashlib.sha256(body).hexdigest() == digest, "Registry bytes changed")
        registry = json.loads(body)
        index = next(i for i, spec in enumerate(registry["bundles"]) if spec["bundle_id"] == b.bundle_id)
        spec = registry["bundles"][index]
        pointer = f"/bundles/{index}"
        require(row["registry_bundle_pointer"] == pointer and row["source_unknowns_pointer"] == pointer + "/unknowns"
                and row["limitations_pointer"] == pointer + "/limitations", "Exact registry locators required")
        require(row["period"] == dict(spec["period"], form=spec["form"]), "Frozen period binding mismatch")
        require(row["period"] == {"cik": b.period.cik, "accession": b.period.accession,
            "annual_start": b.period.annual_start.isoformat(), "annual_end": b.period.annual_end.isoformat(),
            "form": b.period.form}, "Loaded source period mismatch")
        require(row["evidence_review"] == registry["evidence_reference"] and (ROOT / row["evidence_review"]).exists(),
                "Exact evidence review required")
        require(set(row["fields"]) == {f.value for f in h.Field}, "Every contract family required")
        mapped_ids = []
        statuses = Counter()
        for name, field in row["fields"].items():
            require(set(field) == {"status", "origin", "quality", "review", "scope", "completeness", "aggregation",
                    "bindings", "unresolved_requirements", "null_reason"}, "Exact field mapping shape required")
            require(field["aggregation"] == "none", "No component totals or economic aggregation approved")
            require(field["review"] == "reviewed" and field["unresolved_requirements"]
                    and all(type(s) is str and s.strip() for s in field["unresolved_requirements"]),
                    "Reviewed mapping with explicit unresolved requirements required")
            expected = {i.input_id for i in b.inputs if role_for(row["issuer"], b, i.input_id) is not None
                        and role_for(row["issuer"], b, i.input_id)[0].value == name}
            bindings = field["bindings"]
            require({v["input_id"] for v in bindings} == expected and len(bindings) == len(expected),
                    "Missing, duplicated or misclassified field/source binding")
            if not bindings:
                require(field["status"] == "unavailable" and field["origin"] == "unavailable"
                        and field["quality"] == "unassessed" and field["scope"] == "unknown"
                        and field["completeness"] == "unknown" and type(field["null_reason"]) is str
                        and field["null_reason"].strip(), "Unavailable family requires specific null reason")
            else:
                require(field["origin"] == "reported" and field["quality"] == "limited"
                        and field["null_reason"] is None, "Reported mappings cannot imply assumptions or complete quality")
                require(field["status"] == ("limited_support" if name == h.Field.DA.value else "mapped"),
                        "D&A support cannot certify the primitive")
                require(field["completeness"] == ("complete" if name == h.Field.CFO.value else "partial")
                        and field["scope"] == ("consolidated_reported" if name == h.Field.CFO.value else "restricted"),
                        "Only reported consolidated CFO subtotal has complete stated scope")
            for binding in bindings:
                item = b.input(binding["input_id"])
                si = next(i for i, source in enumerate(spec["inputs"]) if source["input_id"] == item.input_id)
                _, role, population = role_for(row["issuer"], b, item.input_id)
                expected_binding = {"input_id": item.input_id, "registry_pointer": pointer + f"/inputs/{si}",
                    "origin": "reported", "role": role, "population": population, "unit": "USD", "scale": 1,
                    "sign": item.display_multiplier, "precision": spec["inputs"][si]["decimals"],
                    "context_id": spec["annual_context_id"], "occurrence_ordinals": spec["inputs"][si]["ordinals"]}
                require(binding == expected_binding, "Exact role, sign/scale, precision or source locator mismatch")
                require(type(binding["scale"]) is int and type(binding["sign"]) is int, "Exact integer sign/scale required")
                for occurrence in item.occurrences:
                    require(occurrence.context_id == binding["context_id"] and occurrence.start == b.period.annual_start
                            and occurrence.end == b.period.annual_end and occurrence.entity_cik == b.period.cik
                            and occurrence.decimals == binding["precision"] and occurrence.normalized_unit == "USD"
                            and not occurrence.dimensions and not occurrence.nil,
                            "Exact annual eligible occurrence binding required")
                require([o.ordinal for o in item.occurrences] == binding["occurrence_ordinals"],
                        "Every confirming occurrence retained")
                # Existing ReportedInput handles exact sign conversion without ambient rounding.
                require(item.displayed_value_usd == (item.value_usd if binding["sign"] == 1
                                                    else item.value_usd.copy_negate()), "Sign conversion mismatch")
                mapped_ids.append(item.input_id)
            statuses[field["status"]] += 1
        require(len(mapped_ids) == len(set(mapped_ids)), "Same source/population cannot be imported twice")
        require(row["supplementary_input_ids"] == [i.input_id for i in b.inputs if i.input_id not in mapped_ids],
                "Unmapped existing input disposition incomplete")
        require(row["reported_cfo_check"] == {"kind": "independent_reported_statement_check",
                "terms_pointer": pointer + "/cfo_terms", "target_input_id": "NetCashProvidedByUsedInOperatingActivities",
                "residual_operand": None}, "Residual cannot substitute for independent reported CFO reconciliation")
        require(tuple(spec["cfo_terms"]) == b.cfo_terms and b.cfo_reconciles, "Existing complete statement check failed")
        require("AllocatedShareBasedCompensationExpense" not in b.cfo_terms and b.cfo_terms.count("ShareBasedCompensation") == 1,
                "SBC expense and add-back cannot be duplicate CFO charges")
        require(not b.valuation_consumption_approved and not b.is_complete_operating_nwc,
                "Original financial limitations must remain")
        report[b.bundle_id] = {**dict(statuses), "field_families": len(h.Field), "mapped_source_inputs": len(mapped_ids),
                              "supplementary_inputs": len(row["supplementary_input_ids"]),
                              "confirming_occurrences": sum(len(b.input(k).occurrences) for k in mapped_ids),
                              "independent_reported_cfo_check": "PASS"}
    return report


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2, sort_keys=True))
