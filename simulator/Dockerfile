FROM python:3.11-slim@sha256:e41613d42d4891e4930f79523f93f81bbc7632584ec65e36ab055f41a800b41e

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SIMULATOR_DATABASE=/data/exams.sqlite3

WORKDIR /app
COPY requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock \
    && groupadd --gid 10001 simulator \
    && useradd --uid 10001 --gid simulator --no-create-home simulator \
    && mkdir /data \
    && chown simulator:simulator /data
COPY app.py ./
COPY data ./data
COPY static ./static
COPY templates ./templates

USER simulator
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=3)"
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--worker-tmp-dir", "/tmp", "--control-socket", "/tmp/gunicorn.ctl", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
