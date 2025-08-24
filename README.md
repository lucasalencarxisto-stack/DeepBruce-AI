# OQS_step2  Dockerized Flask API

## Quickstart
docker build -t oqs_step2:latest .
docker run --name oqs_step2 -p 8000:8000 oqs_step2:latest

Open: http://localhost:8000/
Health: http://localhost:8000/status

## With Docker Compose
docker compose up --build

## Test Endpoints
curl http://localhost:8000/
curl http://localhost:8000/status
curl -X POST http://localhost:8000/echo -H "Content-Type: application/json" -d '{"hello":"world"}'
