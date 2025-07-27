from src.services.ai_service import AIService
from src.services.whatsapp_service import WhatsAppService
from dotenv import load_dotenv

load_dotenv()

class BotEngine:
    def __init__(self):
        self.ai_service = AIService()
        self.whatsapp_service = WhatsAppService()

    def process_message(self, data):
        try:
            if data.get("object") == "whatsapp_business_account":
                for entry in data.get("entry", []):
                    for change in entry.get("changes", []):
                        value = change.get("value", {})
                        messages = value.get("messages", [])
                        if messages:
                            from_number = messages[0].get("from")
                            text = messages[0].get("text", {}).get("body", "")
                            if text:
                                print(f"📩 Mensagem recebida de {from_number}: {text}")
                                response_text = self.ai_service.generate_response(text)
                                self.whatsapp_service.send_message(from_number, response_text)
        except Exception as e:
            print(f"❌ Erro no processamento: {e}")
