from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


sentences = [
    "Residual networks are easier to optimize.",
    "ResNet uses residual connections.",
    "The cat is sleeping on the sofa.",
]


embeddings = model.encode(sentences)


similarity_01 = cos_sim(
    embeddings[0],
    embeddings[1]
)

similarity_02 = cos_sim(
    embeddings[0],
    embeddings[2]
)


print(
    "句子1和句子2相似度:",
    similarity_01.item()
)

print(
    "句子1和句子3相似度:",
    similarity_02.item()
)