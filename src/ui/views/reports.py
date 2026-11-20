"""Reports & Export View: File export (CSV, XLSX, JSON) and audit report download (HTML, PDF)."""

from pathlib import Path

import streamlit as st

from src.core.state import DatasetSession
from src.io.exporter import DatasetExporter
from src.reports.generator import build_report_data
from src.reports.html_report import generate_html_report
from src.reports.pdf_report import generate_pdf_report
from src.ui.charts import plot_quality_comparison
from src.ui.icons import get_svg_icon


def render_reports_view(session: DatasetSession):
    """Render the Reports generation and Dataset Export studio."""
    st.markdown(
        f"""
        <div class="view-header">
            {get_svg_icon("reports", size=26, color="#818cf8")}
            <h2>التقارير والتصدير | Reports & Export</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("صدّر بياناتك المنظفة بصيغ متعددة ونزّل تقارير تدقيق الجودة المهنية الشاملة.")

    if not session.has_data:
        st.warning("لا يوجد ملف بيانات نشط. يرجى رفع ملف أولاً.")
        return

    df = session.current_df
    diff = session.get_diff_summary()
    report_data = build_report_data(session)

    # 1. Quality Improvement Highlights
    c_chart, c_summary = st.columns([1, 1])
    with c_chart:
        fig_comp = plot_quality_comparison(diff.get("score_original", 0.0), diff.get("score_current", 0.0))
        st.plotly_chart(fig_comp, use_container_width=True)

    with c_summary:
        st.markdown("#### ملخص النتائج")
        st.write(f"- **الملف الأصلي:** `{session.filename}`")
        st.write(f"- **الجودة الابتدائية:** `{diff.get('score_original', 0.0):.1f} / 100`")
        st.write(
            f"- **الجودة النهائية:** `{diff.get('score_current', 0.0):.1f} / 100` (زيادة +`{diff.get('score_diff', 0.0):.1f}` نقطة)"
        )
        st.write(f"- **إجمالي العمليات المنفذة:** `{diff.get('actions_count', 0)}` عملية تنظيف.")
        st.write(f"- **الخلايا التي تم تصحيحها:** `{diff.get('total_cells_modified', 0):,}` خلية.")
        st.write(f"- **حجم الملف المنظف:** `{len(df):,}` صف و `{len(df.columns)}` عمود.")

    st.markdown("---")

    # 2. Dataset Export Section
    st.markdown("### تصدير ملف البيانات بعد التنظيف")
    base_name = Path(session.filename).stem or "cleaned_dataset"

    e1, e2, e3 = st.columns(3)
    with e1:
        st.markdown(
            """
            <div class="saas-card">
                <div class="card-title">صيغة CSV</div>
                <div class="card-value">CSV (.csv)</div>
                <div class="card-subtitle">ترميز UTF-8 مع دعم كامل للعربية في Excel.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        csv_bytes = DatasetExporter.to_csv(df)
        st.download_button(
            label="تنزيل ملف CSV",
            data=csv_bytes,
            file_name=f"{base_name}_cleaned.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary",
        )

    with e2:
        st.markdown(
            """
            <div class="saas-card">
                <div class="card-title">صيغة Excel</div>
                <div class="card-value">Excel (.xlsx)</div>
                <div class="card-subtitle">مصنف Microsoft Excel قياسي جاهز للتحليل.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        excel_bytes = DatasetExporter.to_excel(df)
        st.download_button(
            label="تنزيل ملف Excel",
            data=excel_bytes,
            file_name=f"{base_name}_cleaned.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    with e3:
        st.markdown(
            """
            <div class="saas-card">
                <div class="card-title">صيغة JSON</div>
                <div class="card-value">JSON (.json)</div>
                <div class="card-subtitle">تنسيق قياسي مناسب للمطورين وقواعد البيانات.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        json_bytes = DatasetExporter.to_json(df)
        st.download_button(
            label="تنزيل ملف JSON",
            data=json_bytes,
            file_name=f"{base_name}_cleaned.json",
            mime="application/json",
            use_container_width=True,
        )

    st.markdown("---")

    # 3. Comprehensive Audit Report Download (HTML & PDF)
    st.markdown("### تقرير الجودة والتدقيق الشامل (Audit Report)")
    st.write(
        "يتضمن التقرير الشامل تفاصيل حجم البيانات، والمشكلات المكتشفة، وقائمة العمليات المنفذة، ودرجة الجودة النهائية."
    )

    rep1, rep2 = st.columns(2)

    with rep1:
        st.markdown(
            """
            <div class="saas-card">
                <div class="card-title">تقرير ويب تفاعلي</div>
                <div class="card-value">تقرير HTML</div>
                <div class="card-subtitle">صفحة ويب مستقلة وأنيقة جاهزة للعرض أو الطباعة المباشرة.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        html_content = generate_html_report(report_data)
        st.download_button(
            label="تنزيل التقرير (HTML)",
            data=html_content.encode("utf-8"),
            file_name=f"DataFixer_Report_{base_name}.html",
            mime="text/html",
            use_container_width=True,
            type="primary",
        )

    with rep2:
        st.markdown(
            """
            <div class="saas-card">
                <div class="card-title">وثيقة إدارية جاهزة</div>
                <div class="card-value">تقرير PDF</div>
                <div class="card-subtitle">ملف PDF منظم ومضغوط مناسب للتقارير الرسمية والاجتماعات.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        try:
            pdf_bytes = generate_pdf_report(report_data)
            st.download_button(
                label="تنزيل التقرير (PDF)",
                data=pdf_bytes,
                file_name=f"DataFixer_Report_{base_name}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"تعذر تجهيز ملف PDF: {e!s}")

    # In-App HTML Report Live Preview
    with st.expander("استعراض مباشر لتقرير HTML داخل التطبيق"):
        st.components.v1.html(html_content, height=650, scrolling=True)
