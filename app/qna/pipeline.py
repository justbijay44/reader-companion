import logfire

from app.qna.generation import generate_answer
from app.qna.reranker import rerank
from app.qna.retrieval import retrieve


def answer_question(question: str, document_id: str, current_offset: int):
    with logfire.span("answer_question", document_id=document_id):
        candidates = retrieve(question, document_id, current_offset, top_k=15)
        if not candidates:
            return "Not enough of the book has been read yet to answer that."
        top_chunks = rerank(question, candidates, top_k=5)
        return generate_answer(question, top_chunks)