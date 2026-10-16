from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SimpleRAG:
    def __init__(self, docs: list[str]):
        self.docs = docs
        self.vectorizer = TfidfVectorizer()
        self.doc_vectors = self.vectorizer.fit_transform(docs)

    def retrieve(self, query: str, top_k: int = 2) -> list[tuple[str, float]]:
        """回傳 (段落, 相似度) 並依分數由高到低排序。"""
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.doc_vectors)[0]
        top_indices = scores.argsort()[-top_k:][::-1]
        return [(self.docs[i], float(scores[i])) for i in top_indices]