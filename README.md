# Ask Trinity — RAG Chat + Performance Dashboard

A self-contained, Dockerized Retrieval-Augmented Generation app for TrinityRail
documents. Ask questions in a chat UI; every answer is grounded in indexed PDFs
and shows a **live RAG pipeline performance panel** (embed / search / generate
latency, token counts, per-chunk cosine similarity). A `config.py` drawer lets
you change retrieval/generation settings and **re-run the same question** to
compare performance.

```
PDFs → parse (pdfplumber) → chunk → embed → ChromaDB
                                              │
        question → embed → vector search → augment → LLM → answer + metrics
```

## Stack
- **Backend:** FastAPI + ChromaDB (persistent) + sentence-transformers / OpenAI embeddings + OpenAI chat.
- **Frontend:** single static `index.html` (no build step), served by the same container.
- **Everything in one container**, orchestrated with Docker Compose.

## Prerequisites
- Docker + Docker Compose
- An OpenAI API key (used for the generation step, and for the OpenAI embedding options)

## Quick start

```bash
cd trinity-rag-app

# 1. add your API key
cp .env.example .env
#   edit .env → OPENAI_API_KEY=sk-...

# 2. add your PDFs (the crawled TrinityRail pages, or any PDFs)
cp /path/to/RAG-Trinity-main/pdfs/*.pdf backend/pdfs/

# 3. build + run
docker compose up --build
```

Open **http://localhost:8000**

On first boot the service auto-indexes every PDF in `backend/pdfs/` into ChromaDB
(this can take a minute or two — watch the logs). The vector store is persisted
in a named volume, so later restarts are instant.

## Using the app
- Type a question (or tap a suggested prompt). The answer streams in with
  **retrieved sources** (cosine similarity per chunk) and a **RAG Pipeline
  Performance** panel of measured latencies and token counts.
- Open **config.py** (top-right). Change:
  - `TOP_K`, `LLM_MODEL` → apply live, no re-index needed.
  - `EMBEDDING_MODEL`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, `CHROMA_COLLECTION_NAME`
    → require **Re-index vector store** (button in the drawer) to take effect.
- Hit **Apply & Re-run** to run the last question again with the new settings and
  compare the two performance panels side by side.

## API
| Method | Path | Purpose |
|--------|------|---------|
| GET  | `/api/health`  | status + indexed chunk count |
| GET  | `/api/config`  | live config + selectable model lists |
| PUT  | `/api/config`  | update config (partial body) |
| POST | `/api/reindex` | rebuild the vector store with current config |
| POST | `/api/chat`    | `{ "question": "..." }` → `{ answer, sources, metrics }` |

Example:
```bash
curl -s localhost:8000/api/chat -H 'content-type: application/json' \
  -d '{"question":"What tank cars does TrinityRail offer?"}' | jq
```

## Run without Docker (local dev)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
export PDF_DIR=./pdfs CHROMA_DIR=./chroma_db
python scripts/run_indexer.py          # build the index once
uvicorn app:app --reload --port 8000
```

## Notes
- **Embedding vs. index consistency:** retrieval only makes sense when the query
  is embedded with the *same* model the index was built with. That's why changing
  `EMBEDDING_MODEL` (or chunking) flags a re-index — the app rebuilds the store so
  metrics and relevance stay honest.
- **OpenAI embeddings** (`text-embedding-3-*`) and all chat models require
  `OPENAI_API_KEY`. The local sentence-transformers models need no key.
- **Costs:** generation and OpenAI embeddings call the OpenAI API and incur usage
  charges. Local embeddings + your own PDFs keep indexing free.

## Layout
```
trinity-rag-app/
├── docker-compose.yml
├── .env.example
└── backend/
    ├── Dockerfile
    ├── requirements.txt
    ├── app.py                 # FastAPI app + endpoints + static mount
    ├── scripts/run_indexer.py # one-shot indexer
    ├── pdfs/                  # drop your PDFs here
    ├── frontend/
    │   ├── index.html         # the chat + performance UI
    │   └── assets/trinity-mark.png
    └── rag/
        ├── config.py          # defaults, model choices, system prompt
        ├── embeddings.py      # local + OpenAI embedders (normalized)
        ├── processor.py       # PDF → text/tables → chunks
        ├── store.py           # ChromaDB build + query
        └── pipeline.py        # retrieve → augment → generate + metrics
```
