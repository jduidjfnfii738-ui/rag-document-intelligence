
import streamlit as st

from src.auth import (
    initialize_auth_db,
    create_user,
    authenticate_user,
    create_auth_token,
)


def render_auth_interface(cookies):
    """Display signup and login screens."""

    initialize_auth_db()

    st.title("RAG Document Intelligence")
    st.caption("Sign in to access your personal document library.")

    login_tab, signup_tab = st.tabs(
        ["Login", "Create Account"]
    )

    # =========================================
    # LOGIN
    # =========================================

    with login_tab:

        with st.form("login_form"):

            st.subheader("Welcome back")

            email = st.text_input(
                "Email address",
                key="login_email",
            )

            password = st.text_input(
                "Password",
                type="password",
                key="login_password",
            )

            login_clicked = st.form_submit_button(
                "Login",
                use_container_width=True,
                type="primary",
            )

            if login_clicked:

                user = authenticate_user(email, password)

                if user:

                    token = create_auth_token(
                        user["user_id"],
                        user["email"],
                    )

                    cookies["auth_token"] = token
                    cookies.save()

                    st.session_state["authenticated"] = True
                    st.session_state["user_id"] = user["user_id"]
                    st.session_state["user_email"] = user["email"]
                    st.session_state["messages"] = []
                    st.session_state["uploaded_documents"] = []
                    st.session_state["last_question"] = None
                    st.session_state["last_answer"] = None
                    st.session_state["current_page"] = "Dashboard"

                    st.success("Login successful.")
                    st.rerun()

                else:
                    st.error("Invalid email or password.")

    # =========================================
    # SIGNUP
    # =========================================

    with signup_tab:

        with st.form("signup_form"):

            st.subheader("Create your account")

            email = st.text_input(
                "Email address",
                key="signup_email",
            )

            password = st.text_input(
                "Password",
                type="password",
                key="signup_password",
            )

            confirm_password = st.text_input(
                "Confirm password",
                type="password",
                key="signup_confirm_password",
            )

            signup_clicked = st.form_submit_button(
                "Create Account",
                use_container_width=True,
                type="primary",
            )

            if signup_clicked:

                if password != confirm_password:

                    st.error("Passwords do not match.")

                else:

                    result = create_user(email, password)

                    if result["success"]:

                        token = create_auth_token(
                            result["user_id"],
                            result["email"],
                        )

                        cookies["auth_token"] = token
                        cookies.save()

                        st.session_state["authenticated"] = True
                        st.session_state["user_id"] = result["user_id"]
                        st.session_state["user_email"] = result["email"]
                        st.session_state["messages"] = []
                        st.session_state["uploaded_documents"] = []
                        st.session_state["last_question"] = None
                        st.session_state["last_answer"] = None
                        st.session_state["current_page"] = "Dashboard"

                        st.success("Account created successfully.")
                        st.rerun()

                    else:
                        st.error(result["message"])
