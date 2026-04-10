"""In-memory vector index for policy chunks with top-K retrieval."""

import logging

from utils.similarity import cosine_similarity
from modules.llm import get_client

logger = logging.getLogger(__name__)

DEFAULT_TOP_K = 5


class PolicyRAG:
    def __init__(self, embedding_model, top_k=DEFAULT_TOP_K, chunks=None):
        """Build an in-memory embedding index from the supplied chunks.

        Args:
            embedding_model: OpenAI embedding model name.
            top_k: Default number of results to return.
            chunks: list[dict] with keys chunk_id, doc_name, page, text.
        """
        self.embedding_model = embedding_model
        self.top_k = top_k
        self.embeddings = []
        if chunks:
            self._build_index(chunks)

    def _build_index(self, chunks):
        """Embed the provided chunks."""
        if not chunks:
            logger.info("No chunks supplied — nothing to index")
            return

        client = get_client()
        self.embeddings = []

        for chunk in chunks:
            emb = client.embeddings.create(
                model=self.embedding_model,
                input=chunk["text"],
            )
            self.embeddings.append({
                "vector": emb.data[0].embedding,
                "data": chunk,
            })

        logger.info("PolicyRAG index built with %d chunks", len(self.embeddings))

    def retrieve(self, query, top_k=None):
        """Return the top-K most similar chunks for the given query.

        Args:
            query: Natural language question string.
            top_k: Override instance default if provided.

        Returns:
            list[dict]: Up to top_k chunk dicts sorted by descending similarity.
        """
        k = top_k or self.top_k

        if not self.embeddings:
            logger.warning("PolicyRAG index is empty — no chunks to search")
            return []

        client = get_client()
        query_emb = client.embeddings.create(
            model=self.embedding_model,
            input=query,
        ).data[0].embedding

        scored = []
        for item in self.embeddings:
            score = cosine_similarity(query_emb, item["vector"])
            scored.append((score, item["data"]))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [data for _score, data in scored[:k]]

        logger.info(
            "PolicyRAG retrieved %d chunks (top score=%.4f)",
            len(results),
            scored[0][0] if scored else 0.0,
        )
        return results

    def retrieve_as_context(self, query, top_k=None):
        """Retrieve top-K chunks and format them as a single context string.

        Includes page references so the LLM can cite sources.
        """
        chunks = self.retrieve(query, top_k)
        if not chunks:
            return ""

        parts = []
        for i, chunk in enumerate(chunks, 1):
            parts.append(
                f"[Excerpt {i} | {chunk['doc_name']} p.{chunk['page']}]\n"
                f"{chunk['text']}"
            )

        return "\n\n".join(parts)
