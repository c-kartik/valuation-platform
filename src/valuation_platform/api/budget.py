"""HTTP execution budgets, deliberately separate from financial conventions."""

from dataclasses import dataclass
from decimal import Decimal
import json
import re


@dataclass(frozen=True)
class ServerPolicy:
    max_body_bytes: int = 256 * 1024
    max_response_bytes: int = 2 * 1024 * 1024
    deadline_seconds: float = 35.0
    cpu_seconds: int = 30
    body_seconds: float = 10.0

    def __post_init__(self):
        if (type(self.max_body_bytes) is not int or not 1 <= self.max_body_bytes <= 256 * 1024
                or type(self.max_response_bytes) is not int or not 256 <= self.max_response_bytes <= 2 * 1024 * 1024
                or type(self.cpu_seconds) is not int or not 1 <= self.cpu_seconds <= 30
                or not 0 < self.deadline_seconds <= 35 or not 0 < self.body_seconds <= 10):
            raise ValueError("Server policy may only tighten the fixed HTTP ceilings")


DEFAULT_POLICY = ServerPolicy()
NUMBER = re.compile(r'-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?\Z')


class BudgetError(ValueError):
    pass


def check_depth(text):
    """Lexical depth guard only; the existing strict parser owns JSON syntax.

    Escaped quotes/brackets inside strings never contribute to depth. Malformed
    strings/structure still go to the authoritative parser, without repair.
    """
    depth = 0
    quoted = escaped = False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in '{[':
            depth += 1
            if depth > 24:
                raise BudgetError("case: JSON nesting exceeds 24")
        elif char in '}]':
            depth -= 1


def check_tree(doc):
    """Bound the existing parser's tree; no alternate JSON decoder or coercion."""
    pending = [(doc, 'case', '')]
    nodes = 0
    while pending:
        value, path, field = pending.pop()
        nodes += 1
        if nodes > 4096:
            raise BudgetError("case: JSON node count exceeds 4096")
        if type(value) is dict:
            if len(value) > 64:
                raise BudgetError(f"{path}: object exceeds 64 members")
            for key, child in value.items():
                if len(key) > 128:
                    raise BudgetError(f"{path}: key exceeds 128 characters")
                pending.append((child, path + '.' + key, key))
        elif type(value) is list:
            cap = 64 if field == 'components' or field.endswith('_references') or field == 'population_ids' else 128
            if len(value) > cap:
                raise BudgetError(f"{path}: array exceeds {cap} entries")
            pending.extend((child, f"{path}[{i}]", field) for i, child in enumerate(value))
        elif type(value) is str:
            cap = 4096 if field in ('rationale', 'scope') else 2048
            if field.endswith('_id') or field in ('accession', 'schema_version', 'kind', 'origin', 'role', 'unit', 'class_id'):
                cap = 128
            if field.endswith('_references'):
                cap = 1024
            if len(value) > cap:
                raise BudgetError(f"{path}: text exceeds {cap} characters")
            if NUMBER.fullmatch(value):
                if len(value) > 128:
                    raise BudgetError(f"{path}: numeric string exceeds 128 characters")
                exponent = re.split('[eE]', value)
                if len(exponent) == 2 and (len(exponent[1].lstrip('+-')) > 3 or abs(int(exponent[1])) > 100):
                    raise BudgetError(f"{path}: numeric exponent magnitude exceeds 100")
                number = Decimal(value)
                digits = number.as_tuple().digits
                significant = len(digits)  # Conservative, including trailing zeros.
                if significant > 64 or abs(number.as_tuple().exponent) > 100 or abs(number.adjusted()) > 100:
                    raise BudgetError(f"{path}: numeric budget is 64 digits and exponent/adjusted magnitude <= 100")
        elif type(value) is int and abs(value) > 10 ** 12:
            raise BudgetError(f"{path}: integer exceeds HTTP execution budget")


def read_http_case(body):
    # Imported only after readiness has verified private resources.
    from valuation_platform.valuation.case_inputs import _strict_json, read_case
    try:
        text = body.decode('utf-8', errors='strict')
    except UnicodeError as exc:
        raise BudgetError("case: UTF-8 JSON required") from exc
    check_depth(text)
    doc = _strict_json(text)
    check_tree(doc)
    return read_case(text)


def error_body(code, message, errors=()):
    # Bounded public errors; internal exceptions must never be passed here.
    return {'error': {'code': code, 'message': message,
                      'details': [str(e)[:200] for e in list(errors)[:20]]}}


def encode_bounded(result, limit):
    """Bound serialized bytes before IPC; no unbounded dumps/result message."""
    out = bytearray()
    for chunk in json.JSONEncoder(sort_keys=True, indent=2, allow_nan=False).iterencode(result):
        encoded = chunk.encode('utf-8')
        if len(out) + len(encoded) > limit:
            raise BudgetError("result: serialized output exceeds HTTP response budget")
        out.extend(encoded)
    return bytes(out)
