
import uuid

from src.vector_store import (
    get_collection,
    get_collection_count,
    add_documents
)

from src.embeddings import (
    load_embedding_model,
    generate_embeddings
)


# Dedicated test account and unique test run.
TEST_USER_ID = "test_user_vector_store"
TEST_RUN_ID = str(uuid.uuid4())

texts = [
    "Machine learning learns patterns from data.",
    "Neural networks use interconnected layers."
]

ids = [
    f"{TEST_RUN_ID}_chunk_1",
    f"{TEST_RUN_ID}_chunk_2"
]

metadatas = [
    {
        "source": "test.txt",
        "page": 1,
        "test_run_id": TEST_RUN_ID
    },
    {
        "source": "test.txt",
        "page": 1,
        "test_run_id": TEST_RUN_ID
    }
]


# 1. Generate embeddings.
model = load_embedding_model()

embeddings = generate_embeddings(
    model,
    texts
)


# 2. Get ChromaDB collection.
collection = get_collection()


# 3. Store documents for the test user.
add_documents(
    ids=ids,
    documents=texts,
    embeddings=embeddings.tolist(),
    metadatas=metadatas,
    user_id=TEST_USER_ID
)

print("Documents stored successfully!")


# 4. Count only this test user's chunks.
print(
    "Test user chunk count:",
    get_collection_count(TEST_USER_ID)
)


# 5. Retrieve the test records.
results = collection.get(
    ids=ids,
    include=["documents", "metadatas"]
)

print("Retrieved documents:", results["documents"])
print("Retrieved metadata:", results["metadatas"])


# 6. Clean up only this test run's records.
collection.delete(
    where={
        "$and": [
            {"user_id": TEST_USER_ID},
            {"test_run_id": TEST_RUN_ID}
        ]
    }
)

print("Test records cleaned up.")
