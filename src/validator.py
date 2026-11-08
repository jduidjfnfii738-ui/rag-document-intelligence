
def validate_answer(llm, context, answer):

    system_prompt = (
        "You are a strict evidence-based factual claim validator. "

        "RULE 1: CONTEXT IS THE ONLY SOURCE OF TRUTH. "
        "Use only the provided context to verify claims. "
        "Never use pretrained knowledge, memory, assumptions, "
        "or outside information. "

        "RULE 2: CHECK EVERY CLAIM SEPARATELY. "
        "Break the generated answer into individual factual claims. "
        "Verify each claim independently against the context. "

        "RULE 3: REQUIRE EXPLICIT EVIDENCE. "
        "A claim is SUPPORTED only when the context explicitly "
        "provides evidence for it. Do not rely on general knowledge "
        "or assume that a fact is correct. "

        "RULE 4: STRICT CLASSIFICATION. "
        "If even one factual claim is unsupported, classify the "
        "entire answer as UNSUPPORTED. "

        "RULE 5: NO GUESSING. "
        "Never classify a claim as SUPPORTED merely because it "
        "sounds plausible or is factually correct in the real world. "

        "RULE 6: OUTPUT FORMAT. "
        "Return exactly one label: SUPPORTED or UNSUPPORTED. "
        "Do not include explanations or additional text."
    )

    user_prompt = f"""
Context:
{context}

Generated Answer:
{answer}

Validation Task:
Check every factual claim in the generated answer against
the provided context.

If all factual claims are explicitly supported, return:
SUPPORTED

If even one factual claim is not explicitly supported, return:
UNSUPPORTED
"""

    response = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        max_tokens=20,
        temperature=0.0
    )

    result = (
        response["choices"][0]["message"]["content"]
        .strip()
        .upper()
    )

    if result == "SUPPORTED":
        return "SUPPORTED"

    return "UNSUPPORTED"
