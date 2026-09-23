![CI](https://github.com/lucasalencarxisto-stack/DeepBruce-AI/actions/workflows/ci.yml/badge.svg)

# DeepBruce-AI

> Projeto independente, sem afiliacao com a OpenAI.

O DeepBruce e um assistente local com API Flask, streaming SSE, inferencia opcional via Ollama e um pipeline RAG baseado em fontes da Wikipedia. A interface React fica em `frontend/`.

## Requisitos

- Python 3.12+
- Node.js 22+
- Ollama para respostas locais
- Docker e Docker Compose, opcionalmente

## Setup Python

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

No Windows, ative o ambiente com `.venv\\Scripts\\activate`.

## Configuracao `.env`

Crie um arquivo `.env` na raiz:

```dotenv
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=gemma3:1b
OLLAMA_CONNECT_TIMEOUT=5
OLLAMA_READ_TIMEOUT=300
PORT=8000
OQS_NAMESPACE=default
CORS_ORIGINS=http://localhost:5173
MAX_MESSAGE_LENGTH=4000
```

`MAX_MESSAGE_LENGTH` limita o tamanho recebido pelas APIs de chat. Autenticacao obrigatoria nao faz parte da v1.5.

## Ollama

Instale o Ollama, inicie o servico e baixe o modelo configurado:

```bash
ollama serve
ollama pull gemma3:1b
```

Depois, inicie a API:

```bash
python wsgi.py
```

A API fica em `http://localhost:8000`.

## Frontend React

```bash
cd frontend
npm ci
npm run dev
```

O Vite normalmente fica em `http://localhost:5173` e encaminha as chamadas `/api` para a API conforme `vite.config.js`.

Comandos disponiveis:

```bash
npm run lint
npm run build
```

## Testes

Na raiz do projeto:

```bash
python -m pytest -q
```

Os testes cobrem roteamento, conversas, entidades, RAG, streaming SSE e servicos externos com mocks.

## Docker

A imagem principal instala `requirements-rag.txt`, que inclui `requirements.txt` via `-r`:

```bash
docker compose --profile dev up --build
```

O Compose tambem sobe o servico Ollama. Para uso local, configure o modelo e as variaveis no `.env`.

## Arquitetura v1.5

```text
React/Vite
	|
Flask + SSE
	|
Message Router
	|-- Chat --------> Ollama
	|-- Research ----> Entity Resolver -> Wikipedia -> RAG -> Ollama
	`-- Ambiguous ---> Clarification Flow
```

O `ConversationManager` da v1.5 mantem o estado em memoria. Por isso, a imagem usa um worker Gunicorn. Persistencia compartilhada e Redis ficam planejados para a v2.

## V2 Vision

`V2 Vision` e uma tela de roadmap/concept. Ela apresenta ideias futuras como voz natural, avatar, SLM, memoria persistente e cliente nativo; essas funcionalidades nao fazem parte do fluxo principal atual.

