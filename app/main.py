import shutil
from contextlib import asynccontextmanager
from pathlib import Path

import logfire
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

import app.observability
from app.db.models import Book, ReadingProgress
from app.db.progress import get_progress, save_progress
from app.db.session import SessionLocal, init_db
from app.ingestion.indexer import delete_document
from app.ingestion.pipeline import ingest_book
from app.qna.pipeline import answer_question


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield 

app = FastAPI(title="Reading Companion", lifespan=lifespan)
logfire.instrument_fastapi(app)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/health")
def health():
    return {"status": "ok"}

class ProgressUpdate(BaseModel):
    current_page: int
    current_offset: int

class AskRequest(BaseModel):
    question: str

@app.get("/books/{document_id}/progress")
def get_book_progress(document_id: str):
    progress = get_progress(document_id)
    if not progress:
        return {"current_page": 1, "current_offset": 0}
    return {
        "current_page": progress.current_page, 
        "current_offset": progress.current_offset,
    }

@app.post("/books/{document_id}/progress")
def post_book_progress(document_id: str, update: ProgressUpdate):
    save_progress(document_id, update.current_page, update.current_offset)
    return {"status": "saved"}

@app.post("/books/upload")
def upload_book(file: UploadFile = File(...)):  # noqa: B008 -- safe as default
    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    document_id = ingest_book(str(file_path), file.filename)

    with SessionLocal() as session:
        existing = session.query(Book).filter(Book.document_id == document_id).first()
        if not existing:
            session.add(Book(document_id=document_id, filename=file.filename))
            session.commit()

    return {"document_id": document_id, "filename": file.filename}

@app.post("/books/{document_id}/ask")
def ask_question(document_id: str, request: AskRequest):
    progress = get_progress(document_id)
    current_offset = progress.current_offset if progress else 0

    answer = answer_question(request.question, document_id, current_offset)
    return {"answer": answer}

@app.get("/books")
def list_books():
    with SessionLocal() as session:
        books = session.query(Book).all()
        return [
            {"document_id": b.document_id, "filename": b.filename, "uploaded_at": b.uploaded_at}
            for b in books
        ]

@app.delete("/books/{document_id}")
def delete_book(document_id: str):
    with SessionLocal() as session:
        book = session.query(Book).filter(Book.document_id == document_id).first()
        if book:
            session.delete(book)

        progress = session.query(ReadingProgress).filter(
            ReadingProgress.document_id == document_id
        ).first()

        if progress:
            session.delete(progress)

        session.commit()

    delete_document(document_id)

    return {"status": "deleted"}