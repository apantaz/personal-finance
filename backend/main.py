from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.config import database_path
from ingestion.repository import TransactionRepository


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    TransactionRepository(database_path()).initialize()
    yield


app = FastAPI(title="Personal Finance API", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
