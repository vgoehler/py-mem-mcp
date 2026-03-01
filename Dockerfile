FROM python:3.12-slim AS runtime

WORKDIR /app

RUN pip install --no-cache-dir poetry==2.3.2

COPY pyproject.toml poetry.lock* README.md ./
COPY src ./src

RUN poetry config virtualenvs.in-project true && \
    poetry install

ENV PATH="/app/.venv/bin:$PATH"

RUN addgroup --system app && adduser --system --ingroup app app
USER app

EXPOSE 3000

ENTRYPOINT ["python", "-m", "py_mem_mcp.server"]
