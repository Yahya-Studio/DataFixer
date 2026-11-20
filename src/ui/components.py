"""Reusable Streamlit UI visual components with pagination and RTL support."""

import math
from typing import Any

import pandas as pd
import streamlit as st

from src.core.schemas import QualityIssue, QualityScoreBreakdown
from src.ui.icons import get_svg_icon


def render_metric_card(title: str, value: Any, subtitle: str = "", delta: str | None = None, icon_name: str = ""):
    """Render a modern SaaS metric card with optional SVG icon."""
    delta_html = f"<span style='color: #10b981; font-size: 0.8rem; margin-left: 6px;'>{delta}</span>" if delta else ""
    icon_svg = get_svg_icon(icon_name, size=16, color="#818cf8") if icon_name else ""
    st.markdown(
        f"""
        <div class="saas-card">
            <div class="card-title">{icon_svg} <span>{title}</span></div>
            <div class="card-value">{value}</div>
            <div class="card-subtitle">{delta_html}{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_quality_score_card(score: QualityScoreBreakdown, title: str = "مؤشر جودة البيانات"):
    """Render an interpretable breakdown of the Data Quality Score."""
    score_val = score.overall_score
    color = "#10b981" if score_val >= 85 else ("#f59e0b" if score_val >= 65 else "#ef4444")
    badge_label = (
        "ممتاز" if score_val >= 85 else ("مقبول / يحتاج تنظيف" if score_val >= 65 else "حرج / يحتوي أخطاء كثيرة")
    )

    check_icon = get_svg_icon("check", size=22, color=color)

    st.markdown(
        f"""
        <div class="score-banner">
            <div class="score-text">
                <h2>{title}: <span style="color: {color};">{score_val:.1f} / 100</span></h2>
                <p>الحالة العامة: <strong>{badge_label}</strong> &bull; محسوب وفق 4 معايير موضوعية قابلة للتفسير الكامل.</p>
            </div>
            <div style="background: rgba(255, 255, 255, 0.05); padding: 12px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1);">
                {check_icon}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card(
            "الاكتمال (Completeness)",
            f"{score.completeness:.1f}%",
            f"خصم: -{score.completeness_penalty:.1f}",
            icon_name="table",
        )
    with c2:
        render_metric_card(
            "الفرادة (Uniqueness)",
            f"{score.uniqueness:.1f}%",
            f"خصم: -{score.uniqueness_penalty:.1f}",
            icon_name="check",
        )
    with c3:
        render_metric_card(
            "الصحة (Validity)",
            f"{score.validity:.1f}%",
            f"خصم: -{score.validity_penalty:.1f}",
            icon_name="alert",
        )
    with c4:
        render_metric_card(
            "الاتساق (Consistency)",
            f"{score.consistency:.1f}%",
            f"خصم: -{score.consistency_penalty:.1f}",
            icon_name="settings",
        )


def render_issues_table(issues: list[QualityIssue]):
    """Render table of detected issues with severity tags and recommendations."""
    if not issues:
        st.success("🎉 لم يتم العثور على أي مشاكل ملحوظة في البيانات. الملف بحالة ممتازة!")
        return

    st.markdown(f"#### 🔍 المشكلات المكتشفة ({len(issues)})")

    for issue in issues:
        badge_cls = (
            "badge-danger"
            if issue.severity == "high"
            else ("badge-warning" if issue.severity == "medium" else "badge-info")
        )
        col_tag = f"العمود: `{issue.affected_column}`" if issue.affected_column else "كامل الجدول"

        with st.expander(f"⚠️ {issue.title} — {col_tag} ({issue.affected_count:,} حالة)"):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.write(issue.description)
                st.info(f"💡 **الإجراء المقترح:** {issue.recommendation}")
            with c2:
                st.markdown(
                    f"<span class='badge-pill {badge_cls}'>{issue.severity.upper()}</span>", unsafe_allow_html=True
                )
                st.metric("نسبة التأثر", f"{issue.affected_ratio * 100:.1f}%")
                st.metric("العدد المتأثر", f"{issue.affected_count:,}")


def render_paginated_table(df: pd.DataFrame, key: str = "table", default_page_size: int = 50):
    """Render full DataFrame with interactive pagination or all-rows display."""
    total_rows = len(df)
    if total_rows == 0:
        st.info("الجدول لا يحتوي على أي صفوف لعرضها.")
        return

    # Pagination controls
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 2, 3])

    with ctrl_col1:
        size_choice = st.selectbox(
            "عدد الصفوف في الصفحة:",
            [25, 50, 100, 250, "عرض جميع الصفوف (All Rows)"],
            index=1,
            key=f"{key}_page_size",
        )

    if size_choice == "عرض جميع الصفوف (All Rows)":
        st.caption(f"يتم الآن عرض جميع صفوف البيانات بالكامل ({total_rows:,} صف):")
        st.dataframe(df, use_container_width=True)
        return

    page_size = int(size_choice)
    total_pages = max(1, math.ceil(total_rows / page_size))

    # Current page state
    page_state_key = f"{key}_curr_page"
    if page_state_key not in st.session_state:
        st.session_state[page_state_key] = 1

    # Ensure page is within range
    st.session_state[page_state_key] = min(st.session_state[page_state_key], total_pages)
    st.session_state[page_state_key] = max(st.session_state[page_state_key], 1)

    curr_page = st.session_state[page_state_key]

    with ctrl_col2:
        new_page = st.number_input(
            f"الصفحة (من {total_pages}):",
            min_value=1,
            max_value=total_pages,
            value=curr_page,
            step=1,
            key=f"{key}_num_input",
        )
        if new_page != curr_page:
            st.session_state[page_state_key] = new_page
            curr_page = new_page

    start_idx = (curr_page - 1) * page_size
    end_idx = min(start_idx + page_size, total_rows)

    with ctrl_col3:
        st.markdown(
            f"""
            <div style="padding-top: 28px; font-size: 0.88rem; color: #94a3b8;">
                عرض الصفوف <strong>{start_idx + 1:,}</strong> إلى <strong>{end_idx:,}</strong> (من إجمالي <strong>{total_rows:,}</strong> صف)
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Slice DataFrame and display
    sliced_df = df.iloc[start_idx:end_idx]
    st.dataframe(sliced_df, use_container_width=True)

    # Page Navigation Buttons (Previous / Next)
    if total_pages > 1:
        b1, _, b3 = st.columns([1, 4, 1])
        with b1:
            if st.button(
                "⬅️ الصفحة التالية", disabled=(curr_page >= total_pages), key=f"{key}_btn_next", use_container_width=True
            ):
                st.session_state[page_state_key] = curr_page + 1
                st.rerun()
        with b3:
            if st.button(
                "الصفحة السابقة ➡️", disabled=(curr_page <= 1), key=f"{key}_btn_prev", use_container_width=True
            ):
                st.session_state[page_state_key] = curr_page - 1
                st.rerun()


def render_diff_view(df_original: pd.DataFrame, df_current: pd.DataFrame):
    """Render comparative before-and-after view with pagination."""
    t1, t2 = st.tabs(["البيانات بعد المعالجة (Current)", "البيانات الأصلية (Original)"])
    with t1:
        render_paginated_table(df_current, key="diff_current_table")
    with t2:
        render_paginated_table(df_original, key="diff_orig_table")
