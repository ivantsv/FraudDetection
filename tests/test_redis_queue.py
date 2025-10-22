import pytest
import asyncio

import pytest_asyncio

from fraud_app.redis import RedisQueue
from fraud_app.core.config import REDIS_URL


@pytest_asyncio.fixture
async def redis_queue():
    """Фикстура: создаёт очередь и очищает её после теста"""
    queue = RedisQueue(REDIS_URL, queue_name="test:queue")
    await queue.connect()
    await queue.clear()
    
    yield queue
    
    await queue.clear()
    await queue.close()


@pytest.mark.asyncio
async def test_redis_connection(redis_queue):
    """Тест: подключение к Redis"""
    assert redis_queue._redis is not None
    pong = await redis_queue._redis.ping()
    assert pong is True


@pytest.mark.asyncio
async def test_push_transaction(redis_queue):
    """Тест: добавление транзакции в очередь"""
    transaction = {
        "id": "tx-12345",
        "amount": 1000.0,
        "from": "account-1",
        "to": "account-2",
        "type": "transfer"
    }
    
    length = await redis_queue.push(transaction)
    
    assert length == 1
    
    queue_length = await redis_queue.length()
    assert queue_length == 1


@pytest.mark.asyncio
async def test_pop_transaction(redis_queue):
    """Тест: извлечение транзакции из очереди"""
    original_transaction = {
        "id": "tx-67890",
        "amount": 500.0,
        "from": "account-3",
        "to": "account-4"
    }
    
    await redis_queue.push(original_transaction)
    
    popped_transaction = await redis_queue.pop(timeout=1)
    
    assert popped_transaction is not None
    assert popped_transaction["id"] == original_transaction["id"]
    assert popped_transaction["amount"] == original_transaction["amount"]
    
    queue_length = await redis_queue.length()
    assert queue_length == 0


@pytest.mark.asyncio
async def test_pop_empty_queue_with_timeout(redis_queue):
    """Тест: pop из пустой очереди с таймаутом"""
    
    result = await redis_queue.pop(timeout=1)
    
    assert result is None


@pytest.mark.asyncio
async def test_fifo_order(redis_queue):
    """Тест: FIFO порядок (First In, First Out)"""
    transactions = [
        {"id": "tx-1", "amount": 100},
        {"id": "tx-2", "amount": 200},
        {"id": "tx-3", "amount": 300},
    ]
    
    for tx in transactions:
        await redis_queue.push(tx)
    
    for expected_tx in transactions:
        popped_tx = await redis_queue.pop(timeout=1)
        assert popped_tx["id"] == expected_tx["id"]


@pytest.mark.asyncio
async def test_multiple_push(redis_queue):
    """Тест: добавление множества транзакций"""
    count = 10
    
    for i in range(count):
        await redis_queue.push({"id": f"tx-{i}", "amount": i * 100})
    
    length = await redis_queue.length()
    assert length == count


@pytest.mark.asyncio
async def test_clear_queue(redis_queue):
    """Тест: очистка очереди"""
    for i in range(5):
        await redis_queue.push({"id": f"tx-{i}"})
    
    assert await redis_queue.length() > 0
    
    await redis_queue.clear()
    
    length = await redis_queue.length()
    assert length == 0


@pytest.mark.asyncio
async def test_peek_without_removing(redis_queue):
    """Тест: просмотр элементов без извлечения"""
    transactions = [
        {"id": "tx-1", "amount": 100},
        {"id": "tx-2", "amount": 200},
    ]
    
    for tx in transactions:
        await redis_queue.push(tx)
    
    peeked = await redis_queue.peek(count=1)
    
    assert len(peeked) == 1
    assert peeked[0]["id"] == "tx-1"
    
    length = await redis_queue.length()
    assert length == 2


@pytest.mark.asyncio
async def test_context_manager(redis_queue):
    """Тест: использование как context manager"""
    async with redis_queue as queue:
        await queue.push({"id": "ctx-test"})
        length = await queue.length()
        assert length == 1


@pytest.mark.asyncio
async def test_concurrent_push_pop():
    """Тест: конкурентное добавление и извлечение"""
    queue = RedisQueue(REDIS_URL, "test:concurrent")
    await queue.connect()
    await queue.clear()
    
    async def producer():
        """Добавляет 10 транзакций"""
        for i in range(10):
            await queue.push({"id": f"concurrent-{i}"})
            await asyncio.sleep(0.01)
    
    async def consumer():
        """Извлекает транзакции"""
        consumed = []
        for _ in range(10):
            tx = await queue.pop(timeout=5)
            if tx:
                consumed.append(tx)
        return consumed
    
    producer_task = asyncio.create_task(producer())
    consumer_task = asyncio.create_task(consumer())
    
    await producer_task
    consumed_transactions = await consumer_task
    
    assert len(consumed_transactions) == 10
    
    await queue.clear()
    await queue.close()


@pytest.mark.asyncio
async def test_json_serialization_complex_data(redis_queue):
    """Тест: сериализация сложных данных"""
    complex_transaction = {
        "id": "tx-complex",
        "amount": 12345.67,
        "metadata": {
            "ip": "192.168.1.1",
            "device": "mobile",
            "tags": ["high-risk", "international"]
        },
        "timestamp": "2023-10-22T15:30:00Z",
        "is_fraud": False
    }
    
    await redis_queue.push(complex_transaction)
    popped = await redis_queue.pop(timeout=1)
    
    assert popped is not None
    assert popped["id"] == complex_transaction["id"]
    assert popped["amount"] == complex_transaction["amount"]
    assert popped["metadata"]["ip"] == "192.168.1.1"
    assert len(popped["metadata"]["tags"]) == 2


@pytest.mark.asyncio
async def test_error_handling_invalid_json(redis_queue):
    """Тест: обработка ошибок при невалидном JSON"""
    await redis_queue._redis.lpush(redis_queue.queue_name, "invalid-json-{{{")
    
    with pytest.raises(Exception):
        await redis_queue.pop(timeout=1)
    
    await redis_queue.clear()
