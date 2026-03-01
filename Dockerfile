# ---- build stage ----
FROM python:3.12-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir poetry==2.3.2

COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.in-project true && \
    poetry install --only main --no-root

# ---- runtime stage ----
FROM python:3.12-slim AS runtime

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"

COPY --from=builder /app/.venv ./.venv
COPY src ./src

RUN addgroup --system app && adduser --system --ingroup app app
USER app

EXPOSE 3000

ENTRYPOINT ["python", "-m", "py_mem_mcp.server"]
