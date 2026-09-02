from langchain_core.documents import Document
from app.ingestion.chunker import chunk_documents

def test_chunk_doc_basic():
    page_docs = [
        Document(page_content="some text on page_1" * 50, metadata={"page": 1}),
        Document(page_content="some text on page_2" * 50, metadata={"page": 2}),
    ]

    chunks = chunk_documents(page_docs)
    assert len(chunks) > 0

    for chunk in chunks:
        assert chunk.metadata["start_offset"] < chunk.metadata["end_offset"]
        assert chunk.metadata["page"] in (1, 2)

