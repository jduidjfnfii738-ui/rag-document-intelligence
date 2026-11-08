
from src.retriever import (
    retrieve_documents,
    filter_relevant_documents
)

from src.generator import (
    generate_answer
)



def run_rag(question: str, llm, user_id: str):
    """Run RAG using only the authenticated user's documents."""

    if not user_id:
        raise ValueError("A valid user_id is required.")

    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question cannot be empty.")

    if llm is None:
        raise ValueError("A valid language model is required.")

    results = retrieve_documents(
        question,
        user_id=user_id
    )

    filtered_results = filter_relevant_documents(results)

    if not filtered_results["documents"]:
        return {
            "answer": "I don't have enough information in the provided documents.",
            "sources": []
        }

    documents = filtered_results["documents"]
    metadatas = filtered_results["metadatas"]

    sources = []
    seen_sources = set()

    for metadata in metadatas:

        source = metadata.get("source", "Unknown")
        page = metadata.get("page", "Unknown")

        source_key = (source, page)

        if source_key not in seen_sources:
            seen_sources.add(source_key)

            sources.append({
                "source": source,
                "page": page
            })

    context = "\n\n".join(documents)

    answer = generate_answer(
        llm,
        context,
        question
    )

    formatted_sources = [
        f"{citation['source']} — Page {citation['page']}"
        for citation in sources
    ]

    return {
        "answer": answer,
        "sources": formatted_sources
    }
