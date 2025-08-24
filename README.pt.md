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

Chatbot Flask com SSE e OpenAI
Este projeto é uma aplicação simples baseada no Flask, utilizando o modelo GPT da OpenAI. Ele suporta Server-Sent Events (SSE) para respostas em tempo real e gerenciamento de sessões.

Como Configurar o .env
1. Crie um arquivo .env no diretório raiz do projeto.
2. Adicione as seguintes variáveis no arquivo .env:
OPENAI_API_KEY=sua_chave_api_openai
OPENAI_MODEL=gpt-4o-mini
OPENAI_SUMMARY_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=800

Como Rodar Localmente
1. Instale as dependências:
pip install -r requirements.txt
2. Certifique-se de que o ambiente virtual esteja ativado:source venv/bin/activate  # No Linux/macOS
Rode o aplicativo Flask:
.\venv\Scripts\activate  # No Windows
source venv/bin/activate  # No Linux/macOS
3. Rode o aplicativo Flask:
python app.py
4. Acesse o aplicativo em http://127.0.0.1:5000/ no seu navegador.

Como Rodar em Produção
1. Defina debug=False em app.py.
2. Utilize um servidor WSGI como o gunicorn ou uvicorn:
gunicorn app:app

Principais Rotas e Funcionalidades
/status: Rota de verificação de saúde que retorna {"status": "ok"}.

/: Interface principal de chat renderizada em HTML.

/chat: Rota POST que recebe uma mensagem do usuário e a armazena no histórico da sessão.

/stream: Rota GET que transmite as respostas do chatbot em tempo real usando SSE.

/stream2: Rota POST que transmite as respostas do chatbot em tempo real usando um único endpoint.

Exemplos de Requisições
1. Verificação de Saúde
curl http://127.0.0.1:5000/status
Resposta esperada:
{
  "status": "ok"
}
2. Enviar Mensagem para o Chat
curl -X POST http://127.0.0.1:5000/chat -H "Content-Type: application/json" -d '{"message": "Olá, chatbot!"}'
3. Resposta via Stream
curl http://127.0.0.1:5000/stream
4. Endpoint Único de Stream
curl -X POST http://127.0.0.1:5000/stream2 -H "Content-Type: application/json" -d '{"message": "Me conte uma piada"}'

FAQ e Resolução de Problemas
P: Como configuro corretamente o arquivo .env?
R: Certifique-se de adicionar sua chave API da OpenAI e outras variáveis, como OPENAI_MODEL e OPENAI_TEMPERATURE, ao arquivo .env conforme mostrado acima.

P: Como posso rodar o Flask em produção?
R: Use um servidor WSGI como gunicorn para produção e defina debug=False em app.py.

Próximos Passos:
Contribuindo: Se quiser contribuir, sinta-se à vontade para fazer um fork e criar uma pull request!

Resolução de Problemas: Verifique a seção de FAQ acima se encontrar algum problema.
---

## 👨‍💻 Autor

Lucas Alencar  
Estudante de ADS, desenvolvedor iniciante mobile-first, apaixonado por Python, IA e tecnologias transformadoras.  
GitHub: https://github.com/lucasalencarxisto-stack
