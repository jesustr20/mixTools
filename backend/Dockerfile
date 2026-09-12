FROM python:3.12-slim

# LibreOffice + Ghostscript — mismas dependencias de sistema que usa el CI
# (ver .github/workflows/ci.yml)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

# uv (Astral) para instalar dependencias de Python
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

COPY app ./app

# Render inyecta $PORT en runtime — no hardcodear 8000
ENV PORT=8000
EXPOSE 8000

# --workers 1 es OBLIGATORIO: el semáforo de concurrencia de LibreOffice
# (#35/#36) vive en memoria de un solo proceso. Con más de 1 worker, cada
# uno tendría su propio semáforo y el límite de 3 dejaría de cumplirse
# de verdad (3 × N workers, no 3 en total).
CMD ["sh", "-c", "uv run --no-sync uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1"]
