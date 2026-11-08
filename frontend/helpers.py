
from pathlib import Path

import streamlit as st


# =====================================================
# 1. FRONTEND PATHS
# =====================================================

FRONTEND_DIR = Path(__file__).resolve().parent

CSS_FILE = FRONTEND_DIR / "styles.css"


# =====================================================
# 2. LOAD CSS
# =====================================================

def load_css():
    """
    Read the application's CSS file.

    Returns:
        str: CSS content.

    Raises:
        FileNotFoundError: If styles.css does not exist.
    """

    if not CSS_FILE.exists():
        raise FileNotFoundError(
            f"CSS file not found: {CSS_FILE}"
        )

    return CSS_FILE.read_text(encoding="utf-8")


# =====================================================
# 3. APPLY CSS
# =====================================================

def inject_custom_css():
    """
    Load and inject custom CSS into Streamlit.
    """

    css = load_css()

    st.markdown(
        f"""
        <style>
        {css}
        </style>
        """,
        unsafe_allow_html=True
    )


# =====================================================
# 4. INITIALIZE SESSION STATE
# =====================================================


def initialize_session_state():
    """
    Initialize application-wide session state.
    """

    defaults = {
        "messages": lambda: [],
        "current_page": "Dashboard",
        "uploaded_documents": lambda: [],
        "last_question": None,
        "last_answer": None,
    }

    for key, default_value in defaults.items():

        if key not in st.session_state:

            if callable(default_value):
                st.session_state[key] = default_value()
            else:
                st.session_state[key] = default_value


# =====================================================
# 5. FORMAT FILE SIZE
# =====================================================

def format_file_size(size_in_bytes):
    """
    Convert bytes into a readable file size.

    Examples:
        1024 -> 1.00 KB
        1048576 -> 1.00 MB
    """

    if size_in_bytes < 0:
        return "Unknown size"

    units = ["B", "KB", "MB", "GB", "TB"]

    size = float(size_in_bytes)

    for unit in units:

        if size < 1024 or unit == "TB":
            return f"{size:.2f} {unit}"

        size /= 1024

    return "Unknown size"


# =====================================================
# 6. FORMAT DOCUMENT COUNT
# =====================================================

def format_document_count(count):
    """
    Return a readable document count.
    """

    count = int(count)

    if count == 1:
        return "1 document"

    return f"{count:,} documents"


# =====================================================
# 7. RESET CHAT
# =====================================================

def reset_chat():
    """
    Clear the current chat session.
    """

    st.session_state.messages = []

    st.session_state.last_question = None

    st.session_state.last_answer = None
