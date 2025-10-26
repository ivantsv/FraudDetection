FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

COPY ml_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN make -C shared_proto ml
RUN make -C shared_proto metadata fix-imports

EXPOSE 50051

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import grpc; from generated import ml_pb2, ml_pb2_grpc; \
    channel = grpc.insecure_channel('localhost:50051'); \
    stub = ml_pb2_grpc.MLServiceStub(channel); \
    response = stub.HealthCheck(ml_pb2.HealthCheckRequest()); \
    exit(0 if response.status == 'healthy' else 1)" || exit 1


CMD ["python", "ml_service/ml_server.py"]