from services.embedding_service import encode_texts
from services.vector_store import VectorStore

QUESTIONS = [
    "残差学习解决了什么问题？",
    "什么是退化问题？",
    "残差连接的数学表达式是什么？",
    "ResNet 为什么使用恒等映射？",
    "ResNet 在 ImageNet 上取得了什么结果？",
]

INDEXES = {
    "原始索引": (
        "vector_stores/resnet_smart_800.index",
        "vector_stores/resnet_smart_800_chunks.json"
    ),
    "清洗后索引": (
        "vector_stores/resnet_smart_800_clean.index",
        "vector_stores/resnet_smart_800_clean_chunks.json"
    ),
}

# 1. 对五道问题生成 Embedding
question_embeddings = encode_texts(QUESTIONS)

# 2. 加载两个 FAISS 索引
stores = {}

for name, (index_path, chunks_path) in INDEXES.items():

    store = VectorStore.load(index_path, chunks_path)

    stores[name] = store

    print(f"{name}：{store.index.ntotal} 个向量")


# 3. 分别检索，比较 Top-3
for question, embedding in zip(QUESTIONS, question_embeddings):

    print("\n" + "=" * 70)
    print("问题：", question)

    for name, store in stores.items():

        print(f"\n--- {name} ---")

        results = store.search(embedding, top_k=3)

        for rank, result in enumerate(results, start=1):

            print(
                f"Top {rank} | PDF第{result['page']}页"
            )

            print(result["text"][:250])
            print()