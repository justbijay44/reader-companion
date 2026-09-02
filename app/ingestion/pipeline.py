import hashlib

import logfire

from app.ingestion.chunker import chunk_documents
from app.ingestion.embedder import embed_chunks
from app.ingestion.indexer import document_exists, upsert_chunks
from app.ingestion.loader import load_pdf


def file_hash(file_path: str) -> str:
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def ingest_book(file_path: str, filename: str) -> str:
    document_id = file_hash(file_path)

    if document_exists(document_id):
        logfire.info("document already indexed, skipping", document_id=document_id)
        return document_id

    with logfire.span("ingest_book", filename=filename):
        docs = load_pdf(file_path)
        chunks = chunk_documents(docs)
        vectors = embed_chunks(chunks)
        upsert_chunks(document_id, filename, chunks, vectors)

    return document_id