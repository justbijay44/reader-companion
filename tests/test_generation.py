from types import SimpleNamespace

from app.qna import generation


def test_build_prompt_includes_question_n_context():
    chunks = [
        SimpleNamespace(payload={"text": "chunk1 text"}),
        SimpleNamespace(payload={"text": "chunk2 text"}),
    ]

    prompt = generation.build_prompt("Question", chunks)
    assert "Question" in prompt
    assert "chunk1 text" in prompt
    assert "chunk2 text" in prompt

def test_llm_fallback(monkeypatch):
    class FakeModels:
        def generate_content(self, *args, **kwargs):
            raise Exception("limit reached")    # noqa: TRY002 -- simulating API failure

    class FakeGeminiClient:
        models = FakeModels()

    monkeypatch.setattr(
        generation,
        "_gemini_client",
        FakeGeminiClient()
    )

    def fake_groq(*args, **kwargs):
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="groq fallback response"))]
        )
    
    monkeypatch.setattr(
        generation._groq_client.chat.completions,
        "create",
        fake_groq
    )

    chunks = [
            SimpleNamespace(payload={"text": "chunk1 text"}),
            SimpleNamespace(payload={"text": "chunk2 text"}),
        ]
    
    result = generation.generate_answer("What is this book about?", chunks)

    assert result == "groq fallback response"