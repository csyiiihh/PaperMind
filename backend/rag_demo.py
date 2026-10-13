from services.embedding_service import encode_texts
from services.vector_store import VectorStore
from services.rag_service import build_rag_prompt
from services.llm_service import generate_answer


PAPER_ID = "96a453e6-9e85-4aef-9545-75487b7aa4dc"

INDEX_PATH = f"vector_stores/{PAPER_ID}.index"

CHUNKS_PATH = f"vector_stores/{PAPER_ID}_chunks.json"


# 1. 加载论文向量库
vector_store = VectorStore.load(
    INDEX_PATH,
    CHUNKS_PATH
)


# 2. 用户问题
question = "残差学习解决了什么问题？"


# 3. 问题 Embedding
query_embedding = encode_texts([question])[0]


# 4. FAISS 检索
results = vector_store.search(
    query_embedding,
    top_k=3
)


# 5. 构造 RAG Prompt
prompt = build_rag_prompt(
    question,
    results
)


print("========== 检索结果 ==========")

for result in results:
    print(
        f"Chunk {result['chunk_id']} | "
        f"PDF第{result['page']}页 | "
        f"Score: {result['score']:.4f}"
    )


print("\n========== RAG 回答 ==========")


# 6. 调用 DeepSeek
answer = generate_answer(prompt)

print(answer)