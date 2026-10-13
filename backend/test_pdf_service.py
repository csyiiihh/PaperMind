
from services.pdf_service import extract_pages_from_pdf

PAPER_ID = "96a453e6-9e85-4aef-9545-75487b7aa4dc"
PDF_PATH = f"uploads/{PAPER_ID}.pdf"

# 原始提取
original_pages = extract_pages_from_pdf(
    PDF_PATH,
    remove_footnotes=False
)

# 过滤脚注后提取
clean_pages = extract_pages_from_pdf(
    PDF_PATH,
    remove_footnotes=True
)

print("PDF 总页数：", len(original_pages))

for original, clean in zip(original_pages, clean_pages):

    page_num = original["page"]

    original_length = len(original["text"])
    clean_length = len(clean["text"])

    print(
        f"第 {page_num} 页："
        f"原始 {original_length} 字符，"
        f"过滤后 {clean_length} 字符"
    )

# 检查第3页脚注是否删除
page3_text = clean_pages[2]["text"]

print("\n===== 第3页检查 =====")
print(
    "脚注已删除：",
    "This hypothesis, however" not in page3_text
)

print(
    "公式（1）保留：",
    "y = F(x, {Wi}) + x." in page3_text
)

print(
    "公式（2）保留：",
    "y = F(x, {Wi}) + Wsx." in page3_text
)
