FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y make 

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN make -C shared_proto ml metadata transactions fix-imports

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]