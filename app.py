"""DataFixer - Smart Data Cleaning & Quality Assurance SaaS Application.

Main entry point for Streamlit application.
"""

import sys
from pathlib import Path

import streamlit as st

# Ensure project root is in python path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config.settings import config
from src.core.state import DatasetSession
from src.ui.styles import apply_custom_css
from src.ui.views import (
    render_analysis_view,
    render_cleaning_view,
    render_dashboard_view,
    render_history_view,
    render_reports_view,
    render_settings_view,
    render_upload_view,
)
from src.utils.formatting import format_number


def init_session() -> DatasetSession:
    """Initialize or retrieve persistent DatasetSession in Streamlit session_state."""
    if "dataset_session" not in st.session_state:
        st.session_state["dataset_session"] = DatasetSession()
    if "active_page" not in st.session_state:
        st.session_state["active_page"] = "Dashboard"
    return st.session_state["dataset_session"]


def main():
    # Streamlit Page Configuration
    st.set_page_config(
        page_title="DataFixer | Smart Data Cleaning Platform",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inject SaaS Custom CSS
    apply_custom_css()

    session = init_session()

    # Sidebar Navigation & Branding
    with st.sidebar:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 24px; padding: 4px 8px;">
                <div style="background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%); color: white; font-weight: 800; font-size: 20px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 12px; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);">
                    DF
                </div>
                <div>
                    <h2 style="margin: 0; font-size: 20px; font-weight: 800; color: #f8fafc; line-height: 1.1;">DataFixer</h2>
                    <span style="font-size: 11px; color: #818cf8; text-transform: uppercase; letter-spacing: 0.5px;">Data Quality SaaS</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        nav_options = [
            "Dashboard",
            "Upload Dataset",
            "Data Analysis",
            "Data Cleaning",
            "Cleaning History",
            "Reports & Export",
            "Settings",
        ]

        # Sync active_page with sidebar selection
        if "sidebar_nav" not in st.session_state:
            st.session_state["sidebar_nav"] = "Dashboard"

        if st.session_state.get("active_page") and st.session_state["active_page"] in nav_options:
            st.session_state["sidebar_nav"] = st.session_state["active_page"]

        selected_page = st.radio(
            "التنقل في المنصة:",
            nav_options,
            format_func=lambda x: {
                "Dashboard": "📊 لوحة التحكم (Dashboard)",
                "Upload Dataset": "📁 رفع البيانات (Upload)",
                "Data Analysis": "🔬 تحليل الجودة (Analysis)",
                "Data Cleaning": "🧹 تنظيف البيانات (Cleaning)",
                "Cleaning History": "📜 سجل العمليات (History)",
                "Reports & Export": "📥 التصدير والتقارير (Export)",
                "Settings": "⚙️ الإعدادات (Settings)",
            }.get(x, x),
            key="sidebar_nav",
        )
        st.session_state["active_page"] = selected_page

        st.markdown("---")

        # Sidebar Live Status Card
        if session.has_data:
            score = session.current_score.overall_score if session.current_score else 0.0
            color = "#10b981" if score >= 85 else ("#f59e0b" if score >= 65 else "#ef4444")
            st.markdown(
                f"""
                <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 14px; margin-top: 10px;">
                    <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">الملف النشط</div>
                    <div style="font-size: 14px; font-weight: 700; color: #f8fafc; margin: 4px 0; word-break: break-all;">
                        📄 {session.filename}
                    </div>
                    <div style="font-size: 12px; color: #cbd5e1;">
                        {format_number(len(session.current_df))} صف &bull; {len(session.current_df.columns)} عمود
                    </div>
                    <div style="margin-top: 8px; display: flex; align-items: center; justify-content: space-between;">
                        <span style="font-size: 12px; color: #94a3b8;">درجة الجودة:</span>
                        <span style="font-size: 14px; font-weight: 800; color: {color};">{score:.1f}%</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Quick undo shortcut in sidebar
            if session.history.can_undo():
                if st.button("↩️ تراجع سريع", key="sidebar_quick_undo", use_container_width=True):
                    rev = session.undo()
                    if rev:
                        st.toast(f"تم التراجع عن: {rev.name}")
                        st.rerun()
        else:
            st.caption("لم يتم تحميل أي ملف بيانات بعد.")

        st.markdown(
            f"""
            <div style="position: fixed; bottom: 15px; left: 15px; font-size: 11px; color: #64748b;">
                DataFixer v{config.version} &bull; Python 3.14
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Route to selected page
    page = st.session_state["active_page"]
    if page == "Dashboard":
        render_dashboard_view(session)
    elif page == "Upload Dataset":
        render_upload_view(session)
    elif page == "Data Analysis":
        render_analysis_view(session)
    elif page == "Data Cleaning":
        render_cleaning_view(session)
    elif page == "Cleaning History":
        render_history_view(session)
    elif page == "Reports & Export":
        render_reports_view(session)
    elif page == "Settings":
        render_settings_view(session)


if __name__ == "__main__":
    main()
