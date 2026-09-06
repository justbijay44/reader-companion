from types import SimpleNamespace

from fastapi.testclient import TestClient

from app import main
from app.routes import qna

client = TestClient(main.app)

def test_ask_question_returns_answer(monkeypatch):
    def fake_get_progress(document_id):
        return SimpleNamespace(current_offset=500)

    def fake_answer_question(question, document_id, current_offset):
        assert document_id == "doc123"
        assert current_offset == 500
        return "This is a fake answer"

    monkeypatch.setattr(qna, "get_progress", fake_get_progress)
    monkeypatch.setattr(qna, "answer_question", fake_answer_question)

    response = client.post("/books/doc123/ask", json={"question": "What happened?"})

    assert response.status_code == 200
    assert response.json() == {"answer": "This is a fake answer"}