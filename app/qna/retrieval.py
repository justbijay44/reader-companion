import logfire
from qdrant_client.models import FieldCondition, Filter, MatchValue, Range

from app.config import settings
from app.ingestion.embedder import embed_query
from app.ingestion.indexer import get_client


def retrieve(question: str, document_id: str, current_offset: int, top_k: int = 15):
    client = get_client()
    query_vector = embed_query(question)

    with logfire.span("retrieve", document_id=document_id, current_offset=current_offset):
        results = client.query_points(
            collection_name=settings.QDRANT_COLLECTION,
            query=query_vector,
            query_filter=Filter(
                must=[
                    FieldCondition(key="document_id", match=MatchValue(value=document_id)),
                    FieldCondition(key="end_offset", range=Range(lte=current_offset))
                ]
            ),
            limit=top_k
        )
        logfire.info("retrieved chunks", num_results=len(results.points))

    return results.points