import streamlit as st
import requests
import sys, os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from presentation_layer.components.styles import load_custom_css
from config import API_PORT, API_HOST

API_URL = f"http://{API_HOST}:{API_PORT}/api"

st.set_page_config(page_title="Recommendations - Startup Analyzer", page_icon="💡", layout="wide")
load_custom_css()

st.title("💡 AI Business Recommendations")

if "analysis_id" not in st.session_state:
    st.warning("No analysis found. Please go to 'Upload Data' first.")
    st.page_link("pages/1_Upload_Data.py", label="Go to Upload Data")
    st.stop()

analysis_id = st.session_state["analysis_id"]

with st.spinner("Fetching recommendations..."):
    response = requests.get(f"{API_URL}/report/{analysis_id}")
    
    if response.status_code != 200:
        st.error(f"Failed to fetch report: {response.text}")
        st.stop()
        
    report_data = response.json()

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown(f"Recommendations for **{report_data['company_name']}** based on peer comparisons.")

with col2:
    # PDF Download button
    pdf_res = requests.get(f"{API_URL}/export/{analysis_id}/pdf")
    if pdf_res.status_code == 200:
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_res.content,
            file_name=f"{report_data['company_name']}_Analysis_Report.pdf",
            mime="application/pdf",
        )
    else:
        st.error("PDF generation failed.")

st.markdown("---")

recommendations = report_data["recommendations"]

if not recommendations:
    st.info("No recommendations generated.")
else:
    for rec in recommendations:
        impact_class = f"impact-{rec['impact_level'].lower()}"
        card_class = f"rec-card-{rec['impact_level'].lower()}"
        
        st.markdown(f"""
        <div class="rec-card {card_class}">
            <div class="rec-title">{rec['rank']}. {rec['title']}</div>
            <div class="rec-tags">
                <span>🏷️ {rec['category']}</span>
                <span>⚡ Impact: <span class="{impact_class}">{rec['impact_level']}</span></span>
            </div>
            <p style="margin-top: 15px;">{rec['explanation']}</p>
        </div>
        """, unsafe_allow_html=True)
