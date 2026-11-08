
import shutil
import html
from pathlib import Path
from uuid import uuid4

import streamlit as st

from src.config import DATA_DIR
from src.ingestion import ingest_document
from src.document_manager import list_documents, delete_document
from src.vector_store import get_collection_count

from frontend.components import (
    render_section_header,
    render_empty_state,
)

from frontend.helpers import format_file_size


# =====================================================
# 1. CONFIGURATION
# =====================================================

UPLOAD_DIR = DATA_DIR / "uploads"

ALLOWED_EXTENSIONS = ["pdf", "txt"]

MAX_FILE_SIZE_MB = 50


# =====================================================
# 2. AUTHENTICATED USER
# =====================================================

def get_authenticated_user_id():
    """Get and validate the authenticated user's ID."""

    # First verify authentication status.
    if not st.session_state.get("authenticated", False):
        return None

    user_id = st.session_state.get("user_id")

    if not isinstance(user_id, str) or not user_id.strip():
        return None

    user_id = user_id.strip()

    # Prevent unsafe folder names.
    if user_id in [".", ".."] or Path(user_id).name != user_id:
        return None

    return user_id

# =====================================================
# 3. INITIALIZE UPLOAD DIRECTORY
# =====================================================

def initialize_upload_directory(user_id):
    """Create a separate upload directory for each user."""

    user_upload_dir = UPLOAD_DIR / user_id

    user_upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return user_upload_dir


# =====================================================
# 4. DOCUMENT UPLOADER
# =====================================================

def render_document_uploader(user_id):
    """Render the document upload interface."""

    st.html(
        """
        <div class="upload-section">
            <div class="upload-section-title">
                Add documents
            </div>

            <div class="upload-section-description">
                Upload PDF or TXT files to expand your
                knowledge base.
            </div>
        </div>
        """
    )

    uploaded_file = st.file_uploader(
        "Choose a document",
        type=ALLOWED_EXTENSIONS,
        accept_multiple_files=False,
        help="Supported formats: PDF and TXT. Maximum size: 50 MB.",
    )

    if uploaded_file is None:
        return

    file_extension = Path(uploaded_file.name).suffix.lower()

    if file_extension not in [".pdf", ".txt"]:
        st.error("Unsupported file format.")
        return

    file_size = uploaded_file.size

    if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(
            f"File is too large. Maximum allowed size is "
            f"{MAX_FILE_SIZE_MB} MB."
        )
        return

    safe_filename = Path(uploaded_file.name).name

    st.caption(
        f"Selected: {safe_filename} "
        f"({format_file_size(file_size)})"
    )

    if st.button(
        "Upload and process document",
        type="primary",
        use_container_width=True,
        key="process_document_button",
    ):
        process_uploaded_document(
            uploaded_file,
            user_id=user_id
        )


# =====================================================
# 5. PROCESS UPLOADED DOCUMENT
# =====================================================

def process_uploaded_document(uploaded_file, user_id):
    """Save and ingest a document for the authenticated user."""

    user_upload_dir = initialize_upload_directory(user_id)

    original_filename = Path(uploaded_file.name).name

    unique_folder = user_upload_dir / str(uuid4())

    unique_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path = unique_folder / original_filename

    ingestion_successful = False

    try:
        with open(file_path, "wb") as file:
            file.write(uploaded_file.getvalue())

        with st.spinner(
            "Processing document and generating embeddings..."
        ):
            result = ingest_document(
                file_path,
                user_id=user_id
            )

        if result["status"] == "duplicate":
            shutil.rmtree(
                unique_folder,
                ignore_errors=True,
            )

            st.warning(
                "This document has already been uploaded "
                "to your account."
            )
            return

        ingestion_successful = True

        st.success(
            f"Successfully processed: {original_filename}"
        )

        st.rerun()

    except Exception as error:

        if not ingestion_successful:
            shutil.rmtree(
                unique_folder,
                ignore_errors=True,
            )


        st.error(
            "Document processing failed. "
            "Please check the file and try again."
        )

        st.exception(error)


# =====================================================
# 6. DOCUMENT SUMMARY
# =====================================================

def render_document_summary(documents, total_chunks):
    """Display document and chunk statistics."""

    first_column, second_column = st.columns(2)

    with first_column:
        st.metric(
            label="Total Documents",
            value=len(documents),
        )

    with second_column:
        st.metric(
            label="Stored Chunks",
            value=total_chunks,
        )


# =====================================================
# 7. SINGLE DOCUMENT CARD
# =====================================================

def render_document_card(document, index, user_id):
    """Render one document and its delete controls."""

    document_id = document.get("document_id")

    filename = Path(
        str(document.get("source", "Unknown document"))
    ).name

    chunks = document.get("chunks", 0)

    safe_filename = html.escape(filename)

    with st.container(border=True):

        first_column, second_column = st.columns([5, 1])

        with first_column:
            st.html(
                f"""
                <div class="document-card-title">
                    📄 {safe_filename}
                </div>
                """
            )

            st.caption(
                f"{chunks} chunks"
            )

        with second_column:
            delete_clicked = st.button(
                "Delete",
                key=f"delete_document_{index}_{document_id}",
                use_container_width=True,
            )

        confirm_key = f"confirm_delete_{document_id}"

        if delete_clicked:
            st.session_state[confirm_key] = True

        if st.session_state.get(confirm_key, False):

            st.warning(
                f"Are you sure you want to delete {filename}?"
            )

            confirm_column, cancel_column = st.columns(2)

            with confirm_column:
                if st.button(
                    "Confirm deletion",
                    key=f"confirm_button_{index}",
                    type="primary",
                    use_container_width=True,
                ):
                    try:
                        with st.spinner("Deleting document..."):
                            delete_document(
                                document_id,
                                user_id=user_id
                            )

                        # Filesystem cleanup will be added
                        # after upload-folder metadata is stored.

                        st.session_state.pop(
                            confirm_key,
                            None,
                        )

                        st.success(
                            f"{filename} deleted successfully."
                        )

                        st.rerun()

                    except Exception as error:
                        st.error(
                            "Could not delete the document."
                        )

                        st.exception(error)

            with cancel_column:
                if st.button(
                    "Cancel",
                    key=f"cancel_button_{index}",
                    use_container_width=True,
                ):
                    st.session_state.pop(
                        confirm_key,
                        None,
                    )

                    st.rerun()


# =====================================================
# 8. DOCUMENT LIST
# =====================================================

def render_document_list(user_id):
    """Fetch and display only the authenticated user's documents."""

    try:
        documents = list_documents(user_id=user_id)

    except Exception as error:
        st.error("Could not load the document list.")
        st.exception(error)
        return

    if not documents:
        render_empty_state(
            title="No documents yet",
            description=(
                "Upload your first PDF or TXT document "
                "to start building your knowledge base."
            ),
            icon="📚",
        )

        return

    for index, document in enumerate(documents):
        render_document_card(
            document=document,
            index=index,
            user_id=user_id,
        )


# =====================================================
# 9. COMPLETE DOCUMENT PAGE
# =====================================================

def render_document_panel():
    """Render the complete document management page."""

    user_id = get_authenticated_user_id()

    if not user_id:
        st.error(
            "Your session has expired. Please log in again."
        )
        st.stop()

    render_section_header(
        eyebrow="KNOWLEDGE BASE",
        title="Document Management",
        description=(
            "Upload, organize and manage the documents "
            "your AI assistant uses to answer questions."
        ),
    )

    st.divider()

    render_document_uploader(user_id)

    st.divider()

    render_section_header(
        eyebrow="OVERVIEW",
        title="Knowledge Base Statistics",
    )

    try:
        documents = list_documents(user_id=user_id)

        total_chunks = get_collection_count(user_id=user_id)

        render_document_summary(
            documents=documents,
            total_chunks=total_chunks,
        )

    except Exception as error:
        st.error(
            "Could not retrieve knowledge base statistics."
        )

        st.exception(error)

    st.divider()

    render_section_header(
        eyebrow="YOUR LIBRARY",
        title="Indexed Documents",
        description=(
            "Documents currently available to your RAG system."
        ),
    )

    render_document_list(user_id)
