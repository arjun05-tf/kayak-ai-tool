# ── Build stage ───────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime
WORKDIR /app

# Non-root user for security
RUN addgroup --system app && adduser --system --ingroup app app

COPY --from=builder /install /usr/local
COPY . .

# Give the app user write access (needed for latest_promo.png and history.json)
RUN chown -R app:app /app

ENV GROQ_API_KEY=""
ENV LOG_LEVEL="INFO"
ENV PORT=8000

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
