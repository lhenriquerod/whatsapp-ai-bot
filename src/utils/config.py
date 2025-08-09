import os
from dotenv import load_dotenv

# Load .env once at process start
load_dotenv()

# Core / server
PORT = int(os.getenv("PORT", "5000"))
ENV = os.getenv("ENV", "development")  # development|production

# Meta / WhatsApp
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "")
APP_SECRET = os.getenv("APP_SECRET", "")  # used for X-Hub-Signature-256
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")
FB_GRAPH_VERSION = os.getenv("FB_GRAPH_VERSION", "v18.0")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.4"))

# Redis (optional but recommended for scaling and idempotency)
REDIS_URL = os.getenv("REDIS_URL", "")  # e.g., redis://localhost:6379/0

# App behavior
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "Você é um assistente útil e direto.")
RESPONSE_FALLBACK = os.getenv("RESPONSE_FALLBACK", "Desculpe, tive um problema ao responder agora. Tente novamente em instantes.")
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))
IDEMPOTENCY_TTL_SECONDS = int(os.getenv("IDEMPOTENCY_TTL_SECONDS", "3600"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))
RETRY_MAX_ATTEMPTS = int(os.getenv("RETRY_MAX_ATTEMPTS", "3"))