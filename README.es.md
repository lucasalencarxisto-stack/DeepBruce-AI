# 🧠 Proyecto OpenAI Quickstart (Flask + API)

Este proyecto es una aplicación web sencilla construida con Flask y la API de OpenAI. Permite a los usuarios enviar un prompt y recibir una respuesta generada por IA.

<!-- Badges -->
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)

---

## 📋 Tabla de Contenidos

- [Acerca de](#acerca-de)  
- [Configuración Inicial](#configuración-inicial)  
- [Funcionalidades Actuales](#funcionalidades-actuales)  
- [Contribuyendo](#contribuyendo)  
- [Autor](#autor)  

---

## Acerca de

Este proyecto es una aplicación web sencilla construida con Flask y la API de OpenAI. Permite a los usuarios enviar prompts y recibir respuestas generadas por IA.

---

## Contribuyendo

¡Las contribuciones son bienvenidas! Para contribuir:

1. Haz un fork del repositorio  
2. Crea tu rama de característica (`git checkout -b mi-feature`)  
3. Haz commit de tus cambios (`git commit -m 'Agregar feature'`)  
4. Haz push a la rama (`git push origin mi-feature`)  
5. Abre un Pull Request  

Por favor, sigue el estilo de código existente y escribe mensajes de commit claros.

---

## 🛠️ Configuración Inicial

A continuación, se muestran todos los pasos que seguí manualmente para configurar el entorno. Esto demuestra dominio de las herramientas esenciales para el desarrollo web e integración con IA.

1. Clona el repositorio

git clone https://github.com/your-username/openai-quickstart-01.git
cd openai-quickstart-01

2. Crea y activa el entorno virtual  
Windows:  
python -m venv venv  
venv\Scripts\activate  

Linux/Mac:  
python3 -m venv venv  
source venv/bin/activate  

3. Instala las dependencias  
pip install -r requirements.txt  

Si no tienes un archivo requirements.txt, créalo con:  
pip freeze > requirements.txt  

Asegúrate de que incluya al menos:  
flask  
openai  
python-dotenv  

4. Configura la clave API de OpenAI  
Crea un archivo .env con el siguiente contenido:  
OPENAI_API_KEY=tu-api-key-aqui  

Importante: usa .gitignore para nunca subir tu clave a GitHub.

5. Estructura básica esperada  
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

6. Ejecuta la aplicación localmente  
flask run  

Abre tu navegador en: http://127.0.0.1:5000

---

## 📌 Funcionalidades Actuales

- Interfaz web con formulario para enviar prompt  
- Integración con la API de OpenAI  
- Manejo básico de errores  
- Límite en la longitud de entrada del usuario  
- Estilo CSS simple para el frontend  

---

Chatbot Flask con SSE y OpenAI
Este proyecto es una aplicación sencilla basada en Flask utilizando el modelo GPT de OpenAI. Soporta Server-Sent Events (SSE) para respuestas en tiempo real y gestión de sesiones.

Cómo Configurar el .env
1. Crea un archivo .env en el directorio raíz del proyecto.
2. Añade las siguientes variables al archivo .env:
OPENAI_API_KEY=tu_clave_api_openai
OPENAI_MODEL=gpt-4o-mini
OPENAI_SUMMARY_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=800

Cómo Ejecutar Localmente
1. Instala las dependencias:
pip install -r requirements.txt
2. Asegúrate de que el entorno esté activado:
.\venv\Scripts\activate  # En Windows
source venv/bin/activate  # En Linux/macOS
3. Ejecuta la aplicación Flask:
python app.py
4. Accede a la aplicación en http://127.0.0.1:5000/ desde tu navegador.

Cómo Ejecutar en Producción
1. Configura debug=False en app.py.
2. Usa un servidor WSGI como gunicorn o uvicorn:
gunicorn app:app

Rutas Principales y Funcionalidades
/status: Ruta de verificación de salud que devuelve {"status": "ok"}.

/: Interfaz principal del chat renderizada en HTML.

/chat: Ruta POST que recibe un mensaje del usuario y lo guarda en el historial de la sesión.

/stream: Ruta GET que transmite las respuestas del chatbot en tiempo real usando SSE.

/stream2: Ruta POST que transmite las respuestas del chatbot en tiempo real usando un único endpoint.

## Ejemplos de Peticiones

1. Verificación de Salud**
```bash
curl http://127.0.0.1:5000/status
Respuesta esperada:
{
  "status": "ok"
}
2. Enviar Mensaje al Chat
curl -X POST http://127.0.0.1:5000/chat -H "Content-Type: application/json" -d '{"message": "¡Hola, chatbot!"}'
3. Respuesta en Tiempo Real con Stream
curl http://127.0.0.1:5000/stream
4. Endpoint Único para Stream
curl -X POST http://127.0.0.1:5000/stream2 -H "Content-Type: application/json" -d '{"message": "Cuéntame un chiste"}'




---

## 👨‍💻 Autor

Lucas Alencar  
Estudiante de ADS, desarrollador principiante mobile-first, apasionado por Python, IA y tecnologías transformadoras.  
GitHub: https://github.com/lucasalencarxisto-stack
