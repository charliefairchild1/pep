FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Install dependencies first (without the local project) — for layer caching
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --no-dev --no-install-project

# Copy app code. `data/` is created at runtime by SQLite (gitignored).
# `dist/` holds hand-authored HTML for the demos.
COPY src ./src
COPY dist ./dist
RUN mkdir -p data

# Now install the local project itself (src/ is present)
RUN uv sync --no-dev

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["sh", "-c", "uv run uvicorn pep.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
