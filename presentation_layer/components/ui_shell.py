"""
ui_shell.py - Unified Editorial Shell for maxanalysis platform.
Implements:
- inject_styles(): Injects ui_theme.css with high-contrast cinematic black/white theme.
- render_header(active_page, refresh_callback): Sticky top announcement bar + wordmark + back button + 4 navigation items + refresh data button.
- render_footer(): Monochrome footer with four page links and educational disclaimer.
Strictly zero emojis. Thin line SVGs only.
"""

import os
import streamlit as st
from typing import Callable, Optional

# Route to file mapping
PAGE_PATHS = {
    "main": "app.py",
    "home": "app.py",
    "upload": "pages/1_Upload_Data.py",
    "recommendation": "pages/3_Recommendations.py",
    "recommendations": "pages/3_Recommendations.py",
    "dashboard": "pages/2_Analysis_Dashboard.py",
}

# SVG Thin Line Icons (No emojis anywhere)
ICONS = {
    "arrow_left": """<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>""",
    "refresh": """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>""",
    "upload": """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>""",
    "dashboard": """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="0"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg>""",
    "recommendation": """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="9 11 12 14 22 4"></polyline><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path></svg>""",
    "export": """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><polyline points="9 15 12 18 15 15"></polyline></svg>""",
    "benchmark": """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>""",
    "explainable": """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>""",
    "metrics": """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>""",
    "storage": """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>""",
}


def inject_styles():
    """Reads ui_theme.css and injects it into the Streamlit app DOM."""
    css_path = os.path.join(os.path.dirname(__file__), "ui_theme.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def render_header(active_page: str, refresh_callback: Optional[Callable[[], bool]] = None):
    """
    Renders the unified sticky editorial header on every page:
    - Thin announcement bar above the header
    - Left: maxanalysis wordmark and Back button
    - Centre: Navigation buttons ("Main screen", "Upload Data", "Recommendation", "Analysis Dashboard")
    - Right: Refresh Data button wired to existing fetcher
    """
    normalized_active = active_page.lower().strip()
    if normalized_active in ("home", "overview"):
        normalized_active = "main"

    # Maintain navigation history in st.session_state["ui_history"]
    if "ui_history" not in st.session_state:
        st.session_state["ui_history"] = []

    history = st.session_state["ui_history"]
    if not history or history[-1] != normalized_active:
        history.append(normalized_active)

    can_go_back = len(history) > 1

    with st.container(key="ui_header_container"):
        # Thin announcement bar
        st.markdown("""
        <div class="ui-announcement-bar">
            <span>AI-driven startup analysis and recommendations</span>
            <span>Upload data. Get benchmarks. Act on them.</span>
        </div>
        """, unsafe_allow_html=True)

        col_left, col_nav, col_right = st.columns([2.0, 5.2, 1.4], vertical_alignment="center")

        with col_left:
            col_wm, col_bk = st.columns([1.1, 0.9], vertical_alignment="center")
            with col_wm:
                st.markdown('<a href="/" class="ui-wordmark">MAXANALYSIS</a>', unsafe_allow_html=True)
            with col_bk:
                if st.button("Back", key=f"ui_back_btn_{normalized_active}", disabled=not can_go_back, use_container_width=True):
                    if can_go_back:
                        # Pop current page, then pop target page so switch_page re-adds it cleanly
                        history.pop()
                        target_page = history.pop()
                        target_file = PAGE_PATHS.get(target_page, "app.py")
                        st.switch_page(target_file)

        with col_nav:
            nav1, nav2, nav3, nav4 = st.columns(4, vertical_alignment="center")
            
            with nav1:
                is_active = (normalized_active == "main")
                if st.button("Main screen", key=f"nav_btn_main_{normalized_active}", type="primary" if is_active else "secondary", use_container_width=True):
                    st.switch_page(PAGE_PATHS["main"])

            with nav2:
                is_active = (normalized_active == "upload")
                if st.button("Upload Data", key=f"nav_btn_upload_{normalized_active}", type="primary" if is_active else "secondary", use_container_width=True):
                    st.switch_page(PAGE_PATHS["upload"])

            with nav3:
                is_active = (normalized_active in ("recommendation", "recommendations"))
                if st.button("Recommendation", key=f"nav_btn_rec_{normalized_active}", type="primary" if is_active else "secondary", use_container_width=True):
                    st.switch_page(PAGE_PATHS["recommendation"])

            with nav4:
                is_active = (normalized_active == "dashboard")
                if st.button("Analysis Dashboard", key=f"nav_btn_dash_{normalized_active}", type="primary" if is_active else "secondary", use_container_width=True):
                    st.switch_page(PAGE_PATHS["dashboard"])

        with col_right:
            if st.button("Refresh Data", key=f"ui_refresh_btn_{normalized_active}", use_container_width=True):
                with st.spinner("Refreshing dataset..."):
                    # Clear existing cached session state data
                    if normalized_active in ("dashboard", "recommendation", "recommendations"):
                        st.session_state.pop("report_data", None)
                    elif normalized_active == "upload":
                        st.session_state.pop("template_cache", None)
                    elif normalized_active == "main":
                        st.session_state.pop("api_healthy", None)

                    success = True
                    if refresh_callback:
                        try:
                            res = refresh_callback()
                            success = (res is not False)
                        except Exception:
                            success = False

                    st.session_state["ui_refresh_status"] = "Data refreshed successfully" if success else "Data refresh failed"
                st.rerun()

        # Inline status message if refresh occurred
        if "ui_refresh_status" in st.session_state:
            status_msg = st.session_state.pop("ui_refresh_status")
            st.markdown(f'<div class="ui-status-inline">{status_msg}</div>', unsafe_allow_html=True)


def render_footer():
    """Renders the monochromatic black footer on every page."""
    st.markdown("""
    <footer class="ui-footer">
        <div class="ui-footer-left">
            <span class="ui-wordmark" style="font-size: 1.15rem;">MAXANALYSIS</span>
            <span class="ui-footer-copy">B.Tech mini-project prototype for educational purposes</span>
        </div>
        <div class="ui-footer-links">
            <a href="/">Main screen</a>
            <a href="/Upload_Data">Upload Data</a>
            <a href="/Recommendations">Recommendation</a>
            <a href="/Analysis_Dashboard">Analysis Dashboard</a>
        </div>
    </footer>
    """, unsafe_allow_html=True)
