from src.generator import load_llm
from src.validator import validate_answer


llm = load_llm()

context = """
Python is a high-level programming language.
Python was created by Guido van Rossum.
"""

answer = """
Python was released in 1991.
"""

result = validate_answer(
    llm,
    context,
    answer
)

print("Validation Result:")
print(result)
