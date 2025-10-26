import pytest
from fastapi.testclient import TestClient
from server.main import app

client = TestClient(app)

valid_payload = {
    "transaction_id": "TXN001",
    "timestamp": "2025-10-23T12:00:00Z",
    "sender_account": "ACC12345",
    "receiver_account": "ACC54321",
    "amount": 100.0,
    "transaction_type": "transfer",
    "merchant_category": "retail",
    "location": "Moscow, RU",
    "device_used": "mobile",
    "payment_channel": "online",
    "ip_address": "127.0.0.1",
    "device_hash": "abcdef12345678"
}

def test_post_transaction_success(monkeypatch):
    async def mock_push(*args, **kwargs):
        return 1

    from redis_queue_service import RedisQueue
    monkeypatch.setattr(RedisQueue, "push", mock_push)

    payload = valid_payload.copy()
    payload["transaction_id"] = "TXN002"

    response = client.post("/post", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"

def test_post_transaction_sender_equals_receiver():
    payload = valid_payload.copy()
    payload["transaction_id"] = "TXN004"
    payload["sender_account"] = "ACC123"
    payload["receiver_account"] = "ACC123"

    response = client.post("/post", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert any(err["loc"][-1] == "receiver_account" for err in data["detail"])

def test_post_transaction_invalid_type():
    payload = valid_payload.copy()
    payload["transaction_id"] = "TXN005"
    payload["transaction_type"] = "invalid_type"

    response = client.post("/post", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert any(err["loc"][-1] == "transaction_type" for err in data["detail"])

def test_post_transaction_negative_amount():
    payload = valid_payload.copy()
    payload["transaction_id"] = "TXN006"
    payload["amount"] = -50.0

    response = client.post("/post", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert any(err["loc"][-1] == "amount" for err in data["detail"])

def test_post_transaction_missing_required_field():
    payload = valid_payload.copy()
    payload["transaction_id"] = "TXN007"
    payload.pop("transaction_type")

    response = client.post("/post", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert any(err["loc"][-1] == "transaction_type" for err in data["detail"])

def test_post_transaction_invalid_ip():
    payload = valid_payload.copy()
    payload["transaction_id"] = "TXN008"
    payload["ip_address"] = "999.999.999.999"

    response = client.post("/post", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert any(err["loc"][-1] == "ip_address" for err in data["detail"])
