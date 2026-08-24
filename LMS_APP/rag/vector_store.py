import faiss
import numpy as np

class VectorStore:
    def __init__(self):
        self.index = None
        self.documents = []

    def build(self, embeddings, documents):  # similarity index
        embeddings = np.asarray(
            embeddings,
            dtype="float32"
        )

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)
        self.documents = documents

    def search(self, query_embedding, top_k=5):
        if self.index is None:
            raise RuntimeError("Vector store has not been built.")

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        )

        scores, indexes = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for score, index in zip(scores[0], indexes[0]):

            if index == -1:
                continue

            document = self.documents[index].copy()

            document["score"] = float(score)

            results.append(document)

        return results