import streamlit as st
import requests
import sys, os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from presentation_layer.components.styles import load_custom_css
from config import API_PORT, API_HOST

API_URL = f"http://{API_HOST}:{API_PORT}/api"

st.set_page_config(page_title="Upload Data - Startup Analyzer", page_icon="📁", layout="wide")
load_custom_css()

st.title("📁 Upload Startup Data")

tab1, tab2 = st.tabs(["Upload CSV/Excel", "Manual Entry"])

with tab1:
    st.markdown("Upload a CSV or Excel file containing your startup metrics.")
    
    with open(os.path.join(os.path.dirname(__file__), "..", "..", "data-layer", "templates", "upload_template.csv"), "r") as f:
        template_csv = f.read()
    
    st.download_button(
        label="📥 Download Template",
        data=template_csv,
        file_name="startup_template.csv",
        mime="text/csv",
    )
    
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        if st.button("Upload and Analyze"):
            with st.spinner("Uploading and analyzing data..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                response = requests.post(f"{API_URL}/upload", files=files)
                
                if response.status_code == 200:
                    startup_id = response.json()["startup_id"]
                    
                    # Trigger analysis
                    analysis_res = requests.post(f"{API_URL}/analyze/{startup_id}?use_llm=true")
                    if analysis_res.status_code == 200:
                        analysis_id = analysis_res.json()["analysis_id"]
                        st.session_state["analysis_id"] = analysis_id
                        st.success(f"Analysis complete! Proceed to the Dashboard.")
                        
                        # Optionally redirect or provide button
                        st.page_link("pages/2_Analysis_Dashboard.py", label="Go to Dashboard", icon="📊")
                    else:
                        st.error(f"Analysis failed: {analysis_res.text}")
                else:
                    st.error(f"Upload failed: {response.text}")

with tab2:
    st.markdown("Manually enter your startup metrics.")
    
    with st.form("manual_entry_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name", "My Startup")
            industry = st.selectbox("Industry", ["SaaS", "Fintech", "HealthTech", "E-commerce", "EdTech", "CleanTech", "Other"])
            founding_year = st.number_input("Founding Year", min_value=2000, max_value=2024, value=2021)
            funding_stage = st.selectbox("Funding Stage", ["Pre-seed", "Seed", "Series A", "Series B", "Series C+"])
            headcount = st.number_input("Headcount", min_value=1, value=10)
            customer_count = st.number_input("Total Customers", min_value=0, value=100)
            
        with col2:
            monthly_revenue = st.number_input("Monthly Revenue (USD)", min_value=0.0, value=50000.0)
            monthly_expenses = st.number_input("Monthly Expenses (USD)", min_value=0.0, value=60000.0)
            total_funding_usd = st.number_input("Total Funding Raised (USD)", min_value=0.0, value=1000000.0)
            funding_rounds_count = st.number_input("Funding Rounds", min_value=0, value=1)
            marketing_spend = st.number_input("Monthly Marketing Spend (USD)", min_value=0.0, value=10000.0)
            new_customers_monthly = st.number_input("New Customers Monthly", min_value=0, value=10)
            
        submitted = st.form_submit_button("Submit and Analyze")
        
        if submitted:
            payload = {
                "company_name": company_name,
                "industry": industry,
                "founding_year": founding_year,
                "funding_stage": funding_stage,
                "headcount": headcount,
                "total_funding_usd": total_funding_usd,
                "funding_rounds_count": funding_rounds_count,
                "monthly_revenue": monthly_revenue,
                "monthly_expenses": monthly_expenses,
                "marketing_spend": marketing_spend,
                "customer_count": customer_count,
                "new_customers_monthly": new_customers_monthly,
                # default missing values for manual entry
                "cogs": monthly_revenue * 0.2, # guess 80% gross margin
                "operating_expenses": monthly_expenses - (monthly_revenue * 0.2),
                "avg_revenue_per_customer": monthly_revenue / max(1, customer_count),
                "avg_customer_lifetime_months": 24,
                "mom_revenue_growth": 0.05
            }
            
            with st.spinner("Submitting and analyzing data..."):
                response = requests.post(f"{API_URL}/manual-entry", json=payload)
                
                if response.status_code == 200:
                    startup_id = response.json()["startup_id"]
                    analysis_res = requests.post(f"{API_URL}/analyze/{startup_id}?use_llm=true")
                    
                    if analysis_res.status_code == 200:
                        analysis_id = analysis_res.json()["analysis_id"]
                        st.session_state["analysis_id"] = analysis_id
                        st.success("Analysis complete! Proceed to the Dashboard.")
                        st.page_link("pages/2_Analysis_Dashboard.py", label="Go to Dashboard", icon="📊")
                    else:
                        st.error(f"Analysis failed: {analysis_res.text}")
                else:
                    st.error(f"Submission failed: {response.text}")
