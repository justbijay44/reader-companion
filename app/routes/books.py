import shutil
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.db.models import Book, ReadingProgress
from app.db.session import SessionLocal
from app.ingestion.indexer import delete_document
from app.ingestion.pipeline import ingest_book

router = APIRouter(prefix="/books", tags=["books"])
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload")
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

@router.get("/{document_id}")
def get_book(document_id: str):
    with SessionLocal() as session:
        book = session.query(Book).filter(Book.document_id == document_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return {"document_id": document_id, "filename": book.filename}

@router.get("/")
def list_books():
    with SessionLocal() as session:
        books = session.query(Book).all()
        return [
            {"document_id": b.document_id, "filename": b.filename, "uploaded_at": b.uploaded_at}
            for b in books
        ]

@router.delete("/{document_id}")
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

