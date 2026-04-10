"""Split page-level text into overlapping chunks for embedding."""

import logging
import os
import ssl

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 100
DEFAULT_ENCODING = "cl100k_base"

_tiktoken_enc = None


def _get_encoder(encoding):
    """Try to load tiktoken; return None if unavailable."""
    global _tiktoken_enc
    if _tiktoken_enc is not None:
        return _tiktoken_enc
    try:
        # Disable SSL verification for tiktoken's encoding download,
        # matching the verify=False pattern used by httpx in llm.py.
        os.environ["CURL_CA_BUNDLE"] = ""
        os.environ["REQUESTS_CA_BUNDLE"] = ""
        ssl._create_default_https_context = ssl._create_unverified_context
        import tiktoken
        _tiktoken_enc = tiktoken.get_encoding(encoding)
        return _tiktoken_enc
    except Exception:
        logger.warning("tiktoken unavailable — falling back to word-based chunking")
        return None


def _token_chunks(text, chunk_size, chunk_overlap, encoding):
    """Split text into overlapping windows measured in tokens or words."""
    enc = _get_encoder(encoding)

    if enc is not None:
        tokens = enc.encode(text)
        if len(tokens) <= chunk_size:
            return [text]
        chunks = []
        start = 0
        while start < len(tokens):
            end = start + chunk_size
            chunks.append(enc.decode(tokens[start:end]))
            start += chunk_size - chunk_overlap
        return chunks

    words = text.split()
    if len(words) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - chunk_overlap
    return chunks


def chunk_pages(pages, doc_name, chunk_size=DEFAULT_CHUNK_SIZE,
                chunk_overlap=DEFAULT_CHUNK_OVERLAP, encoding=DEFAULT_ENCODING):
    """Convert page-level extracts into overlapping chunks tagged with metadata.

    Args:
        pages: list[dict] from pdf_ingestion.extract_text_from_pdf
               Each dict has 'page' (int) and 'text' (str).
        doc_name: Original filename of the uploaded PDF.
        chunk_size: Maximum tokens per chunk.
        chunk_overlap: Token overlap between consecutive chunks.
        encoding: tiktoken encoding name.

    Returns:
        list[dict]: Each entry has 'chunk_id', 'doc_name', 'page', 'text'.
    """
    all_chunks = []
    chunk_counter = 0

    for page_info in pages:
        page_num = page_info["page"]
        text = page_info["text"]

        text_chunks = _token_chunks(text, chunk_size, chunk_overlap, encoding)

        for fragment in text_chunks:
            all_chunks.append({
                "chunk_id": f"{doc_name}_chunk_{chunk_counter}",
                "doc_name": doc_name,
                "page": page_num,
                "text": fragment,
            })
            chunk_counter += 1

    logger.info(
        "Chunked %s into %d chunks (size=%d, overlap=%d)",
        doc_name, len(all_chunks), chunk_size, chunk_overlap,
    )
    return all_chunks
