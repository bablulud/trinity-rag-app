# Trinity RAG backend + frontend in one slim image.
# The vector index is baked into the image at build time so every container
# (including Cloud Run cold starts / new instances) boots already indexed —
# no per-instance re-indexing on an ephemeral filesystem.
FROM python:3.11-slim

WORKDIR /app

# Build deps for chromadb / sentence-transformers wheels.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the default local embedding model so build-time indexing and the
# first request are fast, and the container works offline after build.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Index lives inside the image (not a mounted volume), so it persists across
# every instance without external storage.
ENV PYTHONUNBUFFERED=1 \
    HF_HUB_OFFLINE=1 \
    PDF_DIR=/app/pdfs \
    CHROMA_DIR=/app/chroma_db

COPY . .

# Build the vector store at image-build time (local embeddings — no API key
# required). Baked into /app/chroma_db.
RUN python scripts/run_indexer.py

# Cloud Run provides $PORT (default 8080); fall back to 8000 for local `docker run`.
EXPOSE 8080
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080}"]
