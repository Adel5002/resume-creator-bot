import threading
import json
import redis
from typing import Optional, List


class RedisSession:
    """Redis-based implementation of session storage for agent conversations.

    Хранит историю сообщений в Redis списке.
    Каждая сессия = отдельный ключ (List).
    """

    def __init__(
        self,
        session_id: str,
        redis_url: str = "redis://localhost:6379",
        prefix: str = "agent_session:",
        ttl: Optional[int] = 60 * 60 * 24 * 7,  # 7 дней по умолчанию
    ):
        """
        Args:
            session_id: уникальный идентификатор сессии
            redis_url: URL к Redis (redis://localhost:6379)
            prefix: префикс ключей (для изоляции)
            ttl: время жизни ключа (в секундах)
        """
        self.session_id = session_id
        self.redis_url = redis_url
        self.prefix = prefix
        self.ttl = ttl
        self._lock = threading.Lock()

        # Подключение к Redis
        self.redis = redis.from_url(redis_url, decode_responses=True)

    def _key(self) -> str:
        """Сформировать ключ Redis для текущей сессии."""
        return f"{self.prefix}{self.session_id}"

    # ---------------------------------------------------------------------
    # Основные методы
    # ---------------------------------------------------------------------

    async def get_items(self, limit: Optional[int] = None) -> List[dict]:
        """Получить историю сообщений для сессии."""
        def _get_items_sync():
            with self._lock:
                key = self._key()
                total = self.redis.llen(key)
                if total == 0:
                    return []
                start = max(total - limit, 0) if limit else 0
                raw_items = self.redis.lrange(key, start, -1)
                items = []
                for raw in raw_items:
                    try:
                        items.append(json.loads(raw))
                    except json.JSONDecodeError:
                        continue
                return items

        import asyncio
        return await asyncio.to_thread(_get_items_sync)

    async def add_items(self, items: List[dict]) -> None:
        """Добавить новые элементы в историю."""
        if not items:
            return

        def _add_items_sync():
            with self._lock:
                key = self._key()
                pipe = self.redis.pipeline()
                for item in items:
                    pipe.rpush(key, json.dumps(item))
                if self.ttl:
                    pipe.expire(key, self.ttl)
                pipe.execute()

        import asyncio
        await asyncio.to_thread(_add_items_sync)

    async def pop_item(self) -> Optional[dict]:
        """Удалить и вернуть последнее сообщение."""
        def _pop_item_sync():
            with self._lock:
                key = self._key()
                raw = self.redis.rpop(key)
                if not raw:
                    return None
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    return None

        import asyncio
        return await asyncio.to_thread(_pop_item_sync)

    async def clear_session(self) -> None:
        """Удалить все сообщения из истории."""
        def _clear_sync():
            with self._lock:
                self.redis.delete(self._key())

        import asyncio
        await asyncio.to_thread(_clear_sync)

    def close(self) -> None:
        """Закрыть соединение с Redis."""
        self.redis.close()
