from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import progress
from app.db.models import Base


def make_test_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)

def test_save_and_get_progress(monkeypatch):
    TestSession = make_test_session()
    monkeypatch.setattr(progress, "SessionLocal", TestSession)

    progress.save_progress("doc123", current_page=5, current_offset=1200)
    result = progress.get_progress("doc123")

    assert result.current_page == 5
    assert result.current_offset == 1200

def test_save_progress_updates_existing(monkeypatch):
    TestSession = make_test_session()
    monkeypatch.setattr(progress, "SessionLocal", TestSession)

    progress.save_progress("doc123", current_page=5, current_offset=1200)
    progress.save_progress("doc123", current_page=10, current_offset=2500)

    result = progress.get_progress("doc123")
    assert result.current_page == 10
    assert result.current_offset == 2500

def test_get_progress_returns_none_for_missing_doc(monkeypatch):
    TestSession = make_test_session()
    monkeypatch.setattr(progress, "SessionLocal", TestSession)

    result = progress.get_progress("nonexist")
    assert result is None