import re
from collections import Counter

from services.pdf_service import extract_pages_from_pdf

PAPER_ID = "96a453e6-9e85-4aef-9545-75487b7aa4dc"
PDF_PATH = f"uploads/{PAPER_ID}.pdf"

original_pages = extract_pages_from_pdf(
    PDF_PATH,
    remove_footnotes=False
)

clean_pages = extract_pages_from_pdf(
    PDF_PATH,
    remove_footnotes=True
)

# 我们已经确认的三条脚注内容
known_footnotes = {
    1: [
        "1http://image-net.org/challenges/LSVRC/2015/\nand\nhttp://mscoco.org/dataset/#detections-challenge2015."
    ],
    3: [
        "2This hypothesis, however, is still an open question. See [28]."
    ],
    7: [
        "5With an initial learning rate of 0.1, it starts converging (<90% error)\nafter several epochs, but still reaches similar accuracy."
    ]
}


def words(text):
    return Counter(
        re.findall(r"[A-Za-z]+", text.lower())
    )


for original, clean in zip(original_pages, clean_pages):

    page_num = original["page"]

    # 从原始文本中排除已知脚注
    expected_text = original["text"]

    for footnote in known_footnotes.get(page_num, []):
        expected_text = expected_text.replace(footnote, "")

    expected_words = words(expected_text)
    actual_words = words(clean["text"])

    missing = expected_words - actual_words
    extra = actual_words - expected_words

    print(f"\n===== 第 {page_num} 页 =====")
    print("缺失单词数量：", sum(missing.values()))
    print("额外单词数量：", sum(extra.values()))

    if missing:
        print("缺失示例：", missing.most_common(10))

    if extra:
        print("额外示例：", extra.most_common(10))