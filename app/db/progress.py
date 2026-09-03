from app.db.models import ReadingProgress
from app.db.session import SessionLocal


def get_progress(document_id: str) -> ReadingProgress | None:
    with SessionLocal() as session:
        return (
            session.query(ReadingProgress)
            .filter(ReadingProgress.document_id == document_id)
            .first()
        )

def save_progress(document_id: str, current_page: int, current_offset: int):
    with SessionLocal() as session:
        progress = (
            session.query(ReadingProgress)
            .filter(ReadingProgress.document_id == document_id)
            .first()
        )

        if progress:
            progress.current_page = current_page
            progress.current_offset = current_offset
        else:
            progress = ReadingProgress(
                document_id=document_id,
                current_page=current_page,
                current_offset=current_offset,
            )
            session.add(progress)

        session.commit()