"""
Interactive Executive Analysis Dashboard for Startup Analyzer AI.
Displays KPI cards, circular efficiency score gauge, peer radar comparisons,
and detailed metric deviation breakdowns.
"""

import streamlit as st
import requests
import sys, os
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from presentation_layer.components.styles import load_custom_css
from presentation_layer.components.charts import (
    create_efficiency_gauge,
    create_radar_chart,
    create_deviation_bar_chart,
    create_cost_breakdown_donut,
)
from config import API_PORT, API_HOST

API_HOST = "127.0.0.1" if API_HOST in ("0.0.0.0", "") else API_HOST
API_URL = f"http://{API_HOST}:{API_PORT}/api"

st.set_page_config(page_title="Analysis Dashboard - Startup Analyzer", page_icon="📊", layout="wide")
load_custom_css()

# ── Step Indicator ──
st.markdown("""
<div class="step-bar">
    <div class="step-item">
        <span class="step-number">1</span>
        <span>Data Ingestion</span>
    </div>
    <div style="color: #475569;">➔</div>
    <div class="step-item active">
        <span class="step-number">2</span>
        <span>Peer Benchmarking</span>
    </div>
    <div style="color: #475569;">➔</div>
    <div class="step-item">
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
            Please upload a dataset or use the 1-click sample company launcher to view benchmarking scores.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_Upload_Data.py", label="➔ Go to Data Ingestion Page", use_container_width=True)
    st.stop()

analysis_id = st.session_state["analysis_id"]

with st.spinner("Fetching benchmark intelligence..."):
    try:
        response = requests.get(f"{API_URL}/report/{analysis_id}")
        if response.status_code != 200:
            st.error(f"Failed to fetch report: {response.text}")
            st.stop()
        report_data = response.json()
    except Exception as e:
        st.error(f"Connection error: {e}")
        st.stop()

# ── Company Identity Header ──
company_name = report_data.get("company_name", "Target Startup")
peer_group = report_data.get("peer_group_label", "Standard Cohort")
computed = report_data.get("computed_metrics", {})
benchmarks = report_data.get("peer_benchmarks", {})
deviations = report_data.get("deviations", [])
eff_score = report_data.get("efficiency_score", 0)

st.markdown(f"""
<div class="glass-card" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem;">
    <div>
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.35rem;">
            <h2 style="margin: 0; font-size: 1.85rem; color: #FFFFFF;">{company_name}</h2>
            <span class="badge badge-neutral">Cohort: {peer_group}</span>
        </div>
        <div style="font-size: 0.88rem; color: #94A3B8;">
            Direct comparison against matched peer group distribution
        </div>
    </div>
    <div>
        <a href="#recommendations-link" style="text-decoration: none;">
            <span class="badge badge-favorable" style="padding: 0.5rem 1rem; font-size: 0.85rem;">
                ⚡ {len(report_data.get('recommendations', []))} Strategic Recommendations Generated
            </span>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Top KPI Metric Cards Row ──
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

runway_val = float(computed.get("runway_months", 0) or 0)
gm_val = float(computed.get("gross_margin", 0) or 0) * 100
ltv_cac_val = float(computed.get("ltv_cac_ratio", 0) or 0)
burn_val = float(computed.get("burn_rate", 0) or 0)

with kpi1:
    eff_badge = "badge-favorable" if eff_score >= 70 else "badge-warning" if eff_score >= 40 else "badge-critical"
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Efficiency Score</div>
        <div class="kpi-value">{eff_score:.0f}<span style="font-size: 1.1rem; color: #64748B;">/100</span></div>
        <div class="kpi-caption">
            <span class="badge {eff_badge}">Model Scored</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    runway_badge = "badge-favorable" if runway_val >= 18 else "badge-warning" if runway_val >= 12 else "badge-critical"
    runway_display = f"{runway_val:.1f} Mo" if runway_val < 99 else "100+ Mo"
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Estimated Runway</div>
        <div class="kpi-value">{runway_display}</div>
        <div class="kpi-caption">
            <span class="badge {runway_badge}">Cash Remaining</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    gm_badge = "badge-favorable" if gm_val >= 70 else "badge-warning" if gm_val >= 50 else "badge-critical"
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Gross Margin</div>
        <div class="kpi-value">{gm_val:.1f}%</div>
        <div class="kpi-caption">
            <span class="badge {gm_badge}">Unit Economics</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    ltv_badge = "badge-favorable" if ltv_cac_val >= 3.0 else "badge-warning" if ltv_cac_val >= 1.5 else "badge-critical"
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">LTV : CAC Ratio</div>
        <div class="kpi-value">{ltv_cac_val:.1f}x</div>
        <div class="kpi-caption">
            <span class="badge {ltv_badge}">Target: ≥ 3.0x</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs for Analytical Exploration ──
tab_overview, tab_deviations, tab_diagnostics = st.tabs([
    "📈 Executive Benchmarks",
    "🎯 Metric Deviations & Z-Scores",
    "🔬 Financial Diagnostics"
])

with tab_overview:
    col_g, col_r = st.columns([1, 1.4], gap="large")
    with col_g:
        st.plotly_chart(create_efficiency_gauge(eff_score), use_container_width=True)
        st.markdown("""
        <div style="font-size: 0.85rem; color: #94A3B8; text-align: center; margin-top: -15px;">
            The score reflects a composite of unit economics, runway viability, gross margin, and revenue growth calibrated by the trained LightGBM model.
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
        st.markdown("##### Detailed Metric Deviations")
        if not deviations:
            st.info("All metrics fall within normal peer ranges.")
        else:
            dev_rows = []
            for d in deviations:
                severity = d.get("severity", "ok")
                pill = "🔴 Critical" if severity == "critical" else "⚠️ Warning" if severity == "warning" else "✅ Favorable"
                
                dev_rows.append({
                    "Metric": d.get("label", d.get("metric")),
                    "Your Value": f"{d.get('your_value', 0):.2f}",
                    "Peer Mean": f"{d.get('benchmark_mean', 0):.2f}",
                    "Z-Score": f"{d.get('z_score', 0):+.2f}σ",
                    "Severity": pill
                })
            df_devs = pd.DataFrame(dev_rows)
            st.dataframe(df_devs, use_container_width=True, hide_index=True)

with tab_diagnostics:
    col_cost_donut, col_fin_metrics = st.columns([1, 1.3], gap="large")

    with col_cost_donut:
        st.markdown("##### Monthly Cost Structure")
        cogs_val = float(computed.get("cogs", 0) or 0)
        opex_val = float(computed.get("operating_expenses", 0) or 0)
        mkt_val = float(computed.get("marketing_spend", 0) or 0)
        st.plotly_chart(create_cost_breakdown_donut(cogs_val, opex_val, mkt_val), use_container_width=True)

    with col_fin_metrics:
        st.markdown("##### Key Performance Metrics Summary")
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Net Monthly Burn", f"${burn_val:,.0f}")
            st.metric("Monthly Revenue", f"${float(computed.get('monthly_revenue', 0) or 0):,.0f}")
        with m2:
            st.metric("Rev / Employee", f"${float(computed.get('revenue_per_employee', 0) or 0):,.0f}")
            st.metric("Customer ARPU", f"${float(computed.get('avg_revenue_per_customer', 0) or 0):,.0f}/mo")

# ── Bottom Action Link ──
st.markdown("<br><hr id='recommendations-link' style='border-color: rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
col_bt1, col_bt2 = st.columns([2, 1])
with col_bt1:
    st.markdown("""
    <div style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF;">
        Ready to explore tailored growth strategies?
    </div>
    <div style="font-size: 0.9rem; color: #94A3B8;">
        The AI has identified key optimization levers based on these deviations.
    </div>
    """, unsafe_allow_html=True)
with col_bt2:
    st.page_link("pages/3_Recommendations.py", label="View AI Recommendations ➔", icon="💡", use_container_width=True)
