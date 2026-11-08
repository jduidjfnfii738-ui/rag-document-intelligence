
from pathlib import Path
import uuid

from src.document_loader import load_document
from src.text_splitter import split_text

from src.embeddings import (
    load_embedding_model,
    generate_embeddings
)

from src.vector_store import add_documents

from src.document_manager import (
    calculate_file_hash,
    find_duplicate_document
)


embedding_model = load_embedding_model()


def ingest_document(
    file_path: Path,
    user_id: str,
    skip_duplicate_check=False
):
    """Load, chunk, embed and store a document for one user."""


    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("A valid user_id is required.")

    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(
            f"Document file does not exist: {file_path}"
        )


    documents = load_document(file_path)


    if not documents:
        raise ValueError("No readable content found in the document.")

    for document in documents:
        if not isinstance(document, dict):
            raise TypeError("Each loaded document must be a dictionary.")

        if not isinstance(document.get("text"), str):
            raise ValueError("Document text must be a string.")

        if not document["text"].strip():
            raise ValueError("Document contains empty text.")

        if not isinstance(document.get("metadata"), dict):
            raise ValueError("Document metadata must be a dictionary.")


    file_hash = calculate_file_hash(file_path)

    # Check duplicates only within this user's documents.
    if not skip_duplicate_check:

        duplicate = find_duplicate_document(
            file_hash,
            user_id=user_id
        )

        if duplicate:
            return {
                "source": file_path.name,
                "status": "duplicate",
                "existing_document_id": duplicate["document_id"]
            }

    document_id = str(uuid.uuid4())

    # The parent folder uniquely identifies the uploaded file folder.
    upload_folder_id = file_path.parent.name

    if not upload_folder_id or upload_folder_id in {".", ".."}:
        raise ValueError("Invalid upload folder identifier.")


    all_chunks = []

    for document in documents:

        chunks = split_text(document["text"])

        for chunk_id, chunk in enumerate(chunks, start=1):

            all_chunks.append({
                "text": chunk,
                "metadata": {
                    **document["metadata"],
                    "document_id": document_id,
                    "file_hash": file_hash,
                    "upload_folder_id": upload_folder_id,
                    "chunk_id": chunk_id
                }
            })

    if not all_chunks:
        raise ValueError(
            "No text chunks were generated from the document."
        )

    texts = [
        chunk["text"]
        for chunk in all_chunks
    ]

    embeddings = generate_embeddings(
        embedding_model,
        texts
    )


    if len(embeddings) != len(texts):
        raise ValueError(
            "The number of embeddings does not match the number of text chunks."
        )


    ids = [
        f"{document_id}_{i}"
        for i in range(len(all_chunks))
    ]

    metadatas = [
        {
            key: value
            for key, value in chunk["metadata"].items()
            if value is not None
        }
        for chunk in all_chunks
    ]

    add_documents(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        user_id=user_id
    )

    return {
        "document_id": document_id,
        "upload_folder_id": upload_folder_id,
        "source": file_path.name,
        "chunks_created": len(all_chunks),
        "status": "success"
    }
