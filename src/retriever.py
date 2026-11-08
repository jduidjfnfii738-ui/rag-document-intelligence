
from src.vector_store import get_collection

from src.config import (
    TOP_K,
    DISTANCE_THRESHOLD
)

from src.embeddings import (
    load_embedding_model,
    generate_query_embedding
)


embedding_model = load_embedding_model()


def retrieve_documents(query: str, user_id: str):
    """Retrieve relevant documents belonging only to one user."""

    if not user_id:
        raise ValueError("A valid user_id is required.")

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    collection = get_collection()

    query_embedding = generate_query_embedding(
        embedding_model,
        query
    )

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=TOP_K,
        where={"user_id": str(user_id)}
    )

    return results


def has_relevant_context(results):
    """Check whether retrieved context meets the distance threshold."""

    distances = results["distances"]

    if not distances or not distances[0]:
        return False

    best_distance = min(distances[0])

    return best_distance <= DISTANCE_THRESHOLD



def filter_relevant_documents(results):
    """Keep only documents within the relevance threshold."""

    distances = results.get("distances") or [[]]
    documents = results.get("documents") or [[]]
    metadatas = results.get("metadatas") or [[]]

    if not distances[0] or not documents[0] or not metadatas[0]:
        return {
            "documents": [],
            "metadatas": []
        }

    distances = distances[0]
    documents = documents[0]
    metadatas = metadatas[0]

    if not (
        len(distances)
        == len(documents)
        == len(metadatas)
    ):
        raise ValueError("Retrieved results have inconsistent lengths.")

    relevant_documents = []
    relevant_metadatas = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):
        if distance <= DISTANCE_THRESHOLD:
            relevant_documents.append(document)
            relevant_metadatas.append(metadata)

    return {
        "documents": relevant_documents,
        "metadatas": relevant_metadatas
    }
