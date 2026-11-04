"""Apply explicitly reviewed issuer treatments over the sealed original history.

META's identified PP&E disposal receipts change investment, not source facts,
forecast inputs, financing or the historical CFO/interest/tax convention.
"""
from decimal import Decimal
from fractions import Fraction
import hashlib
import json
from urllib.parse import urlsplit

from . import cfo_history
from .filing_fcff import calculate

OVERLAY='docs/company-resolutions/META/adopted-history.json'
OVERLAY_SHA256='f12fa6a2a988405f2c7129a73c1a9a850f370139409222c66561c0c986d536a6'
BASIS='REPORTED_CFO_NET_IDENTIFIED_PPE'


def amount(value):
    if type(value) is not str or not Decimal(value).is_finite():
        raise ValueError('Finite source decimal string required')
    return Fraction(value)


def adopted_window(root,kind):
    rows=cfo_history.adopted_window(root,kind)
    if kind=='aapl-fy2025':
        from .apple_operating_history import apply_window
        return apply_window(root,rows)
    if kind!='meta-fy2025':return rows
    payload=(root/OVERLAY).read_bytes()
    if hashlib.sha256(payload).hexdigest()!=OVERLAY_SHA256:
        raise ValueError('Meta resolution overlay differs from reviewed pin')
    overlay=json.loads(payload)
    if overlay['schema_version']!='approved-meta-net-investment-v1' or overlay['decision_id']!='META-INV-001' or len(overlay['periods'])!=5:
        raise ValueError('Unapproved Meta investment overlay')
    for row,treatment in zip(rows,overlay['periods'],strict=True):
        rev=row['revenue'];identity=treatment['identity'];calc=row['fcff_calculation'];inputs=calc['inputs']
        if (identity['cik']!=1326801 or identity['form']!='10-K' or
            (identity['annual_start'],identity['annual_end'],identity['accession'])!=(rev['period_start'],rev['period_end'],rev['accession']) or
            treatment['original_cash_ppe_usd']!=inputs['cash_ppe']):
            raise ValueError('Meta overlay period or original investment mismatch')
        receipt=amount(treatment['identified_receipts_usd']);net=amount(treatment['net_cash_ppe_usd'])
        if receipt<0 or net<0 or net+receipt!=amount(inputs['cash_ppe']):raise ValueError('Invalid identified receipt/net investment')
        if bool(receipt)!=bool(treatment['source_urls']):raise ValueError('Receipt needs an exact filing source')
        for url in treatment['source_urls']:
            if urlsplit(url).scheme!='https' or urlsplit(url).hostname!='www.sec.gov':raise ValueError('Official receipt source required')
        if receipt:
            inputs['cash_ppe_before_receipts']=inputs['cash_ppe'];inputs['identified_ppe_receipts']=str(receipt)
        inputs['cash_ppe']=str(net)
        result=calculate(*(inputs[k] for k in cfo_history.OPERANDS))
        if result['amount_usd']!=treatment['fcff_usd']:raise ValueError('Meta overlay FCFF arithmetic mismatch')
        row['fcff']=result['amount_usd'];row['fcff_basis']=BASIS
        for url in treatment['source_urls']:
            if url not in calc['sources']:calc['sources'].append(url)
    return rows


def policy(kind):
    if kind=='aapl-fy2025':
        from .apple_operating_history import policy as apple_policy
        return apple_policy()
    result=cfo_history.policy()
    if kind=='meta-fy2025':
        result['basis']=BASIS
        result['notice']='Meta cash PP&E is net of identified disposal receipts: FY2022 $245m; FY2023 $221m. Unallocated investing amounts remain unresolved. '+result['notice']
    return result
