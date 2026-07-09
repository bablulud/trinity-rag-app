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
    """(Re)build the collection from every document in DOCS_DIR using cfg's model/chunking."""
    cl = client()
    name = cfg["CHROMA_COLLECTION_NAME"]
    # fresh collection
    try:
        cl.delete_collection(name)
    except Exception:
        pass
    col = get_collection(cl, name)

    docs = processor.list_documents(config.DOCS_DIR)
    if not docs:
        log(f"No documents found in {config.DOCS_DIR}")
        return {"files": 0, "chunks": 0}

    model = cfg["EMBEDDING_MODEL"]

    # Collect every chunk across all documents first, then embed/add in large
    # batches. Batching amortizes network round-trips (a single OpenAI embeddings
    # call handles hundreds of chunks), which is orders of magnitude faster than
    # one call per file.
    all_ids: List[str] = []
    all_docs: List[str] = []
    all_metas: List[Dict] = []
    files_with_text = 0
    for path in docs:
        chunks = processor.process_document(path, cfg["CHUNK_SIZE"], cfg["CHUNK_OVERLAP"])
        if not chunks:
            continue
        files_with_text += 1
        base = os.path.basename(path)
        for i, chunk in enumerate(chunks):
            all_ids.append(f"{base}::{i}")
            all_docs.append(chunk)
            all_metas.append({"source": base, "chunk": i})

    total = len(all_docs)
    batch = int(os.getenv("INDEX_BATCH", "256"))
    for start in range(0, total, batch):
        end = min(start + batch, total)
        vecs = embeddings.embed(model, all_docs[start:end])
        col.add(
            ids=all_ids[start:end],
            documents=all_docs[start:end],
            embeddings=vecs,
            metadatas=all_metas[start:end],
        )
        log(f"embedded {end}/{total} chunks")

    log(f"done: {files_with_text} files, {total} chunks, model={model}")
    return {"files": files_with_text, "chunks": total}


def add_document(cfg: Dict, path: str) -> Dict:
    """Incrementally index a single file into the existing collection.

    Replaces any prior chunks from the same filename so re-uploading updates in
    place. Unlike reindex(), it does not rebuild the whole store.
    """
    cl = client()
    col = get_collection(cl, cfg["CHROMA_COLLECTION_NAME"])
    base = os.path.basename(path)

    chunks = processor.process_document(path, cfg["CHUNK_SIZE"], cfg["CHUNK_OVERLAP"])
    if not chunks:
        return {"file": base, "chunks": 0}

    try:
        col.delete(where={"source": base})
    except Exception:
        pass

    ids: List[str] = []
    docs: List[str] = []
    metas: List[Dict] = []
    for i, chunk in enumerate(chunks):
        ids.append(f"{base}::{i}")
        docs.append(chunk)
        metas.append({"source": base, "chunk": i})

    model = cfg["EMBEDDING_MODEL"]
    batch = int(os.getenv("INDEX_BATCH", "256"))
    for start in range(0, len(docs), batch):
        end = min(start + batch, len(docs))
        vecs = embeddings.embed(model, docs[start:end])
        col.upsert(
            ids=ids[start:end],
            documents=docs[start:end],
            embeddings=vecs,
            metadatas=metas[start:end],
        )

    return {"file": base, "chunks": len(docs)}


def query(cfg: Dict, qvec: List[float]):
    cl = client()
    col = get_collection(cl, cfg["CHROMA_COLLECTION_NAME"])
    return col.query(
        query_embeddings=[qvec],
        n_results=cfg["TOP_K"],
        include=["documents", "metadatas", "distances"],
    )
