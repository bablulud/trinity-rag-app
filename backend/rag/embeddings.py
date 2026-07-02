"""Embedding backends.

Two families are supported so the UI's EMBEDDING_MODEL knob is meaningful:
  * local  — sentence-transformers models (run on CPU, no API cost)
  * openai — text-embedding-3-* (higher quality, needs OPENAI_API_KEY)

Embeddings are L2-normalized so cosine similarity == dot product, which lines up
with the Chroma collection created with {"hnsw:space": "cosine"}.
"""
from functools import lru_cache
from typing import List

from . import config

_OPENAI_DIMS = {"text-embedding-3-small": 1536, "text-embedding-3-large": 3072}


def _is_openai(model: str) -> bool:
    return model.startswith("text-embedding-")


@lru_cache(maxsize=8)
def _load_st(model: str):
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(model)


def dims(model: str) -> int:
    if _is_openai(model):
        return _OPENAI_DIMS.get(model, 1536)
    return _load_st(model).get_sentence_embedding_dimension()


def embed(model: str, texts: List[str]) -> List[List[float]]:
    """Return one normalized vector per input text."""
    if _is_openai(model):
        from openai import OpenAI
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        resp = client.embeddings.create(model=model, input=texts)
        vecs = [d.embedding for d in resp.data]
        return [_normalize(v) for v in vecs]
    st = _load_st(model)
    # sentence-transformers can normalize for us
    return st.encode(texts, normalize_embeddings=True).tolist()


def _normalize(v: List[float]) -> List[float]:
    import math
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]
