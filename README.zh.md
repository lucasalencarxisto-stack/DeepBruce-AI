# 🧠 OpenAI 快速启动项目 (Flask + API)

该项目是一个使用 Flask 和 OpenAI API 构建的简单 Web 应用程序。它允许用户提交提示，并接收由 AI 生成的响应。

<!-- Badges -->
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)

---

## 📋 目录

- [关于](#关于)  
- [初始设置](#初始设置)  
- [当前功能](#当前功能)  
- [贡献](#贡献)  
- [作者](#作者)  

---

## 关于

该项目是一个使用 Flask 和 OpenAI API 构建的简单 Web 应用程序。它允许用户提交提示，并接收由 AI 生成的响应。

---

## 贡献

欢迎贡献！贡献步骤如下：

1. Fork 本仓库  
2. 创建功能分支 (`git checkout -b feature-name`)  
3. 提交你的更改 (`git commit -m '添加功能'`)  
4. 推送到分支 (`git push origin feature-name`)  
5. 提交 Pull Request  

请遵循现有代码风格，并撰写清晰的提交信息。

---

## 🛠️ 初始设置

以下是我手动配置环境所遵循的所有步骤。这展示了对基本 Web 开发工具和 AI 集成的掌握。

1. 克隆仓库

git clone https://github.com/your-username/openai-quickstart-01.git
cd openai-quickstart-01

2. 创建并激活虚拟环境  
Windows:  
python -m venv venv  
venv\Scripts\activate  

Linux/Mac:  
python3 -m venv venv  
source venv/bin/activate  

3. 安装依赖项  
pip install -r requirements.txt  

如果没有 requirements.txt 文件，可以使用以下命令创建：  
pip freeze > requirements.txt  

确保其中至少包含：  
flask  
openai  
python-dotenv  

4. 配置 OpenAI API 密钥  
创建一个 .env 文件，内容如下：  
OPENAI_API_KEY=你的-api-密钥  

重要提示：使用 .gitignore 避免将密钥上传到 GitHub。

5. 预期的基本目录结构  
openai-quickstart-01/  
├── app.py  
├── .env  
├── requirements.txt  
├── README.md  
├── templates/  
│   └── index.html  
├── static/  
│   └── css/  
│       └── style.css  

6. 本地运行应用  
flask run  

在浏览器打开： http://127.0.0.1:5000

---

## 📌 当前功能

- 具有提示提交表单的 Web 界面  
- 与 OpenAI API 集成  
- 基础错误处理  
- 用户输入长度限制  
- 简单的前端 CSS 样式  

---

基于 Flask 和 SSE 的 OpenAI 聊天机器人
该项目是一个基于 Flask 的简单聊天机器人应用，使用 OpenAI 的 GPT 模型。它支持 Server-Sent Events (SSE)，用于实时响应和会话管理。

如何配置 .env
1. 在项目的根目录创建一个 .env 文件。
2. 将以下变量添加到 .env 文件中：
OPENAI_API_KEY=你的_openai_api_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_SUMMARY_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=800

如何本地运行
1. 安装依赖：
pip install -r requirements.txt
2. 确保已激活虚拟环境：
.\venv\Scripts\activate  # 在 Windows 上
source venv/bin/activate  # 在 Linux/macOS 上
3. 运行 Flask 应用：
python app.py
4. 通过浏览器访问 http://127.0.0.1:5000/。

如何在生产环境中运行
1. 在 app.py 中设置 debug=False。
2. 使用 WSGI 服务器如 gunicorn 或 uvicorn：
gunicorn app:app

主要路由和功能
/status: 健康检查路由，返回 {"status": "ok"}。

/: 主聊天界面，以 HTML 渲染。

/chat: 接收用户消息并将其存储在会话历史中的 POST 路由。

/stream: 使用 SSE 实时流式传输聊天机器人响应的 GET 路由。

/stream2: 使用单一端点实时流式传输聊天机器人响应的 POST 路由。

## 示例请求
1. 健康检查**
```bash
curl http://127.0.0.1:5000/status
期望的响应:
{
  "status": "ok"
}
2. 发送消息到聊天
curl -X POST http://127.0.0.1:5000/chat -H "Content-Type: application/json" -d '{"message": "你好，聊天机器人！"}'
3. 使用 Stream 获取实时响应
curl http://127.0.0.1:5000/stream
4. 使用单一端点的 Stream
curl -X POST http://127.0.0.1:5000/stream2 -H "Content-Type: application/json" -d '{"message": "讲个笑话"}'


---

## 👨‍💻 作者

Lucas Alencar  
ADS 学生，移动优先初级开发者，热衷于 Python、人工智能和变革性技术。  
GitHub: https://github.com/lucasalencarxisto-stack
