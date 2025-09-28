# API independente — sem LLMs externos
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
  && rm -rf /var/lib/apt/lists/*
  
COPY . /app
EXPOSE 5001
ENV PORT=5001
CMD ["python", "app.py"]

