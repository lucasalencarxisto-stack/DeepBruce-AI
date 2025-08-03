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

## 👨‍💻 Autor

Lucas Alencar  
Estudiante de ADS, desarrollador principiante mobile-first, apasionado por Python, IA y tecnologías transformadoras.  
GitHub: https://github.com/lucasalencarxisto-stack
