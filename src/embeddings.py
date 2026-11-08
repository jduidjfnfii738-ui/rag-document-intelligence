from sentence_transformers import SentenceTransformer

from src.config import EMBEDDING_MODEL_NAME

def load_embedding_model():
    model=SentenceTransformer(EMBEDDING_MODEL_NAME)

    return model

def generate_embeddings(model,texts):
    embeddings=model.encode(texts)

    return embeddings

def generate_query_embedding(model,query):
    embedding=model.encode(query)

    return embedding
