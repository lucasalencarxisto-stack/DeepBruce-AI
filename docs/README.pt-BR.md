# 🚀 OQS_step2 — API Flask Dockerizada (Ollama + OpenAI)

Uma API de Chat em Flask Dockerizada com suporte a Ollama (local, grátis) e OpenAI API (remoto, pago). Projetada para rodar em qualquer ambiente e servir de base para integrações de IA em portfólio ou produção.

---

## ✨ Recursos
- API REST em Flask + Gunicorn
- Providers: Ollama (local, grátis) e OpenAI (remoto, pago)
- Endpoints compatíveis com OpenAI
- Streaming por linhas com heartbeats
- Configuração via `.env`; pronto para Docker Compose

---

## 🛠️ Quickstart

1) Copie o `.env` e ajuste conforme necessário
```
cp .env.example .env
```

2) Suba com Docker Compose (simples)
```
docker compose up -d --build
```
API: http://localhost:8000

Opcional (override de dev: mapeia UI estática e healthchecks)
```
docker compose -f docker-compose.yml -f docker-compose.override.yml up -d --build
```
API: http://localhost:9101

3) Health
```
curl http://localhost:8000/health   # ou :9101 se usar o override
```

---

## 🔁 Trocar Provider (Ollama ↔ OpenAI)

Por padrão, usamos Ollama (local, grátis). Para usar OpenAI, no `.env` defina:
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

## 🔌 Endpoints
- GET `/health`: info do serviço + disponibilidade do Ollama (se habilitado)
- GET `/config`: modelo atual, ctx, predict
- GET `/models`: modelos do provider (tags do Ollama)
- POST `/chat`: body `{ message, stream? }` (suporta streaming)
- OpenAI‑compatível: `POST /v1/chat/completions`, `GET /v1/models`

Teste rápido (Ollama padrão):
```
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá em 3 idiomas"}'
```
Com override, troque a porta para 9101.

Tester (roda `test_ai.py`):
```
docker compose run --rm tester
```

---

## 🗂️ Estrutura
```
.
├─ app/
│  ├─ __init__.py        # API Flask principal
│  ├─ app/ollama_client.py# Cliente Ollama (lista/chat/stream)
│  ├─ openai_proxy.py     # app auxiliar (chat simples OpenAI/Ollama)
│  └─ static/             # assets estáticos da UI
├─ templates/index.html   # UI simples de chat
├─ test_ai.py             # teste rápido
├─ Dockerfile
├─ docker-compose*.yml
└─ .env(.example)
```

---

## 🧾 Licença
MIT. Veja `LICENSE`.

