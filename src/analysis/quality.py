"""Comprehensive Data Quality Analyzer detecting all 11 core structural and semantic defects."""

import re

import pandas as pd

from src.analysis.outliers import scan_all_numeric_outliers
from src.core.schemas import QualityIssue, QualityScoreBreakdown
from src.core.scorer import QualityScorer


class QualityAnalyzer:
    """Detects 11 major data anomalies and computes an interpretable Data Quality Score."""

    COMMON_NULL_STRINGS = {"", "nan", "none", "null", "n/a", "na", "-", "--", "?", "nil", "undefined"}

    @classmethod
    def analyze_dataset(cls, df: pd.DataFrame) -> tuple[list[QualityIssue], QualityScoreBreakdown]:
        """Perform comprehensive quality evaluation across all 11 problem types."""
        issues: list[QualityIssue] = []
        num_rows = len(df)
        num_cols = len(df.columns)

        if num_rows == 0 or num_cols == 0:
            return issues, QualityScorer.calculate_score(0, 0, [])

        # 1. Check duplicate column names
        col_names = list(df.columns)
        seen_cols = set()
        dup_cols = []
        for c in col_names:
            c_norm = str(c).strip().lower()
            if c_norm in seen_cols:
                dup_cols.append(str(c))
            else:
                seen_cols.add(c_norm)

        if dup_cols:
            issues.append(
                QualityIssue(
                    id="dup_cols",
                    category="headers",
                    title="أسماء أعمدة مكررة",
                    description=f"يحتوي الجدول على أعمدة مكررة الأسماء أو متطابقة عند تجاهل حالة الأحرف: {', '.join(dup_cols)}",
                    affected_count=len(dup_cols),
                    affected_ratio=len(dup_cols) / num_cols,
                    severity="high",
                    recommendation="إعادة تسمية الأعمدة المكررة لتمييزها وتجنب تضارب العمليات الحسابية.",
                )
            )

        # 2. Entirely empty columns
        empty_cols = []
        for col in df.columns:
            series = df[col]
            if series.isna().all() or (series.astype(str).str.strip().isin(cls.COMMON_NULL_STRINGS)).all():
                empty_cols.append(str(col))

        if empty_cols:
            issues.append(
                QualityIssue(
                    id="empty_columns",
                    category="empty_col",
                    title="أعمدة فارغة بالكامل",
                    description=f"تم اكتشاف {len(empty_cols)} عمود لا يحتوي على أي بيانات مفيدة: {', '.join(empty_cols)}",
                    affected_count=len(empty_cols),
                    affected_ratio=len(empty_cols) / num_cols,
                    severity="high",
                    recommendation="حذف الأعمدة الفارغة لتخفيف حجم البيانات وتسريع المعالجة.",
                )
            )

        # 3. Entirely empty rows
        empty_row_mask = df.isna().all(axis=1) | (
            df.astype(str).apply(lambda row: row.str.strip().isin(cls.COMMON_NULL_STRINGS).all(), axis=1)
        )
        empty_rows_count = int(empty_row_mask.sum())
        if empty_rows_count > 0:
            issues.append(
                QualityIssue(
                    id="empty_rows",
                    category="empty_row",
                    title="صفوف فارغة بالكامل",
                    description=f"يوجد {empty_rows_count} صف فارغ تماماً من أي قيم مفيدة.",
                    affected_count=empty_rows_count,
                    affected_ratio=empty_rows_count / num_rows,
                    severity="high",
                    recommendation="حذف الصفوف الفارغة بالكامل تلقائياً لتحسين جودة النموذج والتحليل.",
                    sample_indices=df[empty_row_mask].index[:10].tolist(),
                )
            )

        # 4. Duplicate rows (excluding fully empty ones)
        non_empty_df = df[~empty_row_mask]
        dup_rows_count = int(non_empty_df.duplicated().sum())
        if dup_rows_count > 0:
            sample_dups = non_empty_df[non_empty_df.duplicated(keep=False)].index[:10].tolist()
            issues.append(
                QualityIssue(
                    id="duplicate_rows",
                    category="duplicates",
                    title="صفوف مكررة",
                    description=f"يحتوي الملف على {dup_rows_count} صف مكرر بالكامل ومطابق لصفوف أخرى.",
                    affected_count=dup_rows_count,
                    affected_ratio=dup_rows_count / num_rows,
                    severity="medium",
                    recommendation="إزالة التكرارات مع الاحتفاظ بالنسخة الأولى لضمان دقة المؤشرات الإحصائية.",
                    sample_indices=sample_dups,
                )
            )

        # 5. Missing / Empty values per column (excluding completely empty columns)
        for col in df.columns:
            if col in empty_cols:
                continue
            series = df[col]
            missing_mask = series.isna()
            if series.dtype == object or str(series.dtype) == "string":
                str_s = series.astype(str).str.strip().str.lower()
                missing_mask = missing_mask | str_s.isin(cls.COMMON_NULL_STRINGS)

            missing_count = int(missing_mask.sum())
            if missing_count > 0:
                ratio = missing_count / num_rows
                severity = "high" if ratio > 0.3 else ("medium" if ratio > 0.05 else "low")
                issues.append(
                    QualityIssue(
                        id=f"missing_{col}",
                        category="missing",
                        title=f"قيم مفقودة في عمود [{col}]",
                        description=f"العمود '{col}' يحتوي على {missing_count} قيمة مفقودة أو فارغة بنسبة {ratio * 100:.1f}%.",
                        affected_column=str(col),
                        affected_count=missing_count,
                        affected_ratio=ratio,
                        severity=severity,
                        recommendation="تعويض القيم المفقودة (المتوسط، الوسيط، المنوال) أو حذف الصفوف المتأثرة.",
                        sample_indices=df[missing_mask].index[:10].tolist(),
                    )
                )

        # 6. Text columns: Whitespace & Casing & Categories
        text_cols = df.select_dtypes(include=["object", "string"]).columns
        for col in text_cols:
            if col in empty_cols:
                continue
            clean_s = df[col].dropna().astype(str)
            if len(clean_s) == 0:
                continue

            # 6.1 Whitespace issues (leading, trailing, or double inner space)
            has_edge_spaces = clean_s.str.startswith(" ") | clean_s.str.endswith(" ")
            has_double_spaces = clean_s.str.contains(r"\s{2,}", regex=True)
            whitespace_mask = has_edge_spaces | has_double_spaces
            whitespace_count = int(whitespace_mask.sum())

            if whitespace_count > 0:
                issues.append(
                    QualityIssue(
                        id=f"whitespace_{col}",
                        category="whitespace",
                        title=f"مسافات زائدة في نصوص [{col}]",
                        description=f"تم اكتشاف {whitespace_count} نص يحتوي على مسافات زائدة في البداية أو النهاية أو مسافات مزدوجة.",
                        affected_column=str(col),
                        affected_count=whitespace_count,
                        affected_ratio=whitespace_count / num_rows,
                        severity="low",
                        recommendation="إزالة المسافات الزائدة (Trim & Normalize Whitespace) لتوحيد المقارنات.",
                        sample_indices=clean_s[whitespace_mask].index[:10].tolist(),
                    )
                )

            # 6.2 Casing Inconsistency in Categorical columns
            # Unique raw values vs unique lowercase values
            raw_unique = clean_s.str.strip().unique()
            lower_unique = {v.lower() for v in raw_unique}
            if len(raw_unique) > len(lower_unique) and len(raw_unique) < 200:
                diff_count = len(raw_unique) - len(lower_unique)
                issues.append(
                    QualityIssue(
                        id=f"casing_{col}",
                        category="casing",
                        title=f"تفاوت في حالة الأحرف في [{col}]",
                        description=f"يوجد تفاوت في كتابة الحروف لنفس التصنيفات (مثال: Active مقابل active) بتكرار {diff_count} حالات.",
                        affected_column=str(col),
                        affected_count=diff_count,
                        affected_ratio=diff_count / max(1, len(raw_unique)),
                        severity="medium",
                        recommendation="توحيد حالة الأحرف (Lowercase / Uppercase / Titlecase) لضمان دقة التصنيف.",
                    )
                )

            # 6.3 Detect numbers stored as text (Type issue)
            # Check if >70% of non-null string entries can be converted to float/int
            numeric_like = pd.to_numeric(clean_s.str.replace(r"[$,€£% ]", "", regex=True), errors="coerce").notna()
            num_convertible = int(numeric_like.sum())
            if num_convertible > 0 and (num_convertible / len(clean_s)) >= 0.75:
                issues.append(
                    QualityIssue(
                        id=f"type_numeric_{col}",
                        category="types",
                        title=f"بيانات رقمية مخزنة كنص في [{col}]",
                        description=f"{num_convertible} قيمة من أصل {len(clean_s)} في العمود تمثل أرقاماً لكنها مسجلة كنصوص.",
                        affected_column=str(col),
                        affected_count=num_convertible,
                        affected_ratio=num_convertible / num_rows,
                        severity="medium",
                        recommendation="تحويل نوع العمود إلى رقمي (Integer أو Float) للتمكن من إجراء العمليات الحسابية.",
                    )
                )

            # 6.4 Detect dates stored as text / inconsistent dates
            if col not in empty_cols:
                cls._check_date_issues(df, col, clean_s, num_rows, issues)

        # 7. Outliers in numeric columns
        outliers_dict = scan_all_numeric_outliers(df, method="iqr")
        for col, summary in outliers_dict.items():
            if summary.count > 0:
                issues.append(
                    QualityIssue(
                        id=f"outlier_{col}",
                        category="outliers",
                        title=f"قيم شاذة (Outliers) في [{col}]",
                        description=f"تم اكتشاف {summary.count} قيمة تتجاوز النطاق الطبيعي [{summary.lower_bound:.1f} إلى {summary.upper_bound:.1f}] بحسب تحليل IQR.",
                        affected_column=str(col),
                        affected_count=summary.count,
                        affected_ratio=summary.ratio,
                        severity="low" if summary.ratio < 0.05 else "medium",
                        recommendation="معاينة القيم الشاذة لتحديد ما إذا كانت أخطاء إدخال أو قيماً حقيقية، مع إمكانية تحجيمها (Clipping).",
                        sample_indices=summary.sample_indices,
                    )
                )

        score_breakdown = QualityScorer.calculate_score(num_rows, num_cols, issues)
        return issues, score_breakdown

    @classmethod
    def _check_date_issues(
        cls,
        df: pd.DataFrame,
        col: str,
        clean_s: pd.Series,
        num_rows: int,
        issues: list[QualityIssue],
    ) -> None:
        """Heuristic to detect date columns stored as strings with inconsistent formats or unparseable dates."""
        col_lower = str(col).lower()
        date_keywords = ["date", "time", "day", "created", "updated", "birth", "expiry", "تاريخ", "يوم", "وقت"]
        is_date_col_name = any(k in col_lower for k in date_keywords)

        # Sample values to check date pattern
        sample_s = clean_s.iloc[: min(len(clean_s), 100)]
        date_pattern = re.compile(r"^\d{4}[-/.]\d{1,2}[-/.]\d{1,2}|^\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}")
        matches_pattern = sample_s.apply(lambda x: bool(date_pattern.search(str(x))))

        if is_date_col_name or matches_pattern.mean() > 0.4:
            # Attempt parsing
            parsed = pd.to_datetime(clean_s, errors="coerce", format="mixed")
            invalid_count = int(parsed.isna().sum())
            valid_count = int(parsed.notna().sum())

            if valid_count > 0 and invalid_count > 0:
                ratio = invalid_count / len(clean_s)
                issues.append(
                    QualityIssue(
                        id=f"invalid_dates_{col}",
                        category="dates",
                        title=f"تواريخ غير صالحة أو غير متسقة في [{col}]",
                        description=f"العمود يحتوي على {invalid_count} قيمة لا تطابق صيغ التواريخ القياسية أو فشل تحليلها.",
                        affected_column=str(col),
                        affected_count=invalid_count,
                        affected_ratio=ratio,
                        severity="medium",
                        recommendation="توحيد تنسيق التواريخ إلى YYYY-MM-DD ومعالجة التواريخ المعطوبة.",
                        sample_indices=clean_s[parsed.isna()].index[:10].tolist(),
                    )
                )
            elif valid_count > 0 and not pd.api.types.is_datetime64_any_dtype(df[col]):
                # Entire column is dates but typed as object
                issues.append(
                    QualityIssue(
                        id=f"unconverted_date_{col}",
                        category="types",
                        title=f"تواريخ مخزنة كنص في [{col}]",
                        description=f"العمود '{col}' يحتوي على تواريخ صالحة لكنه مسجل كنوع نصي (Object).",
                        affected_column=str(col),
                        affected_count=valid_count,
                        affected_ratio=valid_count / num_rows,
                        severity="low",
                        recommendation="تحويل نوع البيانات إلى Datetime لتسهيل التصفية والتحليلات الزمنية.",
                    )
                )
