import streamlit as st
import sys, os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from presentation_layer.components.styles import load_custom_css

st.set_page_config(
    page_title="Startup Analyzer AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_custom_css()

st.title("🚀 AI-Driven Startup Analysis & Recommendation")
st.markdown("""
Welcome to the **Startup Analyzer AI**.

This tool ingests a target startup's operational and financial data, benchmarks it against patterns learned from a dataset of successful startups (matched by industry/stage/size peer group), and produces a prioritised, explainable set of business recommendations.

### Get Started:
1. Go to **Upload Data** in the sidebar to provide your startup metrics.
2. View your benchmark scores in the **Analysis Dashboard**.
3. Read your data-grounded AI advice in **Recommendations**.
""")

st.info("👈 Please select a page from the sidebar to continue.")
