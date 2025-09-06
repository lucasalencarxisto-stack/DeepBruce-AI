# 🚀 OQS_step2 — Dockerized Flask API (Ollama + OpenAI)

A **Dockerized Flask Chat API** with support for both **Ollama (local, free)** and **OpenAI API (remote, paid)**.  
Designed to run anywhere and serve as a base for AI integrations in portfolio or production projects.

---

## ✨ Features
- 🌐 REST API in **Flask**
- 📦 Deploy with **Docker + Compose**
- 🔀 Multi-provider support:
  - **Ollama** → local models (`llama3.2:3b`, etc.)
  - **OpenAI** → GPT-4o, GPT-4o-mini, etc.
- ⚡ OpenAI-compatible endpoints
- 🛡️ Configurable via `.env`
- 🔍 Built-in healthcheck and status

---

## 🛠️ Quickstart

### 1. Clone repository
```bash
git clone https://github.com/YOUR-USERNAME/oqs_step2.git
cd oqs_step2


2. Create .env
cp .env.example .env

Edit to choose PROVIDER= Ollama (defeaut) or OpenAI 

3. Start with Docker Compose
docker compose up -d --build

4. Test health
Se você usar apenas `docker-compose.yml` (sem override):
  - `curl http://localhost:8000/health`

Se você usar também `docker-compose.override.yml` (padrão para dev):
  - `curl http://localhost:9101/health`

Main Endpoints
. Configurations 
GET /config

. Health
GET /health

. Avaliable Models
GET /models

. chat
POST /chat
{ "message": "Olá, mundo!" }

. OpenAI-Compatible
POST /v1/chat/completions
POST /v1/models

🧪 Quickly test — Ollama (default)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá em 3 idiomas"}'

Se estiver usando o override, troque a porta para 9101.

🧪 Quickly test — OpenAI (if you have a key)
1) Edite seu `.env`:
```
PROVIDER=openai
OPENAI_API_KEY=sk-xxxx
OPENAI_MODEL=gpt-4o-mini
```
2) Suba/atualize os serviços:
```
docker compose up -d --build
```
3) Chame o endpoint (use 8000 ou 9101, conforme sua escolha de compose):
```
curl -X POST http://localhost:9101/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá do OpenAI"}'
```

💡 Dica: `tester` roda o `test_ai.py` (para Ollama por padrão). Para usar OpenAI, garanta `PROVIDER=openai` e `OPENAI_API_KEY` no `.env` e rode: `docker compose run --rm tester`.

🗂️ Project Structure

.
├─ app/
│  ├─ __init__.py       # Flask API mainly
│  ├─ ollama_client.py  # Client Ollama
│  └─ static/           # Frontend static (is there is one)
├─ test_ai.py           # Test Script (Ollama/OpenAI)
├─ Dockerfile
├─ docker-compose.yml
├─ docker-compose.override.yml
├─ .env.example
├─ LICENSE
└─ docs/
   └─ LICENSE.md

📖 License

Distributed under the MIT License.

Multilingual explanations at docs/LICENSE.md.

📛 Badges

---

👉 This way, you can **delete/rename** the other READMEs and leave only this main `README.md`.
Do you want me to also prepare a **shorter English version** (for the main, more "global" GitHub) and leave this one in Portuguese inside `docs/README.pt-BR.md`?

## 🔁 Trocar de Provider (Ollama ↔ OpenAI)

- Por padrão, o projeto usa `PROVIDER=ollama` (grátis, local) e conversa com o serviço `ollama` do docker-compose.
- Para usar OpenAI, edite seu `.env` e defina:
  - `PROVIDER=openai`
  - `OPENAI_API_KEY=...`
  - Opcional: `OPENAI_MODEL=gpt-4o-mini` (ou outro)
- Reinicie com `docker compose up -d --build`.

## 🌐 Portas (dev vs compose simples)

- Somente `docker-compose.yml`: API exposta em `http://localhost:8000`.
- Com `docker-compose.override.yml`: API exposta em `http://localhost:9101` (mapeada para a porta interna 8000).
# 🚀 OQS_step2 — Dockerized Flask Chat API (Ollama + OpenAI)

Minimal, production‑ready Flask API for chat with both local Ollama models and OpenAI. Ships with a simple web UI, OpenAI‑compatible endpoints, and Docker Compose.

---

## ✨ Features
- REST API with Flask + Gunicorn
- Providers: Ollama (local, free) and OpenAI (remote, paid)
- OpenAI‑compatible routes (models, chat)
- Streaming over line‑delimited chunks with heartbeats
- Configured via `.env`; ready‑to‑run with Docker Compose

---

## 🛠️ Quickstart

1) Copy env and adjust as needed
```
cp .env.example .env
```

2) Start (plain compose)
```
docker compose up -d --build
```
API: http://localhost:8000

Optional (dev override: maps static UI and healthchecks)
```
docker compose -f docker-compose.yml -f docker-compose.override.yml up -d --build
```
API: http://localhost:9101

3) Health
```
curl http://localhost:8000/health   # or :9101 if using override
```

---

## 🔁 Switch Providers (Ollama ↔ OpenAI)

Default is Ollama (local, free). To use OpenAI, set in `.env`:
```
PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```
Rebuild/restart:
```
docker compose up -d --build
```

---

## 🟡 Dev vs 🟢 Prod (Compose)

- Dev (with `docker-compose.override.yml`):
  - `depends_on: service_started` for the API → UI becomes available fast even if Ollama is still warming up.
  - Ollama healthcheck is tolerant (`start_period: 90s`, many retries). While Ollama is not ready, some calls may return a "degraded" fallback.
- Prod (base `docker-compose.yml` only):
  - `depends_on: service_healthy` → API starts only after Ollama passes healthcheck.
  - More predictable start at the cost of a slower first boot.

Tune these values to your infra (CPU/IO of the host) if needed.

---

## 🔌 Endpoints
- GET `/health`: service info + Ollama availability (if enabled)
- GET `/config`: current model, ctx, predict
- GET `/models`: provider models (Ollama tags)
- POST `/chat`: body `{ message, stream? }` (supports streaming)
- OpenAI‑compatible: `POST /v1/chat/completions`, `GET /v1/models`

Quick test (Ollama default):
```
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá em 3 idiomas"}'
```
Using override, replace port with 9101.

Tester (runs `test_ai.py`):
```
docker compose run --rm tester
```

---

## 🗂️ Structure
```
.
├─ app/
│  ├─ __init__.py        # main Flask API
│  ├─ app/ollama_client.py# Ollama client (list/chat/stream)
│  ├─ openai_proxy.py     # aux app (simple OpenAI/Ollama chat)
│  └─ static/             # static assets for UI
├─ templates/index.html   # simple chat UI
├─ test_ai.py             # quick smoke test
├─ Dockerfile
├─ docker-compose*.yml
└─ .env(.example)
```

---

## 🧾 License
MIT. See `LICENSE`.

Language variants available (e.g., `README.pt.md`, `README.es.md`, `README.zh.md`).
