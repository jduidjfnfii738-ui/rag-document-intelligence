
"""
RAG Document Intelligence
Main dashboard and application page routing.
"""

import streamlit as st

from src.document_manager import list_documents
from src.vector_store import get_collection_count

from frontend.components import (
    render_section_header,
    render_stat_card,
    render_brand,
    render_sidebar_navigation,
    render_footer,
)

from frontend.document_panel import render_document_panel
from frontend.chat_interface import render_chat_interface

from frontend.helpers import (
    initialize_session_state,
    inject_custom_css,
)


# =====================================================
# 1. APPLICATION CONSTANTS
# =====================================================

APP_NAME = "RAG Intelligence"

PAGE_DASHBOARD = "Dashboard"
PAGE_CHAT = "AI Chat"
PAGE_DOCUMENTS = "Documents"
PAGE_SETTINGS = "Settings"

AVAILABLE_PAGES = (
    PAGE_DASHBOARD,
    PAGE_CHAT,
    PAGE_DOCUMENTS,
    PAGE_SETTINGS,
)

# This must match the key used by the sidebar radio widget
NAVIGATION_STATE_KEY = "page_navigation"


# =====================================================
# 2. PAGE CONFIGURATION
# =====================================================

def configure_page():
    """Configure the Streamlit application."""

    st.set_page_config(
        page_title=APP_NAME,
        page_icon="✦",
        layout="wide",
        initial_sidebar_state="expanded",
    )


# =====================================================
# 3. APPLICATION INITIALIZATION
# =====================================================

def initialize_application():
    """Initialize session state and application styling."""

    initialize_session_state()

    # Ensure the current page always has a valid value.
    if st.session_state.current_page not in AVAILABLE_PAGES:
        st.session_state.current_page = PAGE_DASHBOARD

    inject_custom_css()


# =====================================================
# 4. CENTRALIZED NAVIGATION
# =====================================================

def navigate_to_page(page_name):
    """
    Navigate to a page and synchronize both navigation states.

    This function is used by dashboard buttons.
    It runs as a Streamlit button callback before rerun.
    """

    if page_name not in AVAILABLE_PAGES:
        return

    st.session_state.current_page = page_name

    # Synchronize the sidebar radio widget.
    st.session_state[NAVIGATION_STATE_KEY] = page_name





def render_sidebar(cookies):
    """Render the complete application sidebar."""

    with st.sidebar:

        # Application branding
        render_brand()

        st.divider()

        # Sidebar navigation
        selected_page = render_sidebar_navigation()

        st.divider()

        # Logged-in user information
        st.caption("SIGNED IN AS")
        st.write(st.session_state.get("user_email", ""))

        # Logout button
        if st.button(
            "Logout",
            key="logout_button",
            use_container_width=True,
        ):

            # Clear authentication cookie
            cookies["auth_token"] = ""
            cookies.save()

            # Clear user session data
            for key in [
                "authenticated",
                "user_id",
                "user_email",
                "messages",
                "last_question",
                "last_answer",
                "uploaded_documents",
                "current_page",
                NAVIGATION_STATE_KEY,
            ]:
                st.session_state.pop(key, None)

            # Return to login screen
            st.rerun()

        st.divider()

        # Sidebar footer
        st.html(
            """
            <div class="sidebar-footer">
                <div class="sidebar-footer-title">
                    RAG Intelligence
                </div>
                <div class="sidebar-footer-description">
                    Document-powered AI assistant
                </div>
            </div>
            """
        )

    return selected_page


# =====================================================
# 5. DASHBOARD METRICS
# =====================================================


def get_dashboard_metrics():
    """Retrieve document and chunk statistics for the authenticated user."""

    user_id = st.session_state.get("user_id")

    if (
        not st.session_state.get("authenticated", False)
        or not isinstance(user_id, str)
        or not user_id.strip()
    ):
        st.warning(
            "Your session has expired. Please log in again."
        )
        return 0, 0

    user_id = user_id.strip()

    try:
        documents = list_documents(user_id=user_id)

        total_documents = len(documents)

        total_chunks = get_collection_count(user_id=user_id)

        return total_documents, total_chunks

    except Exception:
        st.warning(
            "Dashboard statistics could not be loaded. "
            "Please check the document database."
        )

        return 0, 0


def get_session_question_count():
    """Count user questions in the current chat session."""

    messages = st.session_state.get("messages", [])

    return sum(
        1
        for message in messages
        if message.get("role") == "user"
    )


# =====================================================
# 6. DASHBOARD OVERVIEW
# =====================================================

def render_dashboard_overview():
    """Render the main dashboard overview."""

    render_section_header(
        eyebrow="WORKSPACE OVERVIEW",
        title="Your Knowledge Workspace",
        description=(
            "Manage your documents, explore your knowledge "
            "base and interact with your AI assistant."
        ),
    )

    total_documents, total_chunks = get_dashboard_metrics()

    st.html(
        """
        <div class="dashboard-metrics-heading">
            Knowledge Base Overview
        </div>
        """
    )

    first_column, second_column, third_column = st.columns(3)

    with first_column:
        render_stat_card(
            title="Total Documents",
            value=f"{total_documents:,}",
            description="Indexed documents",
            icon="📄",
            color="blue",
        )

    with second_column:
        render_stat_card(
            title="Total Chunks",
            value=f"{total_chunks:,}",
            description="Stored knowledge segments",
            icon="🧩",
            color="purple",
        )

    with third_column:
        render_stat_card(
            title="Questions Asked",
            value=f"{get_session_question_count():,}",
            description="Questions in this session",
            icon="💬",
            color="green",
        )

    st.divider()

    render_section_header(
        eyebrow="GET STARTED",
        title="Explore Your Workspace",
        description=(
            "Choose an area of the application to continue."
        ),
    )

    first_column, second_column = st.columns(2)

    # -----------------------------------------------
    # DOCUMENT LIBRARY CARD
    # -----------------------------------------------

    with first_column:
        with st.container(border=True):

            st.markdown("### Document Library")

            st.write(
                "Upload PDF or TXT files and manage "
                "your indexed knowledge base."
            )

            st.button(
                "Manage Documents",
                key="dashboard_documents_button",
                use_container_width=True,
                on_click=navigate_to_page,
                args=(PAGE_DOCUMENTS,),
            )

    # -----------------------------------------------
    # AI ASSISTANT CARD
    # -----------------------------------------------

    with second_column:
        with st.container(border=True):

            st.markdown("### AI Assistant")

            st.write(
                "Ask natural-language questions and retrieve "
                "answers from your documents."
            )

            st.button(
                "Open AI Chat",
                key="dashboard_chat_button",
                use_container_width=True,
                on_click=navigate_to_page,
                args=(PAGE_CHAT,),
            )


# =====================================================
# 7. SETTINGS PAGE
# =====================================================

def clear_chat_session():
    """Clear the current chat session."""

    st.session_state.messages = []
    st.session_state.last_question = None
    st.session_state.last_answer = None



def render_settings_page():
    """Render application information and settings."""

    if (
        not st.session_state.get("authenticated", False)
        or not st.session_state.get("user_id")
    ):
        st.error("Please log in to access settings.")
        st.stop()

    render_section_header(
        eyebrow="APPLICATION",
        title="Settings",
        description=(
            "Application information and current configuration."
        ),
    )

def render_settings_page():
    """Render application information and settings."""

    if (
        not st.session_state.get("authenticated", False)
        or not st.session_state.get("user_id")
    ):
        st.error("Please log in to access settings.")
        st.stop()

    render_section_header(
        eyebrow="APPLICATION",
        title="Settings",
        description=(
            "Application information and current configuration."
        ),
    )


    st.divider()

    with st.container(border=True):

        st.markdown("### Application Information")

        st.write("**Application:** RAG Intelligence")
        st.write("**Architecture:** Retrieval-Augmented Generation")
        st.write("**Vector Database:** ChromaDB")
        st.write("**Embedding Model:** all-MiniLM-L6-v2")
        st.write("**Language Model:** Gemma 3 4B")
        st.write("**Supported Documents:** PDF and TXT")

    with st.container(border=True):

        st.markdown("### Chat Session")

        message_count = len(
            st.session_state.get("messages", [])
        )

        st.metric(
            "Messages in current session",
            message_count,
        )

        st.button(
            "Clear conversation",
            key="settings_clear_chat",
            on_click=clear_chat_session,
        )


# =====================================================
# 8. PAGE ROUTER
# =====================================================


def render_selected_page(selected_page):
    """Render the page selected by the user."""

    if (
        not st.session_state.get("authenticated", False)
        or not st.session_state.get("user_id")
    ):
        st.error("Please log in to access this page.")
        st.stop()

    page_renderers = {
        PAGE_DASHBOARD: render_dashboard_overview,
        PAGE_CHAT: render_chat_interface,
        PAGE_DOCUMENTS: render_document_panel,
        PAGE_SETTINGS: render_settings_page,
    }

    page_renderer = page_renderers.get(selected_page)

    if page_renderer is None:
        st.error("Page not found.")
        return

    page_renderer()



# =====================================================
# 9. APPLICATION ENTRY POINT
# =====================================================


def main(cookies):
    """Run the complete application."""

    if (
        not st.session_state.get("authenticated", False)
        or not st.session_state.get("user_id")
    ):
        st.error("Please log in to access the application.")
        st.stop()


    initialize_application()

    selected_page = render_sidebar(cookies)

    render_selected_page(selected_page)

    st.divider()

    render_footer()
