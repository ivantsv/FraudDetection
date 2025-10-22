from typing import Any, Optional
from redis import asyncio as aioredis
import json
import logging

logger = logging.getLogger(__name__)


class RedisQueue:
    """
    Асинхронная очередь на Redis для транзакций
    
    Использует:
    - LPUSH для добавления (в начало)
    - BRPOP для извлечения с блокировкой (из конца)
    """
    
    def __init__(self, redis_url: str, queue_name: str = "transactions:queue"):
        self.redis_url = redis_url
        self.queue_name = queue_name
        self._redis: Optional[aioredis.Redis] = None

    async def connect(self):
        """Подключение к Redis"""
        if not self._redis:
            try:
                self._redis = await aioredis.from_url(
                    self.redis_url, 
                    decode_responses=True,
                    encoding="utf-8"
                )
                await self._redis.ping()
                logger.info(f"Connected to Redis: {self.redis_url}")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise

    async def close(self):
        """Закрытие соединения"""
        if self._redis:
            await self._redis.aclose()
            self._redis = None
            logger.info("Redis connection closed")

    async def push(self, transaction: dict) -> int:
        """
        Добавляет транзакцию в очередь
        
        Args:
            transaction: Словарь с данными транзакции
            
        Returns:
            Длина очереди после добавления
        """
        if not self._redis:
            await self.connect()

        try:
            transaction_json = json.dumps(transaction)
            length = await self._redis.lpush(self.queue_name, transaction_json)
            logger.debug(f"Pushed transaction to queue. Queue length: {length}")
            return length
        except Exception as e:
            logger.error(f"Failed to push transaction: {e}")
            raise

    async def pop(self, timeout: int = 0) -> Optional[dict]:
        """
        Извлекает транзакцию из очереди (блокирующий)
        
        Args:
            timeout: Таймаут ожидания в секундах (0 = бесконечно)
            
        Returns:
            Словарь с транзакцией или None при таймауте
        """
        if not self._redis:
            await self.connect()

        try:
            result = await self._redis.brpop(self.queue_name, timeout=timeout)
            
            if result:
                _, data = result
                transaction = json.loads(data)
                logger.debug(f"Popped transaction from queue: {transaction.get('id', 'unknown')}")
                return transaction
            else:
                logger.debug("Queue pop timeout")
                return None
                
        except Exception as e:
            logger.error(f"Failed to pop transaction: {e}")
            raise

    async def length(self) -> int:
        """Возвращает длину очереди"""
        if not self._redis:
            await self.connect()
            
        return await self._redis.llen(self.queue_name)

    async def clear(self):
        """Очищает очередь"""
        if not self._redis:
            await self.connect()
            
        await self._redis.delete(self.queue_name)
        logger.info(f"Queue '{self.queue_name}' cleared")

    async def peek(self, count: int = 1) -> list:
        """
        Просмотр элементов очереди без извлечения
        
        Args:
            count: Количество элементов для просмотра
            
        Returns:
            Список транзакций
        """
        if not self._redis:
            await self.connect()
            
        items = await self._redis.lrange(self.queue_name, -count, -1)
        return [json.loads(item) for item in items]

    async def __aenter__(self):
        """Context manager support"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager support"""
        await self.close()