from fastapi import APIRouter
from pydantic import BaseModel

from app.db.models import Book
from app.db.progress import get_progress
from app.db.session import SessionLocal
from app.qna.pipeline import answer_question

router = APIRouter(prefix="/books", tags=['ask'])

class AskRequest(BaseModel):
    question: str

@router.post("/{document_id}/ask")
def ask_question(document_id: str, request: AskRequest):
    with SessionLocal() as session:
        book = session.query(Book).filter(Book.document_id == document_id).first()
        if book and book.status != "ready":
            return {"answer": "This book is still being processed. Please try again shortly."}

    progress = get_progress(document_id)
    current_offset = progress.current_offset if progress else 0

    answer = answer_question(request.question, document_id, current_offset)
    return {"answer": answer}