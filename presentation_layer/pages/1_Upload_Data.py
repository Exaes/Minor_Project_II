"""
Data Ingestion Page - Upload CSV/Excel or Enter Metrics Manually.
"""

import streamlit as st
import requests
import sys, os
import pandas as pd
import io

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from presentation_layer.components.styles import load_custom_css
from config import API_PORT, API_HOST

API_HOST = "127.0.0.1" if API_HOST in ("0.0.0.0", "") else API_HOST
API_URL = f"http://{API_HOST}:{API_PORT}/api"

st.set_page_config(page_title="Upload Data - Startup Analyzer", page_icon="📁", layout="wide")
load_custom_css()

# ── Flow Step Indicator ──
st.markdown("""
<div class="step-bar">
    <div class="step-item active">
        <span class="step-number">1</span>
        <span>Data Ingestion</span>
    </div>
    <div style="color: #475569;">➔</div>
    <div class="step-item">
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

st.title("📁 Ingest Startup Metrics")
st.markdown("Provide your operational and financial numbers via spreadsheet upload or interactive form.")

tab1, tab2 = st.tabs(["📄 Upload CSV / Excel", "✍️ Interactive Manual Entry"])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: FILE UPLOAD
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    col_up_main, col_up_side = st.columns([2, 1], gap="large")

    with col_up_main:
        st.markdown("""
        <div class="glass-card">
            <h4 style="margin-top: 0; color: #FFFFFF; font-size: 1.15rem;">Spreadsheet Upload</h4>
            <p style="font-size: 0.88rem; color: #94A3B8; margin-bottom: 1rem;">
                Select a <code>.csv</code> or <code>.xlsx</code> file containing your startup metrics. The pipeline takes the target record and compares it to its matching cohort.
            </p>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Choose a spreadsheet file",
            type=["csv", "xlsx"],
            label_visibility="collapsed"
        )

        # Quick Load Sample Button
        st.markdown("<p style='font-size: 0.85rem; color: #64748B; margin-top: 0.5rem;'>Don't have a file ready? Test immediately with a sample dataset:</p>", unsafe_allow_html=True)
        if st.button("⚡ Test with Sample SaaS Spreadsheet", use_container_width=False):
            sample_csv_text = (
                "company_name,industry,founding_year,funding_stage,total_funding_usd,funding_rounds_count,monthly_revenue,monthly_expenses,cogs,operating_expenses,gross_profit,headcount,customer_count,monthly_burn,marketing_spend,avg_revenue_per_customer,avg_customer_lifetime_months,new_customers_monthly,mom_revenue_growth,mom_customer_growth,yoy_revenue_growth\n"
                "ApexFlow Labs,SaaS,2021,Seed,1800000,2,55000,68000,11000,57000,44000,14,180,13000,14000,305.5,24,18,0.085,0.065,0.92\n"
            )
            sample_bytes = sample_csv_text.encode("utf-8")
            with st.spinner("Processing sample file..."):
                files = {"file": ("sample_startup.csv", sample_bytes, "text/csv")}
                try:
                    res = requests.post(f"{API_URL}/upload", files=files)
                    if res.status_code == 200:
                        startup_id = res.json()["startup_id"]
                        ana_res = requests.post(f"{API_URL}/analyze/{startup_id}?use_llm=true")
                        if ana_res.status_code == 200:
                            st.session_state["analysis_id"] = ana_res.json()["analysis_id"]
                            st.success("✅ Sample uploaded & analyzed! Proceed to the Dashboard.")
                            st.page_link("pages/2_Analysis_Dashboard.py", label="View Analysis Dashboard ➔", icon="📊")
                        else:
                            st.error(f"Analysis failed: {ana_res.text}")
                    else:
                        st.error(f"Upload failed: {res.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

        if uploaded_file is not None:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Upload and Analyze Spreadsheet", use_container_width=True):
                with st.spinner("Uploading and analyzing your startup data..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    try:
                        response = requests.post(f"{API_URL}/upload", files=files)
                        if response.status_code == 200:
                            startup_id = response.json()["startup_id"]
                            analysis_res = requests.post(f"{API_URL}/analyze/{startup_id}?use_llm=true")
                            if analysis_res.status_code == 200:
                                analysis_id = analysis_res.json()["analysis_id"]
                                st.session_state["analysis_id"] = analysis_id
                                st.success("✅ Analysis complete! Ready to view findings.")
                                st.page_link("pages/2_Analysis_Dashboard.py", label="Go to Analysis Dashboard ➔", icon="📊")
                            else:
                                st.error(f"Analysis failed: {analysis_res.text}")
                        else:
                            st.error(f"Upload failed: {response.text}")
                    except Exception as e:
                        st.error(f"Request failed: {e}")

    with col_up_side:
        # Download Template Card
        template_path = os.path.join(os.path.dirname(__file__), "..", "..", "data_layer", "templates", "upload_template.csv")
        template_csv = ""
        if os.path.exists(template_path):
            with open(template_path, "r") as f:
                template_csv = f.read()

        st.markdown("""
        <div class="glass-card">
            <h4 style="margin-top: 0; color: #FFFFFF; font-size: 1.1rem;">📥 CSV Template</h4>
            <p style="font-size: 0.85rem; color: #94A3B8; margin-bottom: 1rem;">
                Download the standardized CSV header template containing all canonical fields.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.download_button(
            label="Download Template CSV",
            data=template_csv,
            file_name="startup_template.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.markdown("""
        <div class="glass-card" style="margin-top: 1rem;">
            <div style="font-size: 0.8rem; font-weight: 700; color: #A5B4FC; text-transform: uppercase; margin-bottom: 0.5rem;">
                Required Minimum Fields:
            </div>
            <ul style="font-size: 0.82rem; color: #CBD5E1; padding-left: 1.2rem; margin: 0; line-height: 1.6;">
                <li><code>company_name</code></li>
                <li><code>industry</code> (SaaS, Fintech, etc.)</li>
                <li><code>monthly_revenue</code></li>
                <li><code>monthly_expenses</code></li>
                <li><code>headcount</code> (>= 1)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: MANUAL ENTRY FORM
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("""
    <div class="glass-card" style="margin-bottom: 1.5rem;">
        <h4 style="margin-top: 0; color: #FFFFFF; font-size: 1.15rem;">Direct Metrics Entry</h4>
        <p style="font-size: 0.88rem; color: #94A3B8; margin-bottom: 0;">
            Input your metrics directly. Unit economics, burn rate, and gross margins are automatically computed.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("manual_entry_form"):
        col_form1, col_form2 = st.columns(2, gap="large")

        with col_form1:
            st.markdown("##### 🏢 Company Profile & Team")
            company_name = st.text_input("Company Name", value="Veloce AI")
            industry = st.selectbox(
                "Industry Sector",
                ["SaaS", "Fintech", "HealthTech", "E-commerce", "EdTech", "CleanTech"]
            )
            c1, c2 = st.columns(2)
            with c1:
                founding_year = st.number_input("Founding Year", min_value=2010, max_value=2025, value=2022)
            with c2:
                funding_stage = st.selectbox("Funding Stage", ["Pre-seed", "Seed", "Series A", "Series B", "Series C+"], index=1)

            c3, c4 = st.columns(2)
            with c3:
                headcount = st.number_input("Team Headcount", min_value=1, max_value=1000, value=16)
            with c4:
                customer_count = st.number_input("Total Active Customers", min_value=1, max_value=500000, value=190)

        with col_form2:
            st.markdown("##### 💵 Financials & Growth")
            f1, f2 = st.columns(2)
            with f1:
                monthly_revenue = st.number_input("Monthly Revenue ($)", min_value=0.0, value=65000.0, step=5000.0)
            with f2:
                monthly_expenses = st.number_input("Monthly Expenses ($)", min_value=0.0, value=82000.0, step=5000.0)

            f3, f4 = st.columns(2)
            with f3:
                total_funding_usd = st.number_input("Total Funding Raised ($)", min_value=0.0, value=2200000.0, step=100000.0)
            with f4:
                funding_rounds_count = st.number_input("Funding Rounds", min_value=1, max_value=15, value=2)

            f5, f6 = st.columns(2)
            with f5:
                marketing_spend = st.number_input("Marketing Spend ($/mo)", min_value=0.0, value=18000.0, step=2000.0)
            with f6:
                new_customers_monthly = st.number_input("New Customers Added/mo", min_value=1, max_value=10000, value=22)

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("⚡ Save and Run Peer Benchmarking", use_container_width=True)

        if submitted:
            # Derived defaults for realistic balance sheet
            cogs_est = round(monthly_revenue * 0.22, 2)
            opex_est = round(max(0, monthly_expenses - cogs_est), 2)
            arpu_est = round(monthly_revenue / max(1, customer_count), 2)

            payload = {
                "company_name": company_name,
                "industry": industry,
                "founding_year": int(founding_year),
                "funding_stage": funding_stage,
                "headcount": int(headcount),
                "total_funding_usd": float(total_funding_usd),
                "funding_rounds_count": int(funding_rounds_count),
                "monthly_revenue": float(monthly_revenue),
                "monthly_expenses": float(monthly_expenses),
                "marketing_spend": float(marketing_spend),
                "customer_count": int(customer_count),
                "new_customers_monthly": int(new_customers_monthly),
                "cogs": cogs_est,
                "operating_expenses": opex_est,
                "avg_revenue_per_customer": arpu_est,
                "avg_customer_lifetime_months": 24.0,
                "mom_revenue_growth": 0.08,
            }

            with st.spinner("Submitting and analyzing metrics..."):
                try:
                    response = requests.post(f"{API_URL}/manual-entry", json=payload)
                    if response.status_code == 200:
                        startup_id = response.json()["startup_id"]
                        ana_res = requests.post(f"{API_URL}/analyze/{startup_id}?use_llm=true")
                        if ana_res.status_code == 200:
                            st.session_state["analysis_id"] = ana_res.json()["analysis_id"]
                            st.success("✅ Analysis successfully generated! Proceeding to Dashboard.")
                            st.page_link("pages/2_Analysis_Dashboard.py", label="View Analysis Dashboard ➔", icon="📊")
                        else:
                            st.error(f"Analysis failed: {ana_res.text}")
                    else:
                        st.error(f"Submission failed: {response.text}")
                except Exception as e:
                    st.error(f"Request failed: {e}")
