![CI](https://github.com/lucasalencarxisto-stack/DeepBruce-AI/actions/workflows/ci.yml/badge.svg)

# DeepBruce-AI

> Independent project, **not affiliated** with OpenAI.  
> Portions of this project were inspired by the OpenAI Quickstart (MIT). See `THIRD_PARTY_NOTICES.md`.

A prototype assistant with a self-hosted **Flask** API, **SSE** streaming, optional **local inference via Ollama**, and a lightweight **RAG** path that can fetch and inject context from Wikipedia. The stack is fully **Dockerized** and cloud-ready (IaaS/PaaS).

## Highlights
- 🔌 Self-hosted API (Flask) with **Server-Sent Events (SSE)**
- 🧠 **Ollama** support (model-agnostic, local inference)
- 📚 Lightweight **RAG**: fetch → chunk → inject (Wikipedia)
- 🐳 **Docker/Compose** end-to-end
- ⚙️ Tunable prompts & hyper-parameters via `.env`

---

## Quickstart (Python)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -

