
import html

import streamlit as st


# =====================================================
# 1. REUSABLE SVG ICONS
# =====================================================

BRAND_ICON = """
<svg
    viewBox="0 0 48 48"
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    aria-hidden="true"
>
    <rect
        x="5"
        y="5"
        width="38"
        height="38"
        rx="12"
        fill="url(#brandGradient)"
    />

    <path
        d="M16 15.5H27L33 21.5V33H16V15.5Z"
        stroke="white"
        stroke-width="2"
        stroke-linejoin="round"
    />

    <path
        d="M27 15.5V21.5H33"
        stroke="white"
        stroke-width="2"
        stroke-linejoin="round"
    />

    <path
        d="M20 26H29M20 30H27"
        stroke="white"
        stroke-width="1.8"
        stroke-linecap="round"
    />

    <path
        d="M35 10V15M32.5 12.5H37.5"
        stroke="#D9E8FF"
        stroke-width="1.6"
        stroke-linecap="round"
    />

    <defs>
        <linearGradient
            id="brandGradient"
            x1="5"
            y1="5"
            x2="43"
            y2="43"
            gradientUnits="userSpaceOnUse"
        >
            <stop stop-color="#668BFF"/>
            <stop offset="1" stop-color="#9B72F5"/>
        </linearGradient>
    </defs>
</svg>
"""


DOCUMENT_ICON = """
<svg
    viewBox="0 0 24 24"
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    aria-hidden="true"
>
    <path
        d="M6 3.75H14L19 8.75V20.25H6V3.75Z"
        stroke="currentColor"
        stroke-width="1.7"
        stroke-linejoin="round"
    />
    <path
        d="M14 3.75V8.75H19"
        stroke="currentColor"
        stroke-width="1.7"
        stroke-linejoin="round"
    />
    <path
        d="M9 13H16M9 16.5H16"
        stroke="currentColor"
        stroke-width="1.7"
        stroke-linecap="round"
    />
</svg>
"""


# =====================================================
# 2. APPLICATION BRAND
# =====================================================

def render_brand():
    """Render application branding inside the sidebar."""

    st.html(
        f"""
        <div class="brand-container">

            <div class="brand-logo">
                {BRAND_ICON}
            </div>

            <div class="brand-content">

                <div class="brand-name">
                    RAG Intelligence
                </div>

                <div class="brand-subtitle">
                    DOCUMENT KNOWLEDGE PLATFORM
                </div>

            </div>

        </div>
        """
    )


# =====================================================
# 3. SIDEBAR NAVIGATION
# =====================================================

def render_sidebar_navigation():
    """Render sidebar navigation and return selected page."""

    pages = [
        "Dashboard",
        "AI Chat",
        "Documents",
        "Settings",
    ]

    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"

    current_page = st.session_state.current_page

    if current_page not in pages:
        current_page = "Dashboard"

    with st.sidebar:

        st.html(
            """
            <div class="sidebar-section-label">
                WORKSPACE
            </div>
            """
        )

    selected_page = st.sidebar.radio(
        "Navigation",
        pages,
        index=pages.index(current_page),
        label_visibility="collapsed",
        key="page_navigation",
    )

    st.session_state.current_page = selected_page

    return selected_page


# =====================================================
# 4. SECTION HEADER
# =====================================================

def render_section_header(
    title,
    description=None,
    eyebrow=None,
):
    """Render a reusable section heading."""

    safe_title = html.escape(str(title))

    eyebrow_html = ""

    if eyebrow:
        safe_eyebrow = html.escape(str(eyebrow))

        eyebrow_html = f"""
        <div class="section-eyebrow">
            {safe_eyebrow}
        </div>
        """

    description_html = ""

    if description:
        safe_description = html.escape(str(description))

        description_html = f"""
        <p class="section-description">
            {safe_description}
        </p>
        """

    st.html(
        f"""
        <div class="section-header">

            {eyebrow_html}

            <h2 class="section-title">
                {safe_title}
            </h2>

            {description_html}

        </div>
        """
    )


# =====================================================
# 5. DASHBOARD STATISTIC CARD
# =====================================================

def render_stat_card(
    title,
    value,
    description,
    icon,
    color="blue",
):
    """Render a reusable dashboard statistic card."""

    allowed_colors = {
        "blue",
        "green",
        "purple",
        "orange",
    }

    if color not in allowed_colors:
        color = "blue"

    safe_title = html.escape(str(title))
    safe_value = html.escape(str(value))
    safe_description = html.escape(str(description))
    safe_icon = html.escape(str(icon))

    st.html(
        f"""
        <div class="stat-card">

            <div class="stat-card-top">

                <div class="stat-icon {color}">
                    {safe_icon}
                </div>

                <div class="stat-label">
                    {safe_title}
                </div>

            </div>

            <div class="stat-value">
                {safe_value}
            </div>

            <div class="stat-description">
                {safe_description}
            </div>

        </div>
        """
    )


# =====================================================
# 6. STATUS BADGE
# =====================================================

def render_status_badge(
    label,
    status="success",
):
    """Render a status badge."""

    allowed_statuses = {
        "success",
        "warning",
        "error",
        "info",
    }

    if status not in allowed_statuses:
        status = "info"

    safe_label = html.escape(str(label))

    st.html(
        f"""
        <span class="status-badge {status}">
            {safe_label}
        </span>
        """
    )


# =====================================================
# 7. EMPTY STATE
# =====================================================

def render_empty_state(
    title,
    description,
    icon="📄",
):
    """Render an empty-state component."""

    safe_title = html.escape(str(title))
    safe_description = html.escape(str(description))
    safe_icon = html.escape(str(icon))

    st.html(
        f"""
        <div class="empty-state">

            <div class="empty-state-icon">
                {safe_icon}
            </div>

            <div class="empty-state-title">
                {safe_title}
            </div>

            <div class="empty-state-description">
                {safe_description}
            </div>

        </div>
        """
    )


# =====================================================
# 8. APPLICATION FOOTER
# =====================================================

def render_footer():
    """Render the application footer."""

    st.html(
        """
        <div class="app-footer">

            <div>
                RAG Intelligence
            </div>

            <div>
                AI-powered document understanding
            </div>

        </div>
        """
    )
