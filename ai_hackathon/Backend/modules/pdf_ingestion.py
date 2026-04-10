"""Extract text from uploaded PDF files page by page."""

import logging
from pathlib import Path

from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path):
    """Read a PDF file and return a list of dicts with page number and text.

    Args:
        pdf_path: str or Path to the PDF file.

    Returns:
        list[dict]: Each entry has 'page' (1-indexed) and 'text' keys.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    pages = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()
        if not text:
            logger.warning("Page %d of %s produced no text", i + 1, pdf_path.name)
            continue
        pages.append({"page": i + 1, "text": text})

    logger.info("Extracted %d non-empty pages from %s", len(pages), pdf_path.name)
    return pages
