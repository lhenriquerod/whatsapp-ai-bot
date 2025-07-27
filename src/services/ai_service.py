import os
from openai import OpenAI
from dotenv import load_dotenv

# ✅ Carrega variáveis do .env
load_dotenv()

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_response(self, text):
        try:
            print(f"🤖 Chamando GPT para: {text}")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é um assistente útil."},
                    {"role": "user", "content": text}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Erro ao gerar resposta: {e}")
            return "Desculpe, não consegui responder agora."
