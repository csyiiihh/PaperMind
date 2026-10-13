import pymupdf
import re

PAPER_ID = "96a453e6-9e85-4aef-9545-75487b7aa4dc"
PDF_PATH = f"uploads/{PAPER_ID}.pdf"

total_removed = 0

with pymupdf.open(PDF_PATH) as doc:

    for page_num, page in enumerate(doc, start=1):

        blocks = page.get_text("blocks")
        removed = []

        for block in blocks:

            x0, y0, x1, y1, text, *rest = block

            is_footnote = (
                y0 > 690
                and len(text.strip()) < 150
                and re.match(
                    r"^\d+[A-Za-z]",
                    text.strip()
                ) is not None
            )

            if is_footnote:
                removed.append(text.strip())

        if removed:
            print(f"\n===== PDF 第 {page_num} 页 =====")

            for text in removed:
                print("疑似脚注：", text)
                total_removed += 1

print("\n===== 检测完成 =====")
print("疑似脚注总数：", total_removed)