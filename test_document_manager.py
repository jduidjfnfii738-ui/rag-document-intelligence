
from pathlib import Path

from src.document_manager import (
    list_documents,
    delete_document,
    calculate_file_hash,
    find_duplicate_document,
    reindex_document
)

from src.ingestion import ingest_document
from src.vector_store import get_collection


# Dedicated test account.
TEST_USER_ID = "test_user_document_manager"

file_path = Path("data/sample.pdf")


# 1. List documents belonging to the test user.
documents = list_documents(
    user_id=TEST_USER_ID
)

print("Stored Test Documents:")

for document in documents:
    print(document)


# 2. Calculate file hash.
file_hash = calculate_file_hash(file_path)

duplicate = find_duplicate_document(
    file_hash,
    user_id=TEST_USER_ID
)

print("\nDuplicate Detection Result:")
print(duplicate)


# 3. Ingest document.
result = ingest_document(
    file_path,
    user_id=TEST_USER_ID
)

print("\nNew Ingestion Result:")
print(result)


# 4. Check duplicate detection.
duplicate = find_duplicate_document(
    file_hash,
    user_id=TEST_USER_ID
)

print("\nDuplicate Detection After Ingestion:")
print(duplicate)


# 5. Try uploading the same document again.
duplicate_result = ingest_document(
    file_path,
    user_id=TEST_USER_ID
)

print("\nDuplicate Upload Result:")
print(duplicate_result)


# 6. Reindex the document.
if duplicate_result["status"] == "duplicate":

    test_document_id = duplicate_result["existing_document_id"]

    print("\nDocument selected for re-indexing:")
    print(test_document_id)

    reindex_result = reindex_document(
        document_id=test_document_id,
        file_path=file_path,
        user_id=TEST_USER_ID
    )

    print("\nRe-indexing Result:")
    print(reindex_result)

    # Verify old and new records.
    collection = get_collection()

    old_record = collection.get(
        where={
            "$and": [
                {"document_id": test_document_id},
                {"user_id": TEST_USER_ID}
            ]
        }
    )

    new_record = collection.get(
        where={
            "$and": [
                {"document_id": reindex_result["document_id"]},
                {"user_id": TEST_USER_ID}
            ]
        }
    )

    print("\nOld document records:", len(old_record["ids"]))
    print("New document records:", len(new_record["ids"]))

    # 7. Delete the re-indexed test document.
    delete_document(
        reindex_result["document_id"],
        user_id=TEST_USER_ID
    )

    remaining_documents = list_documents(
        user_id=TEST_USER_ID
    )

    print("\nDocuments after deletion:")

    for document in remaining_documents:
        print(document)

else:
    print("\nIngestion did not return a duplicate result.")

from pathlib import Path

from src.document_manager import (
    list_documents,
    delete_document,
    calculate_file_hash,
    find_duplicate_document,
    reindex_document
)

from src.ingestion import ingest_document
from src.vector_store import get_collection


# Dedicated test account.
TEST_USER_ID = "test_user_document_manager"

file_path = Path("data/sample.pdf")


# 1. List documents belonging to the test user.
documents = list_documents(
    user_id=TEST_USER_ID
)

print("Stored Test Documents:")

for document in documents:
    print(document)


# 2. Calculate file hash.
file_hash = calculate_file_hash(file_path)

duplicate = find_duplicate_document(
    file_hash,
    user_id=TEST_USER_ID
)

print("\nDuplicate Detection Result:")
print(duplicate)


# 3. Ingest document.
result = ingest_document(
    file_path,
    user_id=TEST_USER_ID
)

print("\nNew Ingestion Result:")
print(result)


# 4. Check duplicate detection.
duplicate = find_duplicate_document(
    file_hash,
    user_id=TEST_USER_ID
)

print("\nDuplicate Detection After Ingestion:")
print(duplicate)


# 5. Try uploading the same document again.
duplicate_result = ingest_document(
    file_path,
    user_id=TEST_USER_ID
)

print("\nDuplicate Upload Result:")
print(duplicate_result)


# 6. Reindex the document.
if duplicate_result["status"] == "duplicate":

    test_document_id = duplicate_result["existing_document_id"]

    print("\nDocument selected for re-indexing:")
    print(test_document_id)

    reindex_result = reindex_document(
        document_id=test_document_id,
        file_path=file_path,
        user_id=TEST_USER_ID
    )

    print("\nRe-indexing Result:")
    print(reindex_result)

    # Verify old and new records.
    collection = get_collection()

    old_record = collection.get(
        where={
            "$and": [
                {"document_id": test_document_id},
                {"user_id": TEST_USER_ID}
            ]
        }
    )

    new_record = collection.get(
        where={
            "$and": [
                {"document_id": reindex_result["document_id"]},
                {"user_id": TEST_USER_ID}
            ]
        }
    )

    print("\nOld document records:", len(old_record["ids"]))
    print("New document records:", len(new_record["ids"]))

    # 7. Delete the re-indexed test document.
    delete_document(
        reindex_result["document_id"],
        user_id=TEST_USER_ID
    )

    remaining_documents = list_documents(
        user_id=TEST_USER_ID
    )

    print("\nDocuments after deletion:")

    for document in remaining_documents:
        print(document)

else:
    print("\nIngestion did not return a duplicate result.")
