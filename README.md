# Reading Companion

A spoiler-free reading companion for PDFs. Upload a book, read it in the
browser, and ask questions about it — answers are generated only from
content up to the page you've actually reached, so a well-known plot twist
three chapters ahead never leaks into an answer.

## How it works

Standard RAG pipeline — chunk → embed → store in Qdrant → retrieve → generate
— with one added constraint: every chunk is tagged with a monotonic
start/end offset at ingestion time, and retrieval filters out any chunk whose
offset is past the reader's current position. Reading progress (current
page/offset) is saved as you read and restored on return.

Stack:
- **API**: FastAPI
- **Vector store**: Qdrant
- **Metadata / progress**: PostgreSQL (SQLAlchemy)
- **Embeddings**: `BAAI/bge-small-en-v1.5`
- **Reranking**: `BAAI/bge-reranker-base`
- **Generation**: Gemini (primary), Groq (fallback)
- **Frontend**: static HTML/CSS/JS, PDF.js for in-browser rendering
- **Observability**: Logfire

Ingestion (extract → chunk → embed → upsert) runs as a background task on
upload — the book is readable immediately, and Q&A for a section is gated
until that section finishes indexing.

## Project layout

```
app/
  routes/        # FastAPI routers: books (upload/list/delete), progress, qna
  ingestion/      # PDF loading, chunking, embedding, Qdrant indexing
  qna/            # retrieval, reranking, prompt building, generation
  db/             # SQLAlchemy models, session, progress persistence
static/           # frontend (index.html, script.js, style.css)
tests/            # pytest suite
sample_data/      # sample PDF for local testing
```

## Running it

### With Docker (recommended)

```bash
cp .env.example .env   # fill in the values described below
docker compose up --build
```

The app will be available at `http://localhost:8000`. Qdrant's dashboard is
at `http://localhost:6333/dashboard`.

### Locally (without Docker)

Requires Python 3.12, plus a running Qdrant and PostgreSQL instance (e.g. via
`docker compose up qdrant postgres`).

```bash
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload
```

## Configuration

Set these in `.env` (see `.env.example`):

| Variable | Description |
|---|---|
| `QDRANT_URL` | Qdrant connection URL (`http://qdrant:6333` in Docker) |
| `QDRANT_COLLECTION` | Qdrant collection name |
| `GEMINI_API_KEY` | Gemini API key (primary generation model) |
| `GROQ_API_KEY` | Groq API key (fallback generation model) |
| `DATABASE_URL` | PostgreSQL connection string |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Used by the `postgres` Docker service |
| `LOGFIRE_TOKEN` | Optional — enables Logfire observability |

## API overview

| Method | Path | Description |
|---|---|---|
| `POST` | `/books/upload` | Upload a PDF; ingestion runs in the background |
| `GET` | `/books/` | List uploaded books and their status |
| `GET` | `/books/{document_id}` | Get a single book's metadata |
| `DELETE` | `/books/{document_id}` | Delete a book (DB row, file, and its Qdrant vectors) |
| `GET` | `/books/{document_id}/progress` | Get current reading progress |
| `POST` | `/books/{document_id}/progress` | Save reading progress (current page) |
| `POST` | `/books/{document_id}/ask` | Ask a spoiler-safe question about the book |
| `GET` | `/health` | Health check |

## Tests

```bash
pytest
```

## CI/CD

- `.github/workflows/ci.yml` — runs the test suite on push/PR
- `.github/workflows/cd.yml` — deployment workflow
