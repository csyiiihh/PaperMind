from services.pdf_service import extract_pages_from_pdf
from services.text_splitter import split_pages_smart
from services.embedding_service import encode_texts
from services.vector_store import VectorStore

PAPER_ID = "96a453e6-9e85-4aef-9545-75487b7aa4dc"

pdf_path = f"uploads/{PAPER_ID}.pdf"

pages = extract_pages_from_pdf(pdf_path)

chunk_sizes = [500, 800, 1000]

for size in chunk_sizes:

    chunks = split_pages_smart(
        pages,
        chunk_size=size,
        chunk_overlap=100
    )

    lengths = [len(chunk["text"]) for chunk in chunks]

    print(f"\nChunk Size: {size}")
    print(f"Chunk 数量: {len(chunks)}")
    print(f"平均长度: {sum(lengths) / len(lengths):.2f}")
    print(f"最短长度: {min(lengths)}")
    print(f"最长长度: {max(lengths)}")

    # 1. 提取 Chunk 中的文本
    chunk_texts = [chunk["text"] for chunk in chunks]

    # 2. 将文本转换成向量
    embeddings = encode_texts(chunk_texts)

    # 3. 创建 FAISS 向量索引
    vector_store = VectorStore(
        dimension=embeddings.shape[1]
    )

    # 4. 将向量和对应的 Chunk 信息加入索引
    vector_store.add(embeddings, chunks)

    # 5. 保存不同参数对应的索引
    index_path = f"vector_stores/resnet_smart_{size}.index"
    chunks_path = f"vector_stores/resnet_smart_{size}_chunks.json"

    vector_store.save(index_path, chunks_path)

    print(f"向量维度: {embeddings.shape[1]}")
    print(f"索引已保存: {index_path}")