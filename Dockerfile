# ---------- Stage 1: base (shared by test + production) ----------
FROM python:3.13-slim AS base

LABEL maintainer="DevOps TA Demo" \
      version="1.0.0" \
      description="Bookshelf Flask app - CI/CD demonstration"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements FIRST so this layer is cached until requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code changes often, so it is copied AFTER the dependencies
COPY app.py config.py ./
COPY templates/ templates/

RUN useradd --create-home --uid 1000 appuser

# ---------- Stage 2: test (used by docker compose test-runner) ----------
FROM base AS test
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY tests/ tests/
USER appuser
CMD ["python", "-m", "pytest", "tests/", "-v"]

# ---------- Stage 3: production (default, last stage) ----------
FROM base AS production

# Set by the CI pipeline to the commit SHA
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}

USER appuser
EXPOSE 5000

# slim has no curl, so use Python for the health check
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health', timeout=2)" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
