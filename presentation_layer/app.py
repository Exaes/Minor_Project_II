"""
Executive Intelligence Platform - maxanalysis.
Main screen page:
1. Hero visual with high-contrast editorial photography, tagline, huge MAXANALYSIS wordmark, and action buttons.
2. Dark feature strip (4 columns).
3. Split story section ("UPLOAD. BENCHMARK. ACT.").
4. Trust row (5 items).
5. Monochromatic footer.
Zero emojis.
"""

import streamlit as st
import requests
import sys, os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from presentation_layer.components.ui_shell import inject_styles, render_header, render_footer, ICONS
from presentation_layer.components.styles import get_image_base64
from config import API_PORT, API_HOST

API_HOST = "127.0.0.1" if API_HOST in ("0.0.0.0", "") else API_HOST
API_URL = f"http://{API_HOST}:{API_PORT}/api"

st.set_page_config(
    page_title="maxanalysis - Intelligence Platform",
    layout="wide",
    initial_sidebar_state="collapsed"
)

inject_styles()

# ── Image Assets Embedded via Base64 Data URIs ──
hero_img = get_image_base64("hero-money.jpeg")
story_img = get_image_base64("story.jpg")
f1_img = get_image_base64("feature-1.jpg")
f2_img = get_image_base64("feature-2.jpg")
f3_img = get_image_base64("feature-3.jpg")
f4_img = get_image_base64("feature-4.jpg")

# ── Existing Data-Loading Function for Health/Status ──
def check_api_health() -> bool:
    try:
        health_res = requests.get(f"http://{API_HOST}:{API_PORT}/health", timeout=1.5)
        if health_res.status_code != 200:
            health_res = requests.get(f"{API_URL}/health", timeout=1.5)
        healthy = (health_res.status_code == 200)
        st.session_state["api_healthy"] = healthy
        return healthy
    except Exception:
        st.session_state["api_healthy"] = False
        return False

# Initial load if not checked yet
if "api_healthy" not in st.session_state:
    check_api_health()

# ── Sticky maxanalysis Header ──
render_header(active_page="main", refresh_callback=check_api_health)

# ── Section 1: Hero Visual (Full width, ~70vh) ──
hero_bg_url = hero_img if hero_img else "app/static/images/hero-money.jpeg"
story_bg_url = story_img if story_img else "app/static/images/story.jpg"
f1_bg_url = f1_img if f1_img else "app/static/images/feature-1.jpg"
f2_bg_url = f2_img if f2_img else "app/static/images/feature-2.jpg"
f3_bg_url = f3_img if f3_img else "app/static/images/feature-3.jpg"
f4_bg_url = f4_img if f4_img else "app/static/images/feature-4.jpg"

st.markdown(f"""
<style>
.ui-hero-container {{
    background: linear-gradient(90deg, rgba(237, 235, 230, 0.88) 0%, rgba(237, 235, 230, 0.55) 45%, rgba(237, 235, 230, 0.12) 100%), url('{hero_bg_url}') no-repeat center center !important;
    background-size: cover !important;
}}
.ui-story-media {{
    background: url('{story_bg_url}') no-repeat center center !important;
    background-size: cover !important;
    min-height: 420px !important;
    filter: grayscale(1) contrast(1.15) !important;
}}
.ui-feature-card:nth-child(1) {{
    background: linear-gradient(rgba(21, 21, 21, 0.88), rgba(21, 21, 21, 0.88)), url('{f1_bg_url}') no-repeat center center !important;
    background-size: cover !important;
}}
.ui-feature-card:nth-child(2) {{
    background: linear-gradient(rgba(21, 21, 21, 0.88), rgba(21, 21, 21, 0.88)), url('{f2_bg_url}') no-repeat center center !important;
    background-size: cover !important;
}}
.ui-feature-card:nth-child(3) {{
    background: linear-gradient(rgba(21, 21, 21, 0.88), rgba(21, 21, 21, 0.88)), url('{f3_bg_url}') no-repeat center center !important;
    background-size: cover !important;
}}
.ui-feature-card:nth-child(4) {{
    background: linear-gradient(rgba(21, 21, 21, 0.88), rgba(21, 21, 21, 0.88)), url('{f4_bg_url}') no-repeat center center !important;
    background-size: cover !important;
}}
.ui-feature-title,
.ui-feature-card h4 {{
    color: #F5F5F2 !important;
}}
</style>
<div class="ui-hero-container">
    <div class="ui-hero-content">
        <div class="ui-hero-tagline">
            UPLOAD YOUR DATA.<br>
            SEE HOW YOU COMPARE.<br>
            ACT ON THE GAPS.
        </div>
        <div class="ui-hero-wordmark">MAXANALYSIS</div>
        <div class="ui-hero-bottom">
            <div></div>
            <div class="ui-hero-sublabel">B.Tech mini project</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Hero Action Controls directly beneath visual
with st.container(key="ui_hero_actions_wrapper"):
    col_h1, col_h2, col_h3, col_h_spacer = st.columns([1.5, 1.8, 1.8, 2.5], vertical_alignment="center")

    with col_h1:
        if st.button("Upload Data", key="hero_btn_upload", use_container_width=True):
            st.switch_page("pages/1_Upload_Data.py")

    with col_h2:
        if st.button("Analysis Dashboard →", key="hero_btn_dashboard", use_container_width=True):
            st.switch_page("pages/2_Analysis_Dashboard.py")

    with col_h3:
        launch_demo = st.button("Load Sample Venture", key="hero_btn_demo", use_container_width=True)

# ── Demo Action Handler (Preserved Unaltered) ──
if launch_demo:
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
                    st.success("Analysis generated successfully. Navigate to Dashboard below:")
                    st.page_link("pages/2_Analysis_Dashboard.py", label="Open Analysis Dashboard")
                else:
                    st.error(f"Analysis error: {ana_res.text}")
            else:
                st.error(f"Demo submission failed: {sub_res.text}")
        except Exception as e:
            st.error(f"Connection failed: {e}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Section 2: Dark Feature Strip (4 columns) ──
f_up_icon = ICONS["upload"]
f_dash_icon = ICONS["dashboard"]
f_rec_icon = ICONS["recommendation"]
f_exp_icon = ICONS["export"]

st.markdown(f"""
<div class="ui-feature-strip">
    <div class="ui-feature-card">
        <div class="ui-feature-icon">{f_up_icon}</div>
        <h4 class="ui-feature-title">Upload Data</h4>
        <p class="ui-feature-text">Ingest operational spreadsheets or input verified startup metrics directly.</p>
        <a href="/Upload_Data">Open Ingestion →</a>
    </div>
    <div class="ui-feature-card">
        <div class="ui-feature-icon">{f_dash_icon}</div>
        <h4 class="ui-feature-title">Analysis Dashboard</h4>
        <p class="ui-feature-text">Benchmark unit economics and detect runway risks against cohort percentiles.</p>
        <a href="/Analysis_Dashboard">View Dashboard →</a>
    </div>
    <div class="ui-feature-card">
        <div class="ui-feature-icon">{f_rec_icon}</div>
        <h4 class="ui-feature-title">Recommendation</h4>
        <p class="ui-feature-text">Synthesize prioritized, impact-weighted strategic interventions.</p>
        <a href="/Recommendations">Explore Initiatives →</a>
    </div>
    <div class="ui-feature-card">
        <div class="ui-feature-icon">{f_exp_icon}</div>
        <h4 class="ui-feature-title">Export Report</h4>
        <p class="ui-feature-text">Generate structured executive PDF summaries for stakeholder briefings.</p>
        <a href="/Recommendations">Download Briefing →</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Section 3: Split Story Section ──
col_story_img, col_story_text = st.columns([1, 1], gap="medium")

with col_story_img:
    st.markdown("""
    <div class="ui-story-media" role="img" aria-label="Executive architectural perspective"></div>
    """, unsafe_allow_html=True)

with col_story_text:
    st.markdown("""
    <div style="padding: 1.5rem 0.5rem;">
        <div class="ui-badge ui-badge-outline" style="margin-bottom: 1rem;">Core Architecture</div>
        <h2 class="ui-story-headline">UPLOAD.<br>BENCHMARK.<br>ACT.</h2>
        <p class="ui-story-body">
            Raw financial numbers are ingested and matched against calibrated industry and stage cohorts.
            Multi-dimensional Z-score synthesis detects structural capital risks and operational inefficiencies.
            Heuristic decision rules generate actionable, rank-ordered interventions with immediate PDF export.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Discover the analysis", key="story_discover_btn"):
        st.switch_page("pages/2_Analysis_Dashboard.py")

st.markdown("<br>", unsafe_allow_html=True)

# ── Section 4: Trust Row (5 items) ──
t_b_icon = ICONS["benchmark"]
t_e_icon = ICONS["explainable"]
t_m_icon = ICONS["metrics"]
t_x_icon = ICONS["export"]
t_s_icon = ICONS["storage"]

st.markdown(f"""
<div class="ui-trust-row">
    <div class="ui-trust-item">
        <div class="ui-trust-icon">{t_b_icon}</div>
        <div class="ui-trust-title">Peer benchmarking</div>
        <div class="ui-trust-desc">Stage and sector cohort comparison</div>
    </div>
    <div class="ui-trust-item">
        <div class="ui-trust-icon">{t_e_icon}</div>
        <div class="ui-trust-title">Explainable recommendations</div>
        <div class="ui-trust-desc">Rank-ordered strategic interventions</div>
    </div>
    <div class="ui-trust-item">
        <div class="ui-trust-icon">{t_m_icon}</div>
        <div class="ui-trust-title">15+ financial metrics</div>
        <div class="ui-trust-desc">Runway, margins and burn synthesis</div>
    </div>
    <div class="ui-trust-item">
        <div class="ui-trust-icon">{t_x_icon}</div>
        <div class="ui-trust-title">PDF report export</div>
        <div class="ui-trust-desc">One-click executive document briefing</div>
    </div>
    <div class="ui-trust-item">
        <div class="ui-trust-icon">{t_s_icon}</div>
        <div class="ui-trust-title">Local data storage</div>
        <div class="ui-trust-desc">Secure local SQLite persistence</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Section 5: Footer ──
render_footer()
