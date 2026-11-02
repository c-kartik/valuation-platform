"""Arithmetic for an EBIT-based historical FCFF feasibility test.

Inputs are explicit statement populations. Arithmetic does not certify that a
mixed cash-flow movement is operating working capital, or a cash-flow D&A row
is complete expense D&A. Publication/forecast consumption remains separate.
"""
from decimal import Context, Decimal, localcontext
from fractions import Fraction


METHOD = "ebit-reported-etr-statement-movements-cash-ppe-test-v1"


def amount(value):
    if value is None:
        raise ValueError("Missing operating FCFF operand; no estimate or zero fill")
    if type(value) is not str or not Decimal(value).is_finite():
        raise ValueError("Finite filing decimal strings required")
    return Fraction(value)


def serialized(value):
    with localcontext(Context(prec=50)):
        point = Decimal(value.numerator) / Decimal(value.denominator)
        return {"amount_usd": str(point),
                "exact_fraction_usd": {"numerator": str(value.numerator), "denominator": str(value.denominator)},
                "display_billions": f"{point / Decimal(1000000000):.2f}"}


def calculate(ebit, tax_provision, pretax_income, noncash_costs, cash_ppe, movements):
    """Movements are signed CASH CONTRIBUTIONS, not positive uses of cash.

    SBC is retained as an EBIT expense; only caller-selected noncash operating
    costs are added. The reported consolidated ETR is an allocation convention.
    No extra interest adjustment, CFO, or balance-sheet delta is used here.
    """
    profit, tax, pretax, investment = map(amount, (ebit, tax_provision, pretax_income, cash_ppe))
    if pretax <= 0 or investment < 0:
        raise ValueError("Positive pretax and nonnegative cash PP&E required")
    if not noncash_costs or not movements:
        raise ValueError("Explicit nonempty noncash and movement populations required")
    noncash = sum(map(amount, noncash_costs), Fraction())
    cash_contribution = sum(map(amount, movements), Fraction())
    nopat = profit * (1 - tax / pretax)
    return {"methodology": METHOD, "classification": "OPERATING_METHOD_TEST_NOT_CERTIFIED_FCFF",
            "formula": "EBIT * (1 - tax provision / pretax income) + selected noncash operating costs - cash PP&E + selected signed cash movements",
            "result": serialized(nopat + noncash - investment + cash_contribution),
            "nopat": serialized(nopat), "noncash_costs": serialized(noncash),
            "movement_cash_contribution": serialized(cash_contribution),
            "working_capital_cash_use": serialized(-cash_contribution),
            "reported_etr": serialized(tax / pretax)["amount_usd"],
            "sbc_addback": False, "interest_addback": False,
            "cash_tax_conversion_claim": False, "publishable": False,
            "forecast_calibration_approved": False}
