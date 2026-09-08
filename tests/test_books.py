import io
from types import SimpleNamespace

import pytest
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Base, Book
from app.routes import books


def make_test_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)

@pytest.fixture
def test_db(monkeypatch):
    TestSession = make_test_session()
    monkeypatch.setattr(books, "SessionLocal", TestSession)
    return TestSession

def insert_book(test_db):
    with test_db() as session:
        session.add(Book(document_id="book1", filename="test.pdf", status="ready"))
        session.commit()

def test_list_books(test_db):
    assert books.list_books() == []

def test_get_book(test_db):
    insert_book(test_db)        
    book = books.get_book("book1")
    assert book["filename"] == "test.pdf"
    assert book["document_id"] == "book1"

def test_get_book_missing(test_db):
    with pytest.raises(HTTPException) as exc_info:
        books.get_book("book2")

    assert exc_info.value.status_code == 404

def test_delete_book(test_db, monkeypatch):
    insert_book(test_db)        

    monkeypatch.setattr(books, "delete_document", lambda document_id: None)
    books.delete_book("book1")
    assert books.list_books() == []

def test_delete_book_missing(test_db, monkeypatch):
    monkeypatch.setattr(books, "delete_document", lambda document_id: None)
    assert books.delete_book("book2") == {"status": "deleted"}

def test_upload(test_db, monkeypatch, tmp_path):
    file_ = SimpleNamespace(filename="test.pdf", file=io.BytesIO(b"Some pdf bytes"))
    file1_ = SimpleNamespace(filename="test.pdf", file=io.BytesIO(b"Some pdf bytes"))

    monkeypatch.setattr(books, "UPLOAD_DIR", tmp_path)
    book1 = books.upload_book(BackgroundTasks(), file_)
    book2 = books.upload_book(BackgroundTasks(), file1_)
    assert book1["document_id"] == book2["document_id"]