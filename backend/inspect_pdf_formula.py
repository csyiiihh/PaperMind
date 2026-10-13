import pymupdf

PAPER_ID = "96a453e6-9e85-4aef-9545-75487b7aa4dc"
PDF_PATH = f"uploads/{PAPER_ID}.pdf"

with pymupdf.open(PDF_PATH) as doc:

    # Python 页码从 0 开始
    page = doc[2]

    text = page.get_text("text")

    print("===== PDF 第3页原始文本 =====")
    print(text)