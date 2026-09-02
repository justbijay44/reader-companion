import uuid

import logfire
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.config import settings

_client: QdrantClient | None = None

def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=settings.QDRANT_URL)
    return _client

def make_chunk_id(document_id: str, chunk_index: int) -> str:
    raw = f"{document_id}-{chunk_index}"
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, raw))

def ensure_collection(vector_size: int):
    client = get_client()
    if not client.collection_exists(settings.QDRANT_COLLECTION):
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

def upsert_chunks(document_id: str, filename: str, chunks: list, embeddings: list[list[float]]) -> list[str]:
    client = get_client()
    ensure_collection(vector_size=len(embeddings[0]))

    points, chunk_ids = [], []
    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        chunk_id = make_chunk_id(document_id, idx)
        chunk_ids.append(chunk_id)
        points.append(PointStruct(
            id=chunk_id,
            vector=embedding,
            payload={
                "document_id": document_id,
                "filename": filename,
                "page_number": chunk.metadata.get("page"),
                "start_offset": chunk.metadata.get("start_offset"),
                "end_offset": chunk.metadata.get("end_offset"),
                "text": chunk.page_content,
            },
        ))

    with logfire.span("upsert_to_qdrant", num_points=len(points)):
        client.upsert(collection_name=settings.QDRANT_COLLECTION, points=points)
        logfire.info("upserted chunks", num_points=len(points))

    return chunk_ids

def document_exists(document_id: str) -> bool:
    client = get_client()
    if not client.collection_exists(settings.QDRANT_COLLECTION):
        return False

    with logfire.span("document_exists_check", document_id=document_id):
        result = client.count(
            collection_name=settings.QDRANT_COLLECTION,
            count_filter=Filter(
                must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
            ),
        )
        exists = result.count > 0
        
    return exists