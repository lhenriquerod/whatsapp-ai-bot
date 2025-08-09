"""
Provides a small key-value abstraction with Redis backend (if available)
and an in-memory fallback.
"""
import time
import logging
from typing import Optional, List, Dict, Any

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # fallback later

logger = logging.getLogger(__name__)

class _InMemoryKV:
    def __init__(self):
        self._store: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}

    def setex(self, key: str, ttl_seconds: int, value: str) -> None:
        self._store[key] = value
        self._expiry[key] = time.time() + ttl_seconds

    def exists(self, key: str) -> bool:
        exp = self._expiry.get(key)
        if exp is not None and exp < time.time():
            self._store.pop(key, None)
            self._expiry.pop(key, None)
            return False
        return key in self._store

    # Simple list ops for history
    def lpush(self, key: str, value: str) -> None:
        lst = self._store.setdefault(key, [])
        if not isinstance(lst, list):
            lst = []
        lst.insert(0, value)
        self._store[key] = lst

    def lrange(self, key: str, start: int, end: int) -> List[str]:
        lst = self._store.get(key, [])
        if not isinstance(lst, list):
            return []
        end = (end + 1) if end != -1 else None  # python slice semantics
        return lst[start:end]

    def ltrim(self, key: str, start: int, end: int) -> None:
        lst = self._store.get(key, [])
        if not isinstance(lst, list):
            return
        end = (end + 1) if end != -1 else None
        self._store[key] = lst[start:end]

class KVStore:
    def __init__(self, url: Optional[str] = None):
        self._backend = None
        if url and redis is not None:
            try:
                self._backend = redis.Redis.from_url(url, decode_responses=True)
                # Check connectivity
                self._backend.ping()
                logger.info("Connected to Redis KVStore.")
            except Exception as e:
                logger.warning("Redis not available, using in-memory store. error=%s", e)
                self._backend = _InMemoryKV()
        else:
            if url and redis is None:
                logger.warning("redis-py not installed; falling back to in-memory KV.")
            self._backend = _InMemoryKV()

    # Idempotency helpers
    def set_idempotency(self, message_id: str, ttl_seconds: int) -> None:
        self._backend.setex(f"idemp:{message_id}", ttl_seconds, "1")

    def seen(self, message_id: str) -> bool:
        return self._backend.exists(f"idemp:{message_id}")

    # Conversation history helpers
    def push_history(self, user_key: str, message_json: str, max_len: int) -> None:
        key = f"hist:{user_key}"
        self._backend.lpush(key, message_json)
        # keep only last max_len messages
        self._backend.ltrim(key, 0, max_len - 1)

    def get_history(self, user_key: str, limit: int) -> List[str]:
        key = f"hist:{user_key}"
        return self._backend.lrange(key, 0, limit - 1)