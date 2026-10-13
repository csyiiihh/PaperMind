from services.embedding_service import encode_texts
from services.vector_store import VectorStore
from services.rag_service import build_rag_prompt
from services.llm_service import generate_answer


PAPER_ID = "96a453e6-9e85-4aef-9545-75487b7aa4dc"

QUESTION = "残差学习解决了什么问题？"


def run_rag(index_path, chunks_path):

    # 1. 加载 FAISS 索引
    vector_store = VectorStore.load(
        index_path,
        chunks_path
    )

    # 2. 将问题转换为向量
    query_embedding = encode_texts([QUESTION])[0]

    # 3. 检索 Top 3
    results = vector_store.search(
        query_embedding,
        top_k=3
    )

    # 4. 构建 RAG Prompt
    prompt = build_rag_prompt(
        QUESTION,
        results
    )

    # 5. 调用 DeepSeek 生成回答
    answer = generate_answer(prompt)

    return answer, results


print("\n========== 旧版 RAG 回答 ==========")

old_answer, old_sources = run_rag(
    f"vector_stores/{PAPER_ID}.index",
    f"vector_stores/{PAPER_ID}_chunks.json"
)

print(old_answer)


print("\n========== 新版 RAG 回答 ==========")

new_answer, new_sources = run_rag(
    "vector_stores/resnet_smart.index",
    "vector_stores/resnet_smart_chunks.json"
)

print(new_answer)