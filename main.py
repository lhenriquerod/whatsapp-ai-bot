from flask import Flask, request
from src.core.bot_engine import BotEngine
from src.utils.config import VERIFY_TOKEN

app = Flask(__name__)
bot = BotEngine()

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

        bot.process_message(data)
        return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    from src.utils.config import PORT
    app.run(host="0.0.0.0", port=PORT)
