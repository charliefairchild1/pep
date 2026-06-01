FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev || uv sync --no-dev

# Copy app code. `data/` is created at runtime by SQLite (gitignored).
# `dist/` holds hand-authored HTML for non-Lemma demos; copy if present.
COPY src ./src
COPY dist ./dist
RUN mkdir -p data

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["sh", "-c", "uv run uvicorn pep.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
