from sentence_transformers import CrossEncoder

from app.config import settings

_reranker = CrossEncoder(settings.RERANKER_MODEL)

def rerank(question: str, chunks: list, top_k: int = 5) -> list:
    pairs = [(question, c.payload["text"]) for c in chunks]
    scores = _reranker.predict(pairs)

    scored = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
    return [chunk for chunk, score in scored[:top_k]]