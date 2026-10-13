from services.embedding_service import encode_texts
from services.vector_store import VectorStore


INDEX_PATH = (
    "vector_stores/resnet.index"
)


CHUNKS_PATH = (
    "vector_stores/resnet_chunks.json"
)


print("正在加载 FAISS 索引...")


vector_store = VectorStore.load(
    INDEX_PATH,
    CHUNKS_PATH
)


print(
    "FAISS 中的向量数量:",
    vector_store.index.ntotal
)


query = "残差学习解决了什么问题？"


query_embedding = encode_texts(
    [query]
)[0]


results = vector_store.search(
    query_embedding,
    top_k=3
)


print("\n用户问题:")
print(query)


for result in results:

    print("\n---------------------")

    print(
        "Chunk:",
        result["chunk_id"]
    )

    print(
        "Score:",
        result["score"]
    )

    print(
        result["text"][:500]
    )