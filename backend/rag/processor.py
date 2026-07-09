"""Source document -> clean text -> overlapping chunks.

Supports the formats the crawler produces (Markdown/text/HTML) plus PDFs. Text
is split with LangChain's RecursiveCharacterTextSplitter into CHUNK_SIZE-character
chunks with CHUNK_OVERLAP overlap.
"""
import os
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

TEXT_EXTS = {".md", ".markdown", ".txt"}
HTML_EXTS = {".html", ".htm"}
PDF_EXTS = {".pdf"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}
SUPPORTED_EXTS = TEXT_EXTS | HTML_EXTS | PDF_EXTS | IMAGE_EXTS

# OCR fallback for scanned PDFs and image uploads (Tesseract). Disable with
# OCR_ENABLED=0. OCR_DPI controls rasterization quality (higher = slower/sharper).
OCR_ENABLED = os.getenv("OCR_ENABLED", "1") not in ("0", "false", "False")
OCR_DPI = int(os.getenv("OCR_DPI", "300"))


def _ocr_image(pil_img) -> str:
    import pytesseract

    return pytesseract.image_to_string(pil_img.convert("L"))


def extract_image(path: str) -> str:
    if not OCR_ENABLED:
        return ""
    from PIL import Image

    with Image.open(path) as im:
        return _ocr_image(im)


def extract_pdf(pdf_path: str) -> str:
    import pdfplumber

    parts: List[str] = []
    pdfium_doc = None
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for idx, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                if not text.strip() and OCR_ENABLED:
                    # No embedded text -> scanned/image page. Rasterize with
                    # pypdfium2 and OCR it. Open the pdfium doc lazily so
                    # text-native PDFs never pay the cost.
                    try:
                        if pdfium_doc is None:
                            import pypdfium2 as pdfium

                            pdfium_doc = pdfium.PdfDocument(pdf_path)
                        pil = pdfium_doc[idx].render(scale=OCR_DPI / 72).to_pil()
                        text = _ocr_image(pil)
                    except Exception as e:  # OCR is best-effort
                        print(f"OCR failed on page {idx} of {pdf_path}: {e}")
                        text = ""
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
    finally:
        if pdfium_doc is not None:
            pdfium_doc.close()
    return "\n\n".join(parts)


def extract_html(html_path: str) -> str:
    from bs4 import BeautifulSoup

    with open(html_path, "r", encoding="utf-8", errors="ignore") as fh:
        soup = BeautifulSoup(fh.read(), "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text("\n")


def extract_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        return fh.read()


def extract_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in PDF_EXTS:
        return extract_pdf(path)
    if ext in IMAGE_EXTS:
        return extract_image(path)
    if ext in HTML_EXTS:
        return extract_html(path)
    return extract_text_file(path)


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return [c for c in splitter.split_text(text) if c.strip()]


def process_document(path: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    text = extract_text(path)
    if not text.strip():
        return []
    return chunk_text(text, chunk_size, chunk_overlap)


def list_documents(docs_dir: str) -> List[str]:
    if not os.path.isdir(docs_dir):
        return []
    return sorted(
        os.path.join(docs_dir, f)
        for f in os.listdir(docs_dir)
        if os.path.splitext(f)[1].lower() in SUPPORTED_EXTS
    )
