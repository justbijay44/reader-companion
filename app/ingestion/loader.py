import logfire
import pymupdf
from langchain_core.documents import Document


def is_pdf(file_path: str) -> bool:
    with open(file_path, "rb") as f:
        return f.read(5) == b"%PDF-"

def load_pdf(file_path: str) -> list[Document]:
    if not is_pdf(file_path):
        logfire.error("Invalid pdf upload", file_path=file_path)
        raise ValueError(f"Not a valid PDF: {file_path}")

    doc = pymupdf.open(file_path)
    documents = []

    with logfire.span("load_pdf", num_pages=doc.page_count):
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text()

            if not text.strip():
                continue

            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "page": page_num,
                        "source": file_path,
                    },
                )
            )

    doc.close()
    return documents