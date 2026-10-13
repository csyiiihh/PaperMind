import csv
from pathlib import Path
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

output_path = Path("chunk_size_labels.csv")

labels = {}

# 如果之前已经标注过，就加载已有结果
if output_path.exists():
    with output_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            key = (
                int(row["chunk_size"]),
                row["question"],
                int(row["rank"])
            )

            labels[key] = int(row["label"])


def save_labels():
    with output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)

        writer.writerow([
            "chunk_size",
            "question",
            "rank",
            "label"
        ])

        for key, label in labels.items():
            size, question, rank = key

            writer.writerow([
                size,
                question,
                rank,
                label
            ])

query_embeddings = encode_texts(questions)

for size in chunk_sizes:

    store = VectorStore.load(
        f"vector_stores/resnet_smart_{size}.index",
        f"vector_stores/resnet_smart_{size}_chunks.json"
    )

    print(f"\n========== Chunk Size = {size} ==========")

    for question, embedding in zip(questions, query_embeddings):

        print(f"\n问题：{question}")

        results = store.search(embedding, top_k=3)

        for rank, result in enumerate(results, start=1):

            print(f"\nTop {rank} | PDF第{result['page']}页")
            print(result["text"])

            key = (size, question, rank)

            if key in labels:
                print("已有标注：", labels[key])
                continue

            while True:
                label = input("是否包含直接回答问题的证据？(1/0)：").strip()

                if label in ("0", "1"):
                    break

                print("请输入 0 或 1")

            labels[key] = int(label)

            save_labels()

            print("标注已保存")



def reciprocal_rank(relevance):
    for rank, value in enumerate(relevance, start=1):
        if value == 1:
            return 1 / rank

    return 0.0


print("\n========== 评测结果 ==========")

for size in chunk_sizes:

    all_relevance = []

    for question in questions:
        relevance = []

        for rank in range(1, 4):
            key = (size, question, rank)

            if key not in labels:
                raise RuntimeError(f"缺少标注：{key}")

            relevance.append(labels[key])

        all_relevance.append(relevance)

    hit_1 = sum(
        int(any(r[:1])) for r in all_relevance
    ) / len(all_relevance)

    hit_3 = sum(
        int(any(r[:3])) for r in all_relevance
    ) / len(all_relevance)

    mrr_3 = sum(
        reciprocal_rank(r[:3]) for r in all_relevance
    ) / len(all_relevance)

    print(f"\nChunk Size = {size}")
    print(f"Hit Rate@1: {hit_1:.4f}")
    print(f"Hit Rate@3: {hit_3:.4f}")
    print(f"MRR@3: {mrr_3:.4f}")