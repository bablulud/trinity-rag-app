"""FastAPI service for the Trinity RAG chat + performance UI.

Endpoints
  GET  /api/health            -> status + indexed chunk count
  GET  /api/config            -> live config + selectable model choices
  PUT  /api/config            -> update live config (TOP_K, LLM_MODEL, chunking, ...)
  POST /api/reindex           -> rebuild the vector store with the current config
  POST /api/chat  {question}  -> {answer, sources, metrics}
  /                           -> static frontend (frontend/index.html)
"""
import threading
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from rag import config, pipeline, store

app = FastAPI(title="Ask Trinity — RAG API")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# Live, runtime-mutable config (starts from DEFAULTS).
CONFIG = dict(config.DEFAULTS)
_reindex_lock = threading.Lock()
_reindex_status = {"running": False, "last": None}


@app.on_event("startup")
def _startup():
    # Index automatically on first boot if the store is empty and PDFs exist.
    try:
        if store.collection_count(CONFIG) == 0:
            def _bg():
                with _reindex_lock:
                    _reindex_status["running"] = True
                    try:
                        _reindex_status["last"] = store.reindex(CONFIG)
                    finally:
                        _reindex_status["running"] = False
            threading.Thread(target=_bg, daemon=True).start()
    except Exception as e:  # pragma: no cover
        print("startup index check failed:", e)


class ChatRequest(BaseModel):
    question: str


class ConfigUpdate(BaseModel):
    EMBEDDING_MODEL: Optional[str] = None
    CHUNK_SIZE: Optional[int] = None
    CHUNK_OVERLAP: Optional[int] = None
    CHROMA_COLLECTION_NAME: Optional[str] = None
    TOP_K: Optional[int] = None
    LLM_MODEL: Optional[str] = None


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "openai_key": bool(config.OPENAI_API_KEY),
        "indexed_chunks": store.collection_count(CONFIG),
        "reindexing": _reindex_status["running"],
    }


@app.get("/api/config")
def get_config():
    return {
        "config": CONFIG,
        "embedding_choices": config.EMBEDDING_CHOICES,
        "llm_choices": config.LLM_CHOICES,
        "indexed_chunks": store.collection_count(CONFIG),
        "reindexing": _reindex_status["running"],
    }


@app.put("/api/config")
def put_config(update: ConfigUpdate):
    changed = {}
    for k, v in update.dict().items():
        if v is not None and CONFIG.get(k) != v:
            CONFIG[k] = v
            changed[k] = v
    # Changing chunking / embedding / collection invalidates the index.
    needs_reindex = any(
        k in changed for k in ("EMBEDDING_MODEL", "CHUNK_SIZE", "CHUNK_OVERLAP", "CHROMA_COLLECTION_NAME")
    )
    return {"config": CONFIG, "changed": changed, "needs_reindex": needs_reindex}


@app.post("/api/reindex")
def reindex():
    if _reindex_status["running"]:
        return {"status": "already_running"}
    with _reindex_lock:
        _reindex_status["running"] = True
        try:
            result = store.reindex(CONFIG)
            _reindex_status["last"] = result
        finally:
            _reindex_status["running"] = False
    return {"status": "done", **result}


@app.post("/api/chat")
def chat(req: ChatRequest):
    q = (req.question or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="empty question")
    if not config.OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set")
    try:
        return pipeline.answer(CONFIG, q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Static frontend last, so /api/* wins.
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
