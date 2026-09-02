import logfire
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_documents(page_docs: list[Document]) -> list[Document]:
    full_text = ""
    offset_to_page = []

    for doc in page_docs:
        offset_to_page.append((len(full_text), doc.metadata["page"]))
        full_text += doc.page_content + "\n"

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 800,
        chunk_overlap = 100,
        add_start_index = True,
    )

    with logfire.span("chunk_documents", num_pages=len(page_docs)):
        raw_chunks = splitter.create_documents([full_text])

        def page_for_offset(offset: int) -> int:
            page = offset_to_page[0][1]
            for start, pg in offset_to_page:
                if start > offset:
                    break
                page = pg
            return page

        chunks = []
        for chunk in raw_chunks:
            start = chunk.metadata["start_index"]
            end = start + len(chunk.page_content)
            chunks.append(
                Document(
                    page_content=chunk.page_content,
                    metadata={
                        "start_offset": start,
                        "end_offset": end,
                        "page": page_for_offset(start),
                    },
                )
            )

        logfire.info("chunked_document", num_chunks=len(chunks))
        
    return chunks