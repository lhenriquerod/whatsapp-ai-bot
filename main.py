import os
import requests
from flask import Flask, request
from dotenv import load_dotenv
from openai import OpenAI

# Carregar variáveis de ambiente (.env)
load_dotenv()

app = Flask(__name__)

# Variáveis de ambiente
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.environ.get("WHATSAPP_PHONE_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Cliente OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ Webhook (GET para verificação e POST para mensagens)
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    try:
        # 🔹 GET → Facebook verifica o webhook
        if request.method == "GET":
            token = request.args.get("hub.verify_token")
            challenge = request.args.get("hub.challenge")
            if token == VERIFY_TOKEN:
                print("✅ Webhook verificado com sucesso!")
                return challenge, 200
            print("❌ Token inválido na verificação")
            return "Invalid token", 403

        # 🔹 POST → Mensagens recebidas do WhatsApp
        elif request.method == "POST":
            print("\n📥 [RAW DATA RECEBIDO]:", request.data)
            data = request.get_json()
            print("✅ [JSON PARSEADO]:", data)

            if data.get("object") == "whatsapp_business_account":
                for entry in data.get("entry", []):
                    for change in entry.get("changes", []):
                        value = change.get("value", {})
                        messages = value.get("messages", [])

                        # ✅ PROCESSAR MENSAGEM
                        if messages:
                            from_number = messages[0].get("from")
                            text = messages[0].get("text", {}).get("body", "")

                            if text:
                                print(f"📩 Mensagem recebida de {from_number}: {text}")
                                # Gerar resposta usando GPT
                                response_text = get_gpt_response(text)
                                # Enviar resposta pelo WhatsApp
                                send_message(from_number, response_text)

            return "EVENT_RECEIVED", 200

    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
        return "EVENT_RECEIVED", 200


# ✅ Função para gerar resposta com GPT
def get_gpt_response(user_text):
    try:
        print(f"🤖 Chamando GPT para responder: {user_text}")
        response = client.responses.create(
            model="gpt-4o-mini",
            input=f"O usuário disse: {user_text}. Responda de forma simples, clara e amigável."
        )
        return response.output_text
    except Exception as e:
        print(f"❌ Erro ao chamar GPT: {e}")
        return "Desculpe, estou com dificuldades para responder agora."


# ✅ Função para enviar mensagem pelo WhatsApp
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
        print(f"📤 Mensagem enviada para {to}: {message}")
        print("✅ Resposta do WhatsApp API:", response.json())

    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")


# ✅ Inicialização do servidor
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Servidor rodando na porta {port}...")
    app.run(host="0.0.0.0", port=port)
