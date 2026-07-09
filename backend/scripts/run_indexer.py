"""Standalone indexer — build/refresh the vector DB from every document in DOCS_DIR.

Usage (inside the container or a local venv):
    python scripts/run_indexer.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rag import config, store

if __name__ == "__main__":
    print(f"Indexing documents from {config.DOCS_DIR} into {config.CHROMA_DIR}")
    print(f"Model={config.DEFAULTS['EMBEDDING_MODEL']} "
          f"chunk={config.DEFAULTS['CHUNK_SIZE']}/{config.DEFAULTS['CHUNK_OVERLAP']}")
    result = store.reindex(dict(config.DEFAULTS))
    print(result)
