import logging
import os
import json
from threading import Thread
from flask import Flask, request

from src.core.bot_engine import BotEngine
from src.utils.config import PORT, VERIFY_TOKEN, APP_SECRET, ENV

# Logging config
logging.basicConfig(
    level=logging.INFO if ENV != "development" else logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

app = Flask(__name__)
engine = BotEngine()

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        mode = request.args.get("hub.mode")
        if mode == "subscribe" and verify_token == VERIFY_TOKEN and challenge:
            logging.info("Webhook verified successfully")
            return challenge, 200
        logging.warning("Invalid verify token on GET")
        return "Invalid token", 403

    if request.method == "POST":
        try:
            payload_bytes = request.get_data() or b"{}"
            signature = request.headers.get("X-Hub-Signature-256", "")
            if not engine.verify_signature(APP_SECRET, payload_bytes, signature):
                logging.warning("Invalid signature on POST")
                return "Invalid signature", 403

            data = json.loads(payload_bytes.decode("utf-8")) if payload_bytes else {}
        except Exception as e:
            logging.exception("Failed to parse body: %s", e)
            return "Bad Request", 400

        # Ack immediately; process async
        Thread(target=engine.process_webhook_event, args=(data,), daemon=True).start()
        return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    logging.info("Server starting on port %s", PORT)
    app.run(host="0.0.0.0", port=PORT)