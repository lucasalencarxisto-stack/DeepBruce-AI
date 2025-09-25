# DeepBruce AI

DeepBruce AI is a prototype assistant with a simple, self-hosted API and a lightweight RAG pipeline that pulls fresh context directly from Wikipedia.  
The whole stack is Dockerized and can be lifted to any cloud (IaaS or PaaS) to support deeper Deep Learning / LLM development and experimentation.

## Highlights
- 🔌 Self-hosted API (Flask) with SSE streaming
- 🧠 Local inference via Ollama (model-agnostic)
- 📚 Lightweight RAG: fetch + chunk + prompt-inject from Wikipedia
- 🐳 Fully containerized (Docker / Compose), cloud-ready
- ⚙️ Tunable prompts & hyper-params via `.env`
