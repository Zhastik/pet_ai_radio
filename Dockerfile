FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/var/cache/ai-radio

WORKDIR /srv/ai-radio

COPY requirements.txt requirements-music.txt ./
RUN python -m pip install --no-cache-dir \
        --index-url https://download.pytorch.org/whl/cpu "torch>=2.6,<3" \
    && python -m pip install --no-cache-dir -r requirements-music.txt \
    && python -m pip check

RUN groupadd --gid 10001 radio \
    && useradd --uid 10001 --gid radio --create-home radio \
    && install -d -o radio -g radio "$HF_HOME"

COPY app/ ./app/
USER radio
EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3).close()"]

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--timeout-graceful-shutdown", "20"]
