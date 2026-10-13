import pymupdf
import re

PAPER_ID = "96a453e6-9e85-4aef-9545-75487b7aa4dc"
PDF_PATH = f"uploads/{PAPER_ID}.pdf"

with pymupdf.open(PDF_PATH) as doc:

    page = doc[2]

    blocks = page.get_text("blocks")

    body_blocks = []
    removed_blocks = []

    for block in blocks:

        x0, y0, x1, y1, text, *rest = block

        # 仅用于当前 ResNet 论文的实验性规则
        is_footnote = (
            y0 > 690
            and len(text.strip()) < 150
            and re.match(r"^\d+[A-Za-z]", text.strip())
        )

        if is_footnote:
            removed_blocks.append(text)
        else:
            body_blocks.append(text)

    print("===== 被识别为脚注的内容 =====")

    for text in removed_blocks:
        print(text)

    print("\n===== 统计 =====")
    print("原始文本块数量：", len(blocks))
    print("保留文本块数量：", len(body_blocks))
    print("删除文本块数量：", len(removed_blocks))