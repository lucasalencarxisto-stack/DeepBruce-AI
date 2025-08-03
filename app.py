# Passo 1: Estrutura base do servidor Flask com endpoint de status funcional
# Step 1: Basic structure of the Flask server with a functional status endpoint
# Paso 1: Estructura básica del servidor Flask con un endpoint de estado funcional
# 第一步：Flask 服务器的基本结构，包含一个可用的状态端点

import os
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    Response,
    stream_with_context,
)
# Importa cliente OpenAI para interagir com a API da OpenAI
# Import OpenAI client to interact with OpenAI API
# Importar cliente OpenAI para interactuar con la API de OpenAI
# 导入 OpenAI 客户端以与 OpenAI API 交互
import openai

# Cria cliente OpenAI usando a variável de ambiente OPENAI_API_KEY
# Creates OpenAI client using the environment variable OPENAI_API_KEY
# Crea cliente OpenAI usando la variable de entorno OPENAI_API_KEY
# 使用环境变量 OPENAI_API_KEY 创建 OpenAI 客户端
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# Histórico do chat com uma mensagem inicial do sistema
# Chat history with an initial system message
# Historial del chat con un mensaje inicial del sistema
# 聊天记录，包含初始系统消息
chat_history = [
    {"role": "system", "content": "You are a helpful assistant."},
]

# Endpoint de status para verificar se o servidor está funcionando
# Status endpoint to verify if the server is running
# Endpoint de estado para verificar si el servidor está funcionando
# 用于检查服务器是否运行的状态端点
@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "ok"})

# Endpoint principal que serve a página HTML (interface do chat)
# Main endpoint that serves the HTML page (chat interface)
# Endpoint principal que sirve la página HTML (interfaz de chat)
# 主端点，提供HTML页面（聊天界面）
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", chat_history=chat_history)

# Função para receber mensagem do usuário via POST e adicioná-la ao histórico do chat
# Function to receive user's message via POST and add it to the chat history
# Función para recibir el mensaje del usuario vía POST y agregarlo al historial del chat
# 通过POST接收用户消息并添加到聊天记录的函数
@app.route("/chat", methods=["POST"])
def chat():
    # Obtém a mensagem do JSON da requisição e remove espaços extras
    # Gets the message from the request JSON and strips whitespace
    # Obtiene el mensaje del JSON de la solicitud y elimina espacios en blanco
    # 从请求的JSON中获取消息并去除空白字符
    content = request.json.get("message", "").strip()  

    # Verifica se a mensagem está vazia e retorna erro se for o caso
    # Checks if the message is empty and returns error if so
    # Verifica si el mensaje está vacío y devuelve error en ese caso
    # 检查消息是否为空，如果为空则返回错误
    if not content:
        return jsonify(success=False, error="Empty message not allowed."), 400
   
    # Adiciona a mensagem do usuário ao histórico do chat
    # Adds the user's message to the chat history
    # Agrega el mensaje del usuario al historial del chat
    # 将用户消息添加到聊天记录
    chat_history.append({"role": "user", "content": content})
    
    # Retorna resposta de sucesso em formato JSON
    # Returns success response in JSON format
    # Devuelve respuesta de éxito en formato JSON
    # 返回JSON格式的成功响应
    return jsonify(success=True)

# Endpoint para enviar a resposta do assistente em partes (streaming)
# Endpoint to stream the assistant's response in chunks
# Endpoint para transmitir la respuesta del asistente en partes (streaming)
# 用于分块传输助理回复的端点
@app.route("/stream", methods=["GET"])
def stream():
    def generate():
        assistant_response_content = ""
        # Conteúdo completo acumulado da resposta
        # Full accumulated response content
        # Contenido completo acumulado de la respuesta
        # 累积的完整回复内容
        with client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=chat_history,
            stream=True,
        ) as stream:
            for chunk in stream:
                if chunk.choices[0].delta and chunk.choices[0].delta.content:
                    # Acumula conteúdo recebido em partes
                    # Accumulates content received in chunks
                    # Acumula el contenido recibido en partes
                    # 累积接收到的内容块
                    assistant_response_content += chunk.choices[0].delta.content
                    yield f"data: {chunk.choices[0].delta.content}\n\n"
                if chunk.choices[0].finish_reason == "stop":
                    break  # Para o streaming ao final da resposta
                    # Stops streaming when the response finishes
                    # Detiene la transmisión cuando la respuesta termina
                    # 当回复完成时停止传输
        # Após o streaming, adiciona a resposta completa ao histórico
        # After streaming, adds the full response to chat history
        # Después de la transmisión, añade la respuesta completa al historial del chat
        # 流传输结束后，将完整回复添加到聊天记录
        chat_history.append(
            {"role": "assistant", "content": assistant_response_content}
        )

    return Response(stream_with_context(generate()), mimetype="text/event-stream")

# Endpoint para resetar o histórico do chat e começar uma nova conversa
# Endpoint to reset the chat history and start a new conversation
# Endpoint para reiniciar el historial del chat y comenzar una nueva conversación
# 用于重置聊天记录并开始新对话的端点
@app.route("/reset", methods=["POST"])
def reset_chat():
    global chat_history
    chat_history = [{"role": "system", "content": "You are a helpful assistant."}]
    return jsonify(success=True)


if __name__ == "__main__":
    # Executa o servidor Flask no modo debug para desenvolvimento
    # Runs Flask server in debug mode for development
    # Ejecuta el servidor Flask en modo debug para desarrollo
    # 以调试模式运行 Flask 服务器，用于开发
    app.run(debug=True)

