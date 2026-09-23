"""
AI Business Recommendations Page for Startup Analyzer AI.
Presents prioritised, explainable strategic initiatives, impact filtering,
and PDF export capability.
"""

import streamlit as st
import requests
import sys, os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from presentation_layer.components.styles import load_custom_css
from config import API_PORT, API_HOST

API_HOST = "127.0.0.1" if API_HOST in ("0.0.0.0", "") else API_HOST
API_URL = f"http://{API_HOST}:{API_PORT}/api"

st.set_page_config(page_title="Recommendations - Startup Analyzer", page_icon="💡", layout="wide")
load_custom_css()

# ── Flow Step Indicator ──
st.markdown("""
<div class="step-bar">
    <div class="step-item">
        <span class="step-number">1</span>
        <span>Data Ingestion</span>
    </div>
    <div style="color: #475569;">➔</div>
    <div class="step-item">
        <span class="step-number">2</span>
        <span>Peer Benchmarking</span>
    </div>
    <div style="color: #475569;">➔</div>
    <div class="step-item active">
        <span class="step-number">3</span>
        <span>AI Recommendations</span>
    </div>
</div>
""", unsafe_allow_html=True)

if "analysis_id" not in st.session_state:
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 3rem 2rem;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
        <h3 style="margin-top: 0; color: #FFFFFF;">No Active Analysis Found</h3>
        <p style="font-size: 0.95rem; color: #94A3B8; max-width: 500px; margin: 0 auto 1.5rem auto;">
            Please upload a dataset or use the 1-click sample company launcher to view recommendations.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_Upload_Data.py", label="➔ Go to Data Ingestion Page", use_container_width=True)
    st.stop()

analysis_id = st.session_state["analysis_id"]

with st.spinner("Fetching AI strategic insights..."):
    try:
        response = requests.get(f"{API_URL}/report/{analysis_id}")
        if response.status_code != 200:
            st.error(f"Failed to fetch report: {response.text}")
            st.stop()
        report_data = response.json()
    except Exception as e:
        st.error(f"Connection error: {e}")
        st.stop()

company_name = report_data.get("company_name", "Target Startup")
recommendations = report_data.get("recommendations", [])

# ── Header & PDF Export Card ──
col_head1, col_head2 = st.columns([2.2, 1], gap="large")

with col_head1:
    st.title("💡 Strategic Recommendations")
    st.markdown(f"Prioritised, data-grounded guidance for **{company_name}** based on deviations from successful cohort peers.")

with col_head2:
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    try:
        pdf_res = requests.get(f"{API_URL}/export/{analysis_id}/pdf", timeout=10)
        if pdf_res.status_code == 200:
            st.download_button(
                label="📄 Export Executive PDF Report",
                data=pdf_res.content,
                file_name=f"{company_name}_Executive_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.button("📄 Export PDF (Unavailable)", disabled=True, use_container_width=True)
    except Exception:
        st.button("📄 Export PDF (Service Offline)", disabled=True, use_container_width=True)

# ── Summary Badges Row ──
high_recs = [r for r in recommendations if r.get("impact_level", "").lower() == "high"]
med_recs = [r for r in recommendations if r.get("impact_level", "").lower() == "medium"]
low_recs = [r for r in recommendations if r.get("impact_level", "").lower() == "low"]

sc1, sc2, sc3, sc4 = st.columns(4)
with sc1:
    st.markdown(f"""
    <div class="kpi-card" style="padding: 1rem 1.2rem;">
        <div class="kpi-label">Total Actions</div>
        <div class="kpi-value" style="font-size: 1.8rem;">{len(recommendations)}</div>
    </div>
    """, unsafe_allow_html=True)
with sc2:
    st.markdown(f"""
    <div class="kpi-card" style="padding: 1rem 1.2rem;">
        <div class="kpi-label">High Priority</div>
        <div class="kpi-value" style="font-size: 1.8rem; color: #F87171;">{len(high_recs)}</div>
    </div>
    """, unsafe_allow_html=True)
with sc3:
    st.markdown(f"""
    <div class="kpi-card" style="padding: 1rem 1.2rem;">
        <div class="kpi-label">Medium Priority</div>
        <div class="kpi-value" style="font-size: 1.8rem; color: #FBBF24;">{len(med_recs)}</div>
    </div>
    """, unsafe_allow_html=True)
with sc4:
    st.markdown(f"""
    <div class="kpi-card" style="padding: 1rem 1.2rem;">
        <div class="kpi-label">Optimizations</div>
        <div class="kpi-value" style="font-size: 1.8rem; color: #34D399;">{len(low_recs)}</div>
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
    <div class="glass-card" style="text-align: center; padding: 2rem;">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎉</div>
        <h4 style="margin: 0; color: #FFFFFF;">No recommendations in this filter.</h4>
    </div>
    """, unsafe_allow_html=True)
else:
    for rec in filtered_recs:
        impact_level = rec.get("impact_level", "Medium")
        impact_lower = impact_level.lower()
        
        card_class = f"rec-card-{impact_lower}"
        badge_class = "badge-critical" if impact_lower == "high" else "badge-warning" if impact_lower == "medium" else "badge-favorable"
        
        rank = rec.get("rank", 1)
        title = rec.get("title", "Strategic Opportunity")
        category = rec.get("category", "General")
        explanation = rec.get("explanation", "")
        
        st.markdown(f"""
        <div class="rec-card {card_class}">
            <div class="rec-header">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <span style="background: rgba(255, 255, 255, 0.1); color: #FFFFFF; font-weight: 700; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.85rem;">
                        #{rank}
                    </span>
                    <span class="rec-title">{title}</span>
                </div>
                <div>
                    <span class="badge {badge_class}">⚡ {impact_level} Impact</span>
                </div>
            </div>
            <div class="rec-meta">
                <span class="badge badge-neutral">🏷️ {category}</span>
            </div>
            <div class="rec-body">
                {explanation}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><hr style='border-color: rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
st.page_link("pages/2_Analysis_Dashboard.py", label="➔ Back to Analysis Dashboard", icon="📊")
