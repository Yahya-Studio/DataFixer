"""Settings View: Application configuration, quality weights tuning, and session control."""

import platform

import pandas as pd
import polars as pl
import streamlit as st

from config.settings import config
from src.core.state import DatasetSession


def render_settings_view(session: DatasetSession):
    """Render the application configuration and settings panel."""
    st.markdown("## ⚙️ الإعدادات وخيارات المعالجة | Settings")
    st.caption("تخصيص أوزان تقييم الجودة، وحدود كشف القيم الشاذة، وإدارة الجلسة الحالية.")

    s_tab1, s_tab2, s_tab3 = st.tabs(["🎯 أوزان مؤشر الجودة", "📐 معايير القيم الشاذة", "ℹ️ معلومات النظام"])

    with s_tab1:
        st.markdown("### تخصيص أوزان حساب مؤشر الجودة (Quality Score Weights)")
        st.write("مجموع الأوزان يعادل 100%. يمكنك تخصيص الأولويات وفق متطلبات عملك أو مشروعك:")

        w_comp = st.slider(
            "وزن الاكتمال (Completeness - القيم الفارغة)",
            min_value=0,
            max_value=60,
            value=int(config.weight_completeness),
            step=5,
        )
        w_uniq = st.slider(
            "وزن الفرادة (Uniqueness - التكرارات)",
            min_value=0,
            max_value=60,
            value=int(config.weight_uniqueness),
            step=5,
        )
        w_val = st.slider(
            "وزن الصحة (Validity - الأنواع والتواريخ)",
            min_value=0,
            max_value=60,
            value=int(config.weight_validity),
            step=5,
        )
        w_cons = st.slider(
            "وزن الاتساق (Consistency - النصوص والتنسيق)",
            min_value=0,
            max_value=60,
            value=int(config.weight_consistency),
            step=5,
        )

        total_w = w_comp + w_uniq + w_val + w_cons
        if total_w != 100:
            st.warning(f"مجموع الأوزان الحالي هو {total_w}%. يفضل أن يكون الإجمالي 100% لتجنب انحراف النسب.")

        if st.button("حفظ الأوزان الجديدة وإعادة تقييم الملف الحالي", type="primary"):
            config.weight_completeness = float(w_comp)
            config.weight_uniqueness = float(w_uniq)
            config.weight_validity = float(w_val)
            config.weight_consistency = float(w_cons)
            session.reanalyze_current()
            st.success("تم تحديث أوزان التقييم وإعادة فحص الملف بنجاح!")
            st.rerun()

    with s_tab2:
        st.markdown("### معايير كشف القيم الشاذة (Anomaly & Outlier Parameters)")
        iqr_mult = st.slider(
            "معامل المدى الربيعي (IQR Multiplier):",
            min_value=1.0,
            max_value=3.5,
            value=float(config.outlier_iqr_multiplier),
            step=0.1,
            help="القيمة الافتراضية 1.5. القيم الأكبر تعتبر فقط الحالات الشديدة شاذة.",
        )
        z_thresh = st.slider(
            "عتبة الانحراف المعياري (Z-Score Threshold):",
            min_value=2.0,
            max_value=5.0,
            value=float(config.outlier_zscore_threshold),
            step=0.5,
        )

        if st.button("حفظ معايير الشذوذ"):
            config.outlier_iqr_multiplier = iqr_mult
            config.outlier_zscore_threshold = z_thresh
            session.reanalyze_current()
            st.success("تم حفظ المعايير بنجاح.")

    with s_tab3:
        st.markdown("### معلومات بيئة التشغيل")
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"- **إصدار التطبيق:** DataFixer v{config.version}")
            st.write(f"- **لغة Python:** {platform.python_version()}")
            st.write(f"- **مكتبة Pandas:** {pd.__version__}")
            st.write(f"- **مكتبة Polars:** {pl.__version__}")
        with c2:
            st.write(f"- **مكتبة Streamlit:** {st.__version__}")
            st.write(f"- **الحد الأقصى للملفات:** {config.max_file_size_mb} MB")
            st.write(f"- **حد التاريخ المحفوظ (Undo Steps):** {config.max_history_steps} خطوات")

        st.markdown("---")
        st.markdown("### إدارة الجلسة الحالية")
        if st.button("🗑️ مسح الجلسة والبدء من جديد", type="secondary"):
            st.session_state.clear()
            st.success("تم مسح الجلسة.")
            st.rerun()
