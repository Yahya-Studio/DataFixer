"""Data Analysis View: Quality score, issues list, and Plotly visualizations."""

import pandas as pd
import streamlit as st

from src.analysis.profiler import DatasetProfiler
from src.core.state import DatasetSession
from src.ui.charts import (
    plot_dtypes_donut,
    plot_duplicates_donut,
    plot_missing_values_bar,
    plot_numeric_distribution,
    plot_top_categorical_values,
)
from src.ui.components import render_issues_table, render_quality_score_card
from src.ui.icons import get_svg_icon


def set_active_page(page_name: str):
    """Callback to switch active page cleanly."""
    st.session_state["active_page"] = page_name


def render_analysis_view(session: DatasetSession):
    """Render the Data Quality Analysis & Profiling dashboard."""
    st.markdown(
        f"""
        <div class="view-header">
            {get_svg_icon("analysis", size=26, color="#818cf8")}
            <h2>تحليل جودة البيانات | Data Analysis</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("فحص آلي معمّق لاكتشاف المشكلات الهيكلية والدلالية مع مؤشر جودة دقيق وقابل للتفسير.")

    if not session.has_data:
        st.warning("لا يوجد ملف بيانات نشط. يرجى رفع ملف أولاً من صفحة رفع البيانات.")
        st.button(
            "الانتقال لرفع ملف",
            type="primary",
            on_click=set_active_page,
            args=("Upload Dataset",),
        )
        return

    df = session.current_df
    score = session.current_score
    issues = session.current_issues

    # 1. Quality Score Breakdown
    if score:
        render_quality_score_card(score)

    st.markdown("---")

    # 2. Issues Breakdown Section
    render_issues_table(issues)

    st.markdown("---")
    st.markdown("### 📊 لوحة الرسوم البيانية التفاعلية")

    # Visualizations Row 1: Missing values & Duplicates
    c_chart1, c_chart2 = st.columns([3, 2])
    with c_chart1:
        missing_fig = plot_missing_values_bar(df)
        if missing_fig:
            st.plotly_chart(missing_fig, use_container_width=True)
        else:
            st.success("✨ ممتاز! لا توجد أي قيم مفقودة في أي من الأعمدة.")
    with c_chart2:
        dup_count = int(df.duplicated().sum())
        dup_fig = plot_duplicates_donut(len(df), dup_count)
        st.plotly_chart(dup_fig, use_container_width=True)

    # Visualizations Row 2: Data Types & Column Explorer
    st.markdown("---")
    c_types, c_col_exp = st.columns([2, 3])

    with c_types:
        st.plotly_chart(plot_dtypes_donut(df), use_container_width=True)

    with c_col_exp:
        st.markdown("#### 🔎 مستكشف الأعمدة التفصيلي")
        selected_col = st.selectbox("اختر عموداً لتحليل توزيعاته وإحصاءاته:", list(df.columns))
        if selected_col:
            summary = DatasetProfiler.get_column_summary(df[selected_col])

            # Key mini metrics
            e1, e2, e3 = st.columns(3)
            e1.metric("النوع", summary.get("dtype"))
            e2.metric("القيم الفارغة", f"{summary.get('null_count')} ({summary.get('null_percentage', 0):.1f}%)")
            e3.metric("القيم الفريدة", f"{summary.get('unique_count')} ({summary.get('unique_percentage', 0):.1f}%)")

            # Chart based on type
            if pd.api.types.is_numeric_dtype(df[selected_col]):
                st.plotly_chart(plot_numeric_distribution(df, selected_col), use_container_width=True)
            else:
                st.plotly_chart(plot_top_categorical_values(df, selected_col), use_container_width=True)

    # Section for fast jump to cleaning
    st.markdown("---")
    b_col1, b_col2 = st.columns([3, 1])
    with b_col1:
        st.write("هل ترغب في البدء في تصحيح وتنظيف المشكلات المكتشفة؟")
    with b_col2:
        st.button(
            "الانتقال لأدوات التنظيف (Cleaning)",
            type="primary",
            use_container_width=True,
            on_click=set_active_page,
            args=("Data Cleaning",),
        )
