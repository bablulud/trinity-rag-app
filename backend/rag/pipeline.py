"""The RAG query pipeline: retrieve -> augment -> generate, with real metrics.

Every stage is timed with perf_counter so the UI's "RAG Pipeline Performance"
panel reflects measured latency, not estimates. Token counts come from the
OpenAI usage object; per-chunk cosine similarity comes from Chroma distances.
"""
import os
import time
from typing import Dict

from . import config, embeddings, store


def _ms(t0: float) -> int:
    return round((time.perf_counter() - t0) * 1000)


def answer(cfg: Dict, question: str) -> Dict:
    model = cfg["EMBEDDING_MODEL"]

    # 1. Embed the query -----------------------------------------------------
    t = time.perf_counter()
    qvec = embeddings.embed(model, [question])[0]
    embed_ms = _ms(t)

    # 2. Vector search -------------------------------------------------------
    t = time.perf_counter()
    res = store.query(cfg, qvec)
    search_ms = _ms(t)

    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]
    dists = (res.get("distances") or [[]])[0]

    sources = []
    for doc, meta, dist in zip(docs, metas, dists):
        sim = max(0.0, min(1.0, 1.0 - float(dist)))  # cosine distance -> similarity
        sources.append({
            "source": (meta or {}).get("source", "unknown"),
            "chunk": (meta or {}).get("chunk", 0),
            "similarity": round(sim, 3),
        })

    if not docs:
        return {
            "answer": "The index is empty or no relevant chunks were found. "
                      "Add documents and re-index, or rephrase your question.",
            "sources": [],
            "metrics": _metrics(cfg, model, embed_ms, search_ms, 0, 0, 0, 0, 0.0),
        }

    context = "\n\n".join(
        f"[{i+1}] (source: {s['source']})\n{doc}"
        for i, (doc, s) in enumerate(zip(docs, sources))
    )

    # 3. Generate ------------------------------------------------------------
    from openai import OpenAI
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    prompt = f"Document snippets:\n\n{context}\n\nQuestion: {question}"

    t = time.perf_counter()
    resp = client.chat.completions.create(
        model=cfg["LLM_MODEL"],
        temperature=0,
        messages=[
            {"role": "system", "content": config.ASSISTANT_SYSTEM_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    gen_ms = _ms(t)

    text = (resp.choices[0].message.content or "").strip()
    usage = resp.usage
    prompt_tokens = getattr(usage, "prompt_tokens", 0)
    completion_tokens = getattr(usage, "completion_tokens", 0)

    avg_sim = round(sum(s["similarity"] for s in sources) / len(sources), 3) if sources else 0.0

    return {
        "answer": text,
        "sources": sources,
        "metrics": _metrics(
            cfg, model, embed_ms, search_ms, gen_ms,
            prompt_tokens, completion_tokens, len(docs), avg_sim,
        ),
    }


def _metrics(cfg, model, embed_ms, search_ms, gen_ms, ctx_tok, out_tok, chunks, avg_sim):
    return {
        "embed_ms": embed_ms,
        "search_ms": search_ms,
        "retrieval_ms": embed_ms + search_ms,
        "gen_ms": gen_ms,
        "total_ms": embed_ms + search_ms + gen_ms,
        "context_tokens": ctx_tok,
        "output_tokens": out_tok,
        "chunks": chunks,
        "top_k": cfg["TOP_K"],
        "avg_similarity": avg_sim,
        "embed_model": model,
        "dims": embeddings.dims(model),
        "llm_model": cfg["LLM_MODEL"],
        "chunk_size": cfg["CHUNK_SIZE"],
        "chunk_overlap": cfg["CHUNK_OVERLAP"],
        "collection": cfg["CHROMA_COLLECTION_NAME"],
    }
