from llama_cpp import Llama

from src.config import MODEL_PATH

def load_llm():
    llm=Llama(
        model_path=str(MODEL_PATH),
        n_ctx=2048,
        n_batch=64,
        n_threads=2,
        verbose=False
    )

    return llm


def generate_answer(llm, context, question):
    response = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict document-based question answering assistant. "

                    "RULE 1: CONTEXT IS THE ONLY SOURCE OF TRUTH. "
                    "Use only the information explicitly provided in the context. "
                    "Never use pretrained knowledge, memory, assumptions, or outside information. "

                    "RULE 2: NO UNSUPPORTED FACTS. "
                    "Every factual claim must be directly supported by the context. "
                    "Never invent or add names, dates, numbers, events, explanations, "
                    "or other details that are not present in the context. "

                    "RULE 3: PARTIAL INFORMATION. "
                    "If the context answers only part of the question, "
                    "answer only the supported part. "
                    "For each missing part, explicitly state that the provided documents "
                    "do not contain that information. "
                    "Never fill missing information using your pretrained knowledge. "

                    "RULE 4: NO RELEVANT INFORMATION. "
                    "If the context does not contain the answer, respond exactly with: "
                    "'I don't have enough information in the provided documents.' "

                    "RULE 5: CONTRADICTORY INFORMATION. "
                    "If the provided context contains conflicting statements "
                    "about the same fact, do not choose one statement as correct. "
                    "Do not combine conflicting statements into a single answer "
                    "as if both are true. "
                    "Clearly inform the user that the provided documents contain "
                    "conflicting information and identify the conflicting claims. "
                    "Do not resolve the contradiction using pretrained knowledge "
                    "or outside information. "

                    "RULE 6: FINAL ANSWER CHECK. "
                    "Before responding, verify that every factual statement is supported "
                    "by the context. Remove any unsupported statement. "

                    "Keep the answer concise and do not discuss information outside the context."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Context:\n{context}\n\n"
                    f"Question:\n{question}"
                )
            }
        ],
        max_tokens=128,
        temperature=0.1,
        repeat_penalty=1.15
    )

    return response["choices"][0]["message"]["content"].strip()
