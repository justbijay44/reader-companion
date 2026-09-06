from fastapi import APIRouter
from pydantic import BaseModel

from app.db.progress import get_progress
from app.qna.pipeline import answer_question

router = APIRouter(prefix="/books", tags=['ask'])

class AskRequest(BaseModel):
    question: str

@router.post("/{document_id}/ask")
def ask_question(document_id: str, request: AskRequest):
    progress = get_progress(document_id)
    current_offset = progress.current_offset if progress else 0

    answer = answer_question(request.question, document_id, current_offset)
    return {"answer": answer}