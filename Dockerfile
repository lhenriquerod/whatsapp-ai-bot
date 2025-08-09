FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# dependências
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# código
COPY . .

# recomendações gunicorn
ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:${PORT:-5000} --workers=2 --threads=4 --timeout=60 --graceful-timeout=30 --max-requests=1000 --max-requests-jitter=100"

CMD ["gunicorn", "main:app"]
