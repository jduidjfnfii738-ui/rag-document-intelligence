
import html

import streamlit as st

from src.generator import load_llm
from src.rag_pipeline import run_rag

from frontend.components import (
    render_section_header,
    render_empty_state,
)

from frontend.helpers import reset_chat


# =====================================================
# 1. LOAD LANGUAGE MODEL
# =====================================================

@st.cache_resource(show_spinner="Preparing AI assistant...")
def get_cached_llm():
    """
    Load the local language model once.

    The cached model is reused across Streamlit reruns.
    """

    return load_llm()


# =====================================================
# 2. DISPLAY CHAT SOURCES
# =====================================================

def render_sources(sources):
    """Display document citations associated with an answer."""

    if not sources:
        return

    with st.expander(
        f"📚 View sources ({len(sources)})"
    ):
        for index, source in enumerate(sources, start=1):
            safe_source = html.escape(str(source))

            st.html(
                f"""
                <div class="source-item">
                    <span class="source-number">
                        {index}.
                    </span>

                    <span class="source-name">
                        {safe_source}
                    </span>
                </div>
                """
            )


# =====================================================
# 3. DISPLAY SINGLE MESSAGE
# =====================================================

def render_message(message):
    """
    Render one user or assistant message.

    Message structure:
        {
            "role": "user" or "assistant",
            "content": "...",
            "sources": []
        }
    """

    role = message.get("role", "assistant")

    content = message.get("content", "")

    if role not in ["user", "assistant"]:
        return

    with st.chat_message(role):

        # Markdown is intentional here because answers
        # may contain headings, lists and code blocks.
        st.markdown(content)

        if role == "assistant":
            render_sources(
                message.get("sources", [])
            )


# =====================================================
# 4. DISPLAY CHAT HISTORY
# =====================================================

def render_chat_history():
    """Display all messages stored in session state."""

    messages = st.session_state.messages

    if not messages:
        render_empty_state(
            title="Start a conversation",
            description=(
                "Ask questions about your uploaded documents. "
                "Your AI assistant will retrieve relevant "
                "information and generate an answer."
            ),
            icon="💬",
        )

        return

    for message in messages:
        render_message(message)


# =====================================================
# 5. PROCESS USER QUESTION
# =====================================================


def process_question(question):
    """
    Execute the RAG pipeline for the authenticated user.

    1. Validate the user's session.
    2. Save the user question.
    3. Load the cached language model.
    4. Run user-specific retrieval and generation.
    5. Save the answer and its sources.
    """

    question = question.strip()

    if not question:
        return

    # Get authenticated user ID from session state.
    user_id = st.session_state.get("user_id")

    if not user_id:
        st.error("Your session has expired. Please log in again.")

        for key in [
            "authenticated",
            "user_id",
            "user_email",
            "messages",
            "uploaded_documents",
            "last_question",
            "last_answer",
            "current_page",
            "page_navigation",
        ]:
            st.session_state.pop(key, None)

        st.rerun()

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
            "sources": [],
        }
    )

    try:
        with st.spinner(
            "Searching your documents and generating an answer..."
        ):
            llm = get_cached_llm()

            result = run_rag(
                question=question,
                llm=llm,
                user_id=user_id,
            )

        answer = result.get(
            "answer",
            "I could not generate an answer.",
        )

        sources = result.get(
            "sources",
            [],
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": sources,
            }
        )

        st.session_state.last_question = question
        st.session_state.last_answer = answer

    except Exception as error:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": (
                    "Something went wrong while processing "
                    "your question. Please try again."
                ),
                "sources": [],
            }
        )

        st.error(
            "An error occurred while running the RAG pipeline."
        )

        st.exception(error)


# =====================================================
# 6. CHAT CONTROLS
# =====================================================

def render_chat_controls():
    """Render chat actions."""

    left_column, right_column = st.columns([4, 1])

    with left_column:
        st.caption(
            "Answers are generated using your indexed documents."
        )

    with right_column:
        if st.button(
            "Clear chat",
            use_container_width=True,
            key="clear_chat_button",
        ):
            reset_chat()
            st.rerun()


# =====================================================
# 7. MAIN CHAT INTERFACE
# =====================================================


def render_chat_interface():
    """Render the complete AI chat page."""

    user_id = st.session_state.get("user_id")

    if (
        not st.session_state.get("authenticated", False)
        or not user_id
    ):
        st.error("Please log in to access the chat.")
        st.stop()

    render_section_header(
        eyebrow="AI ASSISTANT",
        title="Chat with your Documents",
        description=(
            "Ask questions in natural language and get "
            "answers grounded in your document collection."
        ),
    )

    render_chat_controls()

    st.divider()

    render_chat_history()

    question = st.chat_input(
        "Ask something about your documents...",
        key="document_chat_input",
    )

    if question:
        process_question(question)
        st.rerun()
