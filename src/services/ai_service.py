from openai import OpenAI
from src.utils.config import OPENAI_API_KEY

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def generate_response(self, user_message: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um assistente atencioso e educado."},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
