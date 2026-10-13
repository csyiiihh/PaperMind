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

# 一次性编码所有问题，避免重复调用模型
query_embeddings = encode_texts(questions)

for question, embedding in zip(questions, query_embeddings):

    old_results = old_store.search(embedding, top_k=3)
    new_results = new_store.search(embedding, top_k=3)

    print("\n" + "=" * 65)
    print("问题：", question)

    for title, results in [
        ("旧版", old_results),
        ("新版", new_results)
    ]:
        print(f"\n【{title} Top 3】")

        for rank, result in enumerate(results, start=1):
            print(
                f"Top {rank} | "
                f"第{result['page']}页 | "
                f"Score={result['score']:.4f}"
            )
            print(result["text"][:200].replace("\n", " "))