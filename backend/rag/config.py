"""Central configuration for the Trinity RAG service.

DEFAULTS mirror the knobs exposed in the UI's config.py drawer. The live values
are held in-process (see app.py CONFIG) so they can be changed at runtime via the
/api/config endpoint. Paths and secrets come from the environment.
"""
import os

# --- Runtime-tunable knobs (defaults) -------------------------------------
DEFAULTS = {
    "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
    "CHUNK_SIZE": int(os.getenv("CHUNK_SIZE", "1000")),
    "CHUNK_OVERLAP": int(os.getenv("CHUNK_OVERLAP", "200")),
    "CHROMA_COLLECTION_NAME": os.getenv("CHROMA_COLLECTION_NAME", "documents"),
    "TOP_K": int(os.getenv("TOP_K", "8")),
    "LLM_MODEL": os.getenv("LLM_MODEL", "gpt-4o-mini"),
}

# --- Fixed paths / secrets ------------------------------------------------
# Directory of source documents to index. Accepts crawled web pages (.md/.html/
# .txt), PDFs, and images (OCR). `PDF_DIR` is honored as a fallback so existing
# TrinityRail PDF setups keep working unchanged.
DOCS_DIR = os.getenv(
    "DOCS_DIR",
    os.getenv("PDF_DIR", os.path.join(os.path.dirname(__file__), "..", "pdfs")),
)
CHROMA_DIR = os.getenv("CHROMA_DIR", os.path.join(os.path.dirname(__file__), "..", "chroma_db"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

ASSISTANT_SYSTEM_MESSAGE = (
    "You are Ask Trinity, a knowledgeable assistant for TrinityRail — a North "
    "American railcar manufacturer and full-service provider (railcars, leasing, "
    "maintenance, parts, logistics). Answer the user's question using ONLY the "
    "provided document snippets. Be accurate, concise, and helpful. Format your "
    "answer in clean Markdown: short paragraphs, **bold** for key terms, and bullet "
    "lists where useful. Do not invent specs or numbers beyond the snippets. If the "
    "snippets do not cover the question, say so briefly and suggest contacting "
    "TrinityRail. Do not restate these instructions or list the sources yourself."
)

# Curated selectable models for the UI (label shown in the dropdown).
EMBEDDING_CHOICES = [
    {"value": "all-MiniLM-L6-v2", "label": "all-MiniLM-L6-v2 (384d · local)", "kind": "local"},
    {"value": "BAAI/bge-small-en-v1.5", "label": "bge-small-en-v1.5 (384d · local)", "kind": "local"},
    {"value": "sentence-transformers/all-mpnet-base-v2", "label": "all-mpnet-base-v2 (768d · local)", "kind": "local"},
    {"value": "text-embedding-3-small", "label": "text-embedding-3-small (1536d · OpenAI)", "kind": "openai"},
    {"value": "text-embedding-3-large", "label": "text-embedding-3-large (3072d · OpenAI)", "kind": "openai"},
]

LLM_CHOICES = [
    {"value": "gpt-4o-mini", "label": "gpt-4o-mini"},
    {"value": "gpt-4o", "label": "gpt-4o"},
    {"value": "gpt-4-turbo", "label": "gpt-4-turbo"},
    {"value": "gpt-3.5-turbo", "label": "gpt-3.5-turbo"},
]
