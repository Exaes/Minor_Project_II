"""
Custom CSS and Design System for Startup Analyzer AI.
Provides modern dark mode aesthetics, Google Fonts, glassmorphism,
gradient accents, and responsive card layouts.
"""

import streamlit as st


def load_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    :root {
        --font-heading: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
        --font-body: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        
        --bg-main: #0B0F17;
        --bg-surface: #131B2A;
        --bg-card: rgba(22, 30, 46, 0.75);
        --bg-glass: rgba(255, 255, 255, 0.03);
        
        --border-subtle: rgba(255, 255, 255, 0.08);
        --border-accent: rgba(99, 102, 241, 0.35);
        
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --text-muted: #64748B;
        
        --primary-gradient: linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #EC4899 100%);
        --cyan-gradient: linear-gradient(135deg, #06B6D4 0%, #3B82F6 100%);
        --emerald-gradient: linear-gradient(135deg, #10B981 0%, #059669 100%);
        --rose-gradient: linear-gradient(135deg, #F43F5E 0%, #E11D48 100%);
        --amber-gradient: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
    }

    /* Global Typography & Background */
    html, body, [class*="st-"] {
        font-family: var(--font-body);
        color: var(--text-primary);
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: var(--font-heading) !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }

    .stApp {
        background-color: var(--bg-main);
        background-image: 
            radial-gradient(at 10% 10%, rgba(99, 102, 241, 0.08) 0px, transparent 50%),
            radial-gradient(at 90% 80%, rgba(236, 72, 153, 0.05) 0px, transparent 50%);
        background-attachment: fixed;
    }

    /* Hide standard Streamlit header clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid var(--border-accent);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(16px);
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5), 0 0 30px -15px rgba(99, 102, 241, 0.3);
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.35rem 0.85rem;
        border-radius: 9999px;
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.4);
        color: #A5B4FC;
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .hero-title {
        font-family: var(--font-heading);
        font-size: 2.75rem;
        font-weight: 800;
        line-height: 1.15;
        margin-bottom: 0.75rem;
        background: linear-gradient(135deg, #FFFFFF 30%, #CBD5E1 70%, #94A3B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-gradient-text {
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        color: var(--text-secondary);
        max-width: 650px;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }

    /* Glass Cards */
    .glass-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 1.5rem;
        backdrop-filter: blur(12px);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.3);
        margin-bottom: 1.25rem;
    }

    .glass-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 8px 25px -4px rgba(99, 102, 241, 0.15);
    }

    /* KPI Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1.25rem;
        margin-bottom: 2rem;
    }

    .kpi-card {
        background: linear-gradient(135deg, rgba(26, 35, 54, 0.8) 0%, rgba(18, 25, 38, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.25rem 1.4rem;
        position: relative;
        overflow: hidden;
        transition: all 0.25s ease;
    }

    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--primary-gradient);
        opacity: 0.8;
    }

    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }

    .kpi-label {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-secondary);
        margin-bottom: 0.35rem;
    }

    .kpi-value {
        font-family: var(--font-heading);
        font-size: 2.1rem;
        font-weight: 700;
        color: #FFFFFF;
        line-height: 1.1;
        margin-bottom: 0.35rem;
    }

    .kpi-caption {
        font-size: 0.82rem;
        color: var(--text-muted);
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }

    /* Step Navigation / Flow Bar */
    .step-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(19, 27, 42, 0.7);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 0.9rem 1.5rem;
        margin-bottom: 2rem;
    }

    .step-item {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--text-secondary);
    }

    .step-item.active {
        color: #A5B4FC;
    }

    .step-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.1);
        color: var(--text-secondary);
        font-size: 0.75rem;
    }

    .step-item.active .step-number {
        background: var(--primary-gradient);
        color: #FFFFFF;
    }

    /* Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }

    .badge-critical {
        background: rgba(239, 68, 68, 0.15);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    .badge-warning {
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }

    .badge-favorable {
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .badge-neutral {
        background: rgba(148, 163, 184, 0.15);
        color: #CBD5E1;
        border: 1px solid rgba(148, 163, 184, 0.3);
    }

    /* Recommendations Cards */
    .rec-card {
        background: linear-gradient(135deg, rgba(24, 32, 49, 0.85) 0%, rgba(18, 24, 38, 0.95) 100%);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 1.5rem 1.6rem;
        margin-bottom: 1.25rem;
        position: relative;
        transition: all 0.2s ease;
        backdrop-filter: blur(12px);
    }

    .rec-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px -4px rgba(0, 0, 0, 0.4);
    }

    .rec-card-high {
        border-left: 5px solid #EF4444;
    }

    .rec-card-medium {
        border-left: 5px solid #F59E0B;
    }

    .rec-card-low {
        border-left: 5px solid #10B981;
    }

    .rec-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 0.85rem;
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    .rec-title {
        font-family: var(--font-heading);
        font-size: 1.25rem;
        font-weight: 700;
        color: #F8FAFC;
    }

    .rec-meta {
        display: flex;
        gap: 0.6rem;
        align-items: center;
        flex-wrap: wrap;
        margin-bottom: 0.9rem;
    }

    .rec-body {
        font-size: 0.95rem;
        line-height: 1.65;
        color: #CBD5E1;
    }

    /* Buttons Overrides */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
        color: #FFFFFF;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.4rem;
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.01em;
        transition: all 0.2s ease;
        box-shadow: 0 4px 14px -2px rgba(99, 102, 241, 0.4);
    }

    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%);
        transform: translateY(-1px);
        box-shadow: 0 6px 20px -2px rgba(99, 102, 241, 0.6);
        color: #FFFFFF;
    }

    div.stDownloadButton > button:first-child {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #F8FAFC;
        border-radius: 10px;
        padding: 0.6rem 1.4rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    div.stDownloadButton > button:first-child:hover {
        border-color: #6366F1;
        color: #A5B4FC;
        background: rgba(99, 102, 241, 0.15);
    }

    /* Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        border-bottom: 1px solid var(--border-subtle);
        padding-bottom: 0.25rem;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
        color: var(--text-secondary);
        border: none;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(99, 102, 241, 0.15) !important;
        color: #A5B4FC !important;
        border-bottom: 2px solid #6366F1 !important;
    }

    /* Form Container Polish */
    div[data-testid="stForm"] {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 1.75rem;
        backdrop-filter: blur(12px);
    }

    /* Streamlit Dataframe Style */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--border-subtle);
    }
    </style>
    """, unsafe_allow_html=True)
