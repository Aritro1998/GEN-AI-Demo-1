import json
import logging

from config import resolve_backend_path
from utils.similarity import cosine_similarity
from modules.llm import get_client

logger = logging.getLogger(__name__)


class RAG:
    def __init__(self, data_path, embedding_model, text_fields=None):
        """Load the knowledge base and precompute embeddings for retrieval."""
        # Use the shared path resolver so both API writes and RAG reads point at
        # the same knowledge file location, even when overridden via env vars.
        resolved_path = resolve_backend_path(data_path)
        with resolved_path.open("r", encoding="utf-8") as f:
            self.knowledge = json.load(f)

        self.embedding_model = embedding_model
        self.text_fields = text_fields or []
        self.embeddings = []
        self._build_index()

    def _item_to_text(self, item):
        """Flatten a knowledge record into the text used for embeddings."""
        parts = []

        for field in self.text_fields:
            value = item.get(field)
            if isinstance(value, str) and value.strip():
                parts.append(value.strip())

        if parts:
            return " ".join(parts)

        # Fall back to every non-empty field so retrieval still works even if a
        # knowledge record is missing one of the preferred text fields.
        return " ".join(str(value).strip() for value in item.values() if str(value).strip())

    def _build_index(self):
        """Create embeddings for each knowledge item once at startup."""
        client = get_client()

        for item in self.knowledge:
            text = self._item_to_text(item)

            # Embeddings are precomputed once at startup so runtime retrieval only
            # needs to score vectors instead of recomputing the whole corpus.
            emb = client.embeddings.create(
                model=self.embedding_model,
                input=text,
            )

            self.embeddings.append({
                "vector": emb.data[0].embedding,
                "data": item,
            })

    def retrieve(self, query):
        """Return the most similar knowledge item for the given query."""
        if not self.embeddings:
            logger.warning("Potential issue detected: RAG index is empty")
            return {}

        client = get_client()

        query_emb = client.embeddings.create(
            model=self.embedding_model,
            input=query,
        ).data[0].embedding

        best = None
        best_score = -1

        for item in self.embeddings:
            # Keep the highest-similarity knowledge entry as the retrieval result.
            score = cosine_similarity(query_emb, item["vector"])
            if score > best_score:
                best_score = score
                best = item["data"]

        if best is None:
            logger.warning("Potential issue detected: no RAG context matched the query")
            return {}

        return best
