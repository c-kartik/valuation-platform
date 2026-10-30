"""Issuer-independent Decimal estimation rules. None calculates financial value."""
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext
from functools import wraps
import re

CONTEXT = Context(prec=50, rounding=ROUND_HALF_EVEN)


def isolated(fn):
    @wraps(fn)
    def call(*args, **kwargs):
        with localcontext(CONTEXT):
            return fn(*args, **kwargs)
    return call


def number(value):
    if not isinstance(value, str) or not re.fullmatch(r'-?(?:\d+(?:\.\d+)?|\.\d+)', value) or len(value) > 128:
        raise ValueError('Finite decimal STRING required, without exponent')
    result = Decimal(value)
    if not result.is_finite():
        raise ValueError('Finite decimal required')
    return result


@isolated
def growth(current, prior):
    a, b = number(current), number(prior)
    if b <= 0 or a < 0:
        raise ValueError('Comparable nonnegative current and positive prior revenue required')
    return str(a / b - 1)


@isolated
def cagr(first, last, periods):
    a, b = number(first), number(last)
    if a <= 0 or b < 0 or type(periods) is not int or periods < 1:
        raise ValueError('Positive endpoint and integer period count required')
    return str((b/a) ** (Decimal(1)/periods) - 1)


@isolated
def fade(start, end, count=5):
    if type(count) is not int or count < 2:
        raise ValueError('At least two fade points required')
    a, b = number(start), number(end)
    return [str(a+(b-a)*i/(count-1)) for i in range(count)]


@isolated
def wacc(risk_free, erp, beta, spread, equity_weight, debt_weight, tax_shield):
    rf, ep, be, sp, ew, dw, tax = map(number, (risk_free, erp, beta, spread, equity_weight, debt_weight, tax_shield))
    if ew+dw != 1 or min(ew,dw,ep,be,sp) < 0 or not 0 <= tax <= 1:
        raise ValueError('Invalid WACC weights/components; shield applies only once')
    return str((rf+be*ep)*ew+(rf+sp)*(1-tax)*dw)


@isolated
def incremental_cash_ratio(growth_rate, incremental_fraction):
    g, coefficient = number(growth_rate), number(incremental_fraction)
    if g <= -1:
        raise ValueError('Positive revenue needed for full-revenue WC denominator')
    return str(coefficient*g/(1+g))


@isolated
def diagnostic_axes(wacc_value, terminal_value, wacc_offset, terminal_offset):
    """No clamp: invalid economic combinations remain for the existing grid engine."""
    w,t,ws,ts=map(number,(wacc_value,terminal_value,wacc_offset,terminal_offset))
    if min(ws,ts)<=0:
        raise ValueError('Positive diagnostic offsets required')
    return {'wacc_values':[str(w-ws),str(w),str(w+ws)],'terminal_values':[str(t-ts),str(t),str(t+ts)]}
