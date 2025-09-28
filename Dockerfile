FROM python:3.12-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc libffi-dev libssl-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt ./
RUN pip wheel --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends libffi8 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels /wheels/*
COPY . /app
EXPOSE 8000
ENV FLASK_APP=wsgi.py FLASK_ENV=production OQS_NAMESPACE=default PROVIDER=extractive OLLAMA_HOST=http://127.0.0.1:11434 OLLAMA_MODEL=tinyllama
CMD ["gunicorn","wsgi:app","--bind","0.0.0.0:8000","--worker-class","gevent","--workers","2","--timeout","120"]
