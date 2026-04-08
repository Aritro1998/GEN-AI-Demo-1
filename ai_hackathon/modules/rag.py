import json
from utils.similarity import cosine_similarity
from modules.llm import get_client


class RAG:
    def __init__(self, data_path, embedding_model, text_fields=None):
        with open('C:\\vs-code\\ai_hackathon\\data\\knowledge.json', 'r') as f:
            self.knowledge = json.load(f)

        self.embedding_model = embedding_model
        self.text_fields = text_fields or []
        self.embeddings = []
        self._build_index()

    def _item_to_text(self, item):
        parts = []

        for field in self.text_fields:
            value = item.get(field)
            if isinstance(value, str) and value.strip():
                parts.append(value.strip())

        if parts:
            return " ".join(parts)

        return " ".join(str(value).strip() for value in item.values() if str(value).strip())

    def _build_index(self):
        client = get_client()

        for item in self.knowledge:
            text = self._item_to_text(item)

            emb = client.embeddings.create(
                model=self.embedding_model,
                input=text,
            )

            self.embeddings.append({
                "vector": emb.data[0].embedding,
                "data": item,
            })

    def retrieve(self, query):
        client = get_client()

        query_emb = client.embeddings.create(
            model=self.embedding_model,
            input=query,
        ).data[0].embedding

        best = None
        best_score = -1

        for item in self.embeddings:
            score = cosine_similarity(query_emb, item["vector"])
            if score > best_score:
                best_score = score
                best = item["data"]

        return best
