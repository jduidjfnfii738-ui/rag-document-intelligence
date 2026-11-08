from src.generator import load_llm,generate_answer

llm = load_llm()


context = """
Python was created by Guido van Rossum.
Python was created by James Gosling.
"""

question = "Who created Python?"

answer = generate_answer(
    llm,
    context,
    question
)

print("Generated answer:")
print(answer)


answer_lower = answer.lower()

has_definition = (
    "machine learning" in answer_lower
    and "learn patterns from data" in answer_lower
)

mentions_missing_info = (
    "do not contain information" in answer_lower
    and "who invented machine learning" in answer_lower
)

if has_definition and mentions_missing_info:
    print("Test Passed: Model answered using context and identified missing information.")
else:
    print("Test Failed: Model did not satisfy all requirements.")
