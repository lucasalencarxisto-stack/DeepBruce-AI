# 🧠 OpenAI Quickstart Project (Flask + API)

This project is a simple web application built using Flask and the OpenAI API. It allows users to submit a prompt and receive an AI-generated response.


<!-- Badges -->
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)

---

## 📋 Table of Contents

- [About](#about)  
- [Initial Setup](#initial-setup)  
- [Current Features](#current-features)  
- [Contributing](#contributing)  
- [Author](#author)  

---

## About

This project is a simple web app built with Flask and OpenAI API. It lets users send prompts and get AI responses.

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository  
2. Create your feature branch (`git checkout -b feature-name`)  
3. Commit your changes (`git commit -m 'Add feature'`)  
4. Push to the branch (`git push origin feature-name`)  
5. Open a Pull Request  

Please follow the existing code style and write clear commit messages.

## 🛠️ Initial Setup

Below are all the steps I followed manually to configure the environment. This demonstrates mastery of essential web development tools and AI integration.

1. Clone the repository

git clone https://github.com/your-username/openai-quickstart-01.git
cd openai-quickstart-01

2. Create and activate the virtual environment  
Windows:  
python -m venv venv  
venv\Scripts\activate  

Linux/Mac:  
python3 -m venv venv  
source venv/bin/activate  

3. Install dependencies  
pip install -r requirements.txt  

If you don't have a requirements.txt, create it with:  
pip freeze > requirements.txt  

Make sure it includes at least:  
flask  
openai  
python-dotenv  

4. Configure the OpenAI API key  
Create a .env file with the following content:  
OPENAI_API_KEY=your-api-key-here  

Important: Use .gitignore to never upload your key to GitHub.

5. Expected basic structure  
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

6. Run the app locally  
flask run  

Open your browser at: http://127.0.0.1:5000

---

## 📌 Current Features

- Web interface with a prompt submission form  
- Integration with OpenAI API  
- Basic error handling  
- User input length limit  
- Simple CSS styling for frontend  

---

## 👨‍💻 Author

Lucas Alencar  
ADS student, mobile-first beginner developer, passionate about Python, AI, and transformative technologies.  
GitHub: https://github.com/lucasalencarxisto-stack



---


