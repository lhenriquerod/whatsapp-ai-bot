"""
Configuration module for RAG-E Chat Service.
Loads environment variables with sensible defaults.
"""
import os
from dotenv import load_dotenv

# Load .env once at process start
load_dotenv()

# Server configuration
PORT = int(os.getenv("PORT", "8000"))

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))

# Knowledge Base (Supabase table) configuration
KB_TABLE = os.getenv("KB_TABLE", "base_conhecimento")
KB_OWNER_COL = os.getenv("KB_OWNER_COL", "user_id")
KB_FIELDS = os.getenv("KB_FIELDS", "categoria,dados")
KB_LIMIT = int(os.getenv("KB_LIMIT", "100"))  # Fetch all entries (increased from 10)