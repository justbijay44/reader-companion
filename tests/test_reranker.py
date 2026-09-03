from types import SimpleNamespace

from app.qna import reranker


def test_rerank_orders_by_score_and_respects_top_k(monkeypatch):
    chunks = [
        SimpleNamespace(payload={"text": "low relevance"}),
        SimpleNamespace(payload={"text": "high relevance"}),
        SimpleNamespace(payload={"text": "medium relevance"}),
    ]

    def fake_predict(pairs):
        return [0.1, 0.9, 0.5]

    monkeypatch.setattr(reranker._reranker, "predict", fake_predict)
    result = reranker.rerank("some question", chunks, top_k=2)

    assert len(result) == 2
    assert result[0].payload["text"] == "high relevance"
    assert result[1].payload["text"] == "medium relevance"