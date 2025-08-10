import os
import openai
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()
print("Chave da API:", os.getenv("OPENAI_API_KEY"))

# Acessando a chave da API
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    print("API key not found. Please set the OPENAI_API_KEY in your .env file.")
else:
    # Configure a chave no cliente OpenAI
    openai.api_key = openai_api_key

    # Teste com uma chamada simples à API
    response = openai.Completion.create(
        model="gpt-4o-mini",
        prompt="Hello, world!",
        max_tokens=100
    )

    print(response.choices[0].text)


