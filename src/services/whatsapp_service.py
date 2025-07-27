import os
import requests

class WhatsAppService:
    def __init__(self):
        self.token = os.getenv("WHATSAPP_TOKEN")
        self.phone_id = os.getenv("WHATSAPP_PHONE_ID")

    def send_message(self, to, message):
        url = f"https://graph.facebook.com/v18.0/{self.phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            print(f"📤 Mensagem enviada para {to}: {message}")
            print(f"✅ Resposta da API:", response.json())
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem: {e}")
