import pymupdf

PAPER_ID = "96a453e6-9e85-4aef-9545-75487b7aa4dc"
PDF_PATH = f"uploads/{PAPER_ID}.pdf"

with pymupdf.open(PDF_PATH) as doc:

    page = doc[2]  # PDF 第3页

    blocks = page.get_text("blocks")

    for i, block in enumerate(blocks):

        x0, y0, x1, y1, text, *rest = block

        if (
            "This hypothesis" in text
            or "ReLU" in text
            or "Formally" in text
        ):
            print(f"\n===== Block {i} =====")
            print(f"坐标：({x0:.1f}, {y0:.1f}) → ({x1:.1f}, {y1:.1f})")
            print("内容：")
            print(text[:700])