
from src.rag_pipeline import run_rag
from src.generator import load_llm


# Dedicated test account.
TEST_USER_ID = "test_user_vector_store"


# Load LLM once.
llm = load_llm()


# Test 1: Relevant question.
question = "What is machine learning?"

result = run_rag(
    question=question,
    llm=llm,
    user_id=TEST_USER_ID
)

print("\nTest 1: Relevant Question")
print("Answer:", result["answer"])
print("Sources:", result["sources"])


# Test 2: Irrelevant question.
question = "Who founded Microsoft?"

result = run_rag(
    question=question,
    llm=llm,
    user_id=TEST_USER_ID
)

print("\nTest 2: Irrelevant Question")
print("Answer:", result["answer"])
print("Sources:", result["sources"])
