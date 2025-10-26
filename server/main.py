from fastapi import FastAPI, HTTPException, BackgroundTasks
from contextlib import asynccontextmanager
from redis_queue_service import RedisQueue
from transaction import TransactionRequest
from core import REDIS_URL
from server.logging_config.logging_config import setup_logger
import uuid


redis_queue = RedisQueue(REDIS_URL)
logger = setup_logger(component="ingest")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    await redis_queue.connect()

    yield

    # --- shutdown ---
    await redis_queue.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Fraud API is alive!"}

@app.get("/echo/{msg}")
async def echo(msg: str):
    return {"echo": msg}

@app.post("/post")
async def receive_transaction(tx: TransactionRequest, background_tasks: BackgroundTasks):
    transaction = tx.to_dict()
    transaction["correlation_id"] = str(uuid.uuid4())

    logger.info("Transaction received", extra={
        "correlation_id": transaction["correlation_id"],
        "event": "transaction_received",
        "transaction_id": tx.transaction_id,
        "account": tx.sender_account,
        "amount": tx.amount
    })

    background_tasks.add_task(redis_queue.push, transaction)

    return {
        "status": "accepted",
        "correlation_id": transaction["correlation_id"],
        "message": "Транзакция успешно принята в обработку"
    }
