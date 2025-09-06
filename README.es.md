
---

## 🇪🇸 docs/README.es.md
```markdown
# 🚀 OQS_step2 — API Flask Dockerizada (Ollama + OpenAI)

Una **API de chat en Flask Dockerizada** con soporte para **Ollama (local, gratis)** y **OpenAI API (remoto, de pago)**.  
Diseñada para ejecutarse en cualquier entorno y servir como base para integraciones de IA en portafolio o proyectos de producción.

---

## ✨ Características
- 🌐 API REST en **Flask**
- 📦 Deploy con **Docker + Compose**
- 🔀 Soporte multiproveedor:
  - **Ollama** → modelos locales (`llama3.2:3b`, etc.)
  - **OpenAI** → GPT-4o, GPT-4o-mini, etc.
- ⚡ Endpoints compatibles con **OpenAI API**
- 🛡️ Configurable vía `.env`
- 🔍 Healthcheck y estado incorporados

---

## 🛠️ Quickstart

### 1. Clonar repositorio
```bash
git clone https://github.com/TU-USUARIO/oqs_step2.git
cd oqs_step2

2. Crear .env
cp .env.example .env
"Edite para elegir PROVIDER=ollama (predeterminado) o openai."

3. Levantar con Docker Compose
docker compose up -d --build

4. Probar salud
curl http://localhost:8000/health

⚙️ Endpoints principales
GET  /config
GET  /health
GET  /models
POST /chat               # { "message": "¡Hola, mundo!" }
POST /v1/chat/completions
GET  /v1/models

🧪 Pruebas rápidas
Ollama (predeterminado)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola en 3 idiomas"}'

OpenAI (si tienes clave)
export PROVIDER=openai
export OPENAI_API_KEY=sk-xxxx

docker compose run --rm tester

🗂️ Estructura del Proyecto
.
├─ app/
│  ├─ __init__.py       # API principal Flask
│  ├─ ollama_client.py  # Cliente Ollama
│  └─ static/           # Frontend (si existe)
├─ test_ai.py           # Script de prueba (Ollama/OpenAI)
├─ Dockerfile
├─ docker-compose.yml
├─ docker-compose.override.yml
├─ .env.example
├─ LICENSE
└─ docs/
   └─ LICENSE.md


📖 Licencia
Distribuido bajo la .
Explicaciones multilingües en .

