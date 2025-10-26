FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && \
    apt-get install -y gcc libpq-dev make && \
    rm -rf /var/lib/apt/lists/*

COPY metadata_postgres_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN make -C shared_proto metadata fix-imports

EXPOSE 50052

CMD ["python", "metadata_postgres_service/server.py"]