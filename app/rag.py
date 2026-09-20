from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SimpleRAG:
    def __init__(self, docs):
        self.docs = docs

        # Convert documents into TF-IDF vectors
        self.vectorizer = TfidfVectorizer()

        # Build the document matrix once during initialization
        self.doc_vectors = self.vectorizer.fit_transform(docs)

    def retrieve(self, query, top_k=2):
        # Convert the user's query using the same vectorizer
        query_vector = self.vectorizer.transform([query])

        # Calculate similarity between query and documents
        scores = cosine_similarity(
            query_vector,
            self.doc_vectors
        )[0]

        # Get indices of the most relevant documents
        top_indices = scores.argsort()[-top_k:][::-1]

        # Return retrieved documents
        return [self.docs[i] for i in top_indices]
