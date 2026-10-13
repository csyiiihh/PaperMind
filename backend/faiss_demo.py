from services.pdf_service import extract_text_from_pdf
from services.text_splitter import split_text
from services.embedding_service import encode_texts
from services.vector_store import VectorStore


PDF_PATH = (
    "uploads/"
    "He 等 - 2016 - Deep Residual Learning for Image Recognition.pdf"
)


# 1. PDF → Text

text = extract_text_from_pdf(
    PDF_PATH
)


# 2. Text → Chunks

chunks = split_text(text)


# 3. Chunks → Embeddings

chunk_embeddings = encode_texts(
    chunks
)


print(
    "Chunk embeddings shape:",
    chunk_embeddings.shape
)


# 4. 创建 FAISS

dimension = chunk_embeddings.shape[1]

vector_store = VectorStore(
    dimension=dimension
)


# 5. 向量加入 FAISS

vector_store.add(
    chunk_embeddings,
    chunks
)


# 6. 用户问题

query = "残差学习解决了什么问题？"


# 7. Query → Embedding

query_embedding = encode_texts(
    [query]
)[0]


# 8. FAISS 检索

results = vector_store.search(
    query_embedding,
    top_k=3
)


# 9. 输出

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
        "Text:"
    )

    print(
        result["text"][:500]
    )