import streamlit as st
import requests
import sys, os
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from presentation_layer.components.styles import load_custom_css
from presentation_layer.components.charts import create_efficiency_gauge, create_radar_chart
from config import API_PORT, API_HOST

API_URL = f"http://{API_HOST}:{API_PORT}/api"

st.set_page_config(page_title="Analysis Dashboard - Startup Analyzer", page_icon="📊", layout="wide")
load_custom_css()

st.title("📊 Analysis Dashboard")

if "analysis_id" not in st.session_state:
    st.warning("No analysis found. Please go to 'Upload Data' first.")
    st.page_link("pages/1_Upload_Data.py", label="Go to Upload Data")
    st.stop()

analysis_id = st.session_state["analysis_id"]

with st.spinner("Fetching analysis results..."):
    response = requests.get(f"{API_URL}/report/{analysis_id}")
    
    if response.status_code != 200:
        st.error(f"Failed to fetch report: {response.text}")
        st.stop()
        
    report_data = response.json()

st.markdown(f"### {report_data['company_name']} | Peer Group: {report_data['peer_group_label']}")
st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    st.plotly_chart(create_efficiency_gauge(report_data['efficiency_score']), use_container_width=True)

with col2:
    # Key metrics for radar chart
    radar_metrics = ['gross_margin', 'opex_to_revenue', 'runway_months', 'ltv_cac_ratio', 'mom_revenue_growth']
    st.plotly_chart(
        create_radar_chart(report_data['computed_metrics'], report_data['peer_benchmarks'], radar_metrics),
        use_container_width=True
    )

st.markdown("### 📋 Metric Deviations vs Peers")
deviations = report_data["deviations"]

if not deviations:
    st.info("No significant deviations found.")
else:
    # Build dataframe for display
    dev_data = []
    for d in deviations:
        dev_data.append({
            "Metric": d["label"],
            "Your Value": f"{d['your_value']:.2f}",
            "Peer Avg": f"{d['benchmark_mean']:.2f}",
            "Z-Score": f"{d['z_score']:+.2f}",
            "Status": "🔴 Critical" if d["severity"] == "critical" else "⚠️ Warning" if d["severity"] == "warning" else "✅ OK"
        })
    
    df_dev = pd.DataFrame(dev_data)
    st.dataframe(df_dev, use_container_width=True, hide_index=True)

st.markdown("---")
st.page_link("pages/3_Recommendations.py", label="View AI Recommendations", icon="💡")
