from services.pdf_service import extract_pages_from_pdf
from services.text_splitter import split_pages_smart

PAPER_ID = "96a453e6-9e85-4aef-9545-75487b7aa4dc"
PDF_PATH = f"uploads/{PAPER_ID}.pdf"

# 1. 解析 PDF
pages = extract_pages_from_pdf(PDF_PATH)

# 2. 智能分块
chunks = split_pages_smart(
    pages,
    chunk_size=800,
    chunk_overlap=100
)

# 3. 检查分块数量
print("Chunk 数量：", len(chunks))

# 4. 检查分块覆盖了哪些页面
page_numbers = sorted(set(
    chunk["page"] for chunk in chunks
))

print("Chunk 所在页码：", page_numbers)

# 5. 检查是否包含第9页
has_page_9 = any(
    chunk["page"] == 9
    for chunk in chunks
)

print("是否包含第9页：", has_page_9)

# 6. 检查参考文献标题
has_references = any(
    "References" in chunk["text"]
    for chunk in chunks
)

print("是否包含 References：", has_references)