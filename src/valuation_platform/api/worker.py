"""Spawn target: direct financial functions, bounded bytes, no network/writes."""

import os
from pathlib import Path
import sys

from .budget import BudgetError, encode_bounded, error_body, read_http_case, read_http_document, read_http_scenarios, read_http_sensitivity, read_http_reverse, read_http_fcfe, read_http_apple_analyst, read_http_company_analyst
from .bundle import verify_bundle


def restrict_runtime(root, cpu_seconds):
    """Audit defense plus Unix CPU limit; this is not an OS security sandbox."""
    root = Path(root).resolve()
    sys.dont_write_bytecode = True
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds + 1))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    except ImportError:
        pass  # Parent wall-clock termination remains enforced on non-Unix hosts.

    def audit(event, args):
        if event.startswith('socket.') and event not in ('socket.__new__',):
            raise PermissionError('Financial network access disabled')
        if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
            mode, flags = args[1:3]
            writes = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or (isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            if writes and Path(args[0]).resolve().is_relative_to(root):
                raise PermissionError('Private runtime resources are read-only')
        if event in ('os.remove', 'os.rmdir', 'os.rename', 'os.chmod', 'os.mkdir', 'os.link', 'os.symlink'):
            raise PermissionError('Worker filesystem mutation disabled')
        if event in ('subprocess.Popen', 'os.system', 'os.fork', 'os.posix_spawn'):
            raise PermissionError('Worker subprocess execution disabled')
    sys.addaudithook(audit)


def calculate(connection, body, root, policy):
    fcfe_request = False
    try:
        restrict_runtime(root, policy.cpu_seconds)
        verify_bundle(root)
        from valuation_platform.valuation.case_inputs import run_case
        _, doc = read_http_document(body)
        fcfe_request = type(doc) is dict and doc.get('schema_version') == 'fcfe-forecast-request-v1'
        apple_request = type(doc) is dict and doc.get('schema_version') == 'apple-analyst-request-v1'
        company_request = type(doc) is dict and doc.get('schema_version') == 'company-analyst-request-v1'
        fcfe_request = fcfe_request or apple_request or company_request
        if company_request:
            from valuation_platform.review.company_analyst import run_company_analyst
            result = run_company_analyst(read_http_company_analyst(body), Path(root))
        elif apple_request:
            from valuation_platform.review.apple_analyst import run_apple_analyst
            result = run_apple_analyst(read_http_apple_analyst(body), Path(root))
        elif fcfe_request:
            from valuation_platform.valuation.fcfe import run_fcfe
            result = run_fcfe(read_http_fcfe(body), Path(root))
        elif type(doc) is dict and doc.get('schema_version') == 'internal-investor-review-v1':
            from valuation_platform.review.comparison import run_review
            from valuation_platform.review.sources import MarketOpening
            from valuation_platform.valuation.case_inputs import read_case
            import json
            result = run_review(read_case(json.dumps(doc['case'])),Path(root),MarketOpening.from_dict(doc['market']) if doc['market'] else None,doc['unavailable'])
        elif type(doc) is dict and doc.get('schema_version') in ('analyst-scenario-set-v1', 'investor-scenario-set-v1', 'investor-scenario-set-v2', 'investor-scenario-set-v3'):
            from valuation_platform.valuation.scenario_inputs import run_scenario_set
            result = run_scenario_set(read_http_scenarios(body), Path(root))
        elif type(doc) is dict and doc.get('schema_version') in ('analyst-sensitivity-request-v1', 'investor-sensitivity-request-v1', 'investor-sensitivity-request-v2', 'investor-sensitivity-request-v3'):
            from valuation_platform.valuation.sensitivity_inputs import run_sensitivity
            result = run_sensitivity(read_http_sensitivity(body), Path(root))
        elif type(doc) is dict and doc.get('schema_version') in ('analyst-reverse-dcf-request-v1', 'investor-reverse-dcf-request-v1', 'investor-reverse-dcf-request-v2'):
            from valuation_platform.valuation.reverse_inputs import run_reverse
            result = run_reverse(read_http_reverse(body), Path(root))
        else:
            result = run_case(read_http_case(body), Path(root))
        payload = encode_bounded(result, policy.max_response_bytes)
        message = b'200 ' + payload
    except BudgetError:
        message = b'422 ' + encode_bounded(error_body('response_budget', 'Result exceeds HTTP execution budget.'), 8192)
    except Exception as exc:
        # Includes retained integrity/arithmetic failures. No source path, traceback,
        # submitted body or exception text crosses this boundary.
        message = b'500 ' + encode_bounded(error_body('calculation_failed', 'Calculation failed; no result returned.'), 8192)
        if fcfe_request:
            from valuation_platform.valuation.case_inputs import CaseInputError
            if isinstance(exc, CaseInputError):
                message = b'422 ' + encode_bounded(error_body('invalid_case', 'FCFE input validation failed.', exc.errors), 8192)
    try:
        connection.send_bytes(message)
    except (BrokenPipeError, EOFError, OSError):
        pass
    finally:
        connection.close()
