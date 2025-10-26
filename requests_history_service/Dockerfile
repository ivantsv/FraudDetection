FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && \
    apt-get install -y gcc libpq-dev make && \
    rm -rf /var/lib/apt/lists/*

COPY requests_history_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN make -C shared_proto transactions fix-imports

EXPOSE 50053

CMD ["python", "requests_history_service/server.py"]