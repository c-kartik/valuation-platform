# Local image candidate only; Linux execution and image digest remain unverified.
ARG PYTHON_IMAGE=python:3.12.15-slim-bookworm
FROM ${PYTHON_IMAGE} AS dependencies
COPY requirements-api.lock /tmp/requirements-api.lock
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --only-binary=:all: -r /tmp/requirements-api.lock \
    && /opt/venv/bin/pip check

FROM ${PYTHON_IMAGE}
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/runtime/src \
    VALUATION_APP_ROOT=/opt/runtime \
    PORT=8080
COPY --from=dependencies /opt/venv /opt/venv
COPY runtime/ /opt/runtime/
COPY start.py /opt/start.py
# Verify using the same packaged code/resources before accepting the build.
RUN python -c "from valuation_platform.api.bundle import verify_bundle; verify_bundle('/opt/runtime')" \
    && chmod -R a-w /opt/runtime /opt/venv /opt/start.py
USER 10001:10001
WORKDIR /opt/runtime
EXPOSE 8080
STOPSIGNAL SIGTERM
ENTRYPOINT ["/opt/venv/bin/python", "/opt/start.py"]
