import faiss
import numpy as np
import json


class VectorStore:

    def __init__(self, dimension: int):
        self.dimension = dimension

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.chunks = []


    def add(self, embeddings, chunks):

        embeddings = np.asarray(
            embeddings,
            dtype="float32"
        )

        self.index.add(embeddings)

        self.chunks.extend(chunks)


    def search(self, query_embedding, top_k=3):

        query_embedding = np.asarray(
            [query_embedding],
            dtype="float32"
        )

        scores, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for score, index in zip(scores[0], indices[0]):

            # FAISS 在结果不足时可能返回 -1
            if index < 0:
                continue

            # 根据 FAISS 返回的索引找到完整 Chunk
            chunk = self.chunks[int(index)]

            results.append({
                "chunk_id": chunk["chunk_id"],
                "page": chunk["page"],
                "score": float(score),
                "text": chunk["text"]
            })

        return results


    def save(self, index_path, chunks_path):

        faiss.write_index(self.index, index_path)

        with open(chunks_path, "w", encoding="utf-8") as f:

            json.dump(self.chunks, f, ensure_ascii=False, indent=2)


    @classmethod
    def load(cls, index_path, chunks_path):

        index = faiss.read_index(
            str(index_path)
        )

        with open(chunks_path, "r", encoding="utf-8") as f:

            chunks = json.load(f)

        vector_store = cls(dimension = index.d)

        vector_store.index = index
        vector_store.chunks = chunks

        return vector_store
