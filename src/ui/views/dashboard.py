"""Dashboard View: Overview metrics and direct upload workflow."""

import streamlit as st

from src.core.state import DatasetSession
from src.ui.components import render_metric_card, render_quality_score_card
from src.ui.icons import get_svg_icon
from src.utils.formatting import format_bytes, format_number


def render_dashboard_view(session: DatasetSession):
    """Render the SaaS Dashboard overview."""
    st.markdown("## 📊 لوحة التحكم | Dashboard")
    st.caption("نظرة عامة سريعة على حالة ملف البيانات وجودته والعمليات المنجزة.")

    if not session.has_data:
        # Empty state with single clean call-to-action
        st.info(
            "👋 مرحباً بك في **DataFixer**! لم يتم رفع أي ملف بيانات حتى الآن. ابدأ برفع ملف البيانات لفحص جودته وتنظيفه."
        )

        st.markdown(
            f"""
            <div class="saas-card" style="padding: 35px 25px; text-align: center;">
                <div style="margin-bottom: 12px;">{get_svg_icon("upload", size=42, color="#6366f1")}</div>
                <div class="card-value" style="font-size: 1.6rem; margin-bottom: 8px;">ابدأ العمل مع DataFixer</div>
                <div class="card-subtitle" style="font-size: 0.95rem; max-width: 600px; margin: 0 auto 20px auto;">
                    ارفع ملفات CSV, Excel (XLSX, XLS), أو JSON لاكتشاف المشكلات الهيكلية والدلالية تلقائياً وتنظيفها بسهولة.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        _, b_c2, _ = st.columns([1, 2, 1])
        with b_c2:
            if st.button("🚀 رفع ملف بيانات جديد (Upload Dataset)", use_container_width=True, type="primary"):
                st.session_state["sidebar_nav"] = "Upload Dataset"
                st.session_state["active_page"] = "Upload Dataset"
                st.rerun()
        return

    # Active dataset state
    diff = session.get_diff_summary()
    curr_score = session.current_score
    actions = session.history.get_actions()

    # Top KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_metric_card(
            "الملف النشط",
            session.filename[:18] + ("..." if len(session.filename) > 18 else ""),
            f"الصيغة: {session.file_type.upper()} ({format_bytes(session.file_size_bytes)})",
            icon_name="reports",
        )
    with k2:
        render_metric_card(
            "مؤشر الجودة الكلي",
            f"{curr_score.overall_score:.1f}%" if curr_score else "0%",
            f"التحسن: +{diff.get('score_diff', 0):.1f}%",
            icon_name="check",
        )
    with k3:
        render_metric_card(
            "حجم البيانات الحالي",
            f"{format_number(diff.get('rows_current', 0))} صف",
            f"الأعمدة: {diff.get('cols_current', 0)} عمود",
            icon_name="table",
        )
    with k4:
        render_metric_card(
            "عمليات التنظيف",
            f"{len(actions)} عملية",
            f"خلايا معدلة: {format_number(diff.get('total_cells_modified', 0))}",
            icon_name="cleaning",
        )

    # Score Banner
    if curr_score:
        st.markdown("---")
        render_quality_score_card(curr_score)

    # Overview split: Recent operations & Quick actions
    st.markdown("---")
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("📋 ملخص التغييرات والمقارنة")
        st.write(
            f"- **الصفوف:** من `{diff.get('rows_original', 0):,}` إلى `{diff.get('rows_current', 0):,}` "
            f"({diff.get('rows_diff', 0):+d} صف)"
        )
        st.write(
            f"- **الأعمدة:** من `{diff.get('cols_original', 0)}` إلى `{diff.get('cols_current', 0)}` "
            f"({diff.get('cols_diff', 0):+d} عمود)"
        )
        st.write(
            f"- **إجمالي الخلايا التي تم تصحيحها أو تعديلها:** `{format_number(diff.get('total_cells_modified', 0))}` خلية."
        )
        st.write(f"- **المشاكل المتبقية بحاجة لمعالجة:** `{len(session.current_issues)}` مشكلة.")

    with col_right:
        st.subheader("⚡ إجراءات سريعة")
        if st.button("🔬 فحص تفاصيل جودة البيانات", use_container_width=True):
            st.session_state["sidebar_nav"] = "Data Analysis"
            st.session_state["active_page"] = "Data Analysis"
            st.rerun()

        if st.button("🧹 البدء في تنظيف البيانات", use_container_width=True, type="primary"):
            st.session_state["sidebar_nav"] = "Data Cleaning"
            st.session_state["active_page"] = "Data Cleaning"
            st.rerun()

        if st.button("📥 تصدير البيانات والتقرير", use_container_width=True):
            st.session_state["sidebar_nav"] = "Reports & Export"
            st.session_state["active_page"] = "Reports & Export"
            st.rerun()
