"""Dashboard View: Overview metrics, SaaS onboarding, and direct upload workflow."""

import streamlit as st

from src.core.state import DatasetSession
from src.ui.components import render_metric_card, render_quality_score_card
from src.ui.icons import get_svg_icon
from src.utils.formatting import format_bytes, format_number


def set_active_page(page_name: str):
    """Callback to switch active page cleanly."""
    st.session_state["active_page"] = page_name


def render_dashboard_view(session: DatasetSession):
    """Render the SaaS Dashboard overview."""
    st.markdown(
        f"""
        <div class="view-header">
            {get_svg_icon("dashboard", size=26, color="#818cf8")}
            <h2>لوحة التحكم | Dashboard</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("نظرة عامة على حالة ملف البيانات، وجودته، والمشكلات المعالجة.")

    if not session.has_data:
        # Informative onboarding card
        st.markdown(
            f"""
            <div class="saas-card" style="padding: 32px 24px; margin-top: 15px;">
                <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 15px;">
                    <div style="background: rgba(99, 102, 241, 0.15); padding: 12px; border-radius: 12px; border: 1px solid rgba(99, 102, 241, 0.3);">
                        {get_svg_icon("upload", size=32, color="#818cf8")}
                    </div>
                    <div>
                        <h3 style="margin: 0; color: #f8fafc; font-size: 1.35rem; font-weight: 700;">مرحباً بك في منصة DataFixer</h3>
                        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.9rem;">المنصة الذكية المتكاملة لتحليل جودة البيانات واكتشاف العيوب ومعالجتها آلياً.</p>
                    </div>
                </div>
                <div style="color: #cbd5e1; font-size: 0.92rem; line-height: 1.8; margin-bottom: 20px;">
                    تبدأ دورة عمل DataFixer برفع ملف بياناتك (يدعم <strong>CSV</strong>، <strong>Excel XLSX/XLS</strong>، و <strong>JSON</strong>). يقوم النظام بفحص شامل لاكتشاف المشكلات الهيكلية والدلالية، واحتساب مؤشر الجودة، وتمكينك من تنظيف البيانات مع إمكانية التراجع الكامل (Undo / Redo)، وتصدير النتائج والتقارير الرسمية.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-bottom: 25px;">
                <div class="saas-card" style="padding: 16px;">
                    <div style="font-weight: 700; color: #818cf8; margin-bottom: 4px;">1. رفع البيانات</div>
                    <div style="font-size: 0.84rem; color: #94a3b8;">دعم الترميزات العربية، الفواصل المتعددة، وتحديد أوراق العمل.</div>
                </div>
                <div class="saas-card" style="padding: 16px;">
                    <div style="font-weight: 700; color: #818cf8; margin-bottom: 4px;">2. الفحص الذكي</div>
                    <div style="font-size: 0.84rem; color: #94a3b8;">اكتشاف 11 عيباً هيكلياً واحتساب مؤشر الجودة الشفاف (0 - 100).</div>
                </div>
                <div class="saas-card" style="padding: 16px;">
                    <div style="font-weight: 700; color: #818cf8; margin-bottom: 4px;">3. استوديو التنظيف</div>
                    <div style="font-size: 0.84rem; color: #94a3b8;">معالجة الفراغات، التكرارات، النصوص، التواريخ، والشواذ.</div>
                </div>
                <div class="saas-card" style="padding: 16px;">
                    <div style="font-weight: 700; color: #818cf8; margin-bottom: 4px;">4. التقارير والتصدير</div>
                    <div style="font-size: 0.84rem; color: #94a3b8;">تصدير CSV, Excel, JSON وتوليد تقارير تدقيق HTML و PDF.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        _, b_c2, _ = st.columns([1, 2, 1])
        with b_c2:
            st.button(
                "الانتقال إلى صفحة رفع البيانات (Upload Dataset)",
                type="primary",
                use_container_width=True,
                on_click=set_active_page,
                args=("Upload Dataset",),
            )
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
        st.subheader("ملخص التغييرات والمقارنة")
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
        st.subheader("إجراءات سريعة")
        st.button(
            "فحص تفاصيل جودة البيانات",
            use_container_width=True,
            on_click=set_active_page,
            args=("Data Analysis",),
        )
        st.button(
            "البدء في تنظيف البيانات",
            type="primary",
            use_container_width=True,
            on_click=set_active_page,
            args=("Data Cleaning",),
        )
        st.button(
            "تصدير البيانات والتقرير",
            use_container_width=True,
            on_click=set_active_page,
            args=("Reports & Export",),
        )
