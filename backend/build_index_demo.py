from services.pdf_service import extract_text_from_pdf
from services.text_splitter import split_text
from services.embedding_service import encode_texts
from services.vector_store import VectorStore


PDF_PATH = (
    "uploads/"
    "He 等 - 2016 - Deep Residual Learning for Image Recognition.pdf"
)


INDEX_PATH = (
    "vector_stores/resnet.index"
)


CHUNKS_PATH = (
    "vector_stores/resnet_chunks.json"
)


print("正在解析 PDF...")

text = extract_text_from_pdf(
    PDF_PATH
)


print("正在切分文本...")

chunks = split_text(text)

print(
    "Chunk 数量:",
    len(chunks)
)


print("正在生成 Embedding...")

embeddings = encode_texts(
    chunks
)

print(
    "Embedding shape:",
    embeddings.shape
)


dimension = embeddings.shape[1]


vector_store = VectorStore(
    dimension
)


vector_store.add(
    embeddings,
    chunks
)


print("正在保存 FAISS 索引...")

vector_store.save(
    INDEX_PATH,
    CHUNKS_PATH
)


print("索引保存完成")