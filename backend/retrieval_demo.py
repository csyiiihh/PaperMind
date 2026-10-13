from services.pdf_service import extract_text_from_pdf
from services.text_splitter import split_text
from services.retrieval_service import retrieve_chunks


PDF_PATH = (
    "uploads/"
    "He 等 - 2016 - Deep Residual Learning for Image Recognition.pdf"
)


text = extract_text_from_pdf(PDF_PATH)

chunks = split_text(text)


query = "残差学习解决了什么问题？"


results = retrieve_chunks(
    query=query,
    chunks=chunks,
    top_k=3
)


print("用户问题:")
print(query)

print("\n检索结果:")


for result in results:

    print("\n--------------------------")

    print(
        "Chunk:",
        result["chunk_id"]
    )

    print(
        "Score:",
        result["score"]
    )

    print(
        "Text:"
    )

    print(
        result["text"]
    )