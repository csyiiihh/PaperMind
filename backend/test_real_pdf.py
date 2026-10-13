import fitz
from pathlib import Path

paper_id = "96a453e6-9e85-4aef-9545-75487b7aa4dc"

pdf_path = Path("uploads") / f"{paper_id}.pdf"

with fitz.open(pdf_path) as doc:
    print("PDF 总页数：", len(doc))

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")

        if "references" in text.lower():
            print(f"\n===== PDF 第 {page_num} 页 =====")

            pos = text.lower().find("references")

            print(text[max(0, pos - 200):pos + 400])