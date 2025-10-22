from fastapi import FastAPI
from contextlib import asynccontextmanager
from db import init_db, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    # graceful shutdown

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Fraud API is alive!"}

@app.get("/echo/{msg}")
async def echo(msg: str):
    return {"echo": msg}