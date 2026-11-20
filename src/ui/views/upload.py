"""Upload Dataset View: Ingestion, sheet selection, encoding detection, and full pagination preview."""

from pathlib import Path

import streamlit as st

from config.settings import config
from src.core.state import DatasetSession
from src.io.loader import DataLoaderError, DatasetLoader
from src.ui.components import render_paginated_table
from src.utils.formatting import format_bytes, format_number
from src.utils.security import SecurityValidationError


def render_upload_view(session: DatasetSession):
    """Render the Upload & Dataset Ingestion interface."""
    st.markdown("## 📁 رفع وإدارة ملفات البيانات | Upload Dataset")
    st.caption("ارفع ملف البيانات لاكتشاف المشكلات وتحليل جودته وتنظيفه.")

    uploaded_file = st.file_uploader(
        "اختر ملف البيانات أو قم بسحبه هنا",
        type=config.allowed_extensions,
        help=f"الصيغ المدعومة: {', '.join(config.allowed_extensions).upper()} (الحد الأقصى: {config.max_file_size_mb}MB)",
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        filename = uploaded_file.name
        ext = Path(filename).suffix.lstrip(".").lower()

        selected_sheet = None
        if ext in ("xlsx", "xls"):
            try:
                sheets = DatasetLoader.inspect_excel_sheets(file_bytes)
                if len(sheets) > 1:
                    selected_sheet = st.selectbox(
                        "📑 تم اكتشاف أوراق عمل متعددة. اختر ورقة العمل:",
                        sheets,
                        index=0,
                    )
                else:
                    selected_sheet = sheets[0] if sheets else None
            except Exception as e:
                st.warning(f"ملاحظة عند فحص أوراق العمل: {e!s}")

        # Advanced CSV parameters
        override_encoding = None
        override_delimiter = None
        if ext == "csv":
            with st.expander("⚙️ خيارات متقدمة لقراءة ملف CSV (اختياري)"):
                c_enc, c_delim = st.columns(2)
                with c_enc:
                    enc_opt = st.selectbox(
                        "ترميز الملف (Encoding):",
                        ["تلقائي (Auto-Detect)", "utf-8", "utf-8-sig", "windows-1256 (Arabic)", "iso-8859-1"],
                    )
                    if enc_opt != "تلقائي (Auto-Detect)":
                        override_encoding = enc_opt.split()[0]
                with c_delim:
                    delim_opt = st.selectbox(
                        "الفاصل (Delimiter):",
                        [
                            "تلقائي (Auto-Detect)",
                            "فاصلة ( , )",
                            "فاصلة منقوطة ( ; )",
                            "علامة جدولة ( Tab )",
                            "شريط عمودي ( | )",
                        ],
                    )
                    delim_map = {
                        "فاصلة ( , )": ",",
                        "فاصلة منقوطة ( ; )": ";",
                        "علامة جدولة ( Tab )": "\t",
                        "شريط عمودي ( | )": "|",
                    }
                    if delim_opt in delim_map:
                        override_delimiter = delim_map[delim_opt]

        if st.button("📥 قراءة وتحليل الملف", type="primary", use_container_width=True):
            with st.spinner("جاري قراءة الملف وتحليل بنيته بدقة..."):
                try:
                    df, meta = DatasetLoader.load_from_bytes(
                        file_bytes=file_bytes,
                        filename=filename,
                        sheet_name=selected_sheet,
                        encoding=override_encoding,
                        delimiter=override_delimiter,
                    )
                    session.set_dataset(df, meta)
                    st.success(f"تم تحميل الملف '{meta['filename']}' بنجاح!")
                    st.session_state["sidebar_nav"] = "Data Analysis"
                    st.session_state["active_page"] = "Data Analysis"
                    st.rerun()
                except (SecurityValidationError, DataLoaderError) as e:
                    st.error(f"خطأ في الملف: {e!s}")
                except Exception as e:
                    st.error(f"حدث خطأ غير متوقع: {e!s}")

    # Active dataset preview with full pagination (No 15-row limit)
    if session.has_data:
        st.markdown("---")
        st.markdown("### 👁️ استعراض بيانات الملف النشط")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("اسم الملف", session.filename)
        m2.metric("الحجم", format_bytes(session.file_size_bytes))
        m3.metric("عدد الصفوف", format_number(len(session.current_df)))
        m4.metric("عدد الأعمدة", format_number(len(session.current_df.columns)))

        st.caption("يمكنك استعراض جميع الصفوف أو التنقل عبر الصفحات المحددة أدناه:")
        render_paginated_table(session.current_df, key="upload_preview_table", default_page_size=50)
