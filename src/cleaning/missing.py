"""Missing value handling strategies: drop, fill constant, mean, median, mode."""

from typing import Any

import numpy as np
import pandas as pd


def drop_missing_values(
    df: pd.DataFrame,
    how: str = "any",  # "any" or "all"
    subset: list[str] | None = None,
) -> tuple[pd.DataFrame, int, int]:
    """Drop rows containing missing values.

    Returns:
        (new_df, rows_removed, cells_modified)
    """
    valid_cols = [c for c in (subset or df.columns) if c in df.columns]
    if not valid_cols:
        return df.copy(), 0, 0

    mask = df[valid_cols].isna().any(axis=1) if how == "any" else df[valid_cols].isna().all(axis=1)
    rows_removed = int(mask.sum())

    # Cells affected
    cells_affected = int(df.loc[mask, valid_cols].isna().sum().sum())
    new_df = df[~mask].copy().reset_index(drop=True)
    return new_df, rows_removed, cells_affected


def fill_missing_values(
    df: pd.DataFrame,
    columns: list[str],
    strategy: str = "custom",  # "custom", "mean", "median", "mode", "ffill", "bfill"
    fill_value: Any | None = None,
) -> tuple[pd.DataFrame, int]:
    """Fill missing values across specified columns using chosen strategy.

    Returns:
        (new_df, cells_modified)
    """
    new_df = df.copy()
    total_modified = 0

    for col in columns:
        if col not in new_df.columns:
            continue

        s = new_df[col]
        null_mask = s.isna()
        col_null_count = int(null_mask.sum())
        if col_null_count == 0:
            continue

        replacement = None
        if strategy == "custom":
            replacement = fill_value
        elif strategy == "mean" and pd.api.types.is_numeric_dtype(s):
            mean_val = s.dropna().mean()
            if not np.isnan(mean_val):
                replacement = round(mean_val, 4)
        elif strategy == "median" and pd.api.types.is_numeric_dtype(s):
            med_val = s.dropna().median()
            if not np.isnan(med_val):
                replacement = med_val
        elif strategy == "mode":
            mode_s = s.dropna().mode()
            if not mode_s.empty:
                replacement = mode_s.iloc[0]
        elif strategy == "ffill":
            new_df[col] = s.ffill()
            total_modified += col_null_count
            continue
        elif strategy == "bfill":
            new_df[col] = s.bfill()
            total_modified += col_null_count
            continue

        if replacement is not None:
            new_df[col] = s.fillna(replacement)
            total_modified += col_null_count

    return new_df, total_modified
