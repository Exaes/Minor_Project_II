"""
Startup Analyzer AI - Modern Executive Landing Page.
"""

import streamlit as st
import requests
import sys, os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from presentation_layer.components.styles import load_custom_css
from config import API_PORT, API_HOST

API_HOST = "127.0.0.1" if API_HOST in ("0.0.0.0", "") else API_HOST
API_URL = f"http://{API_HOST}:{API_PORT}/api"

st.set_page_config(
    page_title="Startup Analyzer AI | Intelligence Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_custom_css()

# ── Health check ──
api_healthy = False
try:
    health_res = requests.get(f"{API_URL}/health", timeout=1.5)
    api_healthy = (health_res.status_code == 200)
except Exception:
    api_healthy = False

# ── Hero Section ──
status_color = "#10B981" if api_healthy else "#F59E0B"
status_text = "System Operational" if api_healthy else "Connecting to Backend..."

st.markdown(f"""
<div class="hero-container">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div class="hero-badge">⚡ Enterprise Startup Benchmarking</div>
        <div style="display: inline-flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; color: #94A3B8;">
            <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background-color: {status_color}; box-shadow: 0 0 10px {status_color};"></span>
            {status_text}
        </div>
    </div>
    <div class="hero-title">
        Decisive Intelligence for <span class="hero-gradient-text">High-Growth Startups</span>
    </div>
    <div class="hero-subtitle">
        Benchmark operational unit economics, identify hidden runway risks, and unlock explainable ML & LLM-driven strategic recommendations calibrated to your industry cohort.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Quick Action / Demo Launcher ──
col_demo, col_steps = st.columns([1.2, 2.0], gap="large")

with col_demo:
    st.markdown("""
    <div class="glass-card" style="border-color: rgba(99, 102, 241, 0.4); background: linear-gradient(135deg, rgba(26, 35, 54, 0.85) 0%, rgba(18, 25, 38, 0.95) 100%);">
        <div style="font-size: 0.82rem; font-weight: 700; color: #A5B4FC; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
            ⚡ Instant Evaluation
        </div>
        <h3 style="margin-top: 0; margin-bottom: 0.5rem; color: #FFFFFF; font-size: 1.4rem;">
            One-Click Demo Startup
        </h3>
        <p style="font-size: 0.92rem; color: #94A3B8; line-height: 1.5; margin-bottom: 1.25rem;">
            Test the entire benchmarking and AI recommendation engine instantly using a pre-configured Series A B2B SaaS startup.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 Load Sample Company & Benchmark", use_container_width=True):
        demo_payload = {
            "company_name": "NovaPulse Technologies",
            "industry": "SaaS",
            "founding_year": 2021,
            "funding_stage": "Series A",
            "headcount": 32,
            "total_funding_usd": 6500000.0,
            "funding_rounds_count": 2,
            "monthly_revenue": 145000.0,
            "monthly_expenses": 190000.0,
            "marketing_spend": 42000.0,
            "customer_count": 480,
            "new_customers_monthly": 36,
            "cogs": 26000.0,
            "operating_expenses": 164000.0,
            "avg_revenue_per_customer": 302.08,
            "avg_customer_lifetime_months": 28.0,
            "mom_revenue_growth": 0.075,
            "mom_customer_growth": 0.065,
            "yoy_revenue_growth": 0.88,
        }

        with st.spinner("Analyzing demo startup against peer cohort..."):
            try:
                sub_res = requests.post(f"{API_URL}/manual-entry", json=demo_payload, timeout=5)
                if sub_res.status_code == 200:
                    startup_id = sub_res.json()["startup_id"]
                    ana_res = requests.post(f"{API_URL}/analyze/{startup_id}?use_llm=true", timeout=15)
                    if ana_res.status_code == 200:
                        analysis_id = ana_res.json()["analysis_id"]
                        st.session_state["analysis_id"] = analysis_id
                        st.success("✅ Demo Analysis ready! Navigate to Dashboard below:")
                        st.page_link("pages/2_Analysis_Dashboard.py", label="View Analysis Dashboard ➔", icon="📊")
                    else:
                        st.error(f"Analysis error: {ana_res.text}")
                else:
                    st.error(f"Demo submission failed: {sub_res.text}")
            except Exception as e:
                st.error(f"Connection failed: {e}")

with col_steps:
    st.markdown("""
    <div style="display: flex; flex-direction: column; gap: 1rem;">
        <div class="glass-card" style="margin-bottom: 0;">
            <div style="display: flex; gap: 1rem; align-items: flex-start;">
                <div style="background: rgba(99, 102, 241, 0.2); color: #A5B4FC; width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.1rem; flex-shrink: 0;">1</div>
                <div>
                    <h4 style="margin: 0 0 0.35rem 0; color: #FFFFFF;">Flexible Data Ingestion</h4>
                    <p style="margin: 0; font-size: 0.9rem; color: #94A3B8;">Upload custom CSV / Excel sheets or fill out the streamlined metrics form. Missing values are automatically inferred using statistical defaults.</p>
                </div>
            </div>
        </div>
        <div class="glass-card" style="margin-bottom: 0;">
            <div style="display: flex; gap: 1rem; align-items: flex-start;">
                <div style="background: rgba(6, 182, 212, 0.2); color: #22D3EE; width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.1rem; flex-shrink: 0;">2</div>
                <div>
                    <h4 style="margin: 0 0 0.35rem 0; color: #FFFFFF;">Cohort-Specific ML Benchmarking</h4>
                    <p style="margin: 0; font-size: 0.9rem; color: #94A3B8;">The LightGBM benchmark model clusters your venture with direct industry, stage, and headcount peers to calculate multi-dimensional Z-scores.</p>
                </div>
            </div>
        </div>
        <div class="glass-card" style="margin-bottom: 0;">
            <div style="display: flex; gap: 1rem; align-items: flex-start;">
                <div style="background: rgba(16, 185, 129, 0.2); color: #34D399; width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.1rem; flex-shrink: 0;">3</div>
                <div>
                    <h4 style="margin: 0 0 0.35rem 0; color: #FFFFFF;">Actionable Strategic Advisory & PDF</h4>
                    <p style="margin: 0; font-size: 0.9rem; color: #94A3B8;">Receive ranked, impact-weighted interventions generated by business heuristics and LLMs, complete with one-click executive PDF export.</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Navigation Cards ──
st.markdown("### 🧭 Quick Navigation")
nav_col1, nav_col2, nav_col3 = st.columns(3)

with nav_col1:
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 2rem 1.5rem;">
        <div style="font-size: 2.2rem; margin-bottom: 0.75rem;">📁</div>
        <h4 style="margin: 0 0 0.5rem 0; color: #FFFFFF;">Upload Data</h4>
        <p style="font-size: 0.88rem; color: #94A3B8; margin-bottom: 1.25rem;">
            Upload CSV/Excel spreadsheets or enter startup operational data manually.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_Upload_Data.py", label="Open Data Ingestion ➔", use_container_width=True)

with nav_col2:
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 2rem 1.5rem;">
        <div style="font-size: 2.2rem; margin-bottom: 0.75rem;">📊</div>
        <h4 style="margin: 0 0 0.5rem 0; color: #FFFFFF;">Analysis Dashboard</h4>
        <p style="font-size: 0.88rem; color: #94A3B8; margin-bottom: 1.25rem;">
            Inspect your overall efficiency score, radar cohort comparisons, and metric deviations.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/2_Analysis_Dashboard.py", label="Open Dashboard ➔", use_container_width=True)

with nav_col3:
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 2rem 1.5rem;">
        <div style="font-size: 2.2rem; margin-bottom: 0.75rem;">💡</div>
        <h4 style="margin: 0 0 0.5rem 0; color: #FFFFFF;">AI Recommendations</h4>
        <p style="font-size: 0.88rem; color: #94A3B8; margin-bottom: 1.25rem;">
            Explore prioritised, explainable strategic initiatives and download your PDF report.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/3_Recommendations.py", label="Open Recommendations ➔", use_container_width=True)
