from contextlib import asynccontextmanager

import logfire
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import app.observability
from app.db.session import init_db
from app.routes import books, progress, qna


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield 

app = FastAPI(title="Reading Companion", lifespan=lifespan)
logfire.instrument_fastapi(app)

app.include_router(books.router)
app.include_router(progress.router)
app.include_router(qna.router)

@app.get("/health")
def health():
    return {"status": "ok"}

app.mount("/uploads", StaticFiles(directory="uploads", html=True), name="uploads")
app.mount("/", StaticFiles(directory="static", html=True), name="static")