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

## 👨‍💻 作者

Lucas Alencar  
ADS 学生，移动优先初级开发者，热衷于 Python、人工智能和变革性技术。  
GitHub: https://github.com/lucasalencarxisto-stack
