"""Statement-based historical FCFF under an explicit reported-ETR convention.

This conventional CFO measure is separate from the platform's operating-only,
SBC-expensed, finance-investment forecast convention. No missing input is filled.
"""
from decimal import Context, Decimal, localcontext
from fractions import Fraction


METHOD = "reported-cfo-expensed-interest-reported-etr-cash-ppe-v1"


def calculate(cfo, cash_ppe, interest_expense, tax_provision, pretax_income):
    """Exact rational arithmetic on filing decimal strings; display separately.

    ETR = reported tax provision / reported pretax income. Using that rate for
    the interest add-back is a calculation convention, not a disclosed actual
    interest tax shield. Cash interest and accrued interest are not substituted.
    """
    values = []
    for value in (cfo, cash_ppe, interest_expense, tax_provision, pretax_income):
        if value is None:
            raise ValueError("A missing FCFF operand cannot be estimated or zero-filled")
        if type(value) is not str or not Decimal(value).is_finite():
            raise ValueError("Finite filing decimal strings required")
        values.append(Fraction(value))
    operating, investment, interest, tax, pretax = values
    if investment < 0 or interest < 0 or pretax <= 0:
        raise ValueError("Payment/expense magnitudes and positive reported pretax required")
    rate = tax / pretax
    addition = interest * (1 - rate)
    fcff = operating + addition - investment
    with localcontext(Context(prec=50)):
        def decimal(value):
            return str(Decimal(value.numerator) / Decimal(value.denominator))
        return {
            "methodology": METHOD, "classification": "DERIVED_CALCULATION_UNDER_STATED_CONVENTION",
            "formula": "reported CFO + reported interest expense * (1 - reported tax provision / reported pretax income) - cash PP&E",
            "amount_usd": decimal(fcff),
            "exact_fraction_usd": {"numerator": str(fcff.numerator), "denominator": str(fcff.denominator)},
            "display_billions": f"{Decimal(fcff.numerator) / Decimal(fcff.denominator) / Decimal(1000000000):.2f}",
            "reported_etr": decimal(rate), "after_tax_interest_addback_usd": decimal(addition),
            "cash_fcf_usd": decimal(operating - investment),
            "precision_notice": "Exact arithmetic on reported rounded points; extra calculated digits do not improve filing precision.",
            "tax_notice": "Reported ETR is the named allocation convention, not a separately disclosed unlevered cash-tax rate or actual interest tax shield.",
            "forecast_calibration_approved": False,
        }
