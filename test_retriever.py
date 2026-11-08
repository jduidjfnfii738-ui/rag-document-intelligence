
from src.retriever import (
    retrieve_documents,
    has_relevant_context
)


# Dedicated test account.
TEST_USER_ID = "test_user_vector_store"

query = "What is machine learning?"

results = retrieve_documents(
    query,
    user_id=TEST_USER_ID
)

is_relevant = has_relevant_context(results)

print("Relevant context:", is_relevant)

print("\nRetrieved results:")
print(results)

print("\nDistances:")
print(results["distances"])
