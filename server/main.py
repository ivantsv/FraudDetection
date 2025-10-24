from fastapi import FastAPI, HTTPException, BackgroundTasks
from contextlib import asynccontextmanager
from redis_queue_service import RedisQueue
from transaction import TransactionRequest
from core import REDIS_URL

redis_queue = RedisQueue(REDIS_URL)
transactions_db = {}

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
    if tx.transaction_id in transactions_db:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "duplicate_transaction",
                "message": f"Транзакция с ID '{tx.transaction_id}' уже существует"
            },
        )

    background_tasks.add_task(redis_queue.push, tx.to_dict())

    transactions_db[tx.transaction_id] = tx.model_dump()

    return {
        "status": "accepted",
        "transaction_id": tx.transaction_id,
        "message": "Транзакция успешно принята в обработку"
    }
