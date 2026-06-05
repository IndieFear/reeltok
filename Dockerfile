FROM python:3.12-slim-bookworm

WORKDIR /app

# Dépendances système minimales pour Playwright Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Chromium + libs système (overlay HTML → image)
RUN playwright install --with-deps chromium

COPY . .

# Données persistantes (monter un volume Railway sur /app/data)
RUN mkdir -p /app/data

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]
