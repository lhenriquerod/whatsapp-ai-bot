import os
import requests
from flask import Flask, request
from dotenv import load_dotenv
from openai import OpenAI

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.environ.get("WHATSAPP_PHONE_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    try:
        if request.method == "GET":
            token = request.args.get("hub.verify_token")
            challenge = request.args.get("hub.challenge")
            if token == VERIFY_TOKEN:
                print("✅ Webhook verificado com sucesso.")
                return challenge, 200
            return "Invalid token", 403

        elif request.method == "POST":
            print("🔔 CHEGOU POST NO WEBHOOK 🔔")
            print("RAW DATA:", request.data)
            data = request.get_json()
            print("PARSED JSON:", data)

            if data.get("object") == "whatsapp_business_account":
                for entry in data.get("entry", []):
                    for change in entry.get("changes", []):
                        value = change.get("value", {})
                        messages = value.get("messages", [])
                        if messages:
                            from_number = messages[0].get("from")
                            text = messages[0].get("text", {}).get("body", "")

                            if text:
                                print(f"📩 Mensagem recebida: {text}")
                                response_text = get_gpt_response(text)
                                send_message(from_number, response_text)

            return "EVENT_RECEIVED", 200

    except Exception as e:
        print("❌ Erro no webhook:", e)
        return "EVENT_RECEIVED", 200  # Nunca retorna erro para Meta


def get_gpt_response(user_text):
    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=f"O usuário disse: {user_text}. Responda de forma simples, clara e amigável."
        )
        print("✅ Resposta do GPT:", response.output_text)
        return response.output_text
    except Exception as e:
        print("❌ Erro ao chamar GPT:", e)
        return "Desculpe, tive um problema para processar sua mensagem."


def send_message(to, message):
    try:
        url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_ID}/messages"
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
        print("✅ Mensagem enviada para WhatsApp:", response.json())
    except Exception as e:
        print("❌ Erro ao enviar mensagem para WhatsApp:", e)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
