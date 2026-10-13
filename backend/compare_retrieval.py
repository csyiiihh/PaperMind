from services.embedding_service import encode_texts
from services.vector_store import VectorStore


PAPER_ID = "96a453e6-9e85-4aef-9545-75487b7aa4dc"


# 加载旧索引
old_store = VectorStore.load(
    f"vector_stores/{PAPER_ID}.index",
    f"vector_stores/{PAPER_ID}_chunks.json"
)

# 加载新索引
new_store = VectorStore.load(
    "vector_stores/resnet_smart.index",
    "vector_stores/resnet_smart_chunks.json"
)


question = "残差学习解决了什么问题？"

query_embedding = encode_texts([question])[0]


old_results = old_store.search(
    query_embedding,
    top_k=3
)

new_results = new_store.search(
    query_embedding,
    top_k=3
)


def show_results(title, results):

    print(f"\n========== {title} ==========")

    for rank, result in enumerate(results, start=1):

        print(
            f"\nTop {rank} | "
            f"Chunk {result['chunk_id']} | "
            f"PDF第{result['page']}页 | "
            f"Score: {result['score']:.4f}"
        )

        print("内容：", result["text"][:400])


show_results("旧版固定切分", old_results)

show_results("新版 Smart Chunking", new_results)