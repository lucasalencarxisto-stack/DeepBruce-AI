# 🧠 Projeto OpenAI Quickstart (Flask + API)

Este projeto é uma aplicação web simples construída com Flask e a API da OpenAI. Permite aos usuários enviar um prompt e receber uma resposta gerada pela IA.


<!-- Badges -->
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)

---

## 📋 Sumário

- [Sobre](#sobre)  
- [Configuração Inicial](#configuração-inicial)  
- [Funcionalidades Atuais](#funcionalidades-atuais)  
- [Contribuindo](#contribuindo)  
- [Autor](#autor)  

---

## Sobre

Este projeto é uma aplicação web simples construída com Flask e a API da OpenAI. Permite que usuários enviem prompts e recebam respostas geradas por IA.

---

## Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do repositório  
2. Crie sua branch de recurso (`git checkout -b minha-feature`)  
3. Faça commit das suas alterações (`git commit -m 'Adicionar feature'`)  
4. Faça push para a branch (`git push origin minha-feature`)  
5. Abra um Pull Request  

Por favor, siga o estilo de código existente e escreva mensagens de commit claras.

---

## 🛠️ Configuração Inicial

Abaixo estão todos os passos que segui manualmente para configurar o ambiente. Isso demonstra domínio das ferramentas essenciais para desenvolvimento web e integração com IA.

1. Clone o repositório

git clone https://github.com/your-username/openai-quickstart-01.git
cd openai-quickstart-01

2. Crie e ative o ambiente virtual  
Windows:  
python -m venv venv  
venv\Scripts\activate  

Linux/Mac:  
python3 -m venv venv  
source venv/bin/activate  

3. Instale as dependências  
pip install -r requirements.txt  

Se você não tiver um arquivo requirements.txt, crie-o com:  
pip freeze > requirements.txt  

Certifique-se que ele contenha pelo menos:  
flask  
openai  
python-dotenv  

4. Configure a chave da API OpenAI  
Crie um arquivo .env com o seguinte conteúdo:  
OPENAI_API_KEY=sua-chave-aqui  

Importante: use o .gitignore para nunca enviar sua chave ao GitHub.

5. Estrutura básica esperada  
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

6. Rode o app localmente  
flask run  

Abra seu navegador em: http://127.0.0.1:5000

---

## 📌 Funcionalidades Atuais

- Interface web com formulário para envio de prompt  
- Integração com API da OpenAI  
- Tratamento básico de erros  
- Limite no tamanho da entrada do usuário  
- Estilo CSS simples para o frontend  

---

## 👨‍💻 Autor

Lucas Alencar  
Estudante de ADS, desenvolvedor iniciante mobile-first, apaixonado por Python, IA e tecnologias transformadoras.  
GitHub: https://github.com/lucasalencarxisto-stack
