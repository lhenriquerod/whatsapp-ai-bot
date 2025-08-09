import json
import hmac
import hashlib
import logging
from typing import Dict, Any, List

from src.services.ai_service import AIService
from src.services.whatsapp_service import WhatsAppService
from src.utils.kv_store import KVStore
from src.utils.config import (
    SYSTEM_PROMPT,
    MAX_HISTORY_MESSAGES,
    REDIS_URL,
    IDEMPOTENCY_TTL_SECONDS,
    APP_SECRET,
)

logger = logging.getLogger(__name__)

def mask_phone(number: str) -> str:
    if not number:
        return number
    return f"{'*' * max(0, len(number)-4)}{number[-4:]}"

class BotEngine:
    def __init__(self):
        self.ai = AIService()
        self.wa = WhatsAppService()
        self.kv = KVStore(REDIS_URL or None)

    # -- Entry point called from webhook handler (in a background thread)
    def process_webhook_event(self, data: Dict[str, Any]) -> None:
        try:
            if data.get("object") != "whatsapp_business_account":
                logger.info("Ignoring non-whatsapp object: %s", data.get("object"))
                return
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    # Handle messages
                    for msg in value.get("messages", []):
                        self._handle_message(value, msg)
                    # You may also handle statuses here if needed:
                    for status in value.get("statuses", []):
                        logger.info("Status update: %s", json.dumps(status, ensure_ascii=False))
        except Exception:
            logger.exception("Error processing webhook event")

    # -- Verify X-Hub-Signature-256 (called by main before processing)
    @staticmethod
    def verify_signature(app_secret: str, payload_bytes: bytes, signature_header: str) -> bool:
        try:
            if not app_secret:
                # If APP_SECRET not set, skip verification (not recommended for prod)
                return True
            if not signature_header or not signature_header.startswith("sha256="):
                return False
            digest = hmac.new(app_secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
            expected = f"sha256={digest}"
            # Use hmac.compare_digest to avoid timing attacks
            return hmac.compare_digest(expected, signature_header)
        except Exception:
            logger.exception("Signature verification failed")
            return False

    # -- Internal handlers
    def _handle_message(self, value: Dict[str, Any], msg: Dict[str, Any]) -> None:
        message_id = msg.get("id")
        from_number = msg.get("from")
        msg_type = msg.get("type")
        text = ""

        if not message_id or not from_number:
            logger.warning("Message missing id or from: %s", msg)
            return

        # Idempotency: ignore if we've already processed this message id
        if self.kv.seen(message_id):
            logger.info("Duplicate message ignored id=%s from=%s", message_id, mask_phone(from_number))
            return
        self.kv.set_idempotency(message_id, IDEMPOTENCY_TTL_SECONDS)

        if msg_type == "text":
            text = (msg.get("text") or {}).get("body", "")
        elif msg_type == "interactive":
            # Button reply or list reply
            interactive = msg.get("interactive") or {}
            if interactive.get("type") == "button_reply":
                text = (interactive.get("button_reply") or {}).get("title", "")
            elif interactive.get("type") == "list_reply":
                text = (interactive.get("list_reply") or {}).get("title", "")
        else:
            # Extend for other types (image, audio, etc.), for now send a polite message
            logger.info("Unsupported message type=%s", msg_type)
            self.wa.send_text(from_number, "Ainda não entendo esse tipo de mensagem. Pode escrever em texto?")
            return

        logger.info("Incoming message from=%s text=%s", mask_phone(from_number), text)

        # Build conversation history
        history = self._get_history(from_number)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [
            {"role": "user", "content": text}
        ]

        # Call LLM
        reply = self.ai.generate_response(messages)

        # Persist updated history
        self._push_history(from_number, {"role": "user", "content": text})
        self._push_history(from_number, {"role": "assistant", "content": reply})

        # Send reply
        self.wa.send_text(from_number, reply)

    # -- History helpers (Redis-backed with in-memory fallback implemented in KVStore)
    def _push_history(self, user_key: str, message: Dict[str, Any]) -> None:
        import json as _json
        self.kv.push_history(user_key, _json.dumps(message, ensure_ascii=False), MAX_HISTORY_MESSAGES)

    def _get_history(self, user_key: str) -> List[Dict[str, Any]]:
        import json as _json
        raw = self.kv.get_history(user_key, MAX_HISTORY_MESSAGES)
        return [_json.loads(x) for x in reversed(raw)]  # stored newest first; model expects oldest first