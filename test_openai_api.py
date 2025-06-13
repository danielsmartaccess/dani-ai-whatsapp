import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    print('API key não encontrada no .env')
    exit(1)

client = OpenAI(api_key=api_key)

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Olá, quem é você?"}]
    )
    print('Resposta da API:', response.choices[0].message.content)
except Exception as e:
    print('Erro ao acessar a API OpenAI:', e)
