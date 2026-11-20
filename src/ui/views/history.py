"""Cleaning History View: Operation audit logs, Undo/Redo stack, and diff viewer."""

import streamlit as st

from src.core.state import DatasetSession
from src.ui.components import render_diff_view
from src.ui.icons import get_svg_icon
from src.utils.formatting import format_number


def render_history_view(session: DatasetSession):
    """Render the audit trail and version management interface."""
    st.markdown(
        f"""
        <div class="view-header">
            {get_svg_icon("history", size=26, color="#818cf8")}
            <h2>سجل العمليات والتراجع | Cleaning History</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("تتبع مسار كل عملية تنظيف نُفذت، مع إمكانية التراجع خطوة بخطوة أو إعادة تطبيق العمليات.")

    if not session.has_data:
        st.warning("لا يوجد ملف بيانات نشط. يرجى رفع ملف أولاً.")
        return

    actions = session.history.get_actions()
    can_undo = session.history.can_undo()
    can_redo = session.history.can_redo()
    diff = session.get_diff_summary()

    # Toolbar: Undo, Redo, Reset to Original
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        if st.button("تراجع (Undo)", disabled=not can_undo, use_container_width=True, type="secondary"):
            rev = session.undo()
            if rev:
                st.success(f"تم التراجع عن: {rev.name}")
                st.rerun()

    with c2:
        if st.button("إعادة (Redo)", disabled=not can_redo, use_container_width=True, type="secondary"):
            redone = session.redo()
            if redone:
                st.success(f"تمت إعادة تطبيق: {redone.name}")
                st.rerun()

    with c3:
        if st.button("استعادة الملف الأصلي بالكامل", type="secondary", use_container_width=True):
            st.session_state["confirm_reset"] = True

    if st.session_state.get("confirm_reset", False):
        st.warning("هل أنت متأكد من رغبتك في إلغاء كافة العمليات والرجوع إلى الملف الأصلي؟")
        co1, co2 = st.columns(2)
        with co1:
            if st.button("نعم، استعد الملف الأصلي", type="primary", use_container_width=True):
                session.reset_to_original()
                st.session_state["confirm_reset"] = False
                st.success("تمت استعادة الملف الأصلي ومسح سجل التغييرات.")
                st.rerun()
        with co2:
            if st.button("إلغاء", use_container_width=True):
                st.session_state["confirm_reset"] = False
                st.rerun()

    st.markdown("---")

    # Cumulative Statistics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("إجمالي العمليات", len(actions))
    m2.metric("الخلايا المعدلة", format_number(diff.get("total_cells_modified", 0)))
    m3.metric("صافي تغير الصفوف", f"{diff.get('rows_diff', 0):+d}")
    m4.metric("تغير مؤشر الجودة", f"{diff.get('score_diff', 0):+0.1f} نقطة")

    # Audit Trail Table
    st.markdown("### جدول الإجراءات المسجلة (Audit Trail)")
    if not actions:
        st.info("لم يتم تسجيل أي عمليات تنظيف حتى الآن. ابدأ بتنظيف البيانات من صفحة تنظيف البيانات.")
    else:
        log_rows = []
        for i, a in enumerate(actions, 1):
            t_str = a.timestamp.strftime("%H:%M:%S") if hasattr(a.timestamp, "strftime") else str(a.timestamp)[:8]
            log_rows.append(
                {
                    "#": i,
                    "الوقت": t_str,
                    "اسم العملية": a.name,
                    "الأعمدة": ", ".join(a.target_columns) if a.target_columns else "كل الجدول",
                    "الصفوف (قبل -> بعد)": f"{a.rows_before} -> {a.rows_after}",
                    "خلايا معدلة": a.cells_modified,
                    "مؤشر الجودة": f"{a.score_before:.1f} -> {a.score_after:.1f}",
                }
            )
        st.dataframe(log_rows, use_container_width=True)

    # Before vs After Comparator
    st.markdown("---")
    st.markdown("### مقارنة البيانات قبل وبعد المعالجة")
    render_diff_view(session.original_df, session.current_df)
