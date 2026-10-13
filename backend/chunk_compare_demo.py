from services.pdf_service import extract_pages_from_pdf
from services.text_splitter import split_pages, split_pages_smart


PDF_PATH = (
    "uploads/96a453e6-9e85-4aef-9545-75487b7aa4dc.pdf"
)

pages = extract_pages_from_pdf(PDF_PATH)

old_chunks = split_pages(pages)
new_chunks = split_pages_smart(pages)

print("旧切分数量：", len(old_chunks))
print("新切分数量：", len(new_chunks))

print("\n========== 旧切分示例 ==========")

for chunk in old_chunks[:3]:
    print(
        f"\nChunk {chunk['chunk_id']} "
        f"| PDF第{chunk['page']}页"
    )
    print(repr(chunk["text"][:250]))
    print("Chunk 结尾：", repr(chunk["text"][-150:]))

print("\n========== 新切分示例 ==========")

for chunk in new_chunks[:3]:
    print(
        f"\nChunk {chunk['chunk_id']} "
        f"| PDF第{chunk['page']}页"
    )
    print(repr(chunk["text"][:250]))
    print("Chunk 结尾：", repr(chunk["text"][-150:]))