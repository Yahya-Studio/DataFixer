"""Text cleaning, whitespace trimming, casing normalization, and find-and-replace."""

import re
from typing import Literal

import pandas as pd


def strip_and_normalize_whitespace(
    df: pd.DataFrame,
    columns: list[str],
    remove_inner_extra: bool = True,
) -> tuple[pd.DataFrame, int]:
    """Strip leading/trailing spaces and optionally normalize multiple consecutive inner spaces.

    Returns:
        (new_df, cells_modified)
    """
    new_df = df.copy()
    cells_modified = 0

    for col in columns:
        if col not in new_df.columns:
            continue
        s = new_df[col]
        # Only process object or string columns
        if not (s.dtype == object or pd.api.types.is_string_dtype(s)):
            continue

        def _clean_str(val):
            if not isinstance(val, str):
                return val
            res = val.strip()
            if remove_inner_extra:
                res = re.sub(r"\s+", " ", res)
            return res

        orig_vals = new_df[col].astype(str)
        cleaned = s.apply(_clean_str)
        changed_mask = (orig_vals != cleaned.astype(str)) & s.notna()
        cells_modified += int(changed_mask.sum())
        new_df[col] = cleaned

    return new_df, cells_modified


def change_case(
    df: pd.DataFrame,
    columns: list[str],
    case_type: Literal["lower", "upper", "title", "capitalize"],
) -> tuple[pd.DataFrame, int]:
    """Transform text case across selected columns.

    Returns:
        (new_df, cells_modified)
    """
    new_df = df.copy()
    cells_modified = 0

    for col in columns:
        if col not in new_df.columns:
            continue
        s = new_df[col]
        if not (s.dtype == object or pd.api.types.is_string_dtype(s)):
            continue

        def _transform(val):
            if not isinstance(val, str):
                return val
            if case_type == "lower":
                return val.lower()
            elif case_type == "upper":
                return val.upper()
            elif case_type == "title":
                return val.title()
            elif case_type == "capitalize":
                return val.capitalize()
            return val

        orig_vals = new_df[col].astype(str)
        transformed = s.apply(_transform)
        changed_mask = (orig_vals != transformed.astype(str)) & s.notna()
        cells_modified += int(changed_mask.sum())
        new_df[col] = transformed

    return new_df, cells_modified


def find_and_replace(
    df: pd.DataFrame,
    columns: list[str],
    find_pattern: str,
    replacement: str,
    is_regex: bool = False,
    case_sensitive: bool = True,
) -> tuple[pd.DataFrame, int]:
    """Find and replace substring or regex patterns in specified columns.

    Returns:
        (new_df, cells_modified)
    """
    new_df = df.copy()
    cells_modified = 0

    if not find_pattern:
        return new_df, 0

    flags = 0 if case_sensitive else re.IGNORECASE
    regex = re.compile(find_pattern if is_regex else re.escape(find_pattern), flags)

    for col in columns:
        if col not in new_df.columns:
            continue
        s = new_df[col]

        def _sub(val):
            if not isinstance(val, str):
                return val
            return regex.sub(replacement, val)

        orig_vals = new_df[col].astype(str)
        transformed = s.apply(_sub)
        changed_mask = (orig_vals != transformed.astype(str)) & s.notna()
        cells_modified += int(changed_mask.sum())
        new_df[col] = transformed

    return new_df, cells_modified


def standardize_category_values(
    df: pd.DataFrame,
    column: str,
    mapping: dict[str, str],
) -> tuple[pd.DataFrame, int]:
    """Standardize categorical values based on an explicit mapping dictionary.

    Returns:
        (new_df, cells_modified)
    """
    new_df = df.copy()
    if column not in new_df.columns:
        return new_df, 0

    orig = new_df[column].copy()
    new_df[column] = new_df[column].replace(mapping)
    modified = int((orig != new_df[column]).sum())
    return new_df, modified
