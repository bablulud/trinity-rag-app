"""ChromaDB persistent vector store: build the index and query it.

We pass embeddings in explicitly (rather than letting Chroma embed) so the
EMBEDDING_MODEL knob and the embed-latency metric are under our control. The
collection is created with cosine space; similarity = 1 - distance.
"""
import os
from typing import Dict, List

import chromadb

from . import config, embeddings, processor


def client():
    os.makedirs(config.CHROMA_DIR, exist_ok=True)
    return chromadb.PersistentClient(path=config.CHROMA_DIR)


def get_collection(cl, name: str):
    return cl.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})


def collection_count(cfg: Dict) -> int:
    cl = client()
    try:
        return get_collection(cl, cfg["CHROMA_COLLECTION_NAME"]).count()
    except Exception:
        return 0


def reindex(cfg: Dict, log=print) -> Dict:
    """(Re)build the collection from every PDF in PDF_DIR using cfg's model/chunking."""
    cl = client()
    name = cfg["CHROMA_COLLECTION_NAME"]
    # fresh collection
    try:
        cl.delete_collection(name)
    except Exception:
        pass
    col = get_collection(cl, name)

    pdfs = processor.list_pdfs(config.PDF_DIR)
    if not pdfs:
        log(f"No PDFs found in {config.PDF_DIR}")
        return {"files": 0, "chunks": 0}

    model = cfg["EMBEDDING_MODEL"]
    total_chunks = 0
    for path in pdfs:
        chunks = processor.process_pdf(path, cfg["CHUNK_SIZE"], cfg["CHUNK_OVERLAP"])
        if not chunks:
            continue
        vecs = embeddings.embed(model, chunks)
        base = os.path.basename(path)
        ids = [f"{base}::{i}" for i in range(len(chunks))]
        metas = [{"source": base, "chunk": i} for i in range(len(chunks))]
        col.add(ids=ids, documents=chunks, embeddings=vecs, metadatas=metas)
        total_chunks += len(chunks)
        log(f"indexed {base}: {len(chunks)} chunks")

    log(f"done: {len(pdfs)} files, {total_chunks} chunks, model={model}")
    return {"files": len(pdfs), "chunks": total_chunks}


def query(cfg: Dict, qvec: List[float]):
    cl = client()
    col = get_collection(cl, cfg["CHROMA_COLLECTION_NAME"])
    return col.query(
        query_embeddings=[qvec],
        n_results=cfg["TOP_K"],
        include=["documents", "metadatas", "distances"],
    )
