from services.embedding_service import encode_texts
from services.vector_store import VectorStore


PAPER_ID = "96a453e6-9e85-4aef-9545-75487b7aa4dc"

questions = [
    "残差学习解决了什么问题？",
    "什么是退化问题？",
    "残差连接的数学表达式是什么？",
    "ResNet 为什么使用恒等映射？",
    "ResNet 在 ImageNet 上取得了什么结果？"
]

old_store = VectorStore.load(
    f"vector_stores/{PAPER_ID}.index",
    f"vector_stores/{PAPER_ID}_chunks.json"
)

new_store = VectorStore.load(
    "vector_stores/resnet_smart.index",
    "vector_stores/resnet_smart_chunks.json"
)

embeddings = encode_texts(questions)

for question, embedding in zip(questions, embeddings):

    print("\n" + "=" * 70)
    print("问题：", question)

    for name, store in [
        ("旧版", old_store),
        ("新版", new_store)
    ]:

        results = store.search(embedding, top_k=3)

        print(f"\n========== {name} ==========")

        for rank, result in enumerate(results, start=1):

            print(
                f"\nTop {rank} | "
                f"Chunk {result['chunk_id']} | "
                f"PDF第{result['page']}页"
            )

            # 输出完整 Chunk，而不是只输出前 200 个字符
            print(result["text"])