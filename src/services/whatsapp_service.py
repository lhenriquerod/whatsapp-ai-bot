import json
import time
import logging
import requests
from typing import Dict, Any

from src.utils.config import (
    WHATSAPP_TOKEN,
    WHATSAPP_PHONE_ID,
    FB_GRAPH_VERSION,
    REQUEST_TIMEOUT,
    RETRY_MAX_ATTEMPTS,
)

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.session = requests.Session()
        self.base = f"https://graph.facebook.com/{FB_GRAPH_VERSION}/{WHATSAPP_PHONE_ID}"
        self.headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base}{path}"
        last_exc = None
        for attempt in range(RETRY_MAX_ATTEMPTS):
            try:
                resp = self.session.post(url, headers=self.headers, json=payload, timeout=REQUEST_TIMEOUT)
                if resp.status_code == 429 or 500 <= resp.status_code < 600:
                    logger.warning("WhatsApp API transient error status=%s body=%s", resp.status_code, resp.text)
                    time.sleep(2 ** attempt)
                    continue
                if not resp.ok:
                    logger.error("WhatsApp API non-OK status=%s body=%s", resp.status_code, resp.text)
                return {"status_code": resp.status_code, "body": resp.text, "json": self._safe_json(resp)}
            except Exception as e:  # network error etc
                last_exc = e
                logger.exception("WhatsApp API request failed (attempt %s): %s", attempt + 1, e)
                time.sleep(2 ** attempt)
        raise RuntimeError(f"WhatsApp API failed after retries: {last_exc}")

    @staticmethod
    def _safe_json(resp):
        try:
            return resp.json()
        except Exception:
            return None

    def send_text(self, to: str, body: str) -> Dict[str, Any]:
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": body}
        }
        return self._post("/messages", payload)