"""Column-level operations: renaming, dropping, reordering, and type casting."""

import re
from typing import Literal

import pandas as pd


def rename_columns(df: pd.DataFrame, rename_map: dict[str, str]) -> tuple[pd.DataFrame, int]:
    """Rename columns according to the provided mapping.

    Returns:
        (new_df, cols_renamed)
    """
    valid_map = {k: v.strip() for k, v in rename_map.items() if k in df.columns and v.strip()}
    new_df = df.rename(columns=valid_map)
    return new_df, len(valid_map)


def standardize_column_names(
    df: pd.DataFrame,
    style: Literal["snake_case", "lowercase", "uppercase", "camel_case"] = "snake_case",
) -> tuple[pd.DataFrame, int]:
    """Standardize all column headers (e.g. to snake_case, lowercase, trimmed).

    Returns:
        (new_df, cols_renamed)
    """
    new_columns = []
    renamed_count = 0

    for col in df.columns:
        c = str(col).strip()
        if style == "snake_case":
            # Replace spaces and punctuation with underscores, remove consecutive underscores
            s = re.sub(r"[^\w\s]", "", c)
            s = re.sub(r"\s+", "_", s).lower()
            s = re.sub(r"_+", "_", s).strip("_")
            target = s or f"col_{len(new_columns)}"
        elif style == "lowercase":
            target = c.lower()
        elif style == "uppercase":
            target = c.upper()
        elif style == "camel_case":
            words = re.sub(r"[^\w\s]", "", c).split()
            target = words[0].lower() + "".join(w.capitalize() for w in words[1:]) if words else c
        else:
            target = c

        if target != col:
            renamed_count += 1
        new_columns.append(target)

    # Resolve potential duplicate names caused by case normalization
    unique_columns = []
    seen = {}
    for c in new_columns:
        if c in seen:
            seen[c] += 1
            unique_columns.append(f"{c}_{seen[c]}")
        else:
            seen[c] = 0
            unique_columns.append(c)

    new_df = df.copy()
    new_df.columns = unique_columns
    return new_df, renamed_count


def drop_columns(df: pd.DataFrame, columns_to_drop: list[str]) -> tuple[pd.DataFrame, int]:
    """Drop selected columns from DataFrame.

    Returns:
        (new_df, cols_dropped)
    """
    valid_cols = [c for c in columns_to_drop if c in df.columns]
    new_df = df.drop(columns=valid_cols)
    return new_df, len(valid_cols)


def drop_empty_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Drop columns that are entirely NaN or empty strings.

    Returns:
        (new_df, dropped_col_names)
    """
    empty_cols = []
    common_nulls = {"", "nan", "none", "null", "n/a", "na", "-"}

    for col in df.columns:
        series = df[col]
        if series.isna().all() or (series.astype(str).str.strip().str.lower().isin(common_nulls)).all():
            empty_cols.append(col)

    new_df = df.drop(columns=empty_cols)
    return new_df, empty_cols


def reorder_columns(df: pd.DataFrame, ordered_columns: list[str]) -> pd.DataFrame:
    """Reorder columns while preserving any omitted columns at the end."""
    valid_ordered = [c for c in ordered_columns if c in df.columns]
    remaining = [c for c in df.columns if c not in valid_ordered]
    return df[valid_ordered + remaining].copy()


def cast_column_dtype(
    df: pd.DataFrame,
    column: str,
    target_type: Literal["integer", "float", "string", "boolean", "datetime"],
    date_format: str | None = None,
) -> tuple[pd.DataFrame, bool, str]:
    """Cast a column to target data type with safe error reporting.

    Returns:
        (new_df, success, message)
    """
    if column not in df.columns:
        return df, False, f"العمود '{column}' غير موجود."

    new_df = df.copy()
    try:
        s = new_df[column]
        if target_type == "integer":
            cleaned = pd.to_numeric(s.astype(str).str.replace(r"[$,€£% ]", "", regex=True), errors="coerce")
            new_df[column] = cleaned.astype("Int64")  # Nullable integer
        elif target_type == "float":
            cleaned = pd.to_numeric(s.astype(str).str.replace(r"[$,€£% ]", "", regex=True), errors="coerce")
            new_df[column] = cleaned.astype(float)
        elif target_type == "string":
            new_df[column] = s.astype(str)
        elif target_type == "boolean":
            # Map common truthy/falsy strings
            bool_map = {
                "true": True,
                "1": True,
                "yes": True,
                "y": True,
                "نعم": True,
                "صحيح": True,
                "false": False,
                "0": False,
                "no": False,
                "n": False,
                "لا": False,
                "خطأ": False,
            }
            new_df[column] = s.astype(str).str.strip().str.lower().map(bool_map)
        elif target_type == "datetime":
            new_df[column] = pd.to_datetime(s, format=date_format, errors="coerce")

        return new_df, True, f"تم تحويل نوع العمود '{column}' إلى {target_type} بنجاح."
    except Exception as e:
        return df, False, f"فشل تحويل نوع العمود: {e!s}"
