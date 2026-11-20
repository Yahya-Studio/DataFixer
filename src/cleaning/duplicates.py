"""Deduplication operators for datasets."""

from typing import Literal

import pandas as pd


def remove_duplicates(
    df: pd.DataFrame,
    subset: list[str] | None = None,
    keep: Literal["first", "last", False] = "first",
) -> tuple[pd.DataFrame, int]:
    """Remove duplicate records from DataFrame.

    keep can be:
    - 'first': Keep first occurrence, drop subsequent duplicates.
    - 'last': Keep last occurrence.
    - False: Drop all duplicate occurrences completely.

    Returns:
        (new_df, rows_removed)
    """
    valid_subset = [c for c in (subset or df.columns) if c in df.columns]
    if not valid_subset:
        valid_subset = list(df.columns)

    dup_mask = df.duplicated(subset=valid_subset, keep=keep)
    rows_removed = int(dup_mask.sum())

    new_df = df[~dup_mask].copy().reset_index(drop=True)
    return new_df, rows_removed
