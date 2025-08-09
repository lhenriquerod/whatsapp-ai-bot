import logging
from typing import List, Dict
from openai import OpenAI
from src.utils.config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, RESPONSE_FALLBACK

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def generate_response(self, messages: List[Dict]) -> str:
        try:
            resp = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=OPENAI_TEMPERATURE,
            )
            return resp.choices[0].message.content or RESPONSE_FALLBACK
        except Exception as e:
            logger.exception("OpenAI call failed: %s", e)
            return RESPONSE_FALLBACK