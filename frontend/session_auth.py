
import streamlit as st

from streamlit_cookies_manager import EncryptedCookieManager

from src.auth import verify_auth_token


def get_cookie_manager():
    """Initialize the encrypted cookie manager."""

    cookies = EncryptedCookieManager(
        prefix="rag_document_intelligence/",
        password=st.secrets["cookies_password"],
    )

    if not cookies.ready():
        st.stop()

    return cookies




def restore_login(cookies):
    """Restore authenticated user only from a valid cookie."""

    token = cookies.get("auth_token")

    user = verify_auth_token(token)

    if user is None:

        # Clear invalid or expired browser cookie.
        cookies["auth_token"] = ""
        cookies.save()

        # Clear invalid or expired authentication state.
        for key in [
            "authenticated",
            "user_id",
            "user_email",
            "messages",
            "uploaded_documents",
            "last_question",
            "last_answer",
            "current_page",
        ]:
            st.session_state.pop(key, None)

        return
    # Restore identity only after successful token verification.
    st.session_state["authenticated"] = True
    st.session_state["user_id"] = user["user_id"]
    st.session_state["user_email"] = user["email"]
