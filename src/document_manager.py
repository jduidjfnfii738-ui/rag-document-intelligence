
from src.vector_store import get_collection
from src.config import DATA_DIR

import hashlib
import uuid
import shutil
from pathlib import Path


UPLOAD_DIR = DATA_DIR / "uploads"


def list_documents(user_id: str):
    """List documents belonging to a specific user."""

    if not user_id:
        raise ValueError("A valid user_id is required.")

    collection = get_collection()

    results = collection.get(
        where={"user_id": str(user_id)},
        include=["metadatas"]
    )

    documents = {}

    for metadata in results["metadatas"]:

        document_id = metadata.get("document_id")

        if document_id is None:
            continue

        if document_id not in documents:

            documents[document_id] = {
                "document_id": document_id,
                "source": metadata.get("source", "Unknown"),
                "upload_folder_id": metadata.get("upload_folder_id"),
                "chunks": 0
            }

        documents[document_id]["chunks"] += 1

    return list(documents.values())


def delete_document(document_id: str, user_id: str):
    """Delete a user's document from ChromaDB and its upload folder."""

    if not user_id:
        raise ValueError("A valid user_id is required.")

    if not document_id:
        raise ValueError("A valid document_id is required.")

    collection = get_collection()

    # Verify ownership and retrieve upload-folder metadata.
    results = collection.get(
        where={
            "$and": [
                {"document_id": document_id},
                {"user_id": str(user_id)}
            ]
        },
        include=["metadatas"]
    )

    if not results["ids"]:
        raise ValueError("Document not found for this user.")

    metadatas = results["metadatas"]

    upload_folder_ids = {
        metadata.get("upload_folder_id")
        for metadata in metadatas
        if metadata.get("upload_folder_id")
    }

    # Delete only the authenticated user's chunks.
    collection.delete(
        where={
            "$and": [
                {"document_id": document_id},
                {"user_id": str(user_id)}
            ]
        }
    )

    # Remove the corresponding uploaded folder safely.
    user_upload_dir = UPLOAD_DIR / str(user_id)

    for folder_id in upload_folder_ids:

        # Prevent path traversal outside the user's upload directory.
        folder_path = Path(folder_id)

        if (
            folder_path.name != folder_id
            or folder_id in {".", ".."}
        ):
            raise ValueError("Invalid upload folder identifier.")

        upload_folder = user_upload_dir / folder_id

        if upload_folder.exists() and upload_folder.is_dir():
            shutil.rmtree(upload_folder)


def calculate_file_hash(file_path: Path):
    """Calculate SHA-256 hash of a file."""

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        for chunk in iter(lambda: file.read(4096), b""):
            sha256.update(chunk)

    return sha256.hexdigest()



def find_duplicate_document(file_hash: str, user_id: str):
    """Find duplicate documents within the user's own data."""

    if not user_id:
        raise ValueError("A valid user_id is required.")

    if not file_hash or not isinstance(file_hash, str):
        raise ValueError("A valid file hash is required.")

    collection = get_collection()

    results = collection.get(
        where={
            "$and": [
                {"file_hash": file_hash},
                {"user_id": str(user_id)}
            ]
        },
        include=["metadatas"],
        limit=1
    )

    if not results["metadatas"]:
        return None

    metadata = results["metadatas"][0]

    return {
        "document_id": metadata["document_id"],
        "source": metadata.get("source", "Unknown")
    }




def reindex_document(
    document_id: str,
    file_path: Path,
    user_id: str
):
    """Reindex a document using a separate upload folder."""

    if not user_id:
        raise ValueError("A valid user_id is required.")

    if not document_id:
        raise ValueError("A valid document_id is required.")

    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError("The document file does not exist.")

    user_documents = list_documents(user_id)

    document_exists = any(
        document["document_id"] == document_id
        for document in user_documents
    )

    if not document_exists:
        raise ValueError("Document not found for this user.")

    from src.ingestion import ingest_document

    # Create a completely separate folder for the new index.
    new_folder_id = str(uuid.uuid4())

    new_folder = UPLOAD_DIR / str(user_id) / new_folder_id

    new_folder.mkdir(parents=True, exist_ok=False)

    new_file_path = new_folder / file_path.name

    try:
        # Preserve the original file.
        shutil.copy2(file_path, new_file_path)

        # Index the copied file.
        result = ingest_document(
            new_file_path,
            user_id=user_id,
            skip_duplicate_check=True
        )

    except Exception:
        # Clean up the new folder if ingestion fails.
        if new_folder.exists():
            shutil.rmtree(new_folder)

        raise

    if result["status"] != "success":
        if new_folder.exists():
            shutil.rmtree(new_folder)

        return result

    # Delete the old document only after successful ingestion.
    # Its folder is different from the new document's folder.
    delete_document(
        document_id,
        user_id=user_id
    )

    return result
