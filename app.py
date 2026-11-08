"""
RAG Document Intelligence
Main application entry point.
"""

import streamlit as st

from src.auth import initialize_auth_db

from frontend.auth_interface import render_auth_interface
from frontend.session_auth import (
    get_cookie_manager,
    restore_login,
)
from frontend.dashboard import main


if __name__ == "__main__":

    # Configure the Streamlit page first.
    st.set_page_config(
        page_title="RAG Document Intelligence",
        page_icon="✦",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize authentication database.
    initialize_auth_db()

    # Initialize browser cookies.
    cookies = get_cookie_manager()

    # Restore an existing authenticated session.
    restore_login(cookies)

    # Route the user to the appropriate interface.
    if not st.session_state.get("authenticated", False):
        render_auth_interface(cookies)
    else:
        main(cookies)
