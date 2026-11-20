"""Handling of statistical outliers without silent data loss."""

from typing import Literal

import pandas as pd

from src.analysis.outliers import detect_outliers_iqr, detect_outliers_zscore


def handle_outliers(
    df: pd.DataFrame,
    column: str,
    method: Literal["iqr", "zscore"] = "iqr",
    action: Literal["clip", "replace_median", "replace_mean", "drop_rows"] = "clip",
) -> tuple[pd.DataFrame, int, str]:
    """Handle outliers in a numeric column safely and transparently.

    Returns:
        (new_df, affected_count, message)
    """
    if column not in df.columns:
        return df, 0, f"العمود '{column}' غير موجود."

    summary = detect_outliers_iqr(df[column]) if method == "iqr" else detect_outliers_zscore(df[column])
    if not summary or summary.count == 0:
        return df, 0, f"لم يتم العثور على قيم شاذة في العمود '{column}'."

    new_df = df.copy()
    lower, upper = summary.lower_bound, summary.upper_bound
    series = pd.to_numeric(new_df[column], errors="coerce")
    outlier_mask = (series < lower) | (series > upper)
    count = int(outlier_mask.sum())

    if action == "clip":
        new_df[column] = series.clip(lower=lower, upper=upper)
        msg = f"تم تحجيم (Capping) عدد {count} قيمة شاذة ضمن النطاق [{lower:.2f}, {upper:.2f}]."
    elif action == "replace_median":
        med = float(series[~outlier_mask].median())
        new_df.loc[outlier_mask, column] = med
        msg = f"تم استبدال {count} قيمة شاذة بالوسيط الحسابي ({med:.2f})."
    elif action == "replace_mean":
        mean_val = float(series[~outlier_mask].mean())
        new_df.loc[outlier_mask, column] = mean_val
        msg = f"تم استبدال {count} قيمة شاذة بالمتوسط الحسابي ({mean_val:.2f})."
    elif action == "drop_rows":
        new_df = new_df[~outlier_mask].copy().reset_index(drop=True)
        msg = f"تم حذف {count} صف تحتوي على قيم شاذة."
    else:
        msg = "إجراء غير معروف."

    return new_df, count, msg
