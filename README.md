# 🛡️ Real-Time Fraud Detection System

A production-grade, microservices-based fraud detection platform built with modern architecture patterns and best practices. This system processes financial transactions in real-time, leveraging machine learning models and distributed data storage.

## 🎯 Project Overview

This project demonstrates a complete end-to-end fraud detection pipeline, from transaction ingestion to ML-based prediction and historical data storage. The architecture showcases:

- **Asynchronous processing** with Redis message queues
- **gRPC microservices** for efficient inter-service communication
- **Dual PostgreSQL databases** for metadata and transaction history separation
- **ML model serving** with dynamic threshold configuration
- **Structured logging** with correlation IDs for request tracing
- **Containerized deployment** with Docker Compose orchestration

### System Components

| Service | Technology | Purpose |
|---------|-----------|---------|
| **API Gateway** | FastAPI + Uvicorn | HTTP REST API for transaction ingestion |
| **Redis Queue** | Redis 7 | Asynchronous FIFO message queue |
| **ML Service** | Python + gRPC | Fraud prediction with configurable thresholds |
| **Metadata Service** | PostgreSQL + SQLAlchemy | Model configuration storage |
| **Transaction Service** | PostgreSQL + SQLAlchemy | Historical transaction records |

## 🚀 Key Features

### 1. **Asynchronous Request Processing**
- Non-blocking transaction ingestion via FastAPI
- Background task processing with Redis queues
- FIFO ordering guarantees for consistent processing

### 2. **gRPC Microservices**
- Protocol Buffers for efficient serialization
- Type-safe service contracts
- Health check endpoints for monitoring
- Service reflection for debugging

### 3. **Structured Logging & Observability**
- JSON-formatted logs with `python-json-logger`
- Correlation IDs for end-to-end request tracing
- Component-based log filtering
- Production-ready log aggregation support

### 4. **Database Design**
- **Metadata DB**: Stores ML model configurations (thresholds, versions)
- **Transactions DB**: Immutable audit log of all processed transactions
- Indexed for fast lookups (transaction_id, sender, receiver, timestamp)
- PostgreSQL constraints for data integrity

### 5. **Validation & Data Quality**
- Pydantic models for request validation
- IP address validation
- Timestamp validation (no future dates)
- Account uniqueness checks
- Transaction type whitelisting

### 6. **CI/CD Pipeline**
- GitLab CI with multi-stage pipeline
- Automated testing with pytest
- Health check validation
- Container orchestration testing
- Artifact collection and reporting

## 📋 Technical Requirements

- Docker 24.0+
- Docker Compose v2
- Python 3.12
- Make

## 🛠️ Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd fraud-detection-system
```

### 2. Build and Start Services

```bash
# Build all containers
docker compose build

# Start the system
docker compose up -d

# Check service health
docker compose ps
```

### 3. Verify Services

All services should show `healthy` status:

```bash
docker compose ps
```

Expected output:
```
NAME                  STATUS
api                   Up (healthy)
ml-service            Up (healthy)
metadata-service      Up (healthy)
transactions-service  Up (healthy)
redis                 Up (healthy)
metadata-db           Up (healthy)
transactions-db       Up (healthy)
```

## 📡 API Usage

### Submit Transaction

```bash
curl -X POST http://localhost:8000/post \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TXN123456",
    "timestamp": "2025-10-26T10:30:00.000Z",
    "sender_account": "ACC001",
    "receiver_account": "ACC002",
    "amount": 1500.50,
    "transaction_type": "transfer",
    "merchant_category": "retail",
    "location": "Moscow, RU",
    "device_used": "mobile",
    "payment_channel": "online",
    "ip_address": "192.168.1.100",
    "device_hash": "abcd1234efgh5678"
  }'
```

Response:
```json
{
  "status": "accepted",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Транзакция успешно принята в обработку"
}
```

### Health Check

```bash
curl http://localhost:8000/
```

## 🧪 Testing

### Run All Tests

```bash
docker compose run --rm tests pytest -v
```

### Test Coverage

- ✅ API endpoint validation
- ✅ Redis queue operations (push, pop, FIFO)
- ✅ Concurrent producer-consumer patterns
- ✅ JSON serialization edge cases
- ✅ Pydantic validation rules
- ✅ IP address validation
- ✅ Timestamp validation

### CI/CD Testing

The project includes a comprehensive GitLab CI pipeline:

1. **Build Stage**: Compiles all Docker images
2. **Up Stage**: Starts services and validates health
3. **Test Stage**: Runs pytest suite
4. **Down Stage**: Cleanup and artifact collection

## 📊 Data Models

### Transaction Schema

```python
{
  "transaction_id": str,        # Unique transaction identifier
  "timestamp": datetime,        # ISO 8601 format
  "sender_account": str,        # Min 5 characters
  "receiver_account": str,      # Min 5 characters, must differ from sender
  "amount": float,              # Must be > 0
  "transaction_type": str,      # Enum: transfer, payment, withdrawal, deposit
  "merchant_category": str,     # Business category
  "location": str,              # Geographic location
  "device_used": str,           # Device type
  "payment_channel": str,       # Channel type
  "ip_address": str,            # Valid IPv4/IPv6
  "device_hash": str,           # Min 8 characters
  "correlation_id": str         # Auto-generated UUID
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `DATABASE_URL` (metadata) | `postgresql+asyncpg://user:password@localhost:5432/metadata` | Metadata DB connection |
| `DATABASE_URL` (transactions) | `postgresql+asyncpg://user:password@localhost:5432/transactions` | Transaction DB connection |
| `GRPC_PORT` (ml-service) | `50051` | ML service gRPC port |
| `GRPC_PORT` (metadata-service) | `50052` | Metadata service gRPC port |
| `GRPC_PORT` (transactions-service) | `50053` | Transaction service gRPC port |

## 🎓 What I Learned

This project demonstrates proficiency in:

- **Backend Development**: FastAPI, async/await patterns, REST APIs
- **Microservices Architecture**: Service decomposition, inter-service communication
- **Message Queues**: Redis pub/sub, FIFO guarantees, producer-consumer patterns
- **gRPC**: Protocol Buffers, service definitions, async gRPC servers
- **Database Design**: PostgreSQL, SQLAlchemy ORM, async database access
- **DevOps**: Docker, Docker Compose, multi-stage builds
- **CI/CD**: GitLab CI, automated testing, health checks
- **Testing**: pytest, async testing, integration tests
- **Logging**: Structured logging, correlation IDs, observability

## 📈 Future Enhancements

- [ ] Add Kafka for higher throughput message processing
- [ ] Implement circuit breakers for fault tolerance
- [ ] Add Prometheus metrics and Grafana dashboards
- [ ] Implement distributed tracing with Jaeger
- [ ] Add API rate limiting and authentication
- [ ] Deploy to Kubernetes with Helm charts
- [ ] Add real-time alerting with anomaly detection
- [ ] Implement model versioning and A/B testing
