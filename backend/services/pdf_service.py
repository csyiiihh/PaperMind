
import re
import pymupdf


def is_footnote_block(block):
    """判断文本块是否为疑似脚注（实验性规则）。"""

    x0, y0, x1, y1, text, *rest = block

    text = text.strip()

    return (
        y0 > 690
        and len(text) < 150
        and re.match(r"^\d+[A-Za-z]", text) is not None
    )


def extract_pages_from_pdf(file_path, remove_footnotes=False):

    pages = []

    with pymupdf.open(file_path) as document:

        for page_number, page in enumerate(document, start=1):

            if remove_footnotes:

                blocks = page.get_text("blocks")

                # 保留普通文本块，过滤疑似脚注
                texts = []

                for block in blocks:

                    # 只处理文本类型的 block
                    if block[6] != 0:
                        continue

                    if is_footnote_block(block):
                        continue

                    texts.append(block[4])

                page_text = "\n".join(texts)

            else:
                # 保持原来的提取方式
                page_text = page.get_text()

            pages.append({
                "page": page_number,
                "text": page_text
            })

    return pages
