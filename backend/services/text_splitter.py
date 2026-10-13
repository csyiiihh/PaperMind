import unicodedata

def split_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
):
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start += chunk_size - chunk_overlap

    return chunks


def split_pages(pages, chunk_size=1000, chunk_overlap=200):

    chunks = []

    chunk_id = 0

    for page in pages:

        text = page["text"]

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[start:end]

            chunks.append({
                "chunk_id": chunk_id,
                "page": page["page"],
                "text": chunk_text
            })

            chunk_id += 1

            start += (
                chunk_size - chunk_overlap
            )

    return chunks




import re

def clean_pdf_text(text: str) -> str:

    # 统一 Unicode 字符，例如 ﬁ → fi、ﬂ → fl
    text = unicodedata.normalize("NFKC", text)

    # 1. 修复英文单词跨行断开
    text = re.sub(
        r"(?<=[A-Za-z])-\s*\n\s*(?=[A-Za-z])",
        "",
        text
    )

    # 2. 保留段落分隔
    text = re.sub(
        r"\n\s*\n+",
        "\n\n",
        text
    )

    # 3. 将普通换行转换为空格
    text = re.sub(
        r"(?<!\n)\n(?!\n)",
        " ",
        text
    )

    # 4. 合并连续空格
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    return text.strip()

def get_overlap(text: str, overlap_size: int) -> str:

    if overlap_size <= 0 or not text:
        return ""

    # 按句子边界拆分
    sentences = re.split(
        r"(?<=[.!?。！？])\s+",
        text.strip()
    )

    selected = []
    total_length = 0

    # 从最后一句开始，向前选取完整句子
    for sentence in reversed(sentences):

        sentence_length = len(sentence)

        if total_length + sentence_length > overlap_size:
            break

        selected.insert(0, sentence)
        total_length += sentence_length + 1

    return " ".join(selected)

def split_text_smart(text: str, chunk_size=1000, chunk_overlap=200):

    if chunk_size <= 0:
        raise ValueError("chunk_size 必须大于 0")

    if not 0 <= chunk_overlap < chunk_size:
        raise ValueError("chunk_overlap 必须小于 chunk_size 且不能为负数")

    # 先清洗 PDF 文本
    text = clean_pdf_text(text)

    # 优先按照段落分割
    paragraphs = re.split(r"\n\s*\n", text)

    # 将过长段落继续按照句子切分
    pieces = []

    for paragraph in paragraphs:
        paragraph = paragraph.strip()

        if not paragraph:
            continue

        sentences = re.split(
            r"(?<=[.!?。！？])\s+",
            paragraph
        )

        for sentence in sentences:
            sentence = sentence.strip()

            if not sentence:
                continue

            # 单句太长时，才使用固定长度切分
            if len(sentence) > chunk_size:
                for start in range(0, len(sentence), chunk_size):
                    pieces.append(sentence[start:start + chunk_size])
            else:
                pieces.append(sentence)

    # 组合成 Chunk
    chunks = []
    current = ""

    for piece in pieces:

        candidate = f"{current} {piece}".strip() if current else piece

        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current)

        # 从上一个 Chunk 末尾保留部分上下文
        overlap = get_overlap(current, chunk_overlap)

        candidate = f"{overlap} {piece}".strip() if overlap else piece

        # 重叠部分过长时，优先保留新内容
        if len(candidate) > chunk_size:
            candidate = piece

        current = candidate

    if current:
        chunks.append(current)

    return chunks


def split_pages_smart(pages, chunk_size=1000, chunk_overlap=200):

    chunks = []
    chunk_id = 0

    references_started = False

    for page in pages:

        # 如果已经进入参考文献章节，后续页面全部跳过
        if references_started:
            break

        text = page["text"]

         # 检查当前页面是否包含参考文献标题
        pattern = r"(?im)^\s*(?:references|bibliography)\s*$"
        match = re.search(pattern, text)

        if match:
            # 保留参考文献标题之前的正文
            text = text[:match.start()]

            # 后续页面不再处理
            references_started = True

        if not text.strip():
            continue

        page_chunks = split_text_smart(
            text,
            chunk_size,
            chunk_overlap
        )

        for chunk_text in page_chunks:

            chunks.append({
                "chunk_id": chunk_id,
                "page": page["page"],
                "text": chunk_text
            })

            chunk_id += 1

    return chunks


def remove_references(text: str) -> str:
    """
    删除从 References 标题开始的参考文献内容。
    适用于包含明确 References 标题的英文论文。
    """

    pattern = r"(?im)^\s*(?:references|bibliography)\s*$"

    match = re.search(pattern, text)

    if match:
        return text[:match.start()].strip()

    return text