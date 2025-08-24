import os
import openai
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Acessando a chave da API
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    print("API key not found. Please set the OPENAI_API_KEY in your .env file.")
else:
    # Configure a chave no cliente OpenAI
    openai.api_key = openai_api_key

    # Usando a nova interface da API
    response = openai.chat_completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, world!"}
        ]
    )

    print(response['choices'][0]['message']['content'])



