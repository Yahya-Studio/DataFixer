"""Custom SaaS styling and comprehensive RTL CSS injection for Streamlit."""

import streamlit as st


def apply_custom_css():
    """Inject premium SaaS stylesheet into Streamlit with full RTL support and Lucide icons."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    /* Global Direction & Typography */
    html, body, [class*="css"], .stApp, .stMain {
        font-family: 'Cairo', 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }

    /* Main Container Spacing */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1320px !important;
        direction: rtl !important;
        text-align: right !important;
    }

    /* =========================================================
       SIDEBAR & COLLAPSE FIXES (Prevents bleeding / overlapping)
       ========================================================= */
    section[data-testid="stSidebar"] {
        direction: rtl !important;
        text-align: right !important;
        overflow-x: hidden !important;
        overflow-y: auto !important;
        background-color: #0b1120 !important;
        border-left: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    /* When collapsed by Streamlit, ensure zero elements bleed through */
    section[data-testid="stSidebar"][aria-expanded="false"] {
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        overflow: hidden !important;
        visibility: hidden !important;
    }

    /* Sidebar Content Wrapper */
    div[data-testid="stSidebarContent"] {
        padding: 1.5rem 1rem !important;
        direction: rtl !important;
        text-align: right !important;
    }

    /* Sidebar Navigation Section Title */
    .sidebar-section-title {
        font-size: 0.78rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
        margin-right: 4px;
        direction: rtl;
        text-align: right;
    }

    /* Sidebar Buttons (Navigation Items) */
    [data-testid="stSidebar"] div.stButton {
        margin-bottom: 6px !important;
    }
    [data-testid="stSidebar"] div.stButton > button {
        display: flex !important;
        flex-direction: row-reverse !important;
        justify-content: flex-end !important;
        align-items: center !important;
        width: 100% !important;
        padding: 9px 14px !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        text-align: right !important;
        gap: 12px !important;
        transition: all 0.2s ease !important;
    }

    /* Inactive nav button */
    [data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
        background: transparent !important;
        border: 1px solid transparent !important;
        color: #94a3b8 !important;
    }
    [data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.05) !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
        color: #f8fafc !important;
        transform: translateX(-2px);
    }

    /* Active nav button */
    [data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
        border: 1px solid #6366f1 !important;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important;
        color: #ffffff !important;
    }

    /* =========================================================
       VECTOR SVG ICONS (LUCIDE) INJECTED INTO SIDEBAR BUTTONS
       ========================================================= */
    .st-key-nav_btn_dashboard button::before {
        content: "";
        width: 18px;
        height: 18px;
        background-repeat: no-repeat;
        background-position: center;
        background-size: contain;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23818cf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>');
    }
    .st-key-nav_btn_dashboard button[kind="primary"]::before {
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>');
    }

    .st-key-nav_btn_upload button::before {
        content: "";
        width: 18px;
        height: 18px;
        background-repeat: no-repeat;
        background-position: center;
        background-size: contain;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23818cf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M12 12v9"/><path d="m16 16-4-4-4 4"/></svg>');
    }
    .st-key-nav_btn_upload button[kind="primary"]::before {
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M12 12v9"/><path d="m16 16-4-4-4 4"/></svg>');
    }

    .st-key-nav_btn_analysis button::before {
        content: "";
        width: 18px;
        height: 18px;
        background-repeat: no-repeat;
        background-position: center;
        background-size: contain;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23818cf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>');
    }
    .st-key-nav_btn_analysis button[kind="primary"]::before {
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>');
    }

    .st-key-nav_btn_cleaning button::before {
        content: "";
        width: 18px;
        height: 18px;
        background-repeat: no-repeat;
        background-position: center;
        background-size: contain;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23818cf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg>');
    }
    .st-key-nav_btn_cleaning button[kind="primary"]::before {
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg>');
    }

    .st-key-nav_btn_history button::before {
        content: "";
        width: 18px;
        height: 18px;
        background-repeat: no-repeat;
        background-position: center;
        background-size: contain;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23818cf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/></svg>');
    }
    .st-key-nav_btn_history button[kind="primary"]::before {
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/></svg>');
    }

    .st-key-nav_btn_reports button::before {
        content: "";
        width: 18px;
        height: 18px;
        background-repeat: no-repeat;
        background-position: center;
        background-size: contain;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23818cf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>');
    }
    .st-key-nav_btn_reports button[kind="primary"]::before {
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>');
    }

    .st-key-nav_btn_settings button::before {
        content: "";
        width: 18px;
        height: 18px;
        background-repeat: no-repeat;
        background-position: center;
        background-size: contain;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23818cf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>');
    }
    .st-key-nav_btn_settings button[kind="primary"]::before {
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>');
    }

    /* Page Header with Vector Icon */
    .view-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 6px;
        direction: rtl;
        text-align: right;
    }
    .view-header h2 {
        font-size: 1.75rem;
        font-weight: 800;
        color: #f8fafc;
        margin: 0;
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
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
