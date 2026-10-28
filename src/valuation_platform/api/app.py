"""Local-only FastAPI single-case boundary; no financial schema reimplementation."""

import asyncio
from contextlib import asynccontextmanager
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from starlette.requests import ClientDisconnect

from .budget import DEFAULT_POLICY, BudgetError, error_body, read_http_case, read_http_scenarios
from .bundle import verify_bundle
from .process import Calculator, ExecutionError
from .worker import calculate
from .catalog import build_catalog


class SanitizedErrors:
    """Bound disclosure/caching and cheaply reject known cross-site browsers.

    Fetch Metadata is a browser courtesy barrier, not caller authentication or
    a bot quota: non-browser clients can omit/spoof it and remain anonymous.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        started = False

        async def tracked_send(message):
            nonlocal started
            if message['type'] == 'http.response.start':
                started = True
                message = dict(message)
                headers = [(key, value) for key, value in message.get('headers', [])
                           if key.lower() not in (b'cache-control', b'x-content-type-options')]
                message['headers'] = headers + [(b'cache-control', b'no-store'),
                                                (b'x-content-type-options', b'nosniff')]
            await send(message)

        try:
            if scope['type'] == 'http' and any(
                    key.lower() == b'sec-fetch-site' and value.strip().lower() == b'cross-site'
                    for key, value in scope.get('headers', [])):
                response = JSONResponse(error_body('cross_site_request', 'Cross-site browser requests are not accepted.'), status_code=403)
                await response(scope, receive, tracked_send)
                return
            await self.app(scope, receive, tracked_send)
        except Exception:
            if scope['type'] != 'http':
                raise
            if not started:
                response = JSONResponse(error_body('internal_error', 'Internal service error; no result returned.'), status_code=500)
                await response(scope, receive, tracked_send)


async def body_bytes(request, policy):
    content_type = [part.strip() for part in request.headers.get('content-type', '').lower().split(';')]
    if len(request.headers.getlist('content-type')) != 1 or content_type not in (['application/json'], ['application/json', 'charset=utf-8']):
        raise ExecutionError(415, 'unsupported_representation', 'Use application/json with UTF-8.')
    if request.headers.get('content-encoding', 'identity').lower() != 'identity':
        raise ExecutionError(415, 'unsupported_representation', 'Content encodings are not supported.')
    sizes = request.headers.getlist('content-length')
    if len(sizes) > 1 or sizes and (not sizes[0].isascii() or not sizes[0].isdigit() or len(sizes[0]) > 12):
        raise ExecutionError(422, 'invalid_length', 'Invalid Content-Length.')
    if sizes and int(sizes[0]) > policy.max_body_bytes:
        raise ExecutionError(413, 'request_too_large', 'Request body exceeds HTTP byte budget.')
    body = bytearray()
    try:
        async with asyncio.timeout(policy.body_seconds):
            async for chunk in request.stream():
                if len(body) + len(chunk) > policy.max_body_bytes:
                    raise ExecutionError(413, 'request_too_large', 'Request body exceeds HTTP byte budget.')
                body.extend(chunk)
    except TimeoutError as exc:
        raise ExecutionError(408, 'body_timeout', 'Request body deadline exceeded.') from exc
    except ClientDisconnect as exc:
        raise ExecutionError(499, 'client_disconnected', 'Client disconnected while submitting input.') from exc
    if sizes and int(sizes[0]) != len(body):
        raise ExecutionError(422, 'invalid_length', 'Content-Length does not match body.')
    return bytes(body)


def create_app(root=None, *, policy=DEFAULT_POLICY, worker_target=calculate, worker_args=()):
    """Trusted server configuration only; none of these arguments are HTTP fields."""
    if root is None:
        value = os.environ.get('VALUATION_APP_ROOT')
        if not value:
            raise ValueError('VALUATION_APP_ROOT must name a verified private bundle')
        root = Path(value)
    root = Path(root).resolve()

    @asynccontextmanager
    async def lifespan(app):
        try:
            verify_bundle(root)
            # Imports may read the four pinned registries, once at startup.
            from valuation_platform.valuation.case_inputs import read_case
            assert callable(read_case)
            app.state.catalog = build_catalog(root)
        except Exception:
            raise RuntimeError('Private runtime bundle failed readiness checks') from None
        app.state.calculator = Calculator(root, policy, worker_target, worker_args)
        app.state.ready = True
        try:
            yield
        finally:
            app.state.ready = False
            await app.state.calculator.close()

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(SanitizedErrors)
    app.state.ready = False

    @app.exception_handler(ExecutionError)
    async def execution_error(request, exc):
        headers = {'Retry-After': '1'} if exc.status == 503 else {}
        return JSONResponse(error_body(exc.code, exc.message), status_code=exc.status, headers=headers)

    @app.get('/health')
    async def health():
        return JSONResponse({'status': 'ready' if app.state.ready else 'not_ready'}, status_code=200 if app.state.ready else 503)

    @app.get('/api/v1/catalog')
    async def catalog(request: Request):
        if request.query_params:
            raise ExecutionError(422, 'invalid_case', 'Query parameters are not accepted.')
        if not app.state.ready:
            raise ExecutionError(503, 'not_ready', 'Service is not ready.')
        return Response(app.state.catalog, media_type='application/json', headers={'Cache-Control': 'no-store'})

    async def intake(request, reader=None):
        if request.query_params:
            raise ExecutionError(422, 'invalid_case', 'Query parameters are not accepted.')
        if not app.state.ready:
            raise ExecutionError(503, 'not_ready', 'Service is not ready.')
        body = await body_bytes(request, policy)
        try:
            case = (reader or read_http_case)(body)
        except (ValueError, RecursionError) as exc:
            errors = getattr(exc, 'errors', (str(exc),))
            # Only parser/model diagnostics; never internal worker exceptions.
            return body, None, JSONResponse(error_body('invalid_case', 'Case validation failed.', errors), status_code=422)
        except (TypeError, KeyError, AttributeError):
            return body, None, JSONResponse(error_body('invalid_case', 'Invalid case structure.'), status_code=422)
        return body, case, None

    @app.post('/api/v1/cases/validate')
    async def validate(request: Request):
        body, case, failure = await intake(request)
        if failure is not None:
            return failure
        return {'status': 'valid', 'calculation_performed': False,
                'calculation_scope': 'EQUITY_PER_SHARE' if case.bridge else 'ENTERPRISE_VALUE',
                'semantic_input_review': 'NOT_ASSESSED_BY_CALCULATOR'}

    @app.post('/api/v1/cases/run')
    async def run(request: Request):
        if app.state.ready and app.state.calculator.job is not None:
            raise ExecutionError(503, 'busy', 'One calculation is already running; retry later.')
        body, case, failure = await intake(request)
        if failure is not None:
            return failure

        async def disconnected():
            while True:
                if (await request.receive())['type'] == 'http.disconnect':
                    return

        status, payload = await app.state.calculator.run(body, disconnected)
        return Response(payload, status_code=status, media_type='application/json', headers={'Cache-Control': 'no-store'})

    @app.post('/api/v1/scenarios/validate')
    async def validate_scenarios(request: Request):
        body, scenarios, failure = await intake(request, read_http_scenarios)
        if failure is not None:
            return failure
        return {'status': 'valid', 'calculation_performed': False,
                'calculation_scope': 'EQUITY_PER_SHARE' if scenarios.scenarios[0].case.bridge else 'ENTERPRISE_VALUE',
                'semantic_input_review': 'NOT_ASSESSED_BY_CALCULATOR'}

    @app.post('/api/v1/scenarios/run')
    async def run_scenarios(request: Request):
        if app.state.ready and app.state.calculator.job is not None:
            raise ExecutionError(503, 'busy', 'One calculation is already running; retry later.')
        body, scenarios, failure = await intake(request, read_http_scenarios)
        if failure is not None:
            return failure

        async def disconnected():
            while True:
                if (await request.receive())['type'] == 'http.disconnect':
                    return

        status, payload = await app.state.calculator.run(body, disconnected)
        return Response(payload, status_code=status, media_type='application/json', headers={'Cache-Control': 'no-store'})

    return app
