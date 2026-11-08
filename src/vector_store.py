
import chromadb

from src.config import CHROMA_DIR, COLLECTION_NAME


def get_chroma_client():
    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    return client


def get_collection():
    client = get_chroma_client()

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    return collection



def add_documents(ids, documents, embeddings, metadatas, *, user_id):
    """Add document chunks belonging to a specific user."""

    if not user_id or not str(user_id).strip():
        raise ValueError("A valid user_id is required.")

    # All input collections must have matching lengths.
    if not (
        len(ids)
        == len(documents)
        == len(embeddings)
        == len(metadatas)
    ):
        raise ValueError(
            "IDs, documents, embeddings and metadata must have matching lengths."
        )

    if not ids:
        raise ValueError("At least one document chunk is required.")

    # Validate metadata before storing anything.
    for metadata in metadatas:
        if not isinstance(metadata, dict):
            raise TypeError("Each metadata entry must be a dictionary.")

    user_metadatas = []

    for metadata in metadatas:
        updated_metadata = metadata.copy()
        updated_metadata["user_id"] = str(user_id)
        user_metadatas.append(updated_metadata)

    collection = get_collection()

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=user_metadatas
    )


def get_collection_count(user_id):
    """Return the chunk count for a specific user only."""

    if not user_id:
        raise ValueError("A valid user_id is required.")

    collection = get_collection()

    results = collection.get(
        where={"user_id": str(user_id)},
        include=["metadatas"]
    )

    return len(results["ids"])
