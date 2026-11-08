from src.embeddings import (
    load_embedding_model,
    generate_embeddings,
    generate_query_embedding
)

model = load_embedding_model()

texts = [
    "Machine learning learns patterns from data.",
    "Neural networks use interconnected layers."
]
embedding=generate_embeddings(model,texts)

print("Embedding shape:", embedding.shape)
print("Number of embeddings:", len(embedding))

query = "What is machine learning?"

query_embedding = generate_query_embedding(model, query)

print("Query embedding shape:", query_embedding.shape)
