"""
Executive Analysis Dashboard - maxanalysis platform.
Editorial layout:
- Sticky header with maxanalysis wordmark, back button, nav items, and refresh button.
- Wired Refresh Data button to the existing report fetcher: requests.get(f"{API_URL}/report/{analysis_id}").
- Metric cards on --surface-dark with large Obelisk numerals and grey labels.
- Monochromatic Plotly figures (gauge, radar, deviation bar chart, cost breakdown donut).
- High-contrast metric deviation table with text status badges.
Zero emojis.
"""

import streamlit as st
import requests
import sys, os
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from presentation_layer.components.ui_shell import inject_styles, render_header, render_footer
from presentation_layer.components.charts import (
    create_efficiency_gauge,
    create_radar_chart,
    create_deviation_bar_chart,
    create_cost_breakdown_donut,
)
from config import API_PORT, API_HOST

API_HOST = "127.0.0.1" if API_HOST in ("0.0.0.0", "") else API_HOST
API_URL = f"http://{API_HOST}:{API_PORT}/api"

st.set_page_config(
    page_title="Analysis Dashboard - maxanalysis",
    layout="wide",
    initial_sidebar_state="collapsed"
)

inject_styles()

# ── Existing Data-Loading Function for Report ──
def reload_dashboard_report() -> bool:
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
render_header(active_page="dashboard", refresh_callback=reload_dashboard_report)

if "analysis_id" not in st.session_state:
    st.markdown("""
    <div class="ui-dark-card" style="text-align: center; padding: 4rem 2rem; margin-top: 2rem;">
        <div class="ui-badge ui-badge-outline" style="margin-bottom: 1.25rem;">NO ACTIVE DATASET</div>
        <h3 style="margin: 0 0 0.75rem 0; color: var(--text-on-dark);">NO ACTIVE ANALYSIS FOUND</h3>
        <p style="font-size: 15px; color: var(--text-muted-on-dark); max-width: 520px; margin: 0 auto 2rem auto; line-height: 1.6;">
            Please upload an operational spreadsheet or run the sample venture launcher on the overview screen.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Proceed to Data Ingestion Page", use_container_width=True):
        st.switch_page("pages/1_Upload_Data.py")
    render_footer()
    st.stop()

analysis_id = st.session_state["analysis_id"]

# Fetch or use cached report data via existing endpoint
if "report_data" not in st.session_state or st.session_state.get("current_loaded_id") != analysis_id:
    with st.spinner("Fetching benchmark intelligence..."):
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

# ── Company Identity Header ──
company_name = report_data.get("company_name", "Target Startup")
peer_group = report_data.get("peer_group_label", "Standard Cohort")
computed = report_data.get("computed_metrics", {})
benchmarks = report_data.get("peer_benchmarks", {})
deviations = report_data.get("deviations", [])
eff_score = report_data.get("efficiency_score", 0)

st.markdown(f"""
<div class="ui-dark-card" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1.25rem; margin-top: 1.5rem; margin-bottom: 2rem;">
    <div>
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem; flex-wrap: wrap;">
            <h1 style="margin: 0; color: #F5F5F2 !important; font-size: 2.2rem;">{company_name}</h1>
            <span class="ui-badge ui-badge-outline" style="color: #F5F5F2 !important; border-color: #555555 !important;">Cohort: {peer_group}</span>
        </div>
        <div style="font-size: 14px; color: #A8A8A8 !important;">
            Multi-dimensional percentile benchmarking against direct industry and stage peers
        </div>
    </div>
    <div>
        <span class="ui-badge ui-badge-strong" style="padding: 0.5rem 1rem;">
            {len(report_data.get('recommendations', []))} RECOMMENDATIONS SYNTHESIZED
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Top KPI Metric Cards Row (Large Obelisk Numerals, Dark Cards) ──
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

runway_val = float(computed.get("runway_months", 0) or 0)
gm_val = float(computed.get("gross_margin", 0) or 0) * 100
ltv_cac_val = float(computed.get("ltv_cac_ratio", 0) or 0)
burn_val = float(computed.get("burn_rate", 0) or 0)

with kpi1:
    eff_status = "OPTIMAL" if eff_score >= 70 else "MODERATE" if eff_score >= 40 else "DEFICIT"
    st.markdown(f"""
    <div class="ui-metric-card">
        <div class="ui-metric-label">EFFICIENCY SCORE</div>
        <div class="ui-metric-value">{eff_score:.0f}<span style="font-size: 1.1rem; color: var(--text-muted-on-dark); font-weight: 500;"> / 100</span></div>
        <div class="ui-metric-sub">STATUS: {eff_status}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    runway_status = "VIABLE" if runway_val >= 18 else "WARNING" if runway_val >= 12 else "DEFICIT"
    runway_display = f"{runway_val:.1f} Mo" if runway_val < 99 else "100+ Mo"
    st.markdown(f"""
    <div class="ui-metric-card">
        <div class="ui-metric-label">ESTIMATED RUNWAY</div>
        <div class="ui-metric-value">{runway_display}</div>
        <div class="ui-metric-sub">STATUS: {runway_status}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    gm_status = "HEALTHY" if gm_val >= 70 else "WARNING" if gm_val >= 50 else "DEFICIT"
    st.markdown(f"""
    <div class="ui-metric-card">
        <div class="ui-metric-label">GROSS MARGIN</div>
        <div class="ui-metric-value">{gm_val:.1f}%</div>
        <div class="ui-metric-sub">STATUS: {gm_status}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    ltv_status = "OPTIMAL" if ltv_cac_val >= 3.0 else "WARNING" if ltv_cac_val >= 1.5 else "DEFICIT"
    st.markdown(f"""
    <div class="ui-metric-card">
        <div class="ui-metric-label">LTV : CAC RATIO</div>
        <div class="ui-metric-value">{ltv_cac_val:.1f}x</div>
        <div class="ui-metric-sub">TARGET: ≥ 3.0x ({ltv_status})</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Analytical Tabs ──
tab_overview, tab_deviations, tab_diagnostics = st.tabs([
    "EXECUTIVE BENCHMARKS",
    "METRIC DEVIATIONS & Z-SCORES",
    "FINANCIAL DIAGNOSTICS"
])

# Fetch raw startup financials to accurately populate cost breakdown and key metrics
startup_id = report_data.get("startup_id")
startup_raw = {}
if startup_id:
    try:
        from data_layer.storage.database import SessionLocal
        from data_layer.storage import models as db_models
        db = SessionLocal()
        s_obj = db.query(db_models.Startup).filter(db_models.Startup.id == startup_id).first()
        if s_obj:
            startup_raw = {
                "cogs": getattr(s_obj, "cogs", 0) or 0,
                "operating_expenses": getattr(s_obj, "operating_expenses", 0) or 0,
                "marketing_spend": getattr(s_obj, "marketing_spend", 0) or 0,
                "monthly_revenue": getattr(s_obj, "monthly_revenue", 0) or 0,
                "avg_revenue_per_customer": getattr(s_obj, "avg_revenue_per_customer", 0) or 0,
            }
        db.close()
    except Exception:
        pass

cogs_val = float(startup_raw.get("cogs", 0) or computed.get("cogs", 0) or 0)
opex_val = float(startup_raw.get("operating_expenses", 0) or computed.get("operating_expenses", 0) or 0)
mkt_val = float(startup_raw.get("marketing_spend", 0) or computed.get("marketing_spend", 0) or 0)
rev_val = float(startup_raw.get("monthly_revenue", 0) or computed.get("monthly_revenue", 0) or 0)
arpu_val = float(startup_raw.get("avg_revenue_per_customer", 0) or computed.get("avg_revenue_per_customer", 0) or 0)

with tab_overview:
    col_g, col_r = st.columns([1, 1.4], gap="large")
    with col_g:
        st.plotly_chart(create_efficiency_gauge(eff_score), use_container_width=True)
        st.markdown("""
        <div style="font-size: 13px; color: var(--text-muted-on-light); text-align: center; margin-top: -5px; line-height: 1.5;">
            Composite index of unit economics, runway viability, gross margin, and revenue growth calibrated by the trained model.
        </div>
        """, unsafe_allow_html=True)

    with col_r:
        radar_metrics = ['gross_margin', 'opex_to_revenue', 'runway_months', 'ltv_cac_ratio', 'mom_revenue_growth']
        st.plotly_chart(
            create_radar_chart(computed, benchmarks, radar_metrics),
            use_container_width=True
        )

with tab_deviations:
    col_dev_chart, col_dev_table = st.columns([1.1, 1.2], gap="large")

    with col_dev_chart:
        st.plotly_chart(create_deviation_bar_chart(deviations), use_container_width=True)

    with col_dev_table:
        st.markdown("##### DETAILED METRIC DEVIATIONS")
        if not deviations:
            st.info("All metrics fall within normal peer ranges.")
        else:
            dev_rows = []
            for d in deviations:
                severity = d.get("severity", "ok")
                status_text = "CRITICAL" if severity == "critical" else "WARNING" if severity == "warning" else "FAVORABLE"

                dev_rows.append({
                    "Metric": d.get("label", d.get("metric")),
                    "Your Value": f"{d.get('your_value', 0):.2f}",
                    "Peer Mean": f"{d.get('benchmark_mean', 0):.2f}",
                    "Z-Score": f"{d.get('z_score', 0):+.2f}σ",
                    "Status": status_text
                })
            df_devs = pd.DataFrame(dev_rows)
            st.dataframe(df_devs, use_container_width=True, hide_index=True)

with tab_diagnostics:
    col_cost_donut, col_fin_metrics = st.columns([1, 1.3], gap="large")

    with col_cost_donut:
        st.markdown("##### MONTHLY COST STRUCTURE")
        st.plotly_chart(create_cost_breakdown_donut(cogs_val, opex_val, mkt_val), use_container_width=True)

    with col_fin_metrics:
        st.markdown("##### KEY PERFORMANCE SUMMARY")
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Net Monthly Burn", f"${burn_val:,.0f}")
            st.metric("Monthly Revenue", f"${rev_val:,.0f}")
        with m2:
            st.metric("Rev / Employee", f"${float(computed.get('revenue_per_employee', 0) or 0):,.0f}")
            st.metric("Customer ARPU", f"${arpu_val:,.0f}/mo")

# ── Bottom Action Link ──
st.markdown("<br><hr style='border-color: var(--border-light);'>", unsafe_allow_html=True)
col_bt1, col_bt2 = st.columns([2, 1], vertical_alignment="center")
with col_bt1:
    st.markdown("""
    <div style="font-family: var(--font-heading); font-size: 1.25rem; font-weight: 700; text-transform: uppercase;">
        READY TO EXPLORE STRATEGIC INITIATIVES?
    </div>
    <div style="font-size: 14px; color: var(--text-muted-on-light); line-height: 1.5;">
        The system has generated rank-ordered interventions addressing these cohort deviations.
    </div>
    """, unsafe_allow_html=True)
with col_bt2:
    st.page_link("pages/3_Recommendations.py", label="View Recommendations →", use_container_width=True)

# ── Footer ──
render_footer()
