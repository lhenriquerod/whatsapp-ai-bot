import os
from flask import Flask, request
from dotenv import load_dotenv

from src.core.bot_engine import BotEngine
from src.utils.config import PORT

bot_engine = BotEngine()

# ✅ Carrega variáveis do .env
load_dotenv()

# ✅ Configurações
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# ✅ Inicializa Flask
app = Flask(__name__)

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

        bot_engine.process_message(data)
        return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    print(f"🚀 Servidor rodando na porta {PORT}")
    app.run(host="0.0.0.0", port=PORT)
