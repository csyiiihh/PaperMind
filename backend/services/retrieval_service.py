import numpy as np

from services.embedding_service import encode_texts

def retrieve_chunks(
        query: str,
        chunks: list[str],
        top_k: int = 3
):
    chunk_embeddings = encode_texts(chunks)

    query_embedding = encode_texts([query])[0]

    scores = chunk_embeddings @ query_embedding

    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []

    for index in top_indices:

        results.append({
            "chunk_id": int(index),
            "score": float(scores[index]),
            "text": chunks[index]
        })

    return results