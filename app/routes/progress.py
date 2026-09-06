from fastapi import APIRouter
from pydantic import BaseModel

from app.db.progress import get_progress, save_progress
from app.ingestion.indexer import get_offset_for_page

router = APIRouter(prefix="/books", tags=["progress"])

class ProgressUpdate(BaseModel):
    current_page: int

@router.get("/{document_id}/progress")
def get_book_progress(document_id: str):
    progress = get_progress(document_id)
    if not progress:
        return {"current_page": 1, "current_offset": 0}
    return {
        "current_page": progress.current_page, 
        "current_offset": progress.current_offset,
    }

@router.post("/{document_id}/progress")
def post_book_progress(document_id: str, update: ProgressUpdate):
    current_offset = get_offset_for_page(document_id, update.current_page)
    save_progress(document_id, update.current_page, current_offset)
    return {"status": "saved"}