from services.pdf_service import extract_pages_from_pdf
from services.text_splitter import split_pages_smart
from services.embedding_service import encode_texts
from services.vector_store import VectorStore


PAPER_ID = "96a453e6-9e85-4aef-9545-75487b7aa4dc"

PDF_PATH = f"uploads/{PAPER_ID}.pdf"

INDEX_PATH = "vector_stores/resnet_smart_800_clean.index"
CHUNKS_PATH = "vector_stores/resnet_smart_800_clean_chunks.json"


# 1. 解析 PDF
pages = extract_pages_from_pdf(PDF_PATH)

# 2. 使用新版切分算法
chunks = split_pages_smart(
    pages,
    chunk_size=800,
    chunk_overlap=100
)

print("Smart Chunk 数量：", len(chunks))

# 3. 提取文本
chunk_texts = [
    chunk["text"]
    for chunk in chunks
]

# 4. 生成 Embedding
embeddings = encode_texts(chunk_texts)

# 5. 创建 FAISS 索引
dimension = embeddings.shape[1]

vector_store = VectorStore(dimension)

vector_store.add(
    embeddings,
    chunks
)

# 6. 保存索引
vector_store.save(
    INDEX_PATH,
    CHUNKS_PATH
)

print("Smart FAISS 索引建立成功！")
print("向量数量：", vector_store.index.ntotal)