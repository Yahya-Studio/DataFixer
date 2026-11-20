"""Custom SaaS styling and comprehensive RTL CSS injection for Streamlit."""

import streamlit as st


def apply_custom_css():
    """Inject premium SaaS stylesheet into Streamlit with full RTL support."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    /* Global Direction & Typography */
    html, body, [class*="css"], .stApp, .stMain, [data-testid="stSidebar"], [data-testid="stVerticalBlock"] {
        font-family: 'Cairo', 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }

    /* Container Spacing */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1320px !important;
        direction: rtl !important;
        text-align: right !important;
    }

    /* Sidebar RTL adjustments */
    [data-testid="stSidebar"] {
        direction: rtl !important;
        text-align: right !important;
    }
    [data-testid="stSidebar"] * {
        text-align: right !important;
    }
    
    /* Radio group RTL alignment */
    div[role="radiogroup"] {
        direction: rtl !important;
        text-align: right !important;
        gap: 6px !important;
    }
    div[role="radiogroup"] label {
        direction: rtl !important;
        text-align: right !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        gap: 10px !important;
        padding: 6px 10px !important;
        border-radius: 8px !important;
        transition: background 0.15s ease !important;
    }
    div[role="radiogroup"] label:hover {
        background: rgba(255, 255, 255, 0.05) !important;
    }
    div[role="radiogroup"] label > div:first-child {
        margin: 0 0 0 8px !important;
    }

    /* SaaS Metric Card */
    .saas-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.7) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px 22px;
        backdrop-filter: blur(8px);
        margin-bottom: 16px;
        direction: rtl !important;
        text-align: right !important;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .saas-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        transform: translateY(-2px);
    }
    .saas-card .card-title {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .saas-card .card-value {
        color: #f8fafc;
        font-size: 1.85rem;
        font-weight: 800;
        line-height: 1.2;
    }
    .saas-card .card-subtitle {
        color: #64748b;
        font-size: 0.82rem;
        margin-top: 6px;
    }

    /* Quality Score Banner */
    .score-banner {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 60%, #4338ca 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 24px 30px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        direction: rtl !important;
        text-align: right !important;
    }
    .score-banner .score-text h2 {
        color: #ffffff;
        font-size: 1.6rem;
        font-weight: 800;
        margin: 0;
    }
    .score-banner .score-text p {
        color: #c7d2fe;
        font-size: 0.95rem;
        margin-top: 4px;
    }

    /* Badges */
    .badge-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .badge-danger {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .badge-warning {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .badge-success {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .badge-info {
        background: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }

    /* Tabs RTL */
    button[data-baseweb="tab"] {
        direction: rtl !important;
        font-weight: 600 !important;
    }

    /* Expanders RTL */
    [data-testid="stExpander"] summary {
        direction: rtl !important;
        text-align: right !important;
    }

    /* Tables & DataFrames */
    .dataframe {
        border-radius: 10px !important;
        overflow: hidden !important;
        direction: rtl !important;
        text-align: right !important;
    }

    /* Pagination Bar */
    .pagination-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 14px;
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        margin: 10px 0 16px 0;
        direction: rtl !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
