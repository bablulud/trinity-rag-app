"""PDF -> clean text -> overlapping chunks.

pdfplumber pulls both running text and tables (TrinityRail spec sheets are
table-heavy), then LangChain's RecursiveCharacterTextSplitter cuts the text into
CHUNK_SIZE-character chunks with CHUNK_OVERLAP overlap.
"""
import os
from typing import List

import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_text(pdf_path: str) -> str:
    parts: List[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            if text.strip():
                parts.append(text)
            for table in page.extract_tables() or []:
                rows = [
                    " | ".join((cell or "").strip() for cell in row)
                    for row in table
                    if any(cell for cell in row)
                ]
                if rows:
                    parts.append("\n".join(rows))
    return "\n\n".join(parts)


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return [c for c in splitter.split_text(text) if c.strip()]


def process_pdf(pdf_path: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    text = extract_text(pdf_path)
    if not text.strip():
        return []
    return chunk_text(text, chunk_size, chunk_overlap)


def list_pdfs(pdf_dir: str) -> List[str]:
    if not os.path.isdir(pdf_dir):
        return []
    return sorted(
        os.path.join(pdf_dir, f)
        for f in os.listdir(pdf_dir)
        if f.lower().endswith(".pdf")
    )
