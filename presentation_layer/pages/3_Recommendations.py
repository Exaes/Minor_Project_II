"""
AI Business Recommendations Page - maxanalysis platform.
Editorial layout:
- Sticky header with maxanalysis wordmark, back button, nav items, and refresh button.
- Wired Refresh Data button to the existing report fetcher: requests.get(f"{API_URL}/report/{analysis_id}").
- KPI summary cards on dark surfaces.
- Ranked recommendation cards with large numeral ranks and explicit impact labels ("HIGH IMPACT", "MEDIUM IMPACT", "LOW IMPACT").
- Executive PDF export button styled as an outline button.
Zero emojis.
"""

import streamlit as st
import requests
import sys, os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from presentation_layer.components.ui_shell import inject_styles, render_header, render_footer
from config import API_PORT, API_HOST

API_HOST = "127.0.0.1" if API_HOST in ("0.0.0.0", "") else API_HOST
API_URL = f"http://{API_HOST}:{API_PORT}/api"

st.set_page_config(
    page_title="Recommendations - maxanalysis",
    layout="wide",
    initial_sidebar_state="collapsed"
)

inject_styles()

# ── Existing Data-Loading Function for Report ──
def reload_recommendations_report() -> bool:
    """Calls the existing report loader endpoint for the active analysis_id."""
    analysis_id = st.session_state.get("analysis_id")
    if not analysis_id:
        return False
    try:
        res = requests.get(f"{API_URL}/report/{analysis_id}", timeout=10)
        if res.status_code == 200:
            st.session_state["report_data"] = res.json()
            return True
        return False
    except Exception:
        return False

# ── Sticky maxanalysis Header ──
render_header(active_page="recommendation", refresh_callback=reload_recommendations_report)

if "analysis_id" not in st.session_state:
    st.markdown("""
    <div class="ui-dark-card" style="text-align: center; padding: 4rem 2rem; margin-top: 2rem;">
        <div class="ui-badge ui-badge-outline" style="margin-bottom: 1.25rem;">NO ACTIVE DATASET</div>
        <h3 style="margin: 0 0 0.75rem 0; color: var(--text-on-dark);">NO ACTIVE ANALYSIS FOUND</h3>
        <p style="font-size: 15px; color: var(--text-muted-on-dark); max-width: 520px; margin: 0 auto 2rem auto; line-height: 1.6;">
            Please upload an operational spreadsheet or run the sample venture launcher to generate strategic recommendations.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Proceed to Data Ingestion Page", use_container_width=True):
        st.switch_page("pages/1_Upload_Data.py")
    render_footer()
    st.stop()

analysis_id = st.session_state["analysis_id"]

if "report_data" not in st.session_state or st.session_state.get("current_loaded_id") != analysis_id:
    with st.spinner("Fetching strategic insights..."):
        try:
            response = requests.get(f"{API_URL}/report/{analysis_id}")
            if response.status_code != 200:
                st.error(f"Failed to fetch report: {response.text}")
                st.stop()
            st.session_state["report_data"] = response.json()
            st.session_state["current_loaded_id"] = analysis_id
        except Exception as e:
            st.error(f"Connection error: {e}")
            st.stop()

report_data = st.session_state["report_data"]
company_name = report_data.get("company_name", "Target Startup")
recommendations = report_data.get("recommendations", [])

# ── Header & PDF Export ──
col_head1, col_head2 = st.columns([2.2, 1.1], gap="large", vertical_alignment="center")

with col_head1:
    st.markdown(f"""
    <div style="margin: 1.5rem 0;">
        <div class="ui-badge ui-badge-outline" style="margin-bottom: 0.75rem;">Stage 03 • Strategic Advisory</div>
        <h1 style="margin: 0 0 0.5rem 0;">STRATEGIC RECOMMENDATIONS</h1>
        <p style="margin: 0; font-size: 15px; color: var(--text-muted-on-light); max-width: 680px; line-height: 1.5;">
            Prioritized, explainable guidance for <strong>{company_name}</strong> calibrated against top cohort peer metrics.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_head2:
    try:
        pdf_res = requests.get(f"{API_URL}/export/{analysis_id}/pdf", timeout=10)
        if pdf_res.status_code == 200:
            st.download_button(
                label="Export Executive PDF Report",
                data=pdf_res.content,
                file_name=f"{company_name}_Executive_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
                help="Download full executive report formatted with findings and action roadmap"
            )
        else:
            st.button("Export PDF (Unavailable)", disabled=True, use_container_width=True)
    except Exception:
        st.button("Export PDF (Service Offline)", disabled=True, use_container_width=True)

# ── Summary Badges Row (KPI Cards) ──
high_recs = [r for r in recommendations if r.get("impact_level", "").lower() == "high"]
med_recs = [r for r in recommendations if r.get("impact_level", "").lower() == "medium"]
low_recs = [r for r in recommendations if r.get("impact_level", "").lower() == "low"]

sc1, sc2, sc3, sc4 = st.columns(4)
with sc1:
    st.markdown(f"""
    <div class="ui-metric-card">
        <div class="ui-metric-label">TOTAL ACTIONS</div>
        <div class="ui-metric-value">{len(recommendations)}</div>
        <div class="ui-metric-sub">SYNTHESIZED</div>
    </div>
    """, unsafe_allow_html=True)
with sc2:
    st.markdown(f"""
    <div class="ui-metric-card">
        <div class="ui-metric-label">HIGH IMPACT</div>
        <div class="ui-metric-value">{len(high_recs)}</div>
        <div class="ui-metric-sub">IMMEDIATE FOCUS</div>
    </div>
    """, unsafe_allow_html=True)
with sc3:
    st.markdown(f"""
    <div class="ui-metric-card">
        <div class="ui-metric-label">MEDIUM IMPACT</div>
        <div class="ui-metric-value">{len(med_recs)}</div>
        <div class="ui-metric-sub">QUARTERLY SCOPE</div>
    </div>
    """, unsafe_allow_html=True)
with sc4:
    st.markdown(f"""
    <div class="ui-metric-card">
        <div class="ui-metric-label">LOW IMPACT</div>
        <div class="ui-metric-value">{len(low_recs)}</div>
        <div class="ui-metric-sub">EFFICIENCY GAINS</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Filter Controls ──
col_flt1, col_flt2 = st.columns([1, 2])
with col_flt1:
    selected_impact = st.selectbox(
        "Filter by Priority Level:",
        ["All Priorities", "High Impact Only", "Medium Impact", "Low Impact"]
    )

filtered_recs = recommendations
if selected_impact == "High Impact Only":
    filtered_recs = high_recs
elif selected_impact == "Medium Impact":
    filtered_recs = med_recs
elif selected_impact == "Low Impact":
    filtered_recs = low_recs

st.markdown("<br>", unsafe_allow_html=True)

# ── Render Recommendation Cards ──
if not filtered_recs:
    st.markdown("""
    <div class="ui-dark-card" style="text-align: center; padding: 3rem;">
        <h4 style="margin: 0; color: var(--text-on-dark);">NO RECOMMENDATIONS IN THIS CATEGORY</h4>
    </div>
    """, unsafe_allow_html=True)
else:
    for rec in filtered_recs:
        impact_level = rec.get("impact_level", "Medium").upper()
        if "HIGH" in impact_level:
            impact_text = "HIGH IMPACT"
            badge_class = "ui-badge-strong"
        elif "LOW" in impact_level:
            impact_text = "LOW IMPACT"
            badge_class = "ui-badge-outline"
        else:
            impact_text = "MEDIUM IMPACT"
            badge_class = "ui-badge"

        rank = rec.get("rank", 1)
        title = rec.get("title", "STRATEGIC OPPORTUNITY").upper()
        category = rec.get("category", "General").upper()
        explanation = rec.get("explanation", "")

        card_markup = f"""
        <div class="ui-rec-card">
            <div class="ui-rec-header">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <span class="ui-rec-rank">#{rank}</span>
                    <span class="ui-rec-title">{title}</span>
                </div>
                <div>
                    <span class="ui-badge {badge_class}">{impact_text}</span>
                </div>
            </div>
            <div class="ui-rec-meta">
                CATEGORY: {category}
            </div>
            <div class="ui-rec-body">{explanation}</div>
        </div>
        """
        st.markdown(card_markup, unsafe_allow_html=True)

st.markdown("<br><hr style='border-color: var(--border-light);'>", unsafe_allow_html=True)
if st.button("Return to Analysis Dashboard", use_container_width=False):
    st.switch_page("pages/2_Analysis_Dashboard.py")

# ── Footer ──
render_footer()
