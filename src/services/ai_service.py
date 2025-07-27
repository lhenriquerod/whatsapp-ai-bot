import os
from openai import OpenAI

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_response(self, text):
        try:
            print(f"🤖 Chamando GPT para: {text}")
            response = self.client.responses.create(
                model="gpt-4o-mini",
                input=f"O usuário disse: {text}. Responda de forma clara e amigável."
            )
            return response.output_text
        except Exception as e:
            print(f"❌ Erro ao gerar resposta: {e}")
            return "Desculpe, não consegui responder agora."
