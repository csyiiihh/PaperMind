def build_rag_prompt(question:str, chunks:list):

    context_parts = []

    for chunk in chunks:

        chunk_id = chunk["chunk_id"]
        page = chunk["page"]
        text = chunk["text"]

        context_parts.append(
            f"[Chunk {chunk_id} | PDF第{page}页]\n{text}"
        )

        context = "\n\n".join(context_parts)

    prompt = f"""
                请根据以下论文片段回答用户问题。

                论文片段：
                {context}

                用户问题：
                {question}

                回答要求：
                1. 使用中文回答。
                2. 只依据提供的论文片段，不要补充未经证实的内容。
                3. 引用论文内容时标注对应 PDF 页码。
                4. 如果论文片段不足以回答问题，明确说明证据不足。
                5. 不要编造论文内容或页码。
            """

    return prompt