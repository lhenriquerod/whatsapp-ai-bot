# from flask import Flask, request
# from src.core.bot_engine import BotEngine
# from src.utils.config import VERIFY_TOKEN

# app = Flask(__name__)
# bot = BotEngine()

# @app.route("/webhook", methods=["GET", "POST"])
# def webhook():
#     if request.method == "GET":
#         token = request.args.get("hub.verify_token")
#         challenge = request.args.get("hub.challenge")
#         if token == VERIFY_TOKEN:
#             print("✅ Webhook verificado com sucesso!")
#             return challenge, 200
#         print("❌ Token inválido")
#         return "Invalid token", 403

#     if request.method == "POST":
#         data = request.get_json()
#         print("\n📥 RAW DATA:", data)

#         bot.process_message(data)
#         return "EVENT_RECEIVED", 200

# if __name__ == "__main__":
#     from src.utils.config import PORT
#     app.run(host="0.0.0.0", port=PORT)

import os
import requests
from flask import Flask, request
from openai import OpenAI
from dotenv import load_dotenv

# ✅ Carrega variáveis do .env
load_dotenv()

# ✅ Configurações
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.getenv("PORT", 5000))

if not all([VERIFY_TOKEN, WHATSAPP_TOKEN, WHATSAPP_PHONE_ID, OPENAI_API_KEY]):
    raise ValueError("❌ Algumas variáveis de ambiente estão faltando!")

# ✅ Inicializa OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ Inicializa Flask
app = Flask(__name__)

# ✅ Função para enviar mensagem pelo WhatsApp
def send_message(to, message):
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
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        print(f"📤 Mensagem enviada para {to}: {message}")
        print(f"✅ Resposta da API:", response.json())
    except requests.RequestException as e:
        print(f"❌ Erro ao enviar mensagem: {e}")

# ✅ Função para gerar resposta usando GPT
def generate_response(text):
    try:
        print(f"🤖 Chamando GPT para: {text}")
        response = client.chat.completions.create(
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

# ✅ Webhook para verificar e receber mensagens
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            print("✅ Webhook verificado com sucesso!")
            return challenge, 200
        print("❌ Token inválido")
        return "Invalid token", 403

    if request.method == "POST":
        data = request.get_json()
        print("\n📥 RAW DATA:", data)

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
                            response_text = generate_response(text)
                            send_message(from_number, response_text)
        return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    print(f"🚀 Servidor rodando na porta {PORT}")
    app.run(host="0.0.0.0", port=PORT)
