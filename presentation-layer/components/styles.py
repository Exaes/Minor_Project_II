import streamlit as st

def load_custom_css():
    st.markdown("""
    <style>
    /* Dark theme overrides */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    .st-emotion-cache-1y4p8pa {
        padding-top: 2rem;
    }
    
    /* Metrics Cards */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
        color: #00FF00;
    }
    
    /* Recommendations Cards */
    .rec-card {
        background-color: #1E2329;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 5px solid #3B82F6;
    }
    
    .rec-card-high { border-left-color: #EF4444; }
    .rec-card-medium { border-left-color: #F59E0B; }
    .rec-card-low { border-left-color: #10B981; }
    
    .rec-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .rec-tags span {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-right: 10px;
        background-color: #374151;
    }
    
    .impact-high { color: #EF4444; font-weight: bold; }
    .impact-medium { color: #F59E0B; font-weight: bold; }
    .impact-low { color: #10B981; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)
