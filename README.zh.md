
---

## 🇨🇳 docs/README.zh.md
```markdown
# 🚀 OQS_step2 — Docker化 Flask API (Ollama + OpenAI)

一个 **Docker化的 Flask 聊天 API**，支持 **Ollama（本地，免费）** 和 **OpenAI API（远程，付费）**。  
旨在在任何环境中运行，并作为 AI 集成到作品集或生产项目的基础。

---

## ✨ 特性
- 🌐 基于 **Flask** 的 REST API
- 📦 使用 **Docker + Compose** 部署
- 🔀 多提供者支持:
  - **Ollama** → 本地模型 (`llama3.2:3b` 等)
  - **OpenAI** → GPT-4o, GPT-4o-mini 等
- ⚡ 与 **OpenAI API** 兼容的端点
- 🛡️ 通过 `.env` 配置
- 🔍 内置健康检查和状态

---

## 🛠️ 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/YOUR-USERNAME/oqs_step2.git
cd oqs_step2

2. 创建 .env
cp .env.example .env
编辑选择 PROVIDER=ollama（默认）或 openai

3. 使用 Docker Compose 启动
docker compose up -d --build

4. 测试健康状态
curl http://localhost:8000/health

⚙️ 主要端点
GET  /config
GET  /health
GET  /models
POST /chat               # { "message": "你好，世界！" }
POST /v1/chat/completions
GET  /v1/models

🧪 快速测试
Ollama (默认)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "用三种语言打招呼"}'

OpenAI (如果有密钥)
export PROVIDER=openai
export OPENAI_API_KEY=sk-xxxx

docker compose run --rm tester

🗂️ 项目结构
.
├─ app/
│  ├─ __init__.py       # Flask 主 API
│  ├─ ollama_client.py  # Ollama 客户端
│  └─ static/           # 前端（如果有）
├─ test_ai.py           # 测试脚本 (Ollama/OpenAI)
├─ Dockerfile
├─ docker-compose.yml
├─ docker-compose.override.yml
├─ .env.example
├─ LICENSE
└─ docs/
   └─ LICENSE.md

📖 许可证
根据  分发。
多语言说明见 。