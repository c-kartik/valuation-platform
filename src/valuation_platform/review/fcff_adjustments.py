"""Reconciliation schedules; no unsupported allocations or FCFF publication."""
from fractions import Fraction

from .operating_fcff import amount, serialized


def tax_schedule(provision, current_components, deferred_components, cash_paid, cfo_deferred=None):
    """Tax expense components are signed; cash paid is a payment magnitude."""
    if not current_components or not deferred_components:
        raise ValueError("Explicit current and deferred tax populations required")
    current = sum(map(amount, current_components), Fraction())
    deferred = sum(map(amount, deferred_components), Fraction())
    provision, paid = amount(provision), amount(cash_paid)
    if current + deferred != provision:
        raise ValueError("Current plus deferred provision does not equal reported total")
    if paid < 0:
        raise ValueError("This schedule requires a disclosed net tax payment magnitude")
    return {"current_provision": serialized(current), "deferred_provision": serialized(deferred),
            "total_provision": serialized(provision), "cash_paid": serialized(paid),
            "current_provision_minus_cash_paid": serialized(current-paid),
            "provision_minus_cash_paid": serialized(provision-paid),
            "cfo_deferred_minus_note_deferred": (serialized(amount(cfo_deferred)-deferred) if cfo_deferred is not None else None),
            "provision_control_difference_usd": "0",
            "timing_difference_is_working_capital_adjustment": False,
            "unlevered_operating_cash_tax": None,
            "status": "CONSOLIDATED_TAX_BRIDGE_VERIFIED_OPERATING_ALLOCATION_UNRESOLVED"}


def partition(parent, children):
    if not children:
        raise ValueError("A note partition requires disclosed children, not a residual")
    value = sum(map(amount, children), Fraction())
    if value != amount(parent):
        raise ValueError("Disclosed note children do not equal reported parent")
    return {"sum_of_disclosed_children": serialized(value), "difference_usd": "0",
            "cash_movement_inferred": False, "residual_used": False}


def named_investment(cash_ppe, finance_additions):
    cash = amount(cash_ppe)
    if cash < 0 or (finance_additions is not None and amount(finance_additions) < 0):
        raise ValueError("Investment payment/addition magnitudes required")
    return {"cash_ppe": serialized(cash),
            "cash_ppe_plus_disclosed_finance_additions": (serialized(cash+amount(finance_additions)) if finance_additions is not None else None),
            "finance_additions_missing_is_zero": False, "finance_principal_deducted": False,
            "complete_model_aligned_operating_investment": None}
