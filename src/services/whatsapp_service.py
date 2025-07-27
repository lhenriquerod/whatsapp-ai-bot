import requests
from src.utils.config import WHATSAPP_TOKEN, WHATSAPP_PHONE_ID

class WhatsAppService:
    BASE_URL = "https://graph.facebook.com/v18.0"

    def send_message(self, to: str, message: str):
        url = f"{self.BASE_URL}/{WHATSAPP_PHONE_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()
