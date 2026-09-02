import logfire
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer

from app.config import settings

_model = SentenceTransformer(settings.EMBEDDING_MODEL)


def embed_chunks(chunks: list[Document]) -> list[list[float]]:
    texts = [chunk.page_content for chunk in chunks]

    with logfire.span("embed_chunks", num_chunks=len(texts)):
        embeddings = _model.encode(
            texts,
            batch_size=settings.BATCH_SIZE,
            normalize_embeddings=True,
            show_progress_bar=True
        )

    return embeddings.tolist()