from src.services.whatsapp_service import WhatsAppService
from src.services.ai_service import AIService

class BotEngine:
    def __init__(self):
        self.whatsapp = WhatsAppService()
        self.ai = AIService()

    def process_message(self, sender: str, message: str):
        response_text = self.ai.generate_response(message)
        self.whatsapp.send_message(sender, response_text)
