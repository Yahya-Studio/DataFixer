"""Data Cleaning View: Comprehensive modular cleaning tools with audit tracking."""

import streamlit as st

from src.cleaning.columns import (
    cast_column_dtype,
    drop_columns,
    drop_empty_columns,
    rename_columns,
    standardize_column_names,
)
from src.cleaning.dates import standardize_dates
from src.cleaning.duplicates import remove_duplicates
from src.cleaning.missing import drop_missing_values, fill_missing_values
from src.cleaning.outliers import handle_outliers
from src.cleaning.text import (
    change_case,
    find_and_replace,
    strip_and_normalize_whitespace,
)
from src.core.state import DatasetSession
from src.ui.components import render_paginated_table


def render_cleaning_view(session: DatasetSession):
    """Render the Data Cleaning studio interface."""
    st.markdown("## 🧹 أدوات تنظيف ومعالجة البيانات | Data Cleaning")
    st.caption("نفّذ عمليات التنظيف والتصحيح بدقة مع تسجيل فوري في سجل العمليات وإمكانية التراجع الكامل.")

    if not session.has_data:
        st.warning("⚠️ لا يوجد ملف بيانات نشط. يرجى رفع ملف أولاً من صفحة **Upload Dataset**.")
        return

    df = session.current_df

    # Quick Header Controls: Current Score, Rows, Columns, and Undo
    h1, h2, h3, h4 = st.columns([2, 2, 2, 2])
    with h1:
        st.metric("الصفوف الحالية", f"{len(df):,}")
    with h2:
        st.metric("الأعمدة الحالية", f"{len(df.columns)}")
    with h3:
        score_val = session.current_score.overall_score if session.current_score else 0.0
        st.metric("مؤشر الجودة", f"{score_val:.1f} / 100")
    with h4:
        undo_available = session.history.can_undo()
        if st.button("↩️ تراجع (Undo)", disabled=not undo_available, use_container_width=True):
            reverted = session.undo()
            if reverted:
                st.success(f"تم التراجع عن: {reverted.name}")
                st.rerun()

    st.markdown("---")

    # Cleaning Tabs
    tab_missing, tab_dup, tab_text, tab_cols, tab_nums_dates = st.tabs(
        [
            "1️⃣ القيم المفقودة (Missing)",
            "2️⃣ التكرارات (Duplicates)",
            "3️⃣ تنظيف النصوص (Text)",
            "4️⃣ الأعمدة والأنواع (Columns)",
            "5️⃣ التواريخ والأرقام (Dates & Numbers)",
        ]
    )

    # ---------------- 1. MISSING VALUES ----------------
    with tab_missing:
        st.subheader("معالجة القيم المفقودة والفارغة")
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("##### 🗑️ حذف الصفوف التي تحتوي على قيم مفقودة")
            how_choice = st.radio(
                "شرط الحذف:",
                ["حذف الصف إذا احتوى على أي قيمة فارغة (Any)", "حذف الصف فقط إذا كانت كل قيمه فارغة (All)"],
                key="drop_null_how",
            )
            how_param = "any" if "Any" in how_choice else "all"

            subset_cols = st.multiselect(
                "تطبيق الحذف بالاعتماد على أعمدة محددة (اختياري):", list(df.columns), key="drop_null_subset"
            )

            # Preview count
            chk_cols = subset_cols if subset_cols else list(df.columns)
            potential_drop = (
                df[chk_cols].isna().any(axis=1).sum() if how_param == "any" else df[chk_cols].isna().all(axis=1).sum()
            )
            st.caption(f"عدد الصفوف التي ستتأثر بالحذف: **{potential_drop:,}** صف.")

            if st.button("تأكيد وحذف الصفوف الفارغة", type="primary", key="btn_drop_null"):
                if potential_drop > 0:
                    new_df, rows_removed, cells_mod = drop_missing_values(df, how=how_param, subset=subset_cols or None)
                    session.apply_cleaning_step(
                        new_df=new_df,
                        action_name="حذف صفوف فارغة",
                        operator="drop_missing_values",
                        target_columns=subset_cols or list(df.columns),
                        parameters={"how": how_param},
                        cells_modified=cells_mod,
                        description=f"تم حذف {rows_removed} صف يحتوي على قيم مفقودة.",
                    )
                    st.success(f"تم بنجاح حذف {rows_removed} صف.")
                    st.rerun()
                else:
                    st.info("لا توجد صفوف فارغة مطابقة للشرط.")

        with c2:
            st.markdown("##### ✏️ تعويض واستبدال القيم المفقودة (Imputation)")
            fill_cols = st.multiselect(
                "اختر الأعمدة المراد تعويض قيمها الفارغة:", list(df.columns), key="fill_null_cols"
            )
            strategy = st.selectbox(
                "استراتيجية التعويض:",
                [
                    "قيمة مخصصة (Custom Value)",
                    "المتوسط الحسابي (Mean - للأرقام)",
                    "الوسيط الحسابي (Median - للأرقام)",
                    "القيمة الأكثر تكراراً (Mode / Most Frequent)",
                    "التمرير الأمامي (Forward Fill)",
                    "التمرير الخلفي (Backward Fill)",
                ],
                key="fill_strat",
            )

            custom_val = ""
            if "Custom" in strategy:
                custom_val = st.text_input("أدخل القيمة البديلة:", value="غير محدد", key="fill_custom_val")

            if st.button("تطبيق التعويض", key="btn_apply_fill"):
                if not fill_cols:
                    st.warning("يرجى اختيار عمود واحد على الأقل.")
                else:
                    strat_map = {
                        "قيمة مخصصة (Custom Value)": "custom",
                        "المتوسط الحسابي (Mean - للأرقام)": "mean",
                        "الوسيط الحسابي (Median - للأرقام)": "median",
                        "القيمة الأكثر تكراراً (Mode / Most Frequent)": "mode",
                        "التمرير الأمامي (Forward Fill)": "ffill",
                        "التمرير الخلفي (Backward Fill)": "bfill",
                    }
                    s_code = strat_map[strategy]
                    new_df, cells_mod = fill_missing_values(
                        df, columns=fill_cols, strategy=s_code, fill_value=custom_val
                    )
                    session.apply_cleaning_step(
                        new_df=new_df,
                        action_name=f"تعويض قيم مفقودة ({strategy})",
                        operator="fill_missing_values",
                        target_columns=fill_cols,
                        parameters={"strategy": s_code, "custom_val": custom_val},
                        cells_modified=cells_mod,
                        description=f"تم تعويض {cells_mod} خلية مفقودة عبر استراتيجية {strategy}.",
                    )
                    st.success(f"تم تعويض {cells_mod} قيمة فارغة بنجاح.")
                    st.rerun()

    # ---------------- 2. DUPLICATES ----------------
    with tab_dup:
        st.subheader("معالجة الصفوف المكررة (Deduplication)")
        d_cols = st.multiselect(
            "تحديد أعمدة فحص التكرار (اترك فارغاً لفحص كامل الصف):", list(df.columns), key="dup_cols_select"
        )
        keep_choice = st.selectbox(
            "طريقة التعامل مع النسخ المكررة:",
            [
                "الاحتفاظ بالنسخة الأولى فقط وحذف الباقي (Keep First)",
                "الاحتفاظ بالنسخة الأخيرة وحذف الباقي (Keep Last)",
                "حذف كافة النسخ المكررة تماماً (Drop All)",
            ],
            key="dup_keep_choice",
        )
        keep_param = "first" if "First" in keep_choice else ("last" if "Last" in keep_choice else False)

        subset_to_check = d_cols if d_cols else list(df.columns)
        curr_dups = df.duplicated(subset=subset_to_check, keep=keep_param).sum()
        st.info(f"تم اكتشاف **{curr_dups:,}** صف مكرر وفق الإعدادات الحالية.")

        if st.button("حذف الصفوف المكررة", type="primary", key="btn_drop_dup", disabled=curr_dups == 0):
            new_df, rows_removed = remove_duplicates(df, subset=d_cols or None, keep=keep_param)
            session.apply_cleaning_step(
                new_df=new_df,
                action_name="حذف تكرارات",
                operator="remove_duplicates",
                target_columns=d_cols or list(df.columns),
                parameters={"keep": str(keep_param)},
                cells_modified=rows_removed * len(df.columns),
                description=f"تم إزالة {rows_removed} صف مكرر.",
            )
            st.success(f"تم إزالة {rows_removed} صف مكرر بنجاح.")
            st.rerun()

    # ---------------- 3. TEXT CLEANING ----------------
    with tab_text:
        st.subheader("تنظيف النصوص وتوحيد الصيغ")
        str_cols = list(df.select_dtypes(include=["object", "string"]).columns)

        t_col1, t_col2 = st.columns(2)
        with t_col1:
            st.markdown("##### ✂️ إزالة المسافات الزائدة (Trim & Normalize)")
            trim_cols = st.multiselect("الأعمدة النصية المستهدفة:", str_cols, default=str_cols, key="trim_cols")
            normalize_inner = st.checkbox(
                "توحيد المسافات المتعددة الداخلية إلى مسافة واحدة", value=True, key="norm_inner"
            )

            if st.button("تنفيذ إزالة المسافات", key="btn_trim") and trim_cols:
                new_df, cells_mod = strip_and_normalize_whitespace(df, trim_cols, remove_inner_extra=normalize_inner)
                session.apply_cleaning_step(
                    new_df=new_df,
                    action_name="إزالة مسافات زائدة",
                    operator="strip_and_normalize_whitespace",
                    target_columns=trim_cols,
                    parameters={"normalize_inner": normalize_inner},
                    cells_modified=cells_mod,
                    description=f"تم تنظيف المسافات الزائدة في {cells_mod} نص.",
                )
                st.success(f"تم تنظيف {cells_mod} خلية.")
                st.rerun()

            st.markdown("##### 🔠 توحيد حالة الأحرف (Case Normalization)")
            case_cols = st.multiselect("أعمدة تغيير حالة الأحرف:", str_cols, key="case_cols")
            case_type = st.selectbox(
                "الحالة المرغوبة:",
                ["lowercase (أحرف صغيرة)", "UPPERCASE (أحرف كبيرة)", "Title Case (أول حرف كبير)"],
                key="case_type_select",
            )
            case_code = "lower" if "lowercase" in case_type else ("upper" if "UPPERCASE" in case_type else "title")

            if st.button("توحيد حالة الأحرف", key="btn_case") and case_cols:
                new_df, cells_mod = change_case(df, case_cols, case_type=case_code)
                session.apply_cleaning_step(
                    new_df=new_df,
                    action_name=f"توحيد الأحرف ({case_code})",
                    operator="change_case",
                    target_columns=case_cols,
                    parameters={"case_type": case_code},
                    cells_modified=cells_mod,
                    description=f"تم تعديل حالة الأحرف في {cells_mod} نص.",
                )
                st.success(f"تم تعديل {cells_mod} قيمة.")
                st.rerun()

        with t_col2:
            st.markdown("##### 🔍 البحث والاستبدال (Find & Replace)")
            rep_cols = st.multiselect("الأعمدة المستهدفة للاستبدال:", list(df.columns), key="rep_cols")
            find_str = st.text_input("النص المراد البحث عنه:", key="find_str_val")
            replace_str = st.text_input("النص البديل:", key="replace_str_val")
            c_chk1, c_chk2 = st.columns(2)
            with c_chk1:
                use_regex = st.checkbox("استخدام تعبير نمطي (Regex)", key="rep_use_regex")
            with c_chk2:
                case_sens = st.checkbox("مطابقة حالة الأحرف (Case Sensitive)", value=True, key="rep_case_sens")

            if st.button("تنفيذ البحث والاستبدال", key="btn_find_rep"):
                if rep_cols and find_str:
                    new_df, cells_mod = find_and_replace(
                        df, rep_cols, find_str, replace_str, is_regex=use_regex, case_sensitive=case_sens
                    )
                    session.apply_cleaning_step(
                        new_df=new_df,
                        action_name="بحث واستبدال",
                        operator="find_and_replace",
                        target_columns=rep_cols,
                        parameters={"find": find_str, "replace": replace_str, "regex": use_regex},
                        cells_modified=cells_mod,
                        description=f"تم استبدال النمط في {cells_mod} خلية.",
                    )
                    st.success(f"تم استبدال {cells_mod} قيمة بنجاح.")
                    st.rerun()

    # ---------------- 4. COLUMNS OPERATIONS ----------------
    with tab_cols:
        st.subheader("إدارة الأعمدة وهيكلية البيانات")

        c_op1, c_op2 = st.columns(2)
        with c_op1:
            st.markdown("##### 🏷️ توحيد وتسمية الأعمدة")
            norm_style = st.selectbox(
                "نمط التسمية القياسي:",
                ["snake_case (مثال: full_name)", "lowercase (أحرف صغيرة)", "UPPERCASE (أحرف كبيرة)", "camelCase"],
                key="col_norm_style",
            )
            style_code = norm_style.split()[0]
            if st.button("توحيد كافة أسماء الأعمدة", key="btn_norm_headers"):
                new_df, cols_mod = standardize_column_names(df, style=style_code)
                session.apply_cleaning_step(
                    new_df=new_df,
                    action_name=f"توحيد أسماء الأعمدة ({style_code})",
                    operator="standardize_column_names",
                    parameters={"style": style_code},
                    cells_modified=cols_mod,
                    description=f"تم تعديل أسماء {cols_mod} أعمدة لتطابق نمط {style_code}.",
                )
                st.success(f"تم توحيد أسماء {cols_mod} أعمدة.")
                st.rerun()

            st.markdown("##### ✏️ إعادة تسمية عمود يدوي")
            target_ren_col = st.selectbox("اختر العمود المراد تعديل اسمه:", list(df.columns), key="sel_ren_col")
            new_ren_name = st.text_input("الاسم الجديد:", value=target_ren_col, key="new_ren_name_val")
            if st.button("تحديث اسم العمود", key="btn_ren_single"):
                if new_ren_name and new_ren_name != target_ren_col:
                    new_df, _ = rename_columns(df, {target_ren_col: new_ren_name})
                    session.apply_cleaning_step(
                        new_df=new_df,
                        action_name=f"إعادة تسمية: {target_ren_col} -> {new_ren_name}",
                        operator="rename_columns",
                        target_columns=[target_ren_col],
                        description=f"تم تغيير اسم العمود '{target_ren_col}' إلى '{new_ren_name}'.",
                    )
                    st.success("تم تغيير اسم العمود بنجاح.")
                    st.rerun()

        with c_op2:
            st.markdown("##### 🗑️ حذف الأعمدة غير المطلوبة")
            empty_cols_detected = [c for c in df.columns if df[c].isna().all()]
            if empty_cols_detected:
                st.warning(f"تم اكتشاف أعمدة فارغة بالكامل: {', '.join(empty_cols_detected)}")
                if st.button("حذف كافة الأعمدة الفارغة فوراً", type="primary", key="btn_drop_empty_cols"):
                    new_df, dropped = drop_empty_columns(df)
                    session.apply_cleaning_step(
                        new_df=new_df,
                        action_name="حذف الأعمدة الفارغة بالكامل",
                        operator="drop_empty_columns",
                        target_columns=dropped,
                        description=f"تم حذف {len(dropped)} أعمدة فارغة: {', '.join(dropped)}.",
                    )
                    st.success("تم حذف الأعمدة الفارغة.")
                    st.rerun()

            cols_to_del = st.multiselect("اختر أعمدة لحذفها يدوياً:", list(df.columns), key="del_manual_cols")
            if st.button("حذف الأعمدة المحددة", key="btn_drop_manual_cols") and cols_to_del:
                new_df, dropped_cnt = drop_columns(df, cols_to_del)
                session.apply_cleaning_step(
                    new_df=new_df,
                    action_name="حذف أعمدة",
                    operator="drop_columns",
                    target_columns=cols_to_del,
                    description=f"تم حذف {dropped_cnt} أعمدة.",
                )
                st.success(f"تم حذف {dropped_cnt} أعمدة.")
                st.rerun()

            st.markdown("##### 🔄 تحويل نوع البيانات (Data Type Casting)")
            cast_col = st.selectbox("العمود المراد تحويل نوعه:", list(df.columns), key="cast_col_sel")
            cast_type_choice = st.selectbox(
                "النوع الجديد المستهدف:",
                [
                    "integer (أرقام صحيحة)",
                    "float (أرقام عشرية)",
                    "string (نص)",
                    "boolean (منطقي True/False)",
                    "datetime (تاريخ ووقت)",
                ],
                key="cast_type_choice",
            )
            cast_code = cast_type_choice.split()[0]
            if st.button("تحويل نوع العمود", key="btn_cast_type"):
                new_df, success, msg = cast_column_dtype(df, cast_col, cast_code)
                if success:
                    session.apply_cleaning_step(
                        new_df=new_df,
                        action_name=f"تحويل نوع [{cast_col}] إلى {cast_code}",
                        operator="cast_column_dtype",
                        target_columns=[cast_col],
                        description=msg,
                    )
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    # ---------------- 5. DATES & NUMBERS ----------------
    with tab_nums_dates:
        st.subheader("معالجة التواريخ والقيم الرقمية والشاذة")

        d_col1, d_col2 = st.columns(2)
        with d_col1:
            st.markdown("##### 📅 توحيد صيغ التواريخ")
            date_candidates = list(df.columns)
            selected_date_cols = st.multiselect("اختر أعمدة التواريخ:", date_candidates, key="date_cols_sel")
            target_date_format = st.selectbox(
                "صيغة التاريخ الموحدة:",
                ["%Y-%m-%d (مثال: 2024-05-30)", "%d/%m/%Y (مثال: 30/05/2024)", "%m/%d/%Y (مثال: 05/30/2024)"],
                key="date_fmt_sel",
            )
            fmt_code = target_date_format.split()[0]

            if st.button("توحيد تنسيق التواريخ", key="btn_unify_dates") and selected_date_cols:
                new_df, formatted_cnt, invalid_cnt = standardize_dates(df, selected_date_cols, output_format=fmt_code)
                session.apply_cleaning_step(
                    new_df=new_df,
                    action_name="توحيد تنسيق التواريخ",
                    operator="standardize_dates",
                    target_columns=selected_date_cols,
                    parameters={"format": fmt_code},
                    cells_modified=formatted_cnt,
                    description=f"تم توحيد {formatted_cnt} تاريخ، وتحويل {invalid_cnt} تاريخ غير صالح إلى فارغ.",
                )
                st.success(f"تم توحيد {formatted_cnt} تاريخ بنجاح!")
                st.rerun()

        with d_col2:
            st.markdown("##### 📈 التعامل مع القيم الشاذة (Outliers)")
            numeric_cols = list(df.select_dtypes(include=["number"]).columns)
            if not numeric_cols:
                st.info("لا توجد أعمدة رقمية حالياً. يمكنك تحويل النصوص الرقمية لأرقام أولاً من تبويب الأعمدة.")
            else:
                outlier_col = st.selectbox("اختر العمود الرقمي:", numeric_cols, key="outlier_col_sel")
                outlier_action = st.selectbox(
                    "الإجراء المفضل للتعامل مع القيم الشاذة:",
                    [
                        "تحجيم القيم الشاذة إلى حدود النطاق الطبيعي (Clip/Capping)",
                        "استبدالها بالوسيط الحسابي (Replace with Median)",
                        "استبدالها بالمتوسط الحسابي (Replace with Mean)",
                        "حذف الصفوف المحتوية على قيم شاذة (Drop Rows)",
                    ],
                    key="outlier_action_sel",
                )
                action_code_map = {
                    "تحجيم القيم الشاذة إلى حدود النطاق الطبيعي (Clip/Capping)": "clip",
                    "استبدالها بالوسيط الحسابي (Replace with Median)": "replace_median",
                    "استبدالها بالمتوسط الحسابي (Replace with Mean)": "replace_mean",
                    "حذف الصفوف المحتوية على قيم شاذة (Drop Rows)": "drop_rows",
                }
                a_code = action_code_map[outlier_action]

                if st.button("معالجة القيم الشاذة", key="btn_handle_outliers"):
                    new_df, affected, msg = handle_outliers(df, outlier_col, method="iqr", action=a_code)
                    if affected > 0:
                        session.apply_cleaning_step(
                            new_df=new_df,
                            action_name=f"معالجة شواذ [{outlier_col}]",
                            operator="handle_outliers",
                            target_columns=[outlier_col],
                            parameters={"action": a_code},
                            cells_modified=affected,
                            description=msg,
                        )
                        st.success(msg)
                        st.rerun()
                    else:
                        st.info(msg)

    # Bottom Live Preview
    st.markdown("---")
    st.markdown("#### 👁️ معاينة تفاعلية لكافة صفوف البيانات أثناء العمل")
    render_paginated_table(df, key="cleaning_preview_table", default_page_size=50)
