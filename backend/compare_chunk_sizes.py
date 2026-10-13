from services.embedding_service import encode_texts
from services.vector_store import VectorStore


questions = [
    "残差学习解决了什么问题？",
    "什么是退化问题？",
    "残差连接的数学表达式是什么？",
    "ResNet 为什么使用恒等映射？",
    "ResNet 在 ImageNet 上取得了什么结果？"
]

chunk_sizes = [500, 800, 1000]

# 每道问题只编码一次，保证三组实验使用相同的查询向量
query_embeddings = encode_texts(questions)

for size in chunk_sizes:

    print("\n" + "=" * 70)
    print(f"Chunk Size = {size}")

    store = VectorStore.load(
        f"vector_stores/resnet_smart_{size}.index",
        f"vector_stores/resnet_smart_{size}_chunks.json"
    )

    for question, embedding in zip(questions, query_embeddings):

        results = store.search(embedding, top_k=3)

        print(f"\n问题：{question}")

        total_chars = sum(len(result["text"]) for result in results)

        for rank, result in enumerate(results, start=1):

            print(
                f"Top {rank} | "
                f"PDF第{result['page']}页 | "
                f"Score={result['score']:.4f}"
            )

            print(result["text"][:250])
            print("-" * 40)

        print(f"Top 3 总字符数：{total_chars}")